from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Import models to ensure they are registered with SQLAlchemy
    from app.models import users, learning_pathfinder
    
    # Import and register blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.mainpage_routes import main_bp 
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp) 
    
    # Create upload directories if they don't exist
    with app.app_context():
        os.makedirs('static/uploads/avatars', exist_ok=True)
    
    return app