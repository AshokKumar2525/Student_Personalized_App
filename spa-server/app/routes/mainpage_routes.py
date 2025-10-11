from flask import Blueprint, send_from_directory
import os

main_bp = Blueprint('main', __name__)

# Serve avatar images
@main_bp.route('/static/uploads/avatars/<filename>')
def serve_avatar(filename):
    # Ensure the path is safe and filename is secure
    safe_filename = os.path.basename(filename)
    avatars_dir = os.path.join(os.getcwd(), 'static', 'uploads', 'avatars')
    
    # Check if file exists
    file_path = os.path.join(avatars_dir, safe_filename)
    if not os.path.exists(file_path):
        return {'error': 'Avatar not found'}, 404
    
    return send_from_directory(avatars_dir, safe_filename)

# You can add other main page routes here as well
@main_bp.route('/')
def index():
    return {'message': 'Welcome to Student Personalized App API'}

@main_bp.route('/api/health')
def health_check():
    return {'status': 'healthy', 'service': 'SPA Backend'}