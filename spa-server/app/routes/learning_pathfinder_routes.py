"""
Updated Learning Path Routes - Production Ready
Clean, validated, and optimized API endpoints
"""

from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.learning_pathfinder import (
    UserProfile, LearningPath, PathModule, ModuleResource,
    UserProgress, Course
)
from app.models.users import User
from app.services.learning_path_service import LearningPathService
from functools import wraps
import traceback

learning_pathfinder_bp = Blueprint('learning_pathfinder', __name__)

# Initialize service
lp_service = LearningPathService()


def handle_errors(f):
    """Decorator for consistent error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e), 'type': 'validation_error'}), 400
        except Exception as e:
            current_app.logger.error(f"Error in {f.__name__}: {str(e)}")
            current_app.logger.error(traceback.format_exc())
            return jsonify({'error': 'Internal server error', 'type': 'server_error'}), 500
    return decorated_function


@learning_pathfinder_bp.route('/learning-path/generate-roadmap', methods=['POST'])
@handle_errors
def generate_learning_path():
    """
    Generate a personalized learning roadmap
    
    Request Body:
        {
            "firebase_uid": "string",
            "domain": "string",
            "knowledge_level": "beginner|intermediate|advanced",
            "familiar_techs": ["string"],
            "weekly_hours": int (1-40),
            "learning_pace": "slow|medium|fast"
        }
    
    Response:
        {
            "message": "string",
            "path_id": int,
            "domain": "string",
            "roadmap": {...}
        }
    """
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['firebase_uid', 'domain', 'knowledge_level', 'weekly_hours', 'learning_pace']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            'error': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400
    
    # Verify user exists
    user = User.query.filter_by(id=data['firebase_uid']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Generate learning path
    result = lp_service.generate_learning_path(
        user_id=data['firebase_uid'],
        domain=data['domain'],
        knowledge_level=data['knowledge_level'],
        familiar_techs=data.get('familiar_techs', []),
        weekly_hours=data['weekly_hours'],
        learning_pace=data['learning_pace']
    )
    
    return jsonify(result), 201


@learning_pathfinder_bp.route('/learning-path/user-roadmap', methods=['GET'])
@handle_errors
def get_user_learning_path():
    """
    Get user's current learning path with progress
    
    Query Parameters:
        firebase_uid: string (required)
    
    Response:
        {
            "has_path": bool,
            "path_id": int,
            "domain": "string",
            "domain_name": "string",
            "progress_percentage": float,
            "completed_modules": int,
            "total_modules": int,
            "courses": [...]
        }
    """
    firebase_uid = request.args.get('firebase_uid')
    
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    # Get most recent learning path
    learning_path = LearningPath.query.filter_by(user_id=firebase_uid)\
        .order_by(LearningPath.created_at.desc()).first()
    
    if not learning_path:
        return jsonify({'has_path': False}), 200
    
    # Get all courses with modules
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
            # Get progress for this module
            progress = UserProgress.query.filter_by(
                user_id=firebase_uid,
                module_id=module.id
            ).first()
            
            module_status = progress.status if progress else 'not_started'
            if module_status == 'completed':
                completed_modules += 1
            
            # Get resources
            resources = ModuleResource.query.filter_by(module_id=module.id).all()
            
            modules_data.append({
                'id': module.id,
                'title': module.title,
                'description': module.description,
                'order': module.order,
                'estimated_time': module.estimated_time,
                'status': module_status,
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
        
        courses_data.append({
            'id': course.id,
            'title': course.title,
            'description': course.description,
            'order': course.order,
            'estimated_time': course.estimated_time,
            'modules': modules_data
        })
    
    # Get domain info
    from app.models.learning_pathfinder import Domain
    domain = Domain.query.get(learning_path.domain_id)
    
    progress_percentage = (completed_modules / total_modules * 100) if total_modules > 0 else 0
    
    return jsonify({
        'has_path': True,
        'path_id': learning_path.id,
        'domain': domain.name if domain else 'Unknown',
        'domain_name': f"{domain.name.title()} Development" if domain else 'Unknown',
        'current_version': learning_path.current_version,
        'created_at': learning_path.created_at.isoformat(),
        'progress_percentage': round(progress_percentage, 2),
        'completed_modules': completed_modules,
        'total_modules': total_modules,
        'courses': courses_data
    }), 200


@learning_pathfinder_bp.route('/learning-path/module-content/<int:module_id>', methods=['GET'])
@handle_errors
def get_module_content(module_id):
    """
    Get detailed content for a specific module
    
    Path Parameters:
        module_id: int
    
    Query Parameters:
        firebase_uid: string (required)
    
    Response:
        {
            "module": {...},
            "educational_content": {...},
            "resources": [...],
            "can_access": bool,
            "current_progress": "string"
        }
    """
    firebase_uid = request.args.get('firebase_uid')
    
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    # Get module
    module = PathModule.query.get(module_id)
    if not module:
        return jsonify({'error': 'Module not found'}), 404
    
    # Check if user has access (verify they own this learning path)
    learning_path = LearningPath.query.get(module.path_id)
    if not learning_path or learning_path.user_id != firebase_uid:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get user progress
    progress = UserProgress.query.filter_by(
        user_id=firebase_uid,
        module_id=module_id
    ).first()
    
    # Check if previous module is completed (for linear progression)
    can_access = True
    if module.order > 1:
        previous_module = PathModule.query.filter_by(
            course_id=module.course_id,
            order=module.order - 1
        ).first()
        
        if previous_module:
            prev_progress = UserProgress.query.filter_by(
                user_id=firebase_uid,
                module_id=previous_module.id
            ).first()
            
            can_access = prev_progress and prev_progress.status == 'completed'
    
    # Get resources
    resources = ModuleResource.query.filter_by(module_id=module_id).all()
    
    # Generate educational content (simple structure)
    educational_content = {
        "explanation": f"This module covers {module.title}. {module.description}",
        "key_concepts": [
            f"Understanding {module.title} fundamentals",
            f"Practical application of {module.title}",
            f"Best practices for {module.title}"
        ],
        "examples": [
            f"Example 1: Basic {module.title} implementation",
            f"Example 2: Real-world {module.title} scenario"
        ],
        "practice_problems": [
            f"Practice: Implement {module.title} concepts",
            f"Challenge: Advanced {module.title} problem"
        ]
    }
    
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
                'id': r.id,
                'title': r.title,
                'url': r.url,
                'embed_url': r.url.replace('watch?v=', 'embed/') if 'youtube.com' in r.url else None,
                'type': r.type,
                'difficulty': r.difficulty
            } for r in resources
        ],
        'can_access': can_access,
        'current_progress': progress.status if progress else 'not_started'
    }), 200


@learning_pathfinder_bp.route('/learning-path/update-progress', methods=['POST'])
@handle_errors
def update_module_progress():
    """
    Update progress for a module
    
    Request Body:
        {
            "firebase_uid": "string",
            "module_id": int,
            "status": "not_started|in_progress|completed"
        }
    
    Response:
        {
            "message": "string",
            "module_id": int,
            "status": "string"
        }
    """
    data = request.get_json()
    
    required_fields = ['firebase_uid', 'module_id', 'status']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            'error': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400
    
    # Validate status
    valid_statuses = ['not_started', 'in_progress', 'completed']
    if data['status'] not in valid_statuses:
        return jsonify({
            'error': f'Invalid status. Must be one of {valid_statuses}'
        }), 400
    
    # Get user profile
    profile = UserProfile.query.filter_by(user_id=data['firebase_uid']).first()
    if not profile:
        return jsonify({'error': 'User profile not found'}), 404
    
    # Get or create progress record
    progress = UserProgress.query.filter_by(
        user_id=data['firebase_uid'],
        module_id=data['module_id']
    ).first()
    
    from datetime import datetime
    
    if progress:
        progress.status = data['status']
        if data['status'] == 'completed':
            progress.completion_date = datetime.utcnow()
    else:
        progress = UserProgress(
            user_id=data['firebase_uid'],
            module_id=data['module_id'],
            profile_id=profile.id,
            status='completed',
            completion_date=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db.session.add(progress)
    
    db.session.commit()
    
    # Get current module info to find next module
    current_module = PathModule.query.get(data['module_id'])
    if not current_module:
        return jsonify({'error': 'Module not found'}), 404
    
    # Find next module in the same course
    next_module = PathModule.query.filter_by(
        course_id=current_module.course_id,
        order=current_module.order + 1
    ).first()
    
    next_module_data = None
    if next_module:
        next_module_data = {
            'id': next_module.id,
            'title': next_module.title,
            'description': next_module.description,
            'estimated_time': next_module.estimated_time
        }
    
    return jsonify({
        'message': 'Module completed successfully',
        'next_module': next_module_data,
        'is_course_completed': next_module is None
    }), 200


@learning_pathfinder_bp.route('/learning-path/statistics', methods=['GET'])
@handle_errors
def get_learning_statistics():
    """
    Get user's learning statistics
    
    Query Parameters:
        firebase_uid: string (required)
    
    Response:
        {
            "total_modules": int,
            "completed_modules": int,
            "in_progress_modules": int,
            "total_time_spent": int,
            "average_completion_time": int,
            "completion_rate": float
        }
    """
    firebase_uid = request.args.get('firebase_uid')
    
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    # Get user's learning path
    learning_path = LearningPath.query.filter_by(user_id=firebase_uid)\
        .order_by(LearningPath.created_at.desc()).first()
    
    if not learning_path:
        return jsonify({'error': 'No learning path found'}), 404
    
    # Get all progress records
    progress_records = UserProgress.query.filter_by(user_id=firebase_uid).all()
    
    completed = len([p for p in progress_records if p.status == 'completed'])
    in_progress = len([p for p in progress_records if p.status == 'in_progress'])
    total = len(progress_records)
    
    # Calculate total estimated time
    modules = PathModule.query.filter_by(path_id=learning_path.id).all()
    total_time = sum(m.estimated_time for m in modules)
    
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    return jsonify({
        'total_modules': total,
        'completed_modules': completed,
        'in_progress_modules': in_progress,
        'total_estimated_time': total_time,
        'completion_rate': round(completion_rate, 2)
    }), 200


@learning_pathfinder_bp.route('/learning-path/domains', methods=['GET'])
@handle_errors
def get_available_domains():
    """
    Get list of available learning domains
    
    Response:
        {
            "domains": [
                {
                    "id": int,
                    "name": "string",
                    "description": "string",
                    "total_learners": int
                }
            ]
        }
    """
    from app.models.learning_pathfinder import Domain
    
    domains = Domain.query.all()
    
    domains_data = []
    for domain in domains:
        # Count learners in this domain
        learner_count = LearningPath.query.filter_by(domain_id=domain.id).count()
        
        domains_data.append({
            'id': domain.id,
            'name': domain.name,
            'description': domain.description,
            'total_learners': learner_count
        })
    
    return jsonify({'domains': domains_data}), 200


@learning_pathfinder_bp.route('/learning-path/reset', methods=['POST'])
@handle_errors
def reset_learning_path():
    """
    Reset user's learning path (delete and start fresh)
    
    Request Body:
        {
            "firebase_uid": "string",
            "confirm": true
        }
    
    Response:
        {
            "message": "string"
        }
    """
    data = request.get_json()
    
    if not data.get('firebase_uid'):
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    if not data.get('confirm'):
        return jsonify({'error': 'Confirmation required'}), 400
    
    # Delete all learning paths and related data
    learning_paths = LearningPath.query.filter_by(user_id=data['firebase_uid']).all()
    
    for path in learning_paths:
        # Progress records will be deleted via cascade
        db.session.delete(path)
    
    # Delete user profile
    profile = UserProfile.query.filter_by(user_id=data['firebase_uid']).first()
    if profile:
        db.session.delete(profile)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Learning path reset successfully'
    }), 200


@learning_pathfinder_bp.route('/learning-path/test', methods=['GET'])
def test_endpoint():
    """Health check endpoint"""
    return jsonify({
        'message': 'Learning Path Finder API is working!',
        'status': 'success',
        'version': '2.0'
    }), 200

@learning_pathfinder_bp.route('/learning-path/complete-module', methods=['POST'])
@handle_errors
def complete_module():
    """
    Mark a module as completed and get next module info
    
    Request Body:
        {
            "firebase_uid": "string",
            "module_id": int
        }
    
    Response:
        {
            "message": "string",
            "next_module": {...} or null,
            "is_course_completed": bool
        }
    """
    data = request.get_json()
    
    required_fields = ['firebase_uid', 'module_id']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({
            'error': f'Missing required fields: {", ".join(missing_fields)}'
        }), 400
    
    # Get user profile
    profile = UserProfile.query.filter_by(user_id=data['firebase_uid']).first()
    if not profile:
        return jsonify({'error': 'User profile not found'}), 404
    
    # Update progress
    progress = UserProgress.query.filter_by(
        user_id=data['firebase_uid'],
        module_id=data['module_id']
    ).first()
    