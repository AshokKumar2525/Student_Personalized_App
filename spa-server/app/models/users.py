from app import db
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Index
from app.models.utils import generate_uuid

class User(db.Model):
    """Base user table"""
    __tablename__ = 'users'
    __table_args__ = (
        Index('idx_user_email', 'email'),
    )
    id = db.Column(String(36), primary_key=True, default=generate_uuid)
    email = db.Column(String(120), unique=True, nullable=False)
    full_name = db.Column(String(100))  
    avatar_url = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active = db.Column(DateTime)

    # Relationships
    # Learning path relationships
    profile = db.relationship('UserProfile', back_populates='user', uselist=False)
    learning_paths = db.relationship('LearningPath', back_populates='user', cascade='all, delete-orphan')
    progress = db.relationship('UserProgress', back_populates='user', cascade='all, delete-orphan')
    badges = db.relationship('UserBadge', back_populates='user', cascade='all, delete-orphan')
    points = db.relationship('UserPoints', back_populates='user', uselist=False)
    update_feedback = db.relationship('UpdateFeedback', back_populates='user', cascade='all, delete-orphan')
    activity_submissions = db.relationship('ActivitySubmission', back_populates='user', cascade='all, delete-orphan')
    forum_posts = db.relationship('ForumPost', back_populates='user', cascade='all, delete-orphan')
    forum_replies = db.relationship('ForumReply', back_populates='user', cascade='all, delete-orphan')
    # Finance tracker relationships
    transactions = db.relationship('Transaction', back_populates='user', cascade='all, delete-orphan')
    budgets = db.relationship('Budget', back_populates='user', cascade='all, delete-orphan')
    settings = db.relationship('FinanceSetting', back_populates='user', uselist=False)

    # Scholarship relationships
    scholarship_preferences = db.relationship('UserScholarshipPreference', back_populates='user', uselist=False)
    saved_scholarships = db.relationship('Scholarship', secondary='user_saved_scholarships', back_populates='saved_by')

    # Notification relationships
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    notification_preferences = db.relationship('UserNotificationPreference', back_populates='user', uselist=False)
