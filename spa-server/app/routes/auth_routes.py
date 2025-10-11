from flask import Blueprint, request, jsonify
from app import db
from app.models.users import User
from datetime import datetime
import requests
import os
import uuid
from werkzeug.utils import secure_filename

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/auth/sync-user', methods=['POST'])
def sync_user():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data or 'email' not in data or 'firebase_uid' not in data:
            return jsonify({'error': 'Email and Firebase UID are required'}), 400
        
        email = data['email']
        firebase_uid = data['firebase_uid']
        full_name = data.get('full_name', '')
        avatar_url = data.get('avatar_url', '')
        
        # Check if user already exists
        existing_user = User.query.filter_by(id=firebase_uid).first()
        
        if existing_user:
            # Update existing user
            existing_user.full_name = full_name
            existing_user.avatar_url = avatar_url
            existing_user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'message': 'User updated successfully',
                'user': {
                    'id': existing_user.id,
                    'email': existing_user.email,
                    'full_name': existing_user.full_name,
                    'avatar_url': existing_user.avatar_url
                }
            }), 200
        else:
            # Create new user
            new_user = User(
                id=firebase_uid,  # Using Firebase UID as primary key
                email=email,
                full_name=full_name,
                avatar_url=avatar_url,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            return jsonify({
                'message': 'User created successfully',
                'user': {
                    'id': new_user.id,
                    'email': new_user.email,
                    'full_name': new_user.full_name,
                    'avatar_url': new_user.avatar_url
                }
            }), 201
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to sync user: {str(e)}'}), 500

@auth_bp.route('/api/auth/update-profile', methods=['PUT'])
def update_profile():
    try:
        data = request.get_json()
        
        if not data or 'firebase_uid' not in data:
            return jsonify({'error': 'Firebase UID is required'}), 400
        
        firebase_uid = data['firebase_uid']
        full_name = data.get('full_name')
        avatar_url = data.get('avatar_url')
        
        # Find user
        user = User.query.filter_by(id=firebase_uid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update fields if provided
        if full_name is not None:
            user.full_name = full_name
        if avatar_url is not None:
            user.avatar_url = avatar_url
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'avatar_url': user.avatar_url
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500



# Add these configurations
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads/avatars'
MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/api/auth/upload-avatar', methods=['POST'])
def upload_avatar():
    try:
        if 'avatar' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['avatar']
        firebase_uid = request.form.get('firebase_uid')
        
        if not firebase_uid:
            return jsonify({'error': 'Firebase UID is required'}), 400
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Check file size
            file.seek(0, os.SEEK_END)
            file_length = file.tell()
            file.seek(0)
            
            if file_length > MAX_FILE_SIZE:
                return jsonify({'error': 'File size too large. Maximum 2MB allowed.'}), 400
            
            # Create upload directory if it doesn't exist
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Generate unique filename
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{firebase_uid}_{uuid.uuid4().hex[:8]}.{file_extension}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Save file
            file.save(filepath)
            
            # Update user's avatar_url in database
            avatar_url = f"/static/uploads/avatars/{filename}"  # This matches our route
            user = User.query.filter_by(id=firebase_uid).first()
            
            if user:
                user.avatar_url = avatar_url
                user.updated_at = datetime.utcnow()
                db.session.commit()
                
                return jsonify({
                    'message': 'Avatar uploaded successfully',
                    'avatar_url': avatar_url
                }), 200
            else:
                return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif'}), 400
        
    except Exception as e:
        return jsonify({'error': f'Failed to upload avatar: {str(e)}'}), 500

@auth_bp.route('/api/auth/user/<firebase_uid>', methods=['GET'])
def get_user(firebase_uid):
    try:
        user = User.query.filter_by(id=firebase_uid).first()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'user': {
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'avatar_url': user.avatar_url,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user: {str(e)}'}), 500