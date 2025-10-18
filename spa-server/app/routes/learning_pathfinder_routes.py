from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.learning_pathfinder import (
    UserProfile, LearningPath, PathModule, ModuleResource, 
    UserProgress, Domain, Technology, Course
)
from app.models.users import User
import openai
import os
import json
from datetime import datetime

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

        # Generate roadmap using OpenAI with course-module structure
        roadmap_data = generate_roadmap_with_openai(
            domain=domain,
            knowledge_level=knowledge_level,
            familiar_techs=familiar_techs,
            weekly_hours=weekly_hours,
            learning_pace=learning_pace
        )

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
        db.session.flush()  # This gets the auto-generated ID

        # Create courses and modules
        courses_data = roadmap_data.get('courses', [])
        total_modules = 0
        
        for course_data in courses_data:
            course = Course(
                path_id=learning_path.id,  # Use the auto-generated INTEGER ID
                title=course_data['title'],
                description=course_data['description'],
                order=course_data['order'],
                estimated_time=course_data.get('estimated_time', 0),
                created_at=datetime.utcnow()
            )
            db.session.add(course)
            db.session.flush()  # Get the auto-generated course ID

            # Create modules for this course
            modules_data = course_data.get('modules', [])
            for module_data in modules_data:
                module = PathModule(
                    course_id=course.id,  # Use the auto-generated course ID
                    path_id=learning_path.id,  # Keep path_id for backward compatibility
                    title=module_data['title'],
                    description=module_data['description'],
                    order=module_data['order'],
                    estimated_time=module_data.get('estimated_time', 60),
                    created_at=datetime.utcnow()
                )
                db.session.add(module)
                db.session.flush()  # Get the auto-generated module ID
                total_modules += 1

                # Create module resources
                resources_data = module_data.get('resources', [])
                for resource_data in resources_data:
                    resource = ModuleResource(
                        module_id=module.id,  # Use the auto-generated module ID
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
                    module_id=module.id,  # Use the auto-generated module ID
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

def generate_roadmap_with_openai(domain, knowledge_level, familiar_techs, weekly_hours, learning_pace):
    """Generate learning roadmap with course-module structure"""
    
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if not openai_api_key:
        return get_structured_mock_data(domain, knowledge_level)
    
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        
        prompt = f"""
        Create a comprehensive learning roadmap for {domain} at {knowledge_level} level.
        
        Student profile:
        - Level: {knowledge_level}
        - Weekly study time: {weekly_hours} hours  
        - Learning pace: {learning_pace}
        - Familiar with: {', '.join(familiar_techs) if familiar_techs else 'Nothing yet'}
        
        STRUCTURE:
        First, divide {domain} into 3-4 main COURSES that cover the major topics.
        Then, divide each COURSE into 3-5 MODULES that progress logically.
        
        Return ONLY valid JSON with this structure:
        {{
            "domain": "{domain}",
            "domain_name": "Professional {domain.title()} Development",
            "level": "{knowledge_level}",
            "estimated_completion": "X weeks",
            "progress_percentage": 0.0,
            "completed_modules": 0,
            "total_modules": 12,
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
                                    "type": "video/documentation/article",
                                    "difficulty": "beginner"
                                }}
                            ]
                        }}
                    ]
                }}
            ]
        }}
        
        Make it practical with real projects and industry-relevant content.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert curriculum designer. Create structured learning paths with courses and modules."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        roadmap_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        start_idx = roadmap_text.find('{')
        end_idx = roadmap_text.rfind('}') + 1
        if start_idx != -1 and end_idx != 0:
            roadmap_json = roadmap_text[start_idx:end_idx]
            return json.loads(roadmap_json)
        else:
            current_app.logger.error(f"Invalid JSON response from OpenAI")
            return get_structured_mock_data(domain, knowledge_level)
            
    except Exception as e:
        current_app.logger.error(f"OpenAI API error: {str(e)}")
        return get_structured_mock_data(domain, knowledge_level)

def get_structured_mock_data(domain, knowledge_level):
    """Structured mock data with courses and modules"""
    
    domain_name = domain.title() + " Development"
    
    # Domain-specific course structures
    domain_structures = {
        'web': [
            {
                'title': 'Frontend Fundamentals',
                'description': 'Master the core technologies of web development',
                'estimated_time': 720,
                'modules': [
                    {'title': 'HTML5 & Semantic Markup', 'description': 'Learn modern HTML structure and accessibility', 'estimated_time': 120},
                    {'title': 'CSS3 & Responsive Design', 'description': 'Master CSS Grid, Flexbox and mobile-first design', 'estimated_time': 180},
                    {'title': 'JavaScript Essentials', 'description': 'Learn variables, functions, DOM manipulation', 'estimated_time': 180},
                    {'title': 'Modern JavaScript ES6+', 'description': 'Master arrow functions, destructuring, modules', 'estimated_time': 180},
                    {'title': 'Git & Version Control', 'description': 'Learn essential development workflow tools', 'estimated_time': 60}
                ]
            },
            {
                'title': 'Frontend Frameworks',
                'description': 'Build dynamic applications with modern frameworks',
                'estimated_time': 900,
                'modules': [
                    {'title': 'React Fundamentals', 'description': 'Learn components, props, and state management', 'estimated_time': 180},
                    {'title': 'React Hooks & Advanced Patterns', 'description': 'Master useEffect, useContext, custom hooks', 'estimated_time': 180},
                    {'title': 'State Management', 'description': 'Learn Redux or Context API for complex state', 'estimated_time': 180},
                    {'title': 'Routing & SPAs', 'description': 'Build single-page applications with React Router', 'estimated_time': 120},
                    {'title': 'Testing & Debugging', 'description': 'Learn testing strategies and debugging techniques', 'estimated_time': 120},
                    {'title': 'Build Tools & Deployment', 'description': 'Master Webpack, Vite and deployment processes', 'estimated_time': 120}
                ]
            },
            {
                'title': 'Backend Development',
                'description': 'Build server-side applications and APIs',
                'estimated_time': 840,
                'modules': [
                    {'title': 'Node.js & Express', 'description': 'Learn server-side JavaScript with Express framework', 'estimated_time': 180},
                    {'title': 'RESTful API Design', 'description': 'Design and build professional REST APIs', 'estimated_time': 180},
                    {'title': 'Database Fundamentals', 'description': 'Learn SQL and database design principles', 'estimated_time': 180},
                    {'title': 'Authentication & Security', 'description': 'Implement secure user authentication', 'estimated_time': 120},
                    {'title': 'API Testing', 'description': 'Learn testing strategies for backend services', 'estimated_time': 90},
                    {'title': 'Deployment & DevOps', 'description': 'Deploy applications to cloud platforms', 'estimated_time': 90}
                ]
            }
        ],
        'flutter': [
            {
                'title': 'Dart Programming Language',
                'description': 'Master the fundamentals of Dart programming',
                'estimated_time': 480,
                'modules': [
                    {'title': 'Dart Syntax & Basics', 'description': 'Learn variables, functions, and control flow', 'estimated_time': 120},
                    {'title': 'Object-Oriented Programming', 'description': 'Master classes, inheritance, and polymorphism', 'estimated_time': 180},
                    {'title': 'Asynchronous Programming', 'description': 'Learn async/await and Futures', 'estimated_time': 120},
                    {'title': 'Dart Collections & Libraries', 'description': 'Master lists, maps, and core libraries', 'estimated_time': 60}
                ]
            },
            {
                'title': 'Flutter Fundamentals',
                'description': 'Build beautiful mobile applications with Flutter',
                'estimated_time': 720,
                'modules': [
                    {'title': 'Widget Tree & Basics', 'description': 'Understand Flutter widget hierarchy', 'estimated_time': 120},
                    {'title': 'Layout Widgets', 'description': 'Master Row, Column, Container, and Stack', 'estimated_time': 180},
                    {'title': 'State Management Basics', 'description': 'Learn setState and stateful widgets', 'estimated_time': 120},
                    {'title': 'Navigation & Routing', 'description': 'Implement app navigation between screens', 'estimated_time': 120},
                    {'title': 'Forms & User Input', 'description': 'Handle user input and form validation', 'estimated_time': 90},
                    {'title': 'Theming & Styling', 'description': 'Create consistent app themes and styles', 'estimated_time': 90}
                ]
            },
            {
                'title': 'Advanced Flutter Development',
                'description': 'Build production-ready Flutter applications',
                'estimated_time': 900,
                'modules': [
                    {'title': 'Advanced State Management', 'description': 'Learn Provider, Bloc, or Riverpod', 'estimated_time': 180},
                    {'title': 'API Integration', 'description': 'Connect your app to REST APIs', 'estimated_time': 180},
                    {'title': 'Local Data Storage', 'description': 'Implement SQLite, Hive, or SharedPreferences', 'estimated_time': 120},
                    {'title': 'Animations & Custom Widgets', 'description': 'Create smooth animations and custom UI', 'estimated_time': 180},
                    {'title': 'Firebase Integration', 'description': 'Add authentication, database, and storage', 'estimated_time': 120},
                    {'title': 'App Publishing', 'description': 'Prepare and publish to app stores', 'estimated_time': 120}
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
                {'title': 'Advanced Topics', 'description': 'Explore more complex concepts', 'estimated_time': 120}
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
                        'title': 'Learning Resource',
                        'url': 'https://example.com/learn',
                        'type': 'documentation',
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

@learning_pathfinder_bp.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({'message': 'Learning Path Finder API is working!', 'status': 'success'})