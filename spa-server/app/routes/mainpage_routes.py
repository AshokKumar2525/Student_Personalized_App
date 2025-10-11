from flask import Blueprint, send_from_directory
import os

main_bp = Blueprint('main', __name__)

# Serve avatar images
@main_bp.route('/static/uploads/avatars/<filename>')
def serve_avatar(filename):
    # Ensure the path is safe and filename is secure
    safe_filename = os.path.basename(filename)
    return send_from_directory('static/uploads/avatars', safe_filename)

# You can add other main page routes here as well
@main_bp.route('/')
def index():
    return {'message': 'Welcome to Student Personalized App API'}

@main_bp.route('/api/health')
def health_check():
    return {'status': 'healthy', 'service': 'SPA Backend'}