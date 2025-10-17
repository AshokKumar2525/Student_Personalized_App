# app/routes/notification_routes.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.notification_service import NotificationService
from app.models import Notification, UserNotificationPreference
from app import db

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get user notifications"""
    user_id = get_jwt_identity()
    unread_only = request.args.get('unread', 'false').lower() == 'true'
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))

    notifications = NotificationService.get_user_notifications(user_id, limit, offset, unread_only)

    return jsonify({
        'notifications': [n.to_dict() for n in notifications],
        'count': len(notifications)
    })

@notification_bp.route('/notifications/<string:notification_id>', methods=['PATCH'])
@jwt_required()
def update_notification(notification_id):
    """Mark notification as read or update status"""
    success = NotificationService.mark_as_read(notification_id)
    return jsonify({'success': success})

@notification_bp.route('/notifications/preferences', methods=['GET'])
@jwt_required()
def get_notification_preferences():
    """Get user notification preferences"""
    user_id = get_jwt_identity()
    prefs = UserNotificationPreference.query.filter_by(user_id=user_id).first()

    if not prefs:
        # Create default preferences if none exist
        prefs = UserNotificationPreference(user_id=user_id)
        db.session.add(prefs)
        db.session.commit()

    return jsonify(prefs.to_dict())

@notification_bp.route('/notifications/preferences', methods=['PUT'])
@jwt_required()
def update_notification_preferences():
    """Update user notification preferences"""
    user_id = get_jwt_identity()
    data = request.get_json()

    prefs = UserNotificationPreference.query.filter_by(user_id=user_id).first()
    if not prefs:
        prefs = UserNotificationPreference(user_id=user_id)

    # Update preferences from request data
    for key, value in data.items():
        if hasattr(prefs, key):
            setattr(prefs, key, value)

    db.session.add(prefs)
    db.session.commit()

    return jsonify(prefs.to_dict())
