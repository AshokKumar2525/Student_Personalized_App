# In services/learning_pathfinder_service.py
import os
import json
import requests
from datetime import datetime
from app import db
from app.models.learning_pathfinder import (
    UserProfile, LearningPath, PathModule, ModuleResource, 
    UserProgress, Assessment, UserPoints, LearningPace, ModuleStatus
)
from app.models.users import User

class LearningPathfinderService:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
    
    def generate_learning_path(self, user_id, domain, knowledge_level, familiar_tech, 
                         weekly_hours, learning_pace, goals=None):
        try:
            # First ensure user exists
            user = User.query.filter_by(id=user_id).first()
            if not user:
                raise Exception("User not found")
            
            # Check if user already has a profile
            user_profile = UserProfile.query.filter_by(user_id=user_id).first()
            
            if not user_profile:
                user_profile = UserProfile(
                    user_id=user_id,
                    domain=domain,
                    current_level=knowledge_level,
                    familiar_tech=familiar_tech,
                    daily_time=weekly_hours * 60 // 7,
                    learning_pace=LearningPace(learning_pace)
                )
                db.session.add(user_profile)
                db.session.commit()
            
            # Generate roadmap
            roadmap_data = self._generate_ai_roadmap(
                domain, knowledge_level, familiar_tech, 
                weekly_hours, learning_pace, goals
            )
            
            # Create learning path - reference user directly
            learning_path = LearningPath(
                user_id=user_id,  # Direct reference to users.id
                domain=domain
            )
            db.session.add(learning_path)
            db.session.flush()
        
            # Create modules and resources
            for i, module_data in enumerate(roadmap_data.get('modules', [])):
                module = PathModule(
                    path_id=learning_path.id,
                    title=module_data['title'],
                    description=module_data.get('description', ''),
                    order=i + 1,
                    estimated_time=module_data.get('estimated_time', 60)
                )
                db.session.add(module)
                db.session.flush()
                
                # Add resources
                for resource_data in module_data.get('resources', []):
                    resource = ModuleResource(
                        module_id=module.id,
                        title=resource_data['title'],
                        url=resource_data['url'],
                        type=resource_data['type'],
                        difficulty=resource_data.get('difficulty', 'beginner')
                    )
                    db.session.add(resource)
            
            # Initialize user points for the profile
            user_points = UserPoints.query.filter_by(user_id=user_profile.id).first()
            if not user_points:
                user_points = UserPoints(user_id=user_profile.id, points=0)
                db.session.add(user_points)
            
            db.session.commit()
            return learning_path
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to generate learning path: {str(e)}")
    
    def get_user_progress(self, user_id):
        """Get user's learning progress"""
        try:
            user_profile = UserProfile.query.filter_by(user_id=user_id).first()
            if not user_profile:
                return None
            
            learning_path = LearningPath.query.filter_by(user_id=user_id).first()
            if not learning_path:
                return None
            
            progress = UserProgress.query.filter_by(user_id=user_profile.id).all()
            progress_map = {p.module_id: p for p in progress}
            
            modules = PathModule.query.filter_by(path_id=learning_path.id)\
                .order_by(PathModule.order).all()
            
            completed = len([p for p in progress if p.status == ModuleStatus.COMPLETED])
            total = len(modules)
            
            return {
                'path_id': learning_path.id,
                'domain': learning_path.domain,
                'progress_percentage': (completed / total * 100) if total > 0 else 0,
                'completed_modules': completed,
                'total_modules': total,
                'modules': [
                    {
                        'id': module.id,
                        'title': module.title,
                        'description': module.description,
                        'order': module.order,
                        'estimated_time': module.estimated_time,
                        'status': progress_map.get(module.id, UserProgress()).status.value if module.id in progress_map else 'not_started',
                        'resources': [
                            {
                                'id': resource.id,
                                'title': resource.title,
                                'url': resource.url,
                                'type': resource.type.value,
                                'difficulty': resource.difficulty
                            }
                            for resource in module.resources
                        ]
                    }
                    for module in modules
                ]
            }
        except Exception as e:
            print(f"Error getting user progress: {e}")
            return None
    
    def update_progress(self, user_id, module_id, status):
        """Update user progress for a module"""
        try:
            user_profile = UserProfile.query.filter_by(user_id=user_id).first()
            if not user_profile:
                raise Exception("User profile not found")
            
            progress = UserProgress.query.filter_by(
                user_id=user_profile.id, 
                module_id=module_id
            ).first()
            
            if not progress:
                progress = UserProgress(
                    user_id=user_profile.id,
                    module_id=module_id,
                    status=ModuleStatus(status)
                )
            else:
                progress.status = ModuleStatus(status)
            
            if status == 'completed':
                progress.completion_date = datetime.utcnow()
            
            db.session.add(progress)
            db.session.commit()
            
            return progress
            
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update progress: {str(e)}")
    
    def _generate_ai_roadmap(self, domain, level, tech_stack, hours, pace, goals):
        """Generate roadmap - simplified for now"""
        return self._get_template_roadmap(domain, level)
    
    def _get_template_roadmap(self, domain, level):
        """Template-based roadmap generation"""
        templates = {
            'web': {
                'beginner': {
                    'modules': [
                        {
                            'title': 'HTML & CSS Fundamentals',
                            'description': 'Learn the building blocks of web development',
                            'estimated_time': 120,
                            'resources': [
                                {
                                    'title': 'MDN Web Docs - HTML Basics',
                                    'url': 'https://developer.mozilla.org/en-US/docs/Learn/HTML/Introduction_to_HTML/Getting_started',
                                    'type': 'documentation',
                                    'difficulty': 'beginner'
                                }
                            ]
                        }
                    ]
                }
            }
        }
        
        domain_data = templates.get(domain, templates['web'])
        level_data = domain_data.get(level, domain_data['beginner'])
        
        return level_data