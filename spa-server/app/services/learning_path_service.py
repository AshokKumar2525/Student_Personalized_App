"""
Learning Path Service - Fixed YouTube Integration
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import current_app
from app import db
from app.models.learning_pathfinder import (
    Domain, Technology, UserProfile, LearningPath, 
    Course, PathModule, ModuleResource, UserProgress
)
from openai import OpenAI
import time

class LearningPathService:
    """Optimized service with fixed YouTube integration"""
    
    CACHE_ENABLED = True
    
    def __init__(self):
        self.groq_client = None
        self.openai_client = None
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Initialize AI clients"""
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            try:
                from groq import Groq as GroqClient
                self.groq_client = GroqClient(api_key=groq_key)
                print("✅ Groq initialized")
            except Exception as e:
                print(f"⚠️ Groq init failed: {e}")
                self.groq_client = None
        
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            try:
                self.openai_client = OpenAI(api_key=openai_key)
                print("✅ OpenAI initialized")
            except Exception as e:
                print(f"⚠️ OpenAI init failed: {e}")
    
    def generate_learning_path(
        self,
        user_id: str,
        domain: str,
        knowledge_level: str,
        familiar_techs: List[str],
        weekly_hours: int,
        learning_pace: str
    ) -> Dict[str, Any]:
        """Generate learning path with proper YouTube integration"""
        try:
            # 1-6. Same as before (validation, domain, template, etc.)
            self._validate_inputs(domain, knowledge_level, weekly_hours, learning_pace)
            domain_obj = self._get_or_create_domain(domain)
            template_hash = self._generate_template_hash(
                domain, knowledge_level, weekly_hours // 5, learning_pace
            )
            
            from app.models.roadmap_templates import RoadmapTemplate
            cached_template = None
            
            if self.CACHE_ENABLED:
                cached_template = RoadmapTemplate.query.filter_by(
                    template_hash=template_hash
                ).first()
                
                if cached_template:
                    print(f"✅ Using cached template (used {cached_template.usage_count} times)")
                    cached_template.increment_usage()
                    db.session.commit()
                    roadmap_data = cached_template.roadmap_data
                else:
                    print("🔄 Generating new roadmap template...")
                    roadmap_data = self._generate_roadmap_with_ai(
                        domain, knowledge_level, familiar_techs, weekly_hours, learning_pace
                    )
                    
                    new_template = RoadmapTemplate(
                        template_hash=template_hash,
                        domain_id=domain_obj.id,
                        knowledge_level=knowledge_level,
                        learning_pace=learning_pace,
                        weekly_hours_range=f"{(weekly_hours // 5) * 5}-{((weekly_hours // 5) + 1) * 5}",
                        roadmap_data=roadmap_data,
                        usage_count=1
                    )
                    db.session.add(new_template)
                    db.session.commit()
                    print("✅ Template cached for future use")
            else:
                roadmap_data = self._generate_roadmap_with_ai(
                    domain, knowledge_level, familiar_techs, weekly_hours, learning_pace
                )
            
            profile = self._create_or_update_profile(
                user_id, domain_obj.id, knowledge_level, 
                familiar_techs, weekly_hours, learning_pace
            )
            
            learning_path = self._create_learning_path_structure(
                user_id, domain_obj.id, roadmap_data
            )
            
            # ✅ FIX: Actually fetch and add YouTube videos
            self._add_youtube_resources(learning_path.id, roadmap_data)
            
            from app.models.enhanced_progress import UserStreak
            if not UserStreak.query.filter_by(user_id=user_id).first():
                streak = UserStreak(user_id=user_id)
                db.session.add(streak)
            
            db.session.commit()
            
            response_data = self._prepare_response(learning_path, roadmap_data)
            
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
    
    def _generate_template_hash(self, domain: str, level: str, 
                                 hours_range: int, pace: str) -> str:
        """Generate hash for template caching (groups similar preferences)"""
        content = f"{domain}:{level}:{hours_range}:{pace}"
        return hashlib.md5(content.encode()).hexdigest()
    
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
    
    def _generate_roadmap_with_ai(
        self,
        domain: str,
        knowledge_level: str,
        familiar_techs: List[str],
        weekly_hours: int,
        learning_pace: str
    ) -> Dict[str, Any]:
        """Generate roadmap using AI with fallback to templates"""
        
        prompt = self._build_roadmap_prompt(
            domain, knowledge_level, familiar_techs, weekly_hours, learning_pace
        )
        
        # Try Groq first (fast and free)
        is_groq_failed = False
        if self.groq_client:
            try:
                roadmap = self._call_groq(prompt)
                print("roadmap from groq : \n", roadmap)
                if roadmap and self._validate_roadmap_structure(roadmap):
                    return roadmap
                elif roadmap:
                    print("⚠️ Groq returned invalid structure")
                else:
                    print("⚠️ Groq returned no roadmap")
            except Exception as e:
                print(f"⚠️ Groq failed: {e}")
                is_groq_failed = True
        
        # Fallback to OpenAI
        if self.openai_client and is_groq_failed:
            try:
                roadmap = self._call_openai(prompt)
                print("roadmap from groq : \n", roadmap)
                if roadmap and self._validate_roadmap_structure(roadmap):
                    return roadmap
                elif roadmap:
                    print("⚠️ Groq returned invalid structure")
                else:
                    print("⚠️ Groq returned no roadmap")
            except Exception as e:
                print(f"⚠️ Groq failed: {e}")
                is_groq_failed = True
        
        # Final fallback: template
        print("⚠️ Using template fallback")
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
        
        return f"""Create a comprehensive {domain} learning roadmap.

Student Profile:
- Level: {level}
- {tech_context}
- Available time: {hours} hours/week
- Learning pace: {pace}

Requirements:
1. Create EXACTLY 6-10 courses (NO MORE, NO LESS)
2. Each course must have 6-7 modules
3. Progressive difficulty
4. Include practical examples
5. Estimated time for each module (60-180 minutes)

Return ONLY valid JSON with this structure:
{{
  "domain": "{domain}",
  "level": "{level}",
  "estimated_completion": "X weeks",
  "courses": [
    {{
      "title": "Course Title",
      "description": "Brief description",
      "order": 1,
      "estimated_time": 600,
      "modules": [
        {{
          "title": "Module Title",
          "description": "What students learn",
          "order": 1,
          "estimated_time": 120,
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

CRITICAL: Return complete, valid JSON only. No markdown."""
    
    def _call_groq(self, prompt: str) -> Optional[Dict]:
        """Call Groq API"""
        print("🔄 Calling Groq API...")
        start_time = time.time()
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
                max_tokens=8000,
                timeout=30
            )
            
            elapsed_time = time.time() - start_time
            print(f"⏱️ Groq response time: {elapsed_time:.2f} seconds")
            content = response.choices[0].message.content.strip()
            
            # Clean markdown
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            print("✅ Groq response parsed successfully")
            print("the content from groq response is : ", content)
            return json.loads(content.strip())
        except Exception as e:
            print(f"Groq error: {e}")
            return None
    
    def _call_openai(self, prompt: str) -> Optional[Dict]:
        """Call OpenAI API"""
        print("🔄 Calling OpenAI API...")
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
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
                max_tokens=5000,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            print("✅ OpenAI response parsed successfully")
            return json.loads(content)
            
        except Exception as e:
            print(f"OpenAI error: {e}")
            return None
    
    def _validate_roadmap_structure(self, roadmap: Dict) -> bool:
        """Validate roadmap structure"""
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
        """Generate template-based roadmap"""
        from app.services.roadmap_templates import get_domain_template
        return get_domain_template(domain, level)
    
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
        """Create the complete learning path structure WITHOUT resources"""
        
        learning_path = LearningPath(
            user_id=user_id,
            domain_id=domain_id,
            current_version=1,
            created_at=datetime.utcnow()
        )
        db.session.add(learning_path)
        db.session.flush()
        
        courses_data = roadmap_data.get('courses', [])
        
        for course_data in courses_data:
            modules_data = course_data.get('modules', [])
            course_total_time = sum(module.get('estimated_time', 60) for module in modules_data)
            
            course = Course(
                path_id=learning_path.id,
                title=course_data['title'],
                description=course_data.get('description', ''),
                order=course_data.get('order', 1),
                estimated_time=course_total_time,
                created_at=datetime.utcnow()
            )
            db.session.add(course)
            db.session.flush()
            
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
                
                # Create progress record
                progress = UserProgress(
                    user_id=user_id,
                    module_id=module.id,
                    profile_id=user_id,
                    status='not_started',
                    created_at=datetime.utcnow()
                )
                db.session.add(progress)
                
                # ✅ DON'T add resources here - they'll be added by _add_youtube_resources
        
        return learning_path
    
    def _enhance_with_resources(self, path_id: int, roadmap_data: Dict):
        """Enhance modules with real resources (can be async in production)"""
        # This is a placeholder - in production, use background tasks
        # For now, we use search links which are faster than API calls
        pass
    
    def _add_youtube_resources(self, path_id: int, roadmap_data: Dict):
        """
        Add YouTube resources to modules using YouTube API
        This replaces the old _enhance_with_resources method
        """
        try:
            from app.services.youtube_service import get_youtube_service
            youtube_service = get_youtube_service()
            
            print("🎥 Fetching YouTube videos for modules...")
            
            # Get all modules for this path
            modules = PathModule.query.filter_by(path_id=path_id).all()
            
            for module in modules:
                try:
                    # Search for videos
                    videos = youtube_service.search_videos(
                        query=module.title,
                        max_results=2,  # Get 2 videos per module
                        difficulty='beginner'
                    )
                    
                    # Add videos as resources
                    for video in videos:
                        # Skip if it's not a valid video URL
                        if not video.get('video_id'):
                            continue
                            
                        resource = ModuleResource(
                            module_id=module.id,
                            title=video['title'],
                            url=video['url'],  # This will be https://www.youtube.com/watch?v=VIDEO_ID
                            type='video',
                            difficulty='beginner',
                            created_at=datetime.utcnow()
                        )
                        db.session.add(resource)
                    
                    print(f"✅ Added {len(videos)} videos for: {module.title}")
                    
                except Exception as e:
                    print(f"⚠️ Failed to add videos for {module.title}: {e}")
                    # Add a fallback resource
                    search_url = f"https://www.youtube.com/results?search_query={module.title.replace(' ', '+')}"
                    resource = ModuleResource(
                        module_id=module.id,
                        title=f"Search: {module.title}",
                        url=search_url,
                        type='video',
                        difficulty='beginner',
                        created_at=datetime.utcnow()
                    )
                    db.session.add(resource)
            
            db.session.flush()
            print("✅ YouTube resources added successfully")
            
        except Exception as e:
            print(f"⚠️ Error adding YouTube resources: {e}")
            # Don't fail the entire path generation if YouTube fails
            pass
    
    def _prepare_response(self, learning_path: LearningPath, 
                         roadmap_data: Dict) -> Dict:
        """Prepare final response data with proper resources"""
        
        courses = Course.query.filter_by(path_id=learning_path.id)\
            .order_by(Course.order).all()
        
        courses_response = []
        total_modules = 0
        
        for course in courses:
            modules = PathModule.query.filter_by(course_id=course.id)\
                .order_by(PathModule.order).all()
            
            modules_response = []
            for module in modules:
                # ✅ FIX: Load actual resources
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