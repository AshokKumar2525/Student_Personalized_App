"""
Roadmap Template Caching Model
Stores AI-generated roadmap templates for reuse across users with similar preferences
"""

from app import db
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import JSONB

class RoadmapTemplate(db.Model):
    """
    Cache AI-generated roadmap templates for reuse
    This dramatically reduces AI API calls and generation time
    """
    __tablename__ = 'roadmap_templates'
    __table_args__ = (
        Index('idx_template_hash', 'template_hash'),
        Index('idx_template_domain_level_pace', 'domain_id', 'knowledge_level', 'learning_pace'),
        Index('idx_template_usage', 'usage_count', 'last_used_at'),
    )

    id = db.Column(Integer, primary_key=True)
    template_hash = db.Column(String(64), unique=True, nullable=False, index=True)  # MD5 hash of preferences
    
    # Preferences that define this template
    domain_id = db.Column(Integer, db.ForeignKey('domains.id'), nullable=False, index=True)
    knowledge_level = db.Column(String(16), nullable=False)  # beginner, intermediate, advanced
    learning_pace = db.Column(String(10), nullable=False)  # slow, medium, fast
    weekly_hours_range = db.Column(String(10))  # e.g., "5-10" for grouping similar time commitments
    
    # Cached data
    roadmap_data = db.Column(JSONB, nullable=False)  # Complete AI-generated structure
    
    # Usage tracking
    usage_count = db.Column(Integer, default=1, nullable=False)
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    domain = db.relationship('Domain', backref='roadmap_templates')

    def __repr__(self):
        return f'<RoadmapTemplate {self.domain_id}:{self.knowledge_level}:{self.learning_pace}>'

    def to_dict(self):
        return {
            'id': self.id,
            'template_hash': self.template_hash,
            'domain_id': self.domain_id,
            'knowledge_level': self.knowledge_level,
            'learning_pace': self.learning_pace,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
        }
    
    def increment_usage(self):
        """Update usage statistics"""
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()


class ModuleFeedback(db.Model):
    """
    User feedback on individual modules
    Helps improve content quality and track user satisfaction
    """
    __tablename__ = 'module_feedback'
    __table_args__ = (
        Index('idx_feedback_module', 'module_id'),
        Index('idx_feedback_user', 'user_id'),
        Index('idx_feedback_rating', 'rating'),
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    module_id = db.Column(Integer, db.ForeignKey('path_modules.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Feedback data
    rating = db.Column(Integer, nullable=False)  # 1-5 stars
    comments = db.Column(Text)
    
    # Categorized feedback
    difficulty_rating = db.Column(Integer)  # 1-5 (too easy to too hard)
    content_quality = db.Column(Integer)  # 1-5
    time_accuracy = db.Column(Integer)  # 1-5 (was estimated time accurate?)
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('module_feedbacks', lazy='dynamic', cascade='all, delete-orphan'))
    module = db.relationship('PathModule', backref=db.backref('feedbacks', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<ModuleFeedback user={self.user_id} module={self.module_id} rating={self.rating}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'module_id': self.module_id,
            'rating': self.rating,
            'comments': self.comments,
            'difficulty_rating': self.difficulty_rating,
            'content_quality': self.content_quality,
            'time_accuracy': self.time_accuracy,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class CourseFeedback(db.Model):
    """
    User feedback on entire courses
    Provides higher-level insights into course effectiveness
    """
    __tablename__ = 'course_feedback'
    __table_args__ = (
        Index('idx_course_feedback_course', 'course_id'),
        Index('idx_course_feedback_user', 'user_id'),
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    course_id = db.Column(Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Feedback data
    rating = db.Column(Integer, nullable=False)  # 1-5 stars
    comments = db.Column(Text)
    would_recommend = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('course_feedbacks', lazy='dynamic', cascade='all, delete-orphan'))
    course = db.relationship('Course', backref=db.backref('feedbacks', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<CourseFeedback user={self.user_id} course={self.course_id} rating={self.rating}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'rating': self.rating,
            'comments': self.comments,
            'would_recommend': self.would_recommend,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }