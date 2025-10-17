from app.models import Notification, UserNotificationPreference
from app import db
from datetime import datetime

class NotificationService:
    @staticmethod
    def create_notification(user_id, title, message, feature, notification_type,
                           source_id=None, source_type=None, action_url=None, action_data=None,
                           priority='medium', scheduled_at=None):
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            feature=feature,
            notification_type=notification_type,
            source_id=source_id,
            source_type=source_type,
            action_url=action_url,
            action_data=action_data,
            priority=priority,
            scheduled_at=scheduled_at
        )

        db.session.add(notification)
        db.session.commit()

        return notification

    @staticmethod
    def send_push_notification(notification_id):
        """Mark notification as sent and send to device"""
        notification = Notification.query.get(notification_id)
        if notification:
            notification.is_sent = True
            notification.sent_at = datetime.utcnow()
            db.session.commit()

            # Here you would integrate with your push notification service
            # (Firebase, OneSignal, etc.)
            return True
        return False

    @staticmethod
    def mark_as_read(notification_id):
        """Mark notification as read"""
        notification = Notification.query.get(notification_id)
        if notification:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            db.session.commit()
            return True
        return False

    @staticmethod
    def get_user_notifications(user_id, limit=20, offset=0, unread_only=False):
        """Get notifications for a user"""
        query = Notification.query.filter_by(user_id=user_id).order_by(Notification.created_at.desc())

        if unread_only:
            query = query.filter_by(is_read=False)

        return query.offset(offset).limit(limit).all()

    @staticmethod
    def check_user_preferences(user_id, feature):
        """Check if user wants notifications for a specific feature"""
        prefs = UserNotificationPreference.query.filter_by(user_id=user_id).first()
        if not prefs:
            return True  # Default to True if no preferences set

        # Check feature-specific preference
        if feature == 'learning_path' and not prefs.learning_path_notifications:
            return False
        if feature == 'finance' and not prefs.finance_notifications:
            return False
        if feature == 'scholarship' and not prefs.scholarship_notifications:
            return False

        return True
