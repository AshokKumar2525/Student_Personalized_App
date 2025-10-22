from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.learning_pathfinder import (
    UserProfile, LearningPath, PathModule, ModuleResource, 
    UserProgress, Domain, Technology, Course
)
from app.models.users import User
from openai import OpenAI
from mistralai import Mistral
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os
import json
import re
from datetime import datetime
import requests

learning_pathfinder_bp = Blueprint('learning_pathfinder', __name__)

@learning_pathfinder_bp.route('/learning-path/generate-roadmap', methods=['POST'])
def generate_learning_path():
    try:
        data = request.get_json()
        firebase_uid = data.get('firebase_uid')
        domain = data.get('domain')
        knowledge_level = data.get('knowledge_level')
        familiar_techs = data.get('familiar_techs', [])
        weekly_hours = data.get('weekly_hours', 5)
        learning_pace = data.get('learning_pace', 'medium')

        if not all([firebase_uid, domain, knowledge_level]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Get or create user
        user = User.query.filter_by(id=firebase_uid).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get domain from database
        domain_obj = Domain.query.filter_by(name=domain).first()
        if not domain_obj:
            domain_obj = Domain(name=domain, description=f"Learning path for {domain}")
            db.session.add(domain_obj)
            db.session.commit()

        # Generate roadmap using APIs in order: OpenAI → Mistral → Mock Data
        current_app.logger.info("🚀 Generating roadmap with APIs...")
        roadmap_data = None
        
        # First try: OpenAI
        current_app.logger.info("🟢 Trying OpenAI API first...")
        roadmap_data = generate_roadmap_with_openai(
            domain, knowledge_level, familiar_techs, weekly_hours, learning_pace
        )
        
        # Second try: Mistral if OpenAI fails
        if not roadmap_data:
            current_app.logger.info("🟡 OpenAI failed, trying Mistral API...")
            roadmap_data = generate_roadmap_with_mistral(
                domain, knowledge_level, familiar_techs, weekly_hours, learning_pace
            )
        
        if not roadmap_data:
            current_app.logger.info("🟡 mistral failed, try with groq api...")
            roadmap_data = generate_roadmap_with_groq(
                domain, knowledge_level, familiar_techs, weekly_hours, learning_pace
            )
        
        # Final fallback: Structured mock data
        if not roadmap_data:
            current_app.logger.warning("🔴 Both APIs failed, using structured mock data")
            roadmap_data = get_structured_mock_data(domain, knowledge_level)

        # Enhance roadmap with YouTube videos
        roadmap_data = enhance_roadmap_with_youtube_videos(roadmap_data)

        # Create or update user profile
        profile = UserProfile.query.filter_by(user_id=user.id).first()
        if not profile:
            profile = UserProfile(
                id=user.id,
                user_id=user.id,
                domain_id=domain_obj.id,
                current_level=knowledge_level,
                familiar_techs=[],
                daily_time=weekly_hours * 60 // 7,
                learning_pace=learning_pace
            )
            db.session.add(profile)
        else:
            profile.domain_id = domain_obj.id
            profile.current_level = knowledge_level
            profile.daily_time = weekly_hours * 60 // 7
            profile.learning_pace = learning_pace

        # Create learning path
        learning_path = LearningPath(
            user_id=user.id,
            domain_id=domain_obj.id,
            current_version=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(learning_path)
        db.session.flush()

        # Create courses and modules from roadmap data
        courses_data = roadmap_data.get('courses', [])
        total_modules = 0
        
        for course_data in courses_data:
            course = Course(
                path_id=learning_path.id,
                title=course_data['title'],
                description=course_data['description'],
                order=course_data['order'],
                estimated_time=course_data.get('estimated_time', 0),
                created_at=datetime.utcnow()
            )
            db.session.add(course)
            db.session.flush()

            # Create modules for this course
            modules_data = course_data.get('modules', [])
            for module_data in modules_data:
                module = PathModule(
                    course_id=course.id,
                    path_id=learning_path.id,
                    title=module_data['title'],
                    description=module_data['description'],
                    order=module_data['order'],
                    estimated_time=module_data.get('estimated_time', 60),
                    created_at=datetime.utcnow()
                )
                db.session.add(module)
                db.session.flush()
                total_modules += 1

                # Create module resources with YouTube videos
                resources_data = module_data.get('resources', [])
                for resource_data in resources_data:
                    resource = ModuleResource(
                        module_id=module.id,
                        title=resource_data['title'],
                        url=resource_data['url'],
                        type=resource_data['type'],
                        difficulty=resource_data.get('difficulty', 'beginner'),
                        created_at=datetime.utcnow()
                    )
                    db.session.add(resource)

                # Create initial progress record
                progress = UserProgress(
                    user_id=user.id,
                    module_id=module.id,
                    profile_id=profile.id,
                    status='not_started',
                    created_at=datetime.utcnow()
                )
                db.session.add(progress)

        db.session.commit()

        return jsonify({
            'message': 'Learning path generated successfully',
            'path_id': learning_path.id, 
            'domain': domain,
            'roadmap': roadmap_data
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error generating learning path: {str(e)}")
        return jsonify({'error': 'Failed to generate learning path'}), 500

def enhance_roadmap_with_youtube_videos(roadmap_data):
    """Enhance roadmap modules with YouTube videos and educational content"""
    try:
        for course in roadmap_data.get('courses', []):
            for module in course.get('modules', []):
                # Get video resources with better error handling
                video_resources = get_video_resources(module['title'], max_results=2)
                
                # Add educational content
                educational_content = generate_educational_content(module['title'], module['description'])
                module['educational_content'] = educational_content
                
                # Add video resources to module
                module['resources'] = video_resources + module.get('resources', [])
                
        return roadmap_data
    except Exception as e:
        current_app.logger.error(f"Error enhancing roadmap with YouTube: {str(e)}")
        return roadmap_data

def get_video_resources(topic, max_results=3):
    """Get video resources with proper error handling"""
    try:
        youtube_videos = search_youtube_videos(topic, max_results)
        if youtube_videos:
            return process_youtube_videos(youtube_videos)
    except Exception as e:
        current_app.logger.error(f"YouTube API failed: {e}")
    
    # Fallback to mock videos
    return get_mock_video_resources(topic, max_results)

def process_youtube_videos(youtube_items):
    """Process YouTube API response into our format"""
    video_resources = []
    
    for i, item in enumerate(youtube_items):
        try:
            video_id = item['id']['videoId']
            snippet = item['snippet']
            
            video_resources.append({
                'id': i + 1,
                'title': snippet['title'],
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'embed_url': f"https://www.youtube.com/embed/{video_id}",
                'type': 'video',
                'source': 'youtube',
                'description': snippet.get('description', ''),
                'thumbnail': snippet['thumbnails']['default']['url'],
                'channel': snippet['channelTitle'],
                'difficulty': 'beginner'
            })
        except Exception as e:
            current_app.logger.error(f"Error processing YouTube video: {e}")
            continue
    
    return video_resources

def get_mock_video_resources(topic, max_results=3):
    """Provide better mock video data"""
    mock_videos = [
        {
            'id': 1,
            'title': f'Complete {topic} Tutorial - Beginner Guide',
            'url': 'https://www.youtube.com/watch?v=example1',
            'embed_url': 'https://www.youtube.com/embed/example1',
            'type': 'video',
            'source': 'youtube',
            'description': f'Learn {topic} step by step',
            'thumbnail': '',
            'channel': 'Programming Tutorials',
            'difficulty': 'beginner'
        },
        {
            'id': 2,
            'title': f'{topic} Crash Course - Hands On',
            'url': 'https://www.youtube.com/watch?v=example2',
            'embed_url': 'https://www.youtube.com/embed/example2',
            'type': 'video',
            'source': 'youtube',
            'description': f'Practical {topic} examples',
            'thumbnail': '',
            'channel': 'Code Academy',
            'difficulty': 'beginner'
        }
    ]
    return mock_videos[:max_results]

def search_youtube_videos(query, max_results=3):
    """Search YouTube videos with better error handling"""
    try:
        # Check if API key is available
        YOUTUBE_API_KEY=os.getenv("YOUTUBE_API_KEY")
        if not YOUTUBE_API_KEY:
            current_app.logger.warning("YouTube API key not configured, using mock data")
            return get_mock_videos(query, max_results)
            
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        search_response = youtube.search().list(
            q=f"{query} programming tutorial",
            part='snippet',
            maxResults=max_results,
            type='video',
            videoDuration='medium',
            relevanceLanguage='en',
            safeSearch='moderate'
        ).execute()
        
        return search_response.get('items', [])
        
    except HttpError as e:
        current_app.logger.error(f"YouTube API HTTP error: {e}")
        return get_mock_videos(query, max_results)
    except Exception as e:
        current_app.logger.info("🟢 Sending request to OpenAI...")
        return get_mock_videos(query, max_results)

def get_mock_videos(topic, max_results=3):
    """Provide mock video data when YouTube API fails"""
    mock_videos = [
        {
            'id': {'videoId': 'dQw4w9WgXcQ'},
            'snippet': {
                'title': f'Complete {topic} Tutorial - Beginner to Advanced',
                'channelTitle': 'Programming Tutorials',
                'thumbnails': {'default': {'url': ''}}
            }
        },
        {
            'id': {'videoId': 'dQw4w9WgXcQ'},
            'snippet': {
                'title': f'Learn {topic} Step by Step',
                'channelTitle': 'Code Academy', 
                'thumbnails': {'default': {'url': ''}}
            }
        },
        {
            'id': {'videoId': 'dQw4w9WgXcQ'},
            'snippet': {
                'title': f'{topic} Crash Course',
                'channelTitle': 'Web Dev Simplified',
                'thumbnails': {'default': {'url': ''}}
            }
        }
    ]
    return mock_videos[:max_results]

def get_fallback_youtube_links(query):
    """Provide fallback YouTube links when API fails"""
    # These are generic search links as fallback
    search_query = query.replace(' ', '+')
    return [{
        'title': f'{query} Tutorial',
        'url': f'https://www.youtube.com/results?search_query={search_query}+tutorial',
        'embed_url': None,
        'type': 'video',
        'source': 'youtube',
        'description': f'Search results for {query} tutorials',
        'thumbnail': None,
        'channel': 'YouTube Search'
    }]

def generate_educational_content(topic, description):
    """Generate educational content with multiple API fallbacks"""
    # 1. Try OpenAI first
    try:
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            client = OpenAI(api_key=openai_api_key)
            
            prompt = f"""
            Create concise educational content for: {topic}
            
            Description: {description}
            
            Provide a brief explanation (2-3 paragraphs max), 2-3 key concepts with simple explanations,
            1-2 practical examples, and 1-2 practice problems.
            
            Format as JSON with:
            - explanation: Brief overview of the concept
            - key_concepts: Array of key points with simple explanations
            - examples: Practical, simple examples
            - practice_problems: 1-2 problems to practice
            
            Keep it very concise and beginner-friendly.
            """
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a helpful teacher. Create very concise educational content. Return valid JSON only."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            content_text = response.choices[0].message.content
            return json.loads(content_text)
    except Exception as e:
        current_app.logger.error(f"OpenAI educational content error: {str(e)}")
    
    # 2. Try Groq as fallback
    try:
        groq_content = generate_educational_content_with_groq(topic, description)
        if groq_content:
            return groq_content
    except Exception as e:
        current_app.logger.error(f"Groq educational content error: {str(e)}")
    
    # 3. Final fallback
    return get_fallback_educational_content(topic)

def get_fallback_educational_content(topic):
    """Provide fallback educational content"""
    return {
        "explanation": f"{topic} is an important concept to learn. This module will help you understand the fundamentals through practical examples.",
        "key_concepts": [
            f"Understanding basic {topic} principles",
            f"Practical application of {topic}",
            f"Common use cases and best practices"
        ],
        "examples": [
            f"Example 1: Basic {topic} implementation",
            f"Example 2: Real-world {topic} scenario"
        ],
        "practice_problems": [
            f"Practice: Implement a simple {topic}",
            f"Challenge: Solve a problem using {topic}"
        ]
    }


def generate_roadmap_with_openai(domain, knowledge_level, familiar_techs, weekly_hours, learning_pace):
    """Generate learning roadmap using OpenAI API"""
    try:
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            current_app.logger.error("OpenAI API key not configured")
            return None
        
        client = OpenAI(api_key=openai_api_key)
        
        prompt = f"""
        Create a comprehensive learning roadmap for {domain} at {knowledge_level} level.
        
        Requirements:
        - Create 6-8 courses total
        - Each course should have 5-8 modules
        - Each module should have 2-3 learning resources
        - Include practical projects and assessments
        - Structure should progress from beginner to advanced
        
        Student profile:
        - Level: {knowledge_level}
        - Weekly study time: {weekly_hours} hours  
        - Learning pace: {learning_pace}
        - Familiar with: {', '.join(familiar_techs) if familiar_techs else 'Nothing yet'}
        
        Return ONLY valid JSON with this exact structure:
        {{
            "domain": "{domain}",
            "domain_name": "{domain.title()} Development",
            "level": "{knowledge_level}",
            "estimated_completion": "X weeks",
            "progress_percentage": 0.0,
            "completed_modules": 0,
            "total_modules": 45,
            "courses": [
                {{
                    "id": 1,
                    "title": "Course Title",
                    "description": "What this course covers",
                    "order": 1,
                    "estimated_time": 600,
                    "modules": [
                        {{
                            "id": 1,
                            "title": "Module title",
                            "description": "What will be learned",
                            "order": 1,
                            "estimated_time": 120,
                            "status": "not_started",
                            "resources": [
                                {{
                                    "id": 1,
                                    "title": "Resource title",
                                    "url": "https://example.com/learn",
                                    "type": "video",
                                    "difficulty": "beginner"
                                }},
                                {{
                                    "id": 2,
                                    "title": "Practice Exercise",
                                    "url": "https://example.com/exercise",
                                    "type": "exercise",
                                    "difficulty": "beginner"
                                }}
                            ]
                        }}
                    ]
                }}
            ]
        }}
        
        Important: Return ONLY the JSON object, no additional text.
        Keep the response focused and within token limits.
        """
        
        current_app.logger.info("🟢 Sending request to OpenAI...")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert curriculum designer. Always return COMPLETE, valid JSON format without any additional text. Ensure all JSON braces and brackets are properly closed. Create 6-8 courses with 5-8 modules each."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1500,  # Increased for larger structure
            response_format={"type": "json_object"}
        )
        
        roadmap_text = response.choices[0].message.content
        current_app.logger.info(f"📄 OpenAI raw response length: {len(roadmap_text)}")
        
        # Parse the JSON response
        roadmap_data = json.loads(roadmap_text)
        return validate_and_complete_roadmap(roadmap_data)
        
    except Exception as e:
        current_app.logger.error(f"❌ OpenAI API error: {str(e)}")
        return None

def generate_roadmap_with_mistral(domain, knowledge_level, familiar_techs, weekly_hours, learning_pace):
    """Generate learning roadmap using Mistral API"""
    try:
        mistral_api_key = os.getenv('MISTRAL_API_KEY')
        if not mistral_api_key:
            current_app.logger.error("Mistral API key not configured")
            return None
        
        client = Mistral(api_key=mistral_api_key)
        
        prompt = f"""
        Create a comprehensive learning roadmap for {domain} at {knowledge_level} level.
        
        Requirements:
        - Create 6-8 courses total
        - Each course should have 5-8 modules
        - Each module should have 2-3 learning resources
        - Keep descriptions VERY concise (1 line each)
        - Use short, clear titles
        - Include practical projects and assessments
        - Structure should progress from beginner to advanced
        
        Student profile:
        - Level: {knowledge_level}
        - Weekly study time: {weekly_hours} hours  
        - Learning pace: {learning_pace}
        - Familiar with: {', '.join(familiar_techs) if familiar_techs else 'Nothing yet'}
        
        Return ONLY this JSON structure:
        {{
            "domain": "{domain}",
            "domain_name": "{domain.title()} Development",
            "level": "{knowledge_level}",
            "estimated_completion": "X weeks",
            "progress_percentage": 0.0,
            "completed_modules": 0,
            "total_modules": 30,
            "courses": [
                {{
                    "id": 1,
                    "title": "Short Course Title",
                    "description": "Brief description",
                    "order": 1,
                    "estimated_time": 600,
                    "modules": [
                        {{
                            "id": 1,
                            "title": "Short Module Title",
                            "description": "Brief learning objective",
                            "order": 1,
                            "estimated_time": 120,
                            "status": "not_started",
                            "resources": [
                                {{
                                    "id": 1,
                                    "title": "Resource Name",
                                    "url": "https://example.com/1",
                                    "type": "video",
                                    "difficulty": "beginner"
                                }}
                            ]
                        }}
                    ]
                }}
            ]
        }}
        
        IMPORTANT: 
        - Use VERY short titles and descriptions
        - Ensure JSON is complete and valid
        - Include ALL closing braces and brackets
        - Keep the response focused and within token limits
        """
        
        current_app.logger.info("🟡 Sending request to Mistral AI...")
        
        response = client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert curriculum designer. Always return COMPLETE, valid JSON format without any additional text. Ensure all JSON braces and brackets are properly closed. Create 6-8 courses with 5-8 modules each."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000,  # Mistral has more generous limits
        )
        
        roadmap_text = response.choices[0].message.content
        current_app.logger.info(f"📄 Mistral raw response length: {len(roadmap_text)}")
        
        # Parse the JSON response
        roadmap_data = parse_roadmap_json(roadmap_text)
        
        if roadmap_data:
            # Validate we have enough content
            if validate_roadmap_structure(roadmap_data):
                return validate_and_complete_roadmap(roadmap_data)
            else:
                current_app.logger.warning("Mistral response has insufficient structure")
        
        return None
        
    except Exception as e:
        current_app.logger.error(f"❌ Mistral API error: {str(e)}")
        return None
    
def validate_roadmap_structure(roadmap_data):
    """Check if roadmap has minimum required structure"""
    if not isinstance(roadmap_data, dict):
        return False
    
    if 'courses' not in roadmap_data or not isinstance(roadmap_data['courses'], list):
        return False
    
    if len(roadmap_data['courses']) < 3:  # Require at least 3 courses
        return False
    
    # Check each course has modules
    for course in roadmap_data['courses']:
        if 'modules' not in course or not isinstance(course['modules'], list):
            return False
        if len(course['modules']) < 3:  # Require at least 3 modules per course
            return False
    
    return True

def generate_roadmap_with_groq(domain, knowledge_level, familiar_techs, weekly_hours, learning_pace):
    """Generate learning roadmap using Groq API"""
    try:
        from groq import Groq
        
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            current_app.logger.error("Groq API key not configured")
            return None
        
        client = Groq(api_key=groq_api_key)
        
        prompt = f"""
        Create a comprehensive learning roadmap for {domain} at {knowledge_level} level.
        
        Requirements:
        - Create 6-8 courses total
        - Each course should have 5-8 modules
        - Each module should have 2-3 learning resources
        - Include practical projects and assessments
        - Structure should progress from beginner to advanced
        
        Student profile:
        - Level: {knowledge_level}
        - Weekly study time: {weekly_hours} hours  
        - Learning pace: {learning_pace}
        - Familiar with: {', '.join(familiar_techs) if familiar_techs else 'Nothing yet'}
        
        Return ONLY valid JSON with this exact structure:
        {{
            "domain": "{domain}",
            "domain_name": "{domain.title()} Development",
            "level": "{knowledge_level}",
            "estimated_completion": "X weeks",
            "progress_percentage": 0.0,
            "completed_modules": 0,
            "total_modules": 45,
            "courses": [
                {{
                    "id": 1,
                    "title": "Course Title",
                    "description": "What this course covers",
                    "order": 1,
                    "estimated_time": 600,
                    "modules": [
                        {{
                            "id": 1,
                            "title": "Module title",
                            "description": "What will be learned",
                            "order": 1,
                            "estimated_time": 120,
                            "status": "not_started",
                            "resources": [
                                {{
                                    "id": 1,
                                    "title": "Resource title",
                                    "url": "https://example.com/learn",
                                    "type": "video",
                                    "difficulty": "beginner"
                                }},
                                {{
                                    "id": 2,
                                    "title": "Practice Exercise",
                                    "url": "https://example.com/exercise",
                                    "type": "exercise",
                                    "difficulty": "beginner"
                                }}
                            ]
                        }}
                    ]
                }}
            ]
        }}
        
        Important: Return ONLY the JSON object, no additional text.
        Keep the response focused and within token limits.
        """
        
        current_app.logger.info("🔵 Sending request to Groq API...")
        
        response = client.chat.completions.create(
            model= "gemma-7b-it", #"llama3-8b-8192",  # or "mixtral-8x7b-32768", "gemma-7b-it"
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert curriculum designer. Always return COMPLETE, valid JSON format without any additional text. Ensure all JSON braces and brackets are properly closed. Create 6-8 courses with 5-8 modules each."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content.strip()
        current_app.logger.info(f"📄 Groq raw response length: {len(content)}")
        
        # Clean the response (remove markdown code blocks if present)
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        # Parse the JSON response
        roadmap_data = parse_roadmap_json(content)
        return validate_and_complete_roadmap(roadmap_data) if roadmap_data else None
        
    except Exception as e:
        current_app.logger.error(f"❌ Groq API error: {str(e)}")
        return None
    
def generate_educational_content_with_groq(topic, description):
    """Generate educational content using Groq API"""
    try:
        from groq import Groq
        
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            return get_fallback_educational_content(topic)
        
        client = Groq(api_key=groq_api_key)
        
        prompt = f"""
        Create concise educational content for: {topic}
        
        Description: {description}
        
        Provide a brief explanation (2-3 paragraphs max), 2-3 key concepts with simple explanations,
        1-2 practical examples, and 1-2 practice problems.
        
        Format as JSON with:
        - explanation: Brief overview of the concept
        - key_concepts: Array of key points with simple explanations
        - examples: Practical, simple examples
        - practice_problems: 1-2 problems to practice
        
        Keep it very concise and beginner-friendly.
        """
        
        response = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "system", 
                    "content": "You are a helpful teacher. Create very concise educational content. Return valid JSON only."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean response
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()
        
        educational_data = json.loads(content)
        return educational_data
        
    except Exception as e:
        current_app.logger.error(f"Groq educational content error: {str(e)}")
        return get_fallback_educational_content(topic)

def parse_roadmap_json(roadmap_text):
    """Robust JSON parser that handles incomplete responses"""
    try:
        if not roadmap_text or not isinstance(roadmap_text, str):
            return None
        
        # Clean the response text
        cleaned_text = roadmap_text.strip()
        cleaned_text = re.sub(r'```json\s*', '', cleaned_text)
        cleaned_text = re.sub(r'```\s*', '', cleaned_text)
        
        # Find the start of JSON
        start_idx = cleaned_text.find('{')
        if start_idx == -1:
            return None
        
        # Try to parse as-is first
        try:
            return json.loads(cleaned_text[start_idx:])
        except json.JSONDecodeError:
            pass
        
        # If that fails, try to extract and complete JSON
        brace_count = 0
        in_string = False
        escape_next = False
        result_chars = []
        
        for i in range(start_idx, len(cleaned_text)):
            char = cleaned_text[i]
            
            if escape_next:
                result_chars.append(char)
                escape_next = False
                continue
                
            if char == '\\':
                result_chars.append(char)
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                result_chars.append(char)
                continue
                
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    
            result_chars.append(char)
            
            # If we've closed all braces, we have complete JSON
            if brace_count == 0 and not in_string:
                break
        
        # If we still have unclosed braces, close them
        while brace_count > 0:
            result_chars.append('}')
            brace_count -= 1
        
        json_str = ''.join(result_chars)
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            current_app.logger.error(f"Failed to parse even after completion: {e}")
            return None
            
    except Exception as e:
        current_app.logger.error(f"Roadmap parsing error: {e}")
        return None

def validate_and_complete_roadmap(roadmap_data):
    """Validate the roadmap structure and fill in missing fields"""
    if not isinstance(roadmap_data, dict):
        raise ValueError("Roadmap data must be a dictionary")
    
    # Ensure basic structure exists
    if 'courses' not in roadmap_data:
        roadmap_data['courses'] = []
    
    if not isinstance(roadmap_data['courses'], list):
        roadmap_data['courses'] = []
    
    # Set defaults
    defaults = {
        'domain': 'web',
        'domain_name': 'Web Development',
        'level': 'beginner',
        'estimated_completion': '12 weeks',
        'progress_percentage': 0.0,
        'completed_modules': 0,
    }
    
    for key, value in defaults.items():
        if key not in roadmap_data:
            roadmap_data[key] = value
    
    # Ensure we have adequate course structure
    if len(roadmap_data['courses']) < 5:
        current_app.logger.warning(f"Only {len(roadmap_data['courses'])} courses, using mock data")
        return None
    
    # Validate each course has adequate modules
    for course in roadmap_data['courses']:
        if 'modules' not in course or len(course['modules']) < 5:
            current_app.logger.warning(f"Course {course.get('title', 'unknown')} has insufficient modules")
            return None
    
    # Calculate total modules
    total_modules = sum(len(course.get('modules', [])) for course in roadmap_data['courses'])
    roadmap_data['total_modules'] = total_modules
    
    # Ensure each module has required fields
    course_id = 1
    module_id = 1
    
    for course in roadmap_data['courses']:
        if 'id' not in course:
            course['id'] = course_id
        if 'order' not in course:
            course['order'] = course_id
        course_id += 1
        
        for module in course.get('modules', []):
            if 'id' not in module:
                module['id'] = module_id
            if 'status' not in module:
                module['status'] = 'not_started'
            if 'resources' not in module:
                module['resources'] = []
            if 'estimated_time' not in module:
                module['estimated_time'] = 60
            module_id += 1
    
    current_app.logger.info(f"✅ Successfully validated roadmap with {len(roadmap_data['courses'])} courses and {total_modules} modules")
    return roadmap_data

def get_structured_mock_data(domain, knowledge_level):
    """Structured mock data as fallback with 6-8 courses and 5-8 modules each"""
    current_app.logger.info("🟢 Using structured mock data as fallback")
    
    domain_name = domain.title() + " Development"
    
    # Domain-specific comprehensive course structures
    domain_structures = {
        'web': [
            {
                'title': 'Web Development Fundamentals',
                'description': 'Master HTML, CSS, and JavaScript basics',
                'estimated_time': 720,
                'modules': [
                    {'title': 'HTML5 & Semantic Structure', 'description': 'Learn modern HTML structure', 'estimated_time': 120},
                    {'title': 'CSS3 & Styling', 'description': 'Master CSS fundamentals and layout', 'estimated_time': 180},
                    {'title': 'Responsive Design', 'description': 'Create mobile-friendly websites', 'estimated_time': 120},
                    {'title': 'JavaScript Basics', 'description': 'Learn variables, functions, and DOM', 'estimated_time': 180},
                    {'title': 'Modern JavaScript ES6+', 'description': 'Master modern JS features', 'estimated_time': 120},
                    {'title': 'Developer Tools & Debugging', 'description': 'Learn essential debugging skills', 'estimated_time': 60}
                ]
            },
            {
                'title': 'Frontend Development',
                'description': 'Build dynamic user interfaces',
                'estimated_time': 900,
                'modules': [
                    {'title': 'React Fundamentals', 'description': 'Learn React components and JSX', 'estimated_time': 180},
                    {'title': 'State & Props Management', 'description': 'Master component state management', 'estimated_time': 180},
                    {'title': 'React Hooks', 'description': 'Learn useEffect, useState, custom hooks', 'estimated_time': 120},
                    {'title': 'Component Lifecycle', 'description': 'Understand component mounting and updates', 'estimated_time': 120},
                    {'title': 'Forms & User Input', 'description': 'Handle forms and user interactions', 'estimated_time': 120},
                    {'title': 'API Integration', 'description': 'Connect to external APIs', 'estimated_time': 180}
                ]
            },
            {
                'title': 'Backend Development',
                'description': 'Build server-side applications',
                'estimated_time': 840,
                'modules': [
                    {'title': 'Node.js Fundamentals', 'description': 'Learn server-side JavaScript', 'estimated_time': 120},
                    {'title': 'Express.js Framework', 'description': 'Build web applications with Express', 'estimated_time': 180},
                    {'title': 'RESTful API Design', 'description': 'Design professional REST APIs', 'estimated_time': 180},
                    {'title': 'Database Integration', 'description': 'Connect to SQL and NoSQL databases', 'estimated_time': 180},
                    {'title': 'Authentication & Security', 'description': 'Implement secure user authentication', 'estimated_time': 120},
                    {'title': 'API Testing', 'description': 'Test backend services thoroughly', 'estimated_time': 60}
                ]
            },
            {
                'title': 'Advanced Frontend',
                'description': 'Master advanced frontend concepts',
                'estimated_time': 780,
                'modules': [
                    {'title': 'State Management Libraries', 'description': 'Learn Redux or Context API', 'estimated_time': 180},
                    {'title': 'Routing & Navigation', 'description': 'Implement client-side routing', 'estimated_time': 120},
                    {'title': 'Performance Optimization', 'description': 'Optimize application performance', 'estimated_time': 120},
                    {'title': 'Testing Strategies', 'description': 'Learn unit and integration testing', 'estimated_time': 120},
                    {'title': 'TypeScript Integration', 'description': 'Add type safety to JavaScript', 'estimated_time': 120},
                    {'title': 'Build Tools & Bundlers', 'description': 'Master Webpack and Vite', 'estimated_time': 120}
                ]
            },
            {
                'title': 'Full-Stack Development',
                'description': 'Combine frontend and backend skills',
                'estimated_time': 960,
                'modules': [
                    {'title': 'Full-Stack Architecture', 'description': 'Design complete applications', 'estimated_time': 120},
                    {'title': 'Authentication Flow', 'description': 'Implement secure auth systems', 'estimated_time': 180},
                    {'title': 'Data Management', 'description': 'Handle data across frontend and backend', 'estimated_time': 180},
                    {'title': 'Real-time Features', 'description': 'Add WebSocket functionality', 'estimated_time': 120},
                    {'title': 'Deployment Strategies', 'description': 'Deploy full-stack applications', 'estimated_time': 180},
                    {'title': 'CI/CD Pipeline', 'description': 'Set up continuous integration', 'estimated_time': 120},
                    {'title': 'Monitoring & Analytics', 'description': 'Track application performance', 'estimated_time': 60}
                ]
            },
            {
                'title': 'Professional Development',
                'description': 'Prepare for professional environment',
                'estimated_time': 600,
                'modules': [
                    {'title': 'Code Review Process', 'description': 'Learn professional code review', 'estimated_time': 120},
                    {'title': 'Agile Methodology', 'description': 'Understand agile development', 'estimated_time': 120},
                    {'title': 'Team Collaboration', 'description': 'Work effectively in teams', 'estimated_time': 120},
                    {'title': 'Project Management', 'description': 'Manage development projects', 'estimated_time': 120},
                    {'title': 'Career Preparation', 'description': 'Prepare for job interviews', 'estimated_time': 120}
                ]
            }
        ],
        'flutter': [
            {
                'title': 'Dart Programming Language',
                'description': 'Master Dart programming fundamentals',
                'estimated_time': 600,
                'modules': [
                    {'title': 'Dart Syntax & Basics', 'description': 'Learn Dart fundamentals', 'estimated_time': 120},
                    {'title': 'Object-Oriented Programming', 'description': 'Master OOP in Dart', 'estimated_time': 180},
                    {'title': 'Asynchronous Programming', 'description': 'Learn async/await and Futures', 'estimated_time': 120},
                    {'title': 'Dart Collections', 'description': 'Master lists, maps, and sets', 'estimated_time': 90},
                    {'title': 'Error Handling', 'description': 'Learn exception handling', 'estimated_time': 90}
                ]
            },
            {
                'title': 'Flutter Fundamentals',
                'description': 'Build mobile applications with Flutter',
                'estimated_time': 840,
                'modules': [
                    {'title': 'Flutter Setup & Basics', 'description': 'Set up development environment', 'estimated_time': 120},
                    {'title': 'Widget Tree & Layout', 'description': 'Understand Flutter widget hierarchy', 'estimated_time': 180},
                    {'title': 'Stateful vs Stateless', 'description': 'Learn state management basics', 'estimated_time': 120},
                    {'title': 'Layout Widgets', 'description': 'Master Row, Column, Container', 'estimated_time': 180},
                    {'title': 'Navigation & Routing', 'description': 'Implement app navigation', 'estimated_time': 120},
                    {'title': 'Forms & User Input', 'description': 'Handle user input and validation', 'estimated_time': 120}
                ]
            },
            {
                'title': 'UI/UX Design in Flutter',
                'description': 'Create beautiful user interfaces',
                'estimated_time': 720,
                'modules': [
                    {'title': 'Material Design', 'description': 'Implement Material Design', 'estimated_time': 120},
                    {'title': 'Custom Widgets', 'description': 'Create reusable custom widgets', 'estimated_time': 180},
                    {'title': 'Animations', 'description': 'Add smooth animations', 'estimated_time': 120},
                    {'title': 'Theming & Styling', 'description': 'Create consistent app themes', 'estimated_time': 120},
                    {'title': 'Responsive Design', 'description': 'Build responsive layouts', 'estimated_time': 120},
                    {'title': 'Accessibility', 'description': 'Make apps accessible', 'estimated_time': 60}
                ]
            },
            {
                'title': 'Advanced Flutter Development',
                'description': 'Build production-ready applications',
                'estimated_time': 900,
                'modules': [
                    {'title': 'Advanced State Management', 'description': 'Learn Provider, Bloc, Riverpod', 'estimated_time': 180},
                    {'title': 'API Integration', 'description': 'Connect to REST APIs', 'estimated_time': 180},
                    {'title': 'Local Data Storage', 'description': 'Implement SQLite and shared preferences', 'estimated_time': 120},
                    {'title': 'Firebase Integration', 'description': 'Add Firebase services', 'estimated_time': 180},
                    {'title': 'Testing Strategies', 'description': 'Write unit and widget tests', 'estimated_time': 120},
                    {'title': 'Performance Optimization', 'description': 'Optimize app performance', 'estimated_time': 120}
                ]
            },
            {
                'title': 'Flutter Platform Features',
                'description': 'Leverage platform-specific capabilities',
                'estimated_time': 780,
                'modules': [
                    {'title': 'Platform Channels', 'description': 'Communicate with native code', 'estimated_time': 180},
                    {'title': 'Camera & Gallery', 'description': 'Access device camera and photos', 'estimated_time': 120},
                    {'title': 'Location Services', 'description': 'Implement GPS and maps', 'estimated_time': 120},
                    {'title': 'Push Notifications', 'description': 'Add push notification support', 'estimated_time': 120},
                    {'title': 'In-App Purchases', 'description': 'Implement payment systems', 'estimated_time': 120},
                    {'title': 'Background Processing', 'description': 'Run tasks in background', 'estimated_time': 120}
                ]
            },
            {
                'title': 'Deployment & Publishing',
                'description': 'Prepare apps for production',
                'estimated_time': 600,
                'modules': [
                    {'title': 'App Signing & Building', 'description': 'Prepare release builds', 'estimated_time': 120},
                    {'title': 'App Store Preparation', 'description': 'Prepare for Apple App Store', 'estimated_time': 120},
                    {'title': 'Play Store Preparation', 'description': 'Prepare for Google Play Store', 'estimated_time': 120},
                    {'title': 'Continuous Integration', 'description': 'Set up CI/CD pipeline', 'estimated_time': 120},
                    {'title': 'App Analytics', 'description': 'Track user engagement', 'estimated_time': 120}
                ]
            }
        ]
    }
    
    # Get domain-specific structure or use generic one
    courses_data = domain_structures.get(domain, [
        {
            'title': f'{domain_name} Fundamentals',
            'description': f'Learn the core concepts of {domain_name}',
            'estimated_time': 600,
            'modules': [
                {'title': 'Introduction & Setup', 'description': 'Get started with the basics', 'estimated_time': 120},
                {'title': 'Core Concepts', 'description': 'Learn fundamental principles', 'estimated_time': 180},
                {'title': 'Practical Applications', 'description': 'Apply knowledge to real projects', 'estimated_time': 180},
                {'title': 'Advanced Topics', 'description': 'Explore more complex concepts', 'estimated_time': 120},
                {'title': 'Project Development', 'description': 'Build complete projects', 'estimated_time': 180},
                {'title': 'Testing & Deployment', 'description': 'Test and deploy applications', 'estimated_time': 120}
            ]
        }
    ])
    
    # Calculate total modules
    total_modules = sum(len(course['modules']) for course in courses_data)
    
    # Format courses with proper structure
    formatted_courses = []
    course_order = 1
    module_id = 1
    
    for course in courses_data:
        formatted_modules = []
        module_order = 1
        
        for module in course['modules']:
            formatted_modules.append({
                'id': module_id,
                'title': module['title'],
                'description': module['description'],
                'order': module_order,
                'estimated_time': module['estimated_time'],
                'status': 'not_started',
                'resources': [
                    {
                        'id': 1,
                        'title': 'Official Documentation',
                        'url': 'https://example.com/docs',
                        'type': 'documentation',
                        'difficulty': 'beginner'
                    },
                    {
                        'id': 2,
                        'title': 'Video Tutorial',
                        'url': 'https://example.com/tutorial',
                        'type': 'video',
                        'difficulty': 'beginner'
                    },
                    {
                        'id': 3,
                        'title': 'Practice Exercise',
                        'url': 'https://example.com/exercise',
                        'type': 'exercise',
                        'difficulty': 'beginner'
                    }
                ]
            })
            module_id += 1
            module_order += 1
        
        formatted_courses.append({
            'id': course_order,
            'title': course['title'],
            'description': course['description'],
            'order': course_order,
            'estimated_time': course['estimated_time'],
            'modules': formatted_modules
        })
        course_order += 1

    return {
        "domain": domain,
        "domain_name": domain_name,
        "level": knowledge_level,
        "estimated_completion": "12 weeks",
        "progress_percentage": 0.0,
        "completed_modules": 0,
        "total_modules": total_modules,
        "courses": formatted_courses
    }

@learning_pathfinder_bp.route('/learning-path/module-content/<int:module_id>', methods=['GET'])
def get_module_content(module_id):
    """Get detailed content for a specific module"""
    try:
        firebase_uid = request.args.get('firebase_uid')
        if not firebase_uid:
            return jsonify({'error': 'firebase_uid is required'}), 400

        module = PathModule.query.get(module_id)
        if not module:
            return jsonify({'error': 'Module not found'}), 404

        # Check if user has access to this module
        progress = UserProgress.query.filter_by(
            user_id=firebase_uid,
            module_id=module_id
        ).first()

        if not progress:
            return jsonify({'error': 'Access denied'}), 403

        # Get module resources
        resources = ModuleResource.query.filter_by(module_id=module_id).all()
        
        # Get educational content (would be generated or stored)
        educational_content = generate_educational_content(module.title, module.description)

        # Check if previous module is completed (for progression)
        previous_module = PathModule.query.filter_by(
            course_id=module.course_id,
            order=module.order - 1
        ).first()

        can_access = True
        if previous_module:
            prev_progress = UserProgress.query.filter_by(
                user_id=firebase_uid,
                module_id=previous_module.id
            ).first()
            can_access = prev_progress and prev_progress.status == 'completed'

        return jsonify({
            'module': {
                'id': module.id,
                'title': module.title,
                'description': module.description,
                'order': module.order,
                'estimated_time': module.estimated_time
            },
            'educational_content': educational_content,
            'resources': [
                {
                    'id': resource.id,
                    'title': resource.title,
                    'url': resource.url,
                    'type': resource.type,
                    'difficulty': resource.difficulty
                } for resource in resources
            ],
            'can_access': can_access,
            'current_progress': progress.status if progress else 'not_started'
        })

    except Exception as e:
        current_app.logger.error(f"Error getting module content: {str(e)}")
        return jsonify({'error': 'Failed to get module content'}), 500

@learning_pathfinder_bp.route('/learning-path/complete-module', methods=['POST'])
def complete_module():
    """Mark a module as completed and check progression"""
    try:
        data = request.get_json()
        firebase_uid = data.get('firebase_uid')
        module_id = data.get('module_id')

        if not all([firebase_uid, module_id]):
            return jsonify({'error': 'Missing required fields'}), 400

        # Update module progress
        progress = UserProgress.query.filter_by(
            user_id=firebase_uid,
            module_id=module_id
        ).first()

        if progress:
            progress.status = 'completed'
            progress.completion_date = datetime.utcnow()
        else:
            profile = UserProfile.query.filter_by(user_id=firebase_uid).first()
            if not profile:
                return jsonify({'error': 'User profile not found'}), 404
            
            progress = UserProgress(
                user_id=firebase_uid,
                module_id=module_id,
                profile_id=profile.id,
                status='completed',
                completion_date=datetime.utcnow()
            )
            db.session.add(progress)

        db.session.commit()

        # Get next module information
        current_module = PathModule.query.get(module_id)
        next_module = PathModule.query.filter_by(
            course_id=current_module.course_id,
            order=current_module.order + 1
        ).first()

        return jsonify({
            'message': 'Module completed successfully',
            'next_module': {
                'id': next_module.id,
                'title': next_module.title,
                'description': next_module.description
            } if next_module else None,
            'is_course_completed': not next_module
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error completing module: {str(e)}")
        return jsonify({'error': 'Failed to complete module'}), 500

@learning_pathfinder_bp.route('/learning-path/user-roadmap', methods=['GET'])
def get_user_learning_path():
    """Get the current user's learning path with course-module structure"""
    try:
        firebase_uid = request.args.get('firebase_uid')
        if not firebase_uid:
            return jsonify({'error': 'firebase_uid is required'}), 400

        learning_path = LearningPath.query.filter_by(user_id=firebase_uid)\
            .order_by(LearningPath.created_at.desc()).first()
        
        if not learning_path:
            return jsonify({'has_path': False}), 404

        # Get courses with modules
        courses = Course.query.filter_by(path_id=learning_path.id)\
            .order_by(Course.order).all()
        
        courses_data = []
        total_modules = 0
        completed_modules = 0
        
        for course in courses:
            modules = PathModule.query.filter_by(course_id=course.id)\
                .order_by(PathModule.order).all()
            
            modules_data = []
            for module in modules:
                resources = ModuleResource.query.filter_by(module_id=module.id).all()
                progress = UserProgress.query.filter_by(
                    user_id=firebase_uid, 
                    module_id=module.id
                ).first()
                
                module_status = progress.status if progress else 'not_started'
                if module_status == 'completed':
                    completed_modules += 1
                
                modules_data.append({
                    'id': module.id,
                    'title': module.title,
                    'description': module.description,
                    'order': module.order,
                    'estimated_time': module.estimated_time,
                    'status': module_status,
                    'resources': [
                        {
                            'id': resource.id,
                            'title': resource.title,
                            'url': resource.url,
                            'type': resource.type,
                            'difficulty': resource.difficulty
                        } for resource in resources
                    ]
                })
                total_modules += 1
            
            courses_data.append({
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'order': course.order,
                'estimated_time': course.estimated_time,
                'modules': modules_data
            })

        domain = Domain.query.get(learning_path.domain_id)
        progress_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
        
        return jsonify({
            'has_path': True,
            'path_id': learning_path.id,
            'domain': domain.name if domain else 'Unknown',
            'domain_name': domain.name.title() + " Development" if domain else 'Unknown',
            'current_version': learning_path.current_version,
            'created_at': learning_path.created_at.isoformat(),
            'progress_percentage': progress_percentage,
            'completed_modules': completed_modules,
            'total_modules': total_modules,
            'courses': courses_data
        })

    except Exception as e:
        current_app.logger.error(f"Error getting user roadmap: {str(e)}")
        return jsonify({'error': 'Failed to get learning path'}), 500

@learning_pathfinder_bp.route('/learning-path/update-progress', methods=['POST'])
def update_module_progress():
    """Update progress for a module"""
    try:
        data = request.get_json()
        firebase_uid = data.get('firebase_uid')
        module_id = data.get('module_id')
        status = data.get('status')

        if not all([firebase_uid, module_id, status]):
            return jsonify({'error': 'Missing required fields'}), 400

        profile = UserProfile.query.filter_by(user_id=firebase_uid).first()
        if not profile:
            return jsonify({'error': 'User profile not found'}), 404

        progress = UserProgress.query.filter_by(
            user_id=firebase_uid,
            module_id=module_id
        ).first()

        if progress:
            progress.status = status
            if status == 'completed':
                progress.completion_date = datetime.utcnow()
        else:
            progress = UserProgress(
                user_id=firebase_uid,
                module_id=module_id,
                profile_id=profile.id,
                status=status,
                completion_date=datetime.utcnow() if status == 'completed' else None
            )
            db.session.add(progress)

        db.session.commit()

        return jsonify({
            'message': 'Progress updated successfully',
            'module_id': module_id,
            'status': status
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating progress: {str(e)}")
        return jsonify({'error': 'Failed to update progress'}), 500

@learning_pathfinder_bp.route('/learning-path/test', methods=['GET'])
def test_endpoint():
    return jsonify({'message': 'Learning Path Finder API is working!', 'status': 'success'})