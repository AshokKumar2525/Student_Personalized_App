from app import db
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from app.models.utils import generate_uuid

class Notification(db.Model):
    """Centralized notification system for all features"""
    __tablename__ = 'notifications'
    __table_args__ = (
        Index('idx_notification_user', 'user_id'),
        Index('idx_notification_read', 'user_id', 'is_read'),
        Index('idx_notification_feature', 'feature'),
    )

    id = db.Column(String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, index=True)

    # Notification metadata
    title = db.Column(String(128), nullable=False)
    message = db.Column(Text, nullable=False)
    feature = db.Column(String(32), nullable=False)  # 'learning_path', 'finance', 'scholarship', etc.

    # Status tracking
    is_read = db.Column(Boolean, default=False, nullable=False)

    # Reference to the source
    source_id = db.Column(String(36))  # ID of the related entity
    source_type = db.Column(String(32))  # Type of the related entity

    # Action information
    action_url = db.Column(String(512))  # URL to navigate when notification is clicked
    action_data = db.Column(JSONB)  # Additional data needed for the action

    # Timing
    created_at = db.Column(DateTime, default=datetime.utcnow, nullable=False)
    read_at = db.Column(DateTime)  # When notification was read

    # Relationships
    user = db.relationship('User', back_populates='notifications')

class UserNotificationPreference(db.Model):
    """User preferences for notifications"""
    __tablename__ = 'user_notification_preferences'

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, unique=True)
    
    # Global preferences
    notifications_enabled = db.Column(Boolean, default=True)  # Single toggle for all notifications

    # Feature-specific preferences (if needed for granular control)
    learning_path_notifications = db.Column(Boolean, default=True)
    # finance_notifications = db.Column(Boolean, default=True)
    # scholarship_notifications = db.Column(Boolean, default=True)

    # Notification delivery preferences
    delivery_method = db.Column(String(20), default='both')  # 'in_app', 'push', or 'both'

    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='notification_preferences')
