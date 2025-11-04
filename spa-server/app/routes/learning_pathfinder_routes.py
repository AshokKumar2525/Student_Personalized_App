"""
Optimized Learning Path Routes
Includes caching, lazy loading, and progress tracking
"""

from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models.learning_pathfinder import (
    UserProfile, LearningPath, PathModule, ModuleResource,
    UserProgress, Course, Domain
)
from app.models.users import User
from app.services.learning_path_service import LearningPathService
from functools import wraps
from datetime import datetime, timedelta
import traceback

# Import enhanced models
from app.models.enhanced_progress import LearningSession, UserStreak, RoadmapCache
from app.models.roadmap_templates import ModuleFeedback, CourseFeedback

learning_pathfinder_bp = Blueprint('learning_pathfinder', __name__)
lp_service = LearningPathService()

# In-memory cache for frequently accessed data
_cache = {
    'roadmaps': {},  # user_id: {data, timestamp}
    'modules': {},   # module_id: {data, timestamp}
}
CACHE_DURATION = 300  # 5 minutes


def handle_errors(f):
    """Error handling decorator"""
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
    """Generate personalized learning roadmap"""
    data = request.get_json()
    
    required_fields = ['firebase_uid', 'domain', 'knowledge_level', 'weekly_hours', 'learning_pace']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({'error': f'Missing: {", ".join(missing_fields)}'}), 400
    
    user = User.query.filter_by(id=data['firebase_uid']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    result = lp_service.generate_learning_path(
        user_id=data['firebase_uid'],
        domain=data['domain'],
        knowledge_level=data['knowledge_level'],
        familiar_techs=data.get('familiar_techs', []),
        weekly_hours=data['weekly_hours'],
        learning_pace=data['learning_pace']
    )
    
    # Clear cache for this user
    if data['firebase_uid'] in _cache['roadmaps']:
        del _cache['roadmaps'][data['firebase_uid']]
    
    return jsonify(result), 201


@learning_pathfinder_bp.route('/learning-path/user-roadmap', methods=['GET'])
@handle_errors
def get_user_learning_path():
    """Get user's roadmap with caching"""
    firebase_uid = request.args.get('firebase_uid')
    
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    # Check in-memory cache first
    if firebase_uid in _cache['roadmaps']:
        cached_data = _cache['roadmaps'][firebase_uid]
        if datetime.now() - cached_data['timestamp'] < timedelta(seconds=CACHE_DURATION):
            print("✅ Serving from memory cache")
            return jsonify(cached_data['data']), 200
    
    # Check database cache
    cache_entry = RoadmapCache.query.filter_by(user_id=firebase_uid, is_valid=True).first()
    if cache_entry:
        import json
        print("✅ Serving from database cache")
        response_data = json.loads(cache_entry.roadmap_data)
        
        # Update in-memory cache
        _cache['roadmaps'][firebase_uid] = {
            'data': response_data,
            'timestamp': datetime.now()
        }
        
        return jsonify(response_data), 200
    
    # Fetch fresh data
    learning_path = LearningPath.query.filter_by(user_id=firebase_uid)\
        .order_by(LearningPath.created_at.desc()).first()
    
    if not learning_path:
        return jsonify({'has_path': False}), 200
    
    # Build response
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
            progress = UserProgress.query.filter_by(
                user_id=firebase_uid,
                module_id=module.id
            ).first()
            
            module_status = progress.status if progress else 'not_started'
            if module_status == 'completed':
                completed_modules += 1
            
            # Lazy load resources only when needed
            modules_data.append({
                'id': module.id,
                'title': module.title,
                'description': module.description,
                'order': module.order,
                'estimated_time': module.estimated_time,
                'status': module_status,
                'has_resources': True  # Flag instead of loading all resources
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
    
    response_data = {
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
    }
    
    # Cache the response (update if exists, insert if new)
    import json
    cache_entry = RoadmapCache.query.filter_by(learning_path_id=learning_path.id).first()
    
    if cache_entry:
        # Update existing cache
        cache_entry.roadmap_data = json.dumps(response_data)
        cache_entry.is_valid = True
        cache_entry.updated_at = datetime.now()
    else:
        # Create new cache
        cache_entry = RoadmapCache(
            user_id=firebase_uid,
            learning_path_id=learning_path.id,
            roadmap_data=json.dumps(response_data),
            is_valid=True
        )
        db.session.add(cache_entry)
    
    db.session.commit()
    
    # Update in-memory cache
    _cache['roadmaps'][firebase_uid] = {
        'data': response_data,
        'timestamp': datetime.now()
    }
    
    return jsonify(response_data), 200


@learning_pathfinder_bp.route('/learning-path/module-content/<int:module_id>', methods=['GET'])
@handle_errors
def get_module_content(module_id):
    """Get module content with lazy loading"""
    firebase_uid = request.args.get('firebase_uid')
    
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    # Check cache
    cache_key = f"{firebase_uid}_{module_id}"
    if cache_key in _cache['modules']:
        cached_data = _cache['modules'][cache_key]
        if datetime.now() - cached_data['timestamp'] < timedelta(seconds=CACHE_DURATION):
            print("✅ Serving module from cache")
            return jsonify(cached_data['data']), 200
    
    module = PathModule.query.get(module_id)
    if not module:
        return jsonify({'error': 'Module not found'}), 404
    
    learning_path = LearningPath.query.get(module.path_id)
    if not learning_path or learning_path.user_id != firebase_uid:
        return jsonify({'error': 'Access denied'}), 403
    
    progress = UserProgress.query.filter_by(
        user_id=firebase_uid,
        module_id=module_id
    ).first()
    
    # Check if previous module is completed
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
    
    # Load resources only when accessing module
    resources = ModuleResource.query.filter_by(module_id=module_id).all()
    
    # Simple educational content
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
    
    response_data = {
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
    }
    
    # Cache the response
    _cache['modules'][cache_key] = {
        'data': response_data,
        'timestamp': datetime.now()
    }
    
    return jsonify(response_data), 200


@learning_pathfinder_bp.route('/learning-path/update-progress', methods=['POST'])
@handle_errors
def update_module_progress():
    """Update progress with session tracking"""
    data = request.get_json()
    
    required_fields = ['firebase_uid', 'module_id', 'status']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({'error': f'Missing: {", ".join(missing_fields)}'}), 400
    
    valid_statuses = ['not_started', 'in_progress', 'completed']
    if data['status'] not in valid_statuses:
        return jsonify({'error': f'Invalid status. Must be one of {valid_statuses}'}), 400
    
    profile = UserProfile.query.filter_by(user_id=data['firebase_uid']).first()
    if not profile:
        return jsonify({'error': 'User profile not found'}), 404
    
    # Get or create progress record
    progress = UserProgress.query.filter_by(
        user_id=data['firebase_uid'],
        module_id=data['module_id']
    ).first()
    
    if progress:
        old_status = progress.status
        progress.status = data['status']
        progress.updated_at = datetime.utcnow()
        
        if data['status'] == 'completed' and old_status != 'completed':
            progress.completion_date = datetime.utcnow()
            
            # Update streak
            streak = UserStreak.query.filter_by(user_id=data['firebase_uid']).first()
            if streak:
                streak.update_streak()
            
            # Award points
            from app.models.learning_pathfinder import UserPoints
            points_record = UserPoints.query.filter_by(user_id=data['firebase_uid']).first()
            if not points_record:
                points_record = UserPoints(user_id=data['firebase_uid'], points=0)
                db.session.add(points_record)
            
            points_record.points += 10  # 10 points per module completion
            
    else:
        progress = UserProgress(
            user_id=data['firebase_uid'],
            module_id=data['module_id'],
            profile_id=profile.id,
            status=data['status'],
            completion_date=datetime.utcnow() if data['status'] == 'completed' else None,
            created_at=datetime.utcnow()
        )
        db.session.add(progress)
        
        if data['status'] == 'completed':
            streak = UserStreak.query.filter_by(user_id=data['firebase_uid']).first()
            if streak:
                streak.update_streak()
    
    # Create learning session
    module = PathModule.query.get(data['module_id'])
    if module:
        session = LearningSession(
            user_id=data['firebase_uid'],
            module_id=data['module_id'],
            course_id=module.course_id,
            duration_minutes=data.get('duration_minutes', 0),
            completed_in_session=(data['status'] == 'completed'),
            started_at=datetime.utcnow()
        )
        db.session.add(session)
    
    db.session.commit()
    
    # Invalidate cache
    if data['firebase_uid'] in _cache['roadmaps']:
        del _cache['roadmaps'][data['firebase_uid']]
    
    # Invalidate database cache
    RoadmapCache.query.filter_by(user_id=data['firebase_uid']).update({'is_valid': False})
    db.session.commit()
    
    # Find next module
    current_module = PathModule.query.get(data['module_id'])
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
        'message': 'Progress updated successfully',
        'next_module': next_module_data,
        'is_course_completed': next_module is None
    }), 200


@learning_pathfinder_bp.route('/learning-path/complete-module', methods=['POST'])
@handle_errors
def complete_module():
    """Mark module as completed"""
    data = request.get_json()
    
    required_fields = ['firebase_uid', 'module_id']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({'error': f'Missing: {", ".join(missing_fields)}'}), 400
    
    # Use update_progress endpoint
    return update_module_progress()


@learning_pathfinder_bp.route('/learning-path/statistics', methods=['GET'])
@handle_errors
def get_learning_statistics():
    """Get comprehensive learning statistics"""
    firebase_uid = request.args.get('firebase_uid')
    
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    learning_path = LearningPath.query.filter_by(user_id=firebase_uid)\
        .order_by(LearningPath.created_at.desc()).first()
    
    if not learning_path:
        return jsonify({'error': 'No learning path found'}), 404
    
    # Get progress records
    progress_records = UserProgress.query.filter_by(user_id=firebase_uid).all()
    
    completed = len([p for p in progress_records if p.status == 'completed'])
    in_progress = len([p for p in progress_records if p.status == 'in_progress'])
    total = len(progress_records)
    
    # Calculate total time
    modules = PathModule.query.filter_by(path_id=learning_path.id).all()
    total_time = sum(m.estimated_time for m in modules)
    
    # Get streak data
    streak = UserStreak.query.filter_by(user_id=firebase_uid).first()
    
    # Get points
    from app.models.learning_pathfinder import UserPoints
    points = UserPoints.query.filter_by(user_id=firebase_uid).first()
    
    # Get session data
    total_sessions = LearningSession.query.filter_by(user_id=firebase_uid).count()
    total_learning_time = db.session.query(
        db.func.sum(LearningSession.duration_minutes)
    ).filter_by(user_id=firebase_uid).scalar() or 0
    
    completion_rate = (completed / total * 100) if total > 0 else 0
    
    return jsonify({
        'total_modules': total,
        'completed_modules': completed,
        'in_progress_modules': in_progress,
        'total_estimated_time': total_time,
        'completion_rate': round(completion_rate, 2),
        'current_streak': streak.current_streak if streak else 0,
        'longest_streak': streak.longest_streak if streak else 0,
        'total_points': points.points if points else 0,
        'total_sessions': total_sessions,
        'total_learning_time': total_learning_time
    }), 200


@learning_pathfinder_bp.route('/learning-path/submit-feedback', methods=['POST'])
@handle_errors
def submit_feedback():
    """Submit module or course feedback"""
    data = request.get_json()
    
    required_fields = ['firebase_uid', 'type', 'target_id', 'rating']
    missing_fields = [field for field in required_fields if field not in data]
    
    if missing_fields:
        return jsonify({'error': f'Missing: {", ".join(missing_fields)}'}), 400
    
    if data['type'] == 'module':
        feedback = ModuleFeedback(
            user_id=data['firebase_uid'],
            module_id=data['target_id'],
            rating=data['rating'],
            comments=data.get('comments'),
            difficulty_rating=data.get('difficulty_rating'),
            content_quality=data.get('content_quality'),
            time_accuracy=data.get('time_accuracy')
        )
        db.session.add(feedback)
    
    elif data['type'] == 'course':
        feedback = CourseFeedback(
            user_id=data['firebase_uid'],
            course_id=data['target_id'],
            rating=data['rating'],
            comments=data.get('comments'),
            would_recommend=data.get('would_recommend', True)
        )
        db.session.add(feedback)
    
    else:
        return jsonify({'error': 'Invalid feedback type'}), 400
    
    db.session.commit()
    
    return jsonify({'message': 'Feedback submitted successfully'}), 201


@learning_pathfinder_bp.route('/learning-path/domains', methods=['GET'])
@handle_errors
def get_available_domains():
    """Get list of available domains"""
    domains = Domain.query.all()
    
    domains_data = []
    for domain in domains:
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
    """Reset user's learning path"""
    data = request.get_json()
    
    if not data.get('firebase_uid'):
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    if not data.get('confirm'):
        return jsonify({'error': 'Confirmation required'}), 400
    
    # Clear caches first
    if data['firebase_uid'] in _cache['roadmaps']:
        del _cache['roadmaps'][data['firebase_uid']]
    
    RoadmapCache.query.filter_by(user_id=data['firebase_uid']).delete(synchronize_session=False)
    
    # Delete learning paths (cascade will handle related data automatically)
    LearningPath.query.filter_by(user_id=data['firebase_uid']).delete(synchronize_session=False)
    
    # Delete user profile
    UserProfile.query.filter_by(user_id=data['firebase_uid']).delete(synchronize_session=False)
    
    db.session.commit()
    
    return jsonify({'message': 'Learning path reset successfully'}), 200


@learning_pathfinder_bp.route('/learning-path/streak', methods=['GET'])
@handle_errors
def get_user_streak():
    """Get user streak information"""
    firebase_uid = request.args.get('firebase_uid')
    
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    streak = UserStreak.query.filter_by(user_id=firebase_uid).first()
    
    if not streak:
        return jsonify({
            'current_streak': 0,
            'longest_streak': 0,
            'total_learning_days': 0
        }), 200
    
    return jsonify(streak.to_dict()), 200


@learning_pathfinder_bp.route('/learning-path/test', methods=['GET'])
def test_endpoint():
    """Health check"""
    return jsonify({
        'message': 'Learning Path Finder API is working!',
        'status': 'success',
        'version': '3.0',
        'features': [
            'Template caching',
            'Progress tracking',
            'Session management',
            'Streak gamification',
            'Feedback system'
        ]
    }), 200