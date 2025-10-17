from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    try:
        # Configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://postgres:postgres@localhost:5432/learning_platform')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
        app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hour
        app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 86400  # 1 day

        # Initialize extensions
        db.init_app(app)
        migrate.init_app(app, db)
        jwt.init_app(app)
        CORS(app, resources={r"/*": {"origins": "*"}})

        # Import models to ensure they are registered with SQLAlchemy
        # Import order matters to avoid circular dependencies
        from app.models import utils
        from app.models.users import User
        from app.models.learning_pathfinder import Domain, Technology
        from app.models.finance_tracker import Transaction, Budget, FinanceSetting
        from app.models.scholarships import Scholarship, ScholarshipCriteria, UserScholarshipPreference, user_saved_scholarships
        from app.models.notifications import Notification, UserNotificationPreference
        
        # Import remaining learning pathfinder models after core models
        from app.models.learning_pathfinder import (
            UserProfile, LearningPath, PathModule, ModuleResource, UserProgress,
            LearningActivity, ActivitySubmission, Badge, UserBadge, UserPoints,
            ForumPost, ForumReply, TechUpdate, RoadmapVersion, VersionedModule, UpdateFeedback
        )

        # Import and register blueprints
        from app.routes.auth_routes import auth_bp
        from app.routes.mainpage_routes import main_bp
        # from app.routes.learning_pathfinder_routes import learning_pathfinder_bp
        # from app.routes.notification_routes import notification_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        # app.register_blueprint(learning_pathfinder_bp)
        # app.register_blueprint(notification_bp, url_prefix='/notifications')

        # Create upload directories if they don't exist
        with app.app_context():
            os.makedirs('static/uploads/avatars', exist_ok=True)
        
    except Exception as e:
        print(f"Error during app initialization: {e}")
        raise
    return app

