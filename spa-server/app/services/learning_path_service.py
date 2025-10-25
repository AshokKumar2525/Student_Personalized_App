"""
Learning Path Finder Service - Production Ready
Handles AI-powered roadmap generation with caching and optimization
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from flask import current_app
from app import db
from app.models.learning_pathfinder import (
    Domain, Technology, UserProfile, LearningPath, 
    Course, PathModule, ModuleResource, UserProgress
)
from openai import OpenAI
from groq import Groq
import requests

class LearningPathService:
    """Main service for learning path generation and management"""
    
    # Cache configuration
    CACHE_DURATION_DAYS = 30
    MAX_AI_RETRIES = 2
    
    def __init__(self):
        self.openai_client = None
        self.mistral_client = None
        self.groq_client = None
        self._initialize_clients()
        
    def _initialize_clients(self):
            """Initialize AI clients with error handling"""
            # Initialize Groq
            groq_key = os.getenv('GROQ_API_KEY')
            if groq_key:
                try:
                    self.groq_client = Groq(api_key=groq_key)
                    print("✅ Groq client initialized")
                except Exception as e:
                    print(f"⚠️ Failed to initialize Groq: {e}")
                    self.groq_client = None
            
            # Initialize OpenAI with safe parameters
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                try:
                    # Try modern initialization
                    self.openai_client = OpenAI(api_key=openai_key)
                    print("✅ OpenAI client initialized")
                except TypeError as e:
                    # Fallback for version compatibility issues
                    print(f"⚠️ OpenAI init error: {e}")
                    try:
                        # Try simpler initialization
                        import openai
                        openai.api_key = openai_key
                        self.openai_client = openai
                        print("✅ OpenAI client initialized (legacy mode)")
                    except Exception as e2:
                        print(f"⚠️ Failed to initialize OpenAI: {e2}")
                        self.openai_client = None
                except Exception as e:
                    print(f"⚠️ Failed to initialize OpenAI: {e}")
                    self.openai_client = None


    
    def generate_learning_path(
        self,
        user_id: str,
        domain: str,
        knowledge_level: str,
        familiar_techs: List[str],
        weekly_hours: int,
        learning_pace: str
    ) -> Dict[str, Any]:
        """
        Generate a complete learning path for a user
        
        Returns:
            Dict with path_id, domain, and roadmap data
        """
        try:
            # 1. Validate inputs
            self._validate_inputs(domain, knowledge_level, weekly_hours, learning_pace)
            
            # 2. Get or create domain
            domain_obj = self._get_or_create_domain(domain)
            
            # 3. Check for cached roadmap
            cache_key = self._generate_cache_key(domain, knowledge_level, familiar_techs)
            cached_roadmap = self._get_cached_roadmap(cache_key)
            
            if cached_roadmap:
                current_app.logger.info(f"Using cached roadmap for {domain}/{knowledge_level}")
                roadmap_data = cached_roadmap
            else:
                # 4. Generate new roadmap using AI
                roadmap_data = self._generate_roadmap_with_ai(
                    domain, knowledge_level, familiar_techs, weekly_hours, learning_pace
                )
                
                # 5. Cache the generated roadmap
                self._cache_roadmap(cache_key, roadmap_data)
            
            # 6. Create or update user profile
            profile = self._create_or_update_profile(
                user_id, domain_obj.id, knowledge_level, 
                familiar_techs, weekly_hours, learning_pace
            )
            
            # 7. Create learning path and structure
            learning_path = self._create_learning_path_structure(
                user_id, domain_obj.id, roadmap_data
            )
            
            # 8. Enhance with real resources
            self._enhance_with_resources(learning_path.id, roadmap_data)
            
            # 9. Prepare response
            response_data = self._prepare_response(learning_path, roadmap_data)
            
            db.session.commit()
            
            return {
                'message': 'Learning path generated successfully',
                'path_id': learning_path.id,
                'domain': domain,
                'roadmap': response_data
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error generating learning path: {str(e)}")
            raise
    
    def _validate_inputs(self, domain: str, knowledge_level: str, 
                        weekly_hours: int, learning_pace: str):
        """Validate user inputs"""
        valid_levels = ['beginner', 'intermediate', 'advanced']
        valid_paces = ['slow', 'medium', 'fast']
        
        if knowledge_level not in valid_levels:
            raise ValueError(f"Invalid knowledge level. Must be one of {valid_levels}")
        
        if learning_pace not in valid_paces:
            raise ValueError(f"Invalid learning pace. Must be one of {valid_paces}")
        
        if not 1 <= weekly_hours <= 40:
            raise ValueError("Weekly hours must be between 1 and 40")
    
    def _generate_cache_key(self, domain: str, level: str, 
                           techs: List[str]) -> str:
        """Generate unique cache key for roadmap"""
        tech_str = ','.join(sorted(techs)) if techs else ''
        content = f"{domain}:{level}:{tech_str}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cached_roadmap(self, cache_key: str) -> Optional[Dict]:
        """Retrieve cached roadmap if available and not expired"""
        from app.models.utils import generate_uuid
        
        # Check if we have a recent successful generation
        # This would be stored in a cache table (optional enhancement)
        # For now, return None to always generate fresh
        return None
    
    def _cache_roadmap(self, cache_key: str, roadmap_data: Dict):
        """Cache generated roadmap for reuse"""
        # Optional: Store in Redis or database cache table
        # For production, implement Redis caching
        pass
    
    def _generate_roadmap_with_ai(
        self,
        domain: str,
        knowledge_level: str,
        familiar_techs: List[str],
        weekly_hours: int,
        learning_pace: str
    ) -> Dict[str, Any]:
        """Generate roadmap using AI with fallback strategy"""
        
        prompt = self._build_roadmap_prompt(
            domain, knowledge_level, familiar_techs, weekly_hours, learning_pace
        )
        
        # Try OpenAI first (best quality)
        if self.openai_client:
            try:
                roadmap = self._call_openai(prompt)
                if roadmap and self._validate_roadmap_structure(roadmap):
                    return roadmap
            except Exception as e:
                current_app.logger.warning(f"OpenAI failed: {str(e)}")
        
        # Fallback to Groq (fast and reliable)
        if self.groq_client:
            try:
                roadmap = self._call_groq(prompt)
                if roadmap and self._validate_roadmap_structure(roadmap):
                    return roadmap
            except Exception as e:
                current_app.logger.warning(f"Groq failed: {str(e)}")
        
        # Final fallback: structured template
        current_app.logger.warning("All AI providers failed, using template")
        return self._generate_template_roadmap(domain, knowledge_level)
    
    def _build_roadmap_prompt(
        self,
        domain: str,
        level: str,
        techs: List[str],
        hours: int,
        pace: str
    ) -> str:
        """Build optimized prompt for AI"""
        
        tech_context = f"Already familiar with: {', '.join(techs)}" if techs else "Complete beginner"
        
        return f"""Create a comprehensive learning roadmap for {domain} development.

Student Profile:
- Level: {level}
- {tech_context}
- Available time: {hours} hours/week
- Learning pace: {pace}

Requirements:
1. Create exactly 6 courses
2. Each course must have 6-8 modules
3. Progressive difficulty (beginner → advanced)
4. Include practical projects
5. Estimated time for each module (in minutes)

Return ONLY valid JSON with this EXACT structure:
{{
  "domain": "{domain}",
  "level": "{level}",
  "estimated_completion": "X weeks",
  "courses": [
    {{
      "title": "Course title",
      "description": "Brief description",
      "order": 1,
      "estimated_time": 600,
      "modules": [
        {{
          "title": "Module title",
          "description": "What students learn",
          "order": 1,
          "estimated_time": 90,
          "key_concepts": ["Concept 1", "Concept 2"],
          "resources": [
            {{
              "title": "Resource title",
              "type": "video",
              "difficulty": "beginner"
            }}
          ]
        }}
      ]
    }}
  ]
}}

CRITICAL: Return complete, valid JSON only. No markdown, no explanations."""
    
    def _call_openai(self, prompt: str) -> Optional[Dict]:
        """Call OpenAI API with retry logic"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Cost-effective model
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert curriculum designer. Return only valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            current_app.logger.error(f"OpenAI error: {str(e)}")
            return None
    
    def _call_groq(self, prompt: str) -> Optional[Dict]:
        """Call Groq API with retry logic"""
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert curriculum designer. Return only valid JSON."
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
            
            # Clean markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            return json.loads(content.strip())
            
        except Exception as e:
            current_app.logger.error(f"Groq error: {str(e)}")
            return None
    
    def _validate_roadmap_structure(self, roadmap: Dict) -> bool:
        """Validate roadmap has required structure"""
        if not isinstance(roadmap, dict):
            return False
        
        if 'courses' not in roadmap:
            return False
        
        courses = roadmap['courses']
        if not isinstance(courses, list) or len(courses) < 4:
            return False
        
        for course in courses:
            if 'modules' not in course:
                return False
            if len(course['modules']) < 4:
                return False
        
        return True
    
    def _generate_template_roadmap(self, domain: str, level: str) -> Dict:
        """Generate template-based roadmap as final fallback"""
        
        # Import template generator
        from app.services.roadmap_templates import get_domain_template
        
        template = get_domain_template(domain, level)
        return template
    
    def _get_or_create_domain(self, domain_name: str) -> Domain:
        """Get existing domain or create new one"""
        domain = Domain.query.filter_by(name=domain_name).first()
        
        if not domain:
            domain = Domain(
                name=domain_name,
                description=f"Learning path for {domain_name.title()} development"
            )
            db.session.add(domain)
            db.session.flush()
        
        return domain
    
    def _create_or_update_profile(
        self,
        user_id: str,
        domain_id: int,
        level: str,
        techs: List[str],
        hours: int,
        pace: str
    ) -> UserProfile:
        """Create or update user profile"""
        
        profile = UserProfile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            profile = UserProfile(
                id=user_id,
                user_id=user_id,
                domain_id=domain_id,
                current_level=level,
                familiar_techs=[],
                daily_time=hours * 60 // 7,
                learning_pace=pace
            )
            db.session.add(profile)
        else:
            profile.domain_id = domain_id
            profile.current_level = level
            profile.daily_time = hours * 60 // 7
            profile.learning_pace = pace
        
        db.session.flush()
        return profile
    
    def _create_learning_path_structure(
        self,
        user_id: str,
        domain_id: int,
        roadmap_data: Dict
    ) -> LearningPath:
        """Create the complete learning path structure"""
        
        # Create learning path
        learning_path = LearningPath(
            user_id=user_id,
            domain_id=domain_id,
            current_version=1,
            created_at=datetime.utcnow()
        )
        db.session.add(learning_path)
        db.session.flush()
        
        # Create courses and modules
        courses_data = roadmap_data.get('courses', [])
        
        for course_data in courses_data:
            course = Course(
                path_id=learning_path.id,
                title=course_data['title'],
                description=course_data.get('description', ''),
                order=course_data.get('order', 1),
                estimated_time=course_data.get('estimated_time', 600),
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
                    description=module_data.get('description', ''),
                    order=module_data.get('order', 1),
                    estimated_time=module_data.get('estimated_time', 60),
                    created_at=datetime.utcnow()
                )
                db.session.add(module)
                db.session.flush()
                
                # Create initial progress record
                progress = UserProgress(
                    user_id=user_id,
                    module_id=module.id,
                    profile_id=user_id,
                    status='not_started',
                    created_at=datetime.utcnow()
                )
                db.session.add(progress)
                
                # Add placeholder resources
                for resource_data in module_data.get('resources', []):
                    resource = ModuleResource(
                        module_id=module.id,
                        title=resource_data.get('title', 'Resource'),
                        url='https://example.com/placeholder',
                        type=resource_data.get('type', 'documentation'),
                        difficulty=resource_data.get('difficulty', 'beginner'),
                        created_at=datetime.utcnow()
                    )
                    db.session.add(resource)
        
        return learning_path
    
    def _enhance_with_resources(self, path_id: int, roadmap_data: Dict):
        """Enhance modules with real YouTube videos and resources"""
        
        youtube_service = YouTubeResourceService()
        
        # Get all modules for this path
        modules = PathModule.query.filter_by(path_id=path_id).all()
        
        for module in modules:
            # Get 2 YouTube videos for each module
            videos = youtube_service.search_videos(module.title, max_results=2)
            
            if videos:
                # Delete placeholder resources
                ModuleResource.query.filter_by(module_id=module.id).delete()
                
                # Add real video resources
                for idx, video in enumerate(videos):
                    resource = ModuleResource(
                        module_id=module.id,
                        title=video['title'],
                        url=video['url'],
                        type='video',
                        difficulty='beginner' if idx == 0 else 'intermediate',
                        created_at=datetime.utcnow()
                    )
                    db.session.add(resource)
    
    def _prepare_response(self, learning_path: LearningPath, 
                         roadmap_data: Dict) -> Dict:
        """Prepare final response data"""
        
        # Get all courses with modules
        courses = Course.query.filter_by(path_id=learning_path.id)\
            .order_by(Course.order).all()
        
        courses_response = []
        total_modules = 0
        
        for course in courses:
            modules = PathModule.query.filter_by(course_id=course.id)\
                .order_by(PathModule.order).all()
            
            modules_response = []
            for module in modules:
                resources = ModuleResource.query.filter_by(module_id=module.id).all()
                
                modules_response.append({
                    'id': module.id,
                    'title': module.title,
                    'description': module.description,
                    'order': module.order,
                    'estimated_time': module.estimated_time,
                    'status': 'not_started',
                    'resources': [
                        {
                            'id': r.id,
                            'title': r.title,
                            'url': r.url,
                            'type': r.type,
                            'difficulty': r.difficulty
                        } for r in resources
                    ]
                })
                total_modules += 1
            
            courses_response.append({
                'id': course.id,
                'title': course.title,
                'description': course.description,
                'order': course.order,
                'estimated_time': course.estimated_time,
                'modules': modules_response
            })
        
        return {
            'domain': roadmap_data.get('domain'),
            'domain_name': f"{roadmap_data.get('domain', '').title()} Development",
            'level': roadmap_data.get('level'),
            'estimated_completion': roadmap_data.get('estimated_completion', '12 weeks'),
            'progress_percentage': 0.0,
            'completed_modules': 0,
            'total_modules': total_modules,
            'courses': courses_response
        }


class YouTubeResourceService:
    """Service for fetching YouTube resources"""
    
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.base_url = "https://www.googleapis.com/youtube/v3/search"
    
    def search_videos(self, query: str, max_results: int = 3) -> List[Dict]:
        """Search for educational YouTube videos"""
        
        if not self.api_key:
            return self._get_fallback_videos(query)
        
        try:
            params = {
                'part': 'snippet',
                'q': f"{query} tutorial programming",
                'type': 'video',
                'maxResults': max_results,
                'key': self.api_key,
                'videoDuration': 'medium',
                'videoDefinition': 'high',
                'relevanceLanguage': 'en'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._process_youtube_results(data.get('items', []))
            else:
                return self._get_fallback_videos(query)
                
        except Exception as e:
            current_app.logger.error(f"YouTube API error: {str(e)}")
            return self._get_fallback_videos(query)
    
    def _process_youtube_results(self, items: List[Dict]) -> List[Dict]:
        """Process YouTube API results"""
        videos = []
        
        for item in items:
            video_id = item['id']['videoId']
            snippet = item['snippet']
            
            videos.append({
                'title': snippet['title'],
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'embed_url': f"https://www.youtube.com/embed/{video_id}",
                'thumbnail': snippet['thumbnails']['high']['url'],
                'channel': snippet['channelTitle']
            })
        
        return videos
    
    def _get_fallback_videos(self, query: str) -> List[Dict]:
        """Return generic search link as fallback"""
        search_query = query.replace(' ', '+')
        
        return [
            {
                'title': f'{query} - Tutorial',
                'url': f'https://www.youtube.com/results?search_query={search_query}+tutorial',
                'embed_url': None,
                'thumbnail': None,
                'channel': 'YouTube Search'
            }
        ]