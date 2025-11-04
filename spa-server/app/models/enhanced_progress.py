"""
Enhanced User Progress Model
Adds time tracking, session management, and detailed analytics
"""

from app import db
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Index, CheckConstraint

# This enhances the existing UserProgress model in learning_pathfinder.py
# Add these columns via migration:

"""
Migration to enhance user_progress table:

ALTER TABLE user_progress 
ADD COLUMN started_at TIMESTAMP,
ADD COLUMN time_spent_minutes INTEGER DEFAULT 0,
ADD COLUMN last_accessed_at TIMESTAMP,
ADD COLUMN attempts_count INTEGER DEFAULT 0,
ADD COLUMN completion_percentage FLOAT DEFAULT 0.0;

CREATE INDEX idx_user_progress_last_accessed ON user_progress(user_id, last_accessed_at);
CREATE INDEX idx_user_progress_time_spent ON user_progress(user_id, time_spent_minutes);
"""


class LearningSession(db.Model):
    """
    Track individual learning sessions for analytics
    Helps understand user engagement patterns
    """
    __tablename__ = 'learning_sessions'
    __table_args__ = (
        Index('idx_session_user_date', 'user_id', 'session_date'),
        Index('idx_session_module', 'module_id'),
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    module_id = db.Column(Integer, db.ForeignKey('path_modules.id', ondelete='CASCADE'), index=True)
    course_id = db.Column(Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), index=True)
    
    # Session tracking
    session_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date, index=True)
    duration_minutes = db.Column(Integer, default=0)  # Time spent in this session
    
    # Activity tracking
    resources_viewed = db.Column(Integer, default=0)
    notes_taken = db.Column(db.Boolean, default=False)
    completed_in_session = db.Column(db.Boolean, default=False)
    
    # Timestamps
    started_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = db.Column(DateTime)

    # Relationships
    user = db.relationship('User', backref=db.backref('learning_sessions', lazy='dynamic', cascade='all, delete-orphan'))
    module = db.relationship('PathModule', backref=db.backref('sessions', lazy='dynamic', cascade='all, delete-orphan'))
    course = db.relationship('Course', backref=db.backref('sessions', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<LearningSession user={self.user_id} module={self.module_id} duration={self.duration_minutes}m>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'module_id': self.module_id,
            'course_id': self.course_id,
            'session_date': self.session_date.isoformat() if self.session_date else None,
            'duration_minutes': self.duration_minutes,
            'resources_viewed': self.resources_viewed,
            'completed_in_session': self.completed_in_session,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
        }


class UserStreak(db.Model):
    """
    Track daily learning streaks for gamification
    Encourages consistent learning habits
    """
    __tablename__ = 'user_streaks'
    __table_args__ = (
        Index('idx_streak_user', 'user_id'),
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    
    # Streak tracking
    current_streak = db.Column(Integer, default=0, nullable=False)
    longest_streak = db.Column(Integer, default=0, nullable=False)
    total_learning_days = db.Column(Integer, default=0, nullable=False)
    
    # Date tracking
    last_activity_date = db.Column(db.Date, default=datetime.utcnow().date, nullable=False)
    streak_start_date = db.Column(db.Date, default=datetime.utcnow().date)
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref=db.backref('streak', uselist=False, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<UserStreak user={self.user_id} current={self.current_streak} longest={self.longest_streak}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'total_learning_days': self.total_learning_days,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'streak_start_date': self.streak_start_date.isoformat() if self.streak_start_date else None,
        }
    
    def update_streak(self, activity_date=None):
        """Update streak based on activity"""
        if activity_date is None:
            activity_date = datetime.utcnow().date()
        
        # Check if this is a new day
        if self.last_activity_date != activity_date:
            days_diff = (activity_date - self.last_activity_date).days
            
            if days_diff == 1:
                # Consecutive day - increment streak
                self.current_streak += 1
                if self.current_streak > self.longest_streak:
                    self.longest_streak = self.current_streak
            elif days_diff > 1:
                # Streak broken - reset
                self.current_streak = 1
                self.streak_start_date = activity_date
            
            self.last_activity_date = activity_date
            self.total_learning_days += 1
            self.updated_at = datetime.utcnow()


class RoadmapCache(db.Model):
    """
    Cache complete roadmap data for fast retrieval
    Stores serialized roadmap to avoid expensive joins
    """
    __tablename__ = 'roadmap_cache'
    __table_args__ = (
        Index('idx_cache_path', 'learning_path_id'),
        Index('idx_cache_user', 'user_id'),
        Index('idx_cache_updated', 'updated_at'),
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    learning_path_id = db.Column(Integer, db.ForeignKey('learning_paths.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    
    # Cached data
    roadmap_data = db.Column(db.Text, nullable=False)  # JSON string of complete roadmap
    
    # Cache metadata
    version = db.Column(Integer, default=1)  # Increment on roadmap updates
    is_valid = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship('User', backref=db.backref('roadmap_caches', lazy='dynamic', cascade='all, delete-orphan'))
    learning_path = db.relationship('LearningPath', backref=db.backref('cache', uselist=False, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<RoadmapCache path={self.learning_path_id} valid={self.is_valid}>'

    def to_dict(self):
        import json
        return {
            'id': self.id,
            'user_id': self.user_id,
            'learning_path_id': self.learning_path_id,
            'roadmap_data': json.loads(self.roadmap_data) if self.roadmap_data else None,
            'version': self.version,
            'is_valid': self.is_valid,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def invalidate(self):
        """Mark cache as invalid"""
        self.is_valid = False
        self.updated_at = datetime.utcnow()