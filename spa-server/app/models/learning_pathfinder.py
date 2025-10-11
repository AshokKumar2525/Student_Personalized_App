from datetime import datetime
from app import db
from .utils import generate_uuid

class UserLearningProfile(db.Model):
    __tablename__ = 'user_learning_profiles'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Learning preferences and goals
    current_level = db.Column(db.String(50))  # beginner, intermediate, advanced
    time_commitment = db.Column(db.String(50))  # hours per week
    target_timeline = db.Column(db.String(50))  # 3 months, 6 months, 1 year
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LearningPath(db.Model):
    __tablename__ = 'learning_paths'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Path details
    domain = db.Column(db.String(100), nullable=False)  # e.g., "web development", "data science"
    title = db.Column(db.String(200), nullable=False)  # e.g., "Full Stack Web Development Path"
    description = db.Column(db.Text)  # Optional description

    # Path structure
    milestones = db.Column(db.Text)  # JSON string containing milestones
    estimated_duration = db.Column(db.String(50))  # e.g., "6 months", "1 year"
    difficulty_level = db.Column(db.String(50))  # beginner, intermediate, advanced
    
    # Progress tracking
    current_milestone = db.Column(db.Integer, default=0)
    progress_percentage = db.Column(db.Float, default=0.0)
    is_completed = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LearningResource(db.Model):
    __tablename__ = 'learning_resources'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    learning_path_id = db.Column(db.String(36), db.ForeignKey('learning_paths.id'), nullable=False)
    
    # Resource details
    title = db.Column(db.String(200), nullable=False)
    resource_type = db.Column(db.String(50))  # video, article, course, book, project
    url = db.Column(db.Text)
    description = db.Column(db.Text)
    duration = db.Column(db.String(50))  # e.g., "2 hours", "30 minutes"
    difficulty = db.Column(db.String(50))
    
    # Ordering within path
    milestone_index = db.Column(db.Integer)  # which milestone this belongs to
    resource_order = db.Column(db.Integer)  # order within milestone
    
    # Completion tracking
    is_completed = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Add relationships to LearningPath
LearningPath.resources = db.relationship('LearningResource', backref='learning_path', lazy=True, cascade='all, delete-orphan')