from flask import Blueprint, request, jsonify, current_app, send_from_directory
import os
from werkzeug.utils import secure_filename
from app import db
from app.models.users import User
import uuid

auth_bp = Blueprint('auth', __name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

# Add this route to serve static files
@auth_bp.route('/static/uploads/avatars/<filename>')
def serve_avatar(filename):
    try:
        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
        return send_from_directory(upload_dir, filename)
    except FileNotFoundError:
        return jsonify({'error': 'Avatar not found'}), 404

@auth_bp.route('/auth/sync-user', methods=['POST'])
def sync_user():
    try:
        data = request.get_json()
        print(f"🔍 [BACKEND DEBUG] Received sync-user request")
        print(f"🔍 [BACKEND DEBUG] Request data: {data}")
        
        if not data:
            print("❌ [BACKEND DEBUG] No data received")
            return jsonify({'error': 'No data provided'}), 400
        
        firebase_uid = data.get('firebase_uid')
        email = data.get('email')
        
        print(f"🔍 [BACKEND DEBUG] Firebase UID: {firebase_uid}")
        print(f"🔍 [BACKEND DEBUG] Email: {email}")
        
        if not firebase_uid:
            print("❌ [BACKEND DEBUG] Missing firebase_uid")
            return jsonify({'error': 'Missing firebase_uid field'}), 400
        if not email:
            print("❌ [BACKEND DEBUG] Missing email")
            return jsonify({'error': 'Missing email field'}), 400
        
        # Check if user exists
        user = User.query.filter_by(id=firebase_uid).first()
        print(f"🔍 [BACKEND DEBUG] User lookup result: {user}")
        
        avatar_url = data.get('avatar_url')
        
        # If avatar_url is from Google (external URL), download and save locally
        if avatar_url and avatar_url.startswith('http') and 'google' in avatar_url:
            try:
                print(f"🔄 [BACKEND DEBUG] Downloading Google avatar...")
                import requests
                from io import BytesIO
                
                response = requests.get(avatar_url)
                if response.status_code == 200:
                    # Create uploads directory if it doesn't exist
                    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Generate unique filename
                    file_extension = 'jpg'  # Google avatars are typically JPG
                    filename = f"{firebase_uid}_google_{uuid.uuid4().hex}.{file_extension}"
                    filepath = os.path.join(upload_dir, filename)
                    
                    # Save the image
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    # Update avatar_url to local path
                    avatar_url = f"/static/uploads/avatars/{filename}"
                    print(f"✅ [BACKEND DEBUG] Google avatar saved locally: {avatar_url}")
                    
            except Exception as e:
                print(f"❌ [BACKEND ERROR] Failed to download Google avatar: {str(e)}")
                # Keep the original Google URL if download fails
                pass
        
        if not user:
            print("🔄 [BACKEND DEBUG] Creating new user...")
            
            user = User(
                id=firebase_uid,
                email=email,
                full_name=data.get('full_name'),
                avatar_url=avatar_url
            )
            db.session.add(user)
            db.session.commit()
            print(f"✅ [BACKEND DEBUG] User created: {user.id}")
            
            return jsonify({
                'message': 'User created successfully',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'avatar_url': user.avatar_url
                }
            }), 201
        else:
            print("🔄 [BACKEND DEBUG] Updating existing user...")
            # Update existing user if needed
            update_fields = False
            
            if data.get('full_name') and data.get('full_name') != user.full_name:
                user.full_name = data.get('full_name')
                update_fields = True
            
            # Always update avatar if provided (replace previous one)
            if avatar_url and avatar_url != user.avatar_url:
                user.avatar_url = avatar_url
                update_fields = True
                print(f"✅ [BACKEND DEBUG] Updated user avatar to: {avatar_url}")
            
            if update_fields:
                db.session.commit()
                print(f"✅ [BACKEND DEBUG] User updated: {user.id}")
            
            return jsonify({
                'message': 'User already exists',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'avatar_url': user.avatar_url
                }
            }), 200
            
    except Exception as e:
        print(f"❌ [BACKEND ERROR] Exception in sync-user: {str(e)}")
        import traceback
        print(f"❌ [BACKEND ERROR] Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'error': f'Failed to sync user: {str(e)}'}), 500

@auth_bp.route('/auth/update-profile', methods=['PUT'])
def update_profile():
    try:
        data = request.get_json()
        
        if 'firebase_uid' not in data:
            return jsonify({'error': 'Missing firebase_uid'}), 400
        
        user = User.query.filter_by(id=data['firebase_uid']).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        
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

@auth_bp.route('/auth/upload-avatar', methods=['POST'])
def upload_avatar():
    try:
        if 'avatar' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        firebase_uid = request.form.get('firebase_uid')
        if not firebase_uid:
            return jsonify({'error': 'Missing firebase_uid'}), 400
        
        if file and allowed_file(file.filename):
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'avatars')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Get current user to check for existing avatar
            user = User.query.filter_by(id=firebase_uid).first()
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Delete old avatar file if it exists and is a local file
            if user.avatar_url and user.avatar_url.startswith('/static/uploads/avatars/'):
                old_filename = user.avatar_url.split('/')[-1]
                old_filepath = os.path.join(upload_dir, old_filename)
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
                    print(f"🗑️ [BACKEND DEBUG] Deleted old avatar: {old_filepath}")
            
            # Generate unique filename and save new avatar
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            filename = f"{firebase_uid}_{uuid.uuid4().hex}.{file_extension}"
            filepath = os.path.join(upload_dir, filename)
            
            file.save(filepath)
            print(f"✅ [BACKEND DEBUG] New avatar saved: {filepath}")
            
            # Update user with new avatar URL
            avatar_url = f"/static/uploads/avatars/{filename}"
            user.avatar_url = avatar_url
            db.session.commit()
            
            return jsonify({
                'message': 'Avatar uploaded successfully',
                'avatar_url': avatar_url
            }), 200
        else:
            return jsonify({'error': 'Invalid file type'}), 400
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error uploading avatar: {str(e)}")
        return jsonify({'error': f'Failed to upload avatar: {str(e)}'}), 500

@auth_bp.route('/auth/user/<firebase_uid>', methods=['GET'])
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
                'avatar_url': user.avatar_url
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get user: {str(e)}'}), 500