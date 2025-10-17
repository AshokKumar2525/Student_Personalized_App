from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.learning_pathfinder_service import LearningPathfinderService

learning_pathfinder_bp = Blueprint('learning_pathfinder', __name__, url_prefix='/api/learning-path')
pathfinder_service = LearningPathfinderService()

@learning_pathfinder_bp.route('/generate-roadmap', methods=['POST'])
@jwt_required()
def generate_roadmap():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        print(f"Generating roadmap for user: {user_id}")
        print(f"Request data: {data}")
        
        required_fields = ['domain', 'knowledge_level', 'weekly_hours', 'learning_pace']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        roadmap = pathfinder_service.generate_learning_path(
            user_id=user_id,
            domain=data['domain'],
            knowledge_level=data['knowledge_level'],
            familiar_tech=data.get('familiar_tech', []),
            weekly_hours=data['weekly_hours'],
            learning_pace=data['learning_pace'],
            goals=data.get('goals')
        )
        
        return jsonify({
            'message': 'Learning path generated successfully',
            'path_id': roadmap.id,
            'domain': roadmap.domain
        }), 201
        
    except Exception as e:
        print(f"Error generating roadmap: {str(e)}")
        return jsonify({'error': str(e)}), 500

@learning_pathfinder_bp.route('/user-roadmap', methods=['GET'])
@jwt_required()
def get_user_roadmap():
    try:
        user_id = get_jwt_identity()
        print(f"Getting roadmap for user: {user_id}")
        
        progress = pathfinder_service.get_user_progress(user_id)
        
        if not progress:
            return jsonify({'error': 'No learning path found. Please generate one first.'}), 404
        
        return jsonify(progress), 200
        
    except Exception as e:
        print(f"Error getting roadmap: {str(e)}")
        return jsonify({'error': str(e)}), 500

@learning_pathfinder_bp.route('/update-progress', methods=['POST'])
@jwt_required()
def update_progress():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        
        if 'module_id' not in data or 'status' not in data:
            return jsonify({'error': 'Missing module_id or status'}), 400
        
        progress = pathfinder_service.update_progress(
            user_id=user_id,
            module_id=data['module_id'],
            status=data['status']
        )
        
        return jsonify({
            'message': 'Progress updated successfully',
            'module_id': progress.module_id,
            'status': progress.status.value
        }), 200
        
    except Exception as e:
        print(f"Error updating progress: {str(e)}")
        return jsonify({'error': str(e)}), 500

@learning_pathfinder_bp.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Learning pathfinder API is working!'}), 200