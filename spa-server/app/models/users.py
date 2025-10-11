from app import db
from datetime import datetime
from .utils import generate_uuid

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    full_name = db.Column(db.String(100))
    avatar_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    learning_profile = db.relationship('UserLearningProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    learning_path = db.relationship('LearningPath', backref='user', uselist=False, cascade='all, delete-orphan')