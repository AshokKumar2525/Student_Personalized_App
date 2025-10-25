"""
Email Summarizer Routes
API endpoints for email management and summarization
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.users import User
from app.models.email_summarizer import EmailAccount, Email, EmailSummary, get_all_categories
from app.services.gmail_service import create_gmail_service
from app.services.email_ai_service import get_ai_service
from datetime import datetime, timedelta
from functools import wraps
import traceback

email_bp = Blueprint('email', __name__)

# Error handler decorator
def handle_errors(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            print(f"Error in {f.__name__}: {str(e)}")
            print(traceback.format_exc())
            return jsonify({'error': 'Internal server error'}), 500
    return decorated_function


@email_bp.route('/email/connect', methods=['POST'])
@handle_errors
def connect_gmail():
    """
    Connect Gmail account using OAuth tokens from login
    
    Request Body:
        {
            "firebase_uid": "string",
            "access_token": "string",
            "refresh_token": "string",
            "token_expires_at": "ISO datetime string"
        }
    
    Response:
        {
            "message": "string",
            "email_address": "string",
            "account_id": int
        }
    """
    data = request.get_json()
    
    # Validate required fields
    required = ['firebase_uid', 'access_token']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify user exists
    user = User.query.filter_by(id=data['firebase_uid']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if email account already exists
    existing_account = EmailAccount.query.filter_by(user_id=user.id).first()
    if existing_account:
        # Update tokens
        existing_account.access_token = data['access_token']
        existing_account.refresh_token = data.get('refresh_token')
        if data.get('token_expires_at'):
            existing_account.token_expires_at = datetime.fromisoformat(data['token_expires_at'])
        existing_account.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Gmail account updated',
            'email_address': existing_account.email_address,
            'account_id': existing_account.id
        }), 200
    
    # Get user's Gmail address
    try:
        gmail_service = create_gmail_service(
            data['access_token'],
            data.get('refresh_token')
        )
        email_address = gmail_service.get_user_email()
    except Exception as e:
        return jsonify({'error': f'Failed to connect to Gmail: {str(e)}'}), 400
    
    # Create email account record
    email_account = EmailAccount(
        user_id=user.id,
        email_address=email_address,
        access_token=data['access_token'],
        refresh_token=data.get('refresh_token'),
        token_expires_at=datetime.fromisoformat(data['token_expires_at']) if data.get('token_expires_at') else None,
        is_active=True
    )
    
    db.session.add(email_account)
    db.session.commit()
    
    return jsonify({
        'message': 'Gmail connected successfully',
        'email_address': email_address,
        'account_id': email_account.id
    }), 201


@email_bp.route('/email/sync', methods=['POST'])
@handle_errors
def sync_emails():
    """
    Sync emails from Gmail
    
    Request Body:
        {
            "firebase_uid": "string",
            "max_results": int (optional, default 50),
            "days_back": int (optional, default 30)
        }
    
    Response:
        {
            "message": "string",
            "synced_count": int,
            "categorized_count": int
        }
    """
    data = request.get_json()
    
    if not data.get('firebase_uid'):
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    # Get email account
    email_account = EmailAccount.query.filter_by(
        user_id=data['firebase_uid'],
        is_active=True
    ).first()
    
    if not email_account:
        return jsonify({'error': 'Gmail account not connected'}), 404
    
    # Create Gmail service
    gmail_service = create_gmail_service(
        email_account.access_token,
        email_account.refresh_token
    )
    
    # Get AI service for categorization
    ai_service = get_ai_service()
    
    # Build query for recent emails
    max_results = data.get('max_results', 50)
    days_back = data.get('days_back', 30)
    after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
    query = f'after:{after_date}'
    
    # Fetch emails from Gmail
    result = gmail_service.fetch_emails(max_results=max_results, query=query)
    emails_data = result['emails']
    
    synced_count = 0
    categorized_count = 0
    
    for email_data in emails_data:
        # Check if email already exists
        existing = Email.query.filter_by(message_id=email_data['message_id']).first()
        if existing:
            continue  # Skip duplicates
        
        # Categorize email
        category = ai_service.categorize_email(
            email_data['subject'],
            email_data['sender_email'],
            email_data['snippet']
        )
        
        # Create email record
        email = Email(
            account_id=email_account.id,
            message_id=email_data['message_id'],
            thread_id=email_data['thread_id'],
            subject=email_data['subject'],
            sender_email=email_data['sender_email'],
            sender_name=email_data['sender_name'],
            snippet=email_data['snippet'],
            category=category,
            is_starred=email_data['is_starred'],
            is_read=email_data['is_read'],
            has_attachments=email_data['has_attachments'],
            email_date=email_data['email_date']
        )
        
        db.session.add(email)
        synced_count += 1
        categorized_count += 1
    
    # Update last sync time
    email_account.last_sync_at = datetime.utcnow()
    
    # Get and store history ID for incremental sync
    history_id = gmail_service.get_history_id()
    if history_id:
        email_account.sync_token = str(history_id)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Emails synced successfully',
        'synced_count': synced_count,
        'categorized_count': categorized_count
    }), 200


@email_bp.route('/email/list', methods=['GET'])
@handle_errors
def list_emails():
    """
    Get list of emails with filters
    
    Query Parameters:
        firebase_uid: string (required)
        category: string (optional) - filter by category
        is_read: boolean (optional) - filter by read status
        is_starred: boolean (optional) - filter by starred
        page: int (optional, default 1)
        per_page: int (optional, default 50)
    
    Response:
        {
            "emails": [...],
            "total": int,
            "page": int,
            "per_page": int,
            "categories": [...]
        }
    """
    firebase_uid = request.args.get('firebase_uid')
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    # Get email account
    email_account = EmailAccount.query.filter_by(user_id=firebase_uid).first()
    if not email_account:
        return jsonify({'error': 'Gmail account not connected'}), 404
    
    # Build query
    query = Email.query.filter_by(account_id=email_account.id)
    
    # Apply filters
    category = request.args.get('category')
    if category:
        query = query.filter_by(category=category)
    
    is_read = request.args.get('is_read')
    if is_read is not None:
        query = query.filter_by(is_read=is_read.lower() == 'true')
    
    is_starred = request.args.get('is_starred')
    if is_starred is not None:
        query = query.filter_by(is_starred=is_starred.lower() == 'true')
    
    # Pagination
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    # Order by date (newest first)
    query = query.order_by(Email.email_date.desc())
    
    # Get paginated results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    emails_data = [email.to_dict() for email in pagination.items]
    
    return jsonify({
        'emails': emails_data,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'categories': get_all_categories()
    }), 200


@email_bp.route('/email/<int:email_id>', methods=['GET'])
@handle_errors
def get_email_detail(email_id):
    """
    Get detailed email content
    
    Query Parameters:
        firebase_uid: string (required)
        include_body: boolean (optional) - fetch full body from Gmail
    
    Response:
        {
            "email": {...},
            "body_text": "string" (if include_body=true),
            "body_html": "string" (if include_body=true)
        }
    """
    firebase_uid = request.args.get('firebase_uid')
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    # Get email
    email = Email.query.get(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    # Verify ownership
    email_account = EmailAccount.query.get(email.account_id)
    if not email_account or email_account.user_id != firebase_uid:
        return jsonify({'error': 'Access denied'}), 403
    
    response_data = {
        'email': email.to_dict()
    }
    
    # Fetch full body if requested
    include_body = request.args.get('include_body', 'false').lower() == 'true'
    if include_body:
        gmail_service = create_gmail_service(
            email_account.access_token,
            email_account.refresh_token
        )
        
        body = gmail_service.get_message_body(email.message_id)
        response_data['body_text'] = body['text']
        response_data['body_html'] = body['html']
    
    return jsonify(response_data), 200


@email_bp.route('/email/<int:email_id>/summarize', methods=['POST'])
@handle_errors
def summarize_email(email_id):
    """
    Generate AI summary for an email
    
    Request Body:
        {
            "firebase_uid": "string"
        }
    
    Response:
        {
            "summary": {
                "summary_text": "string",
                "key_points": [...],
                "action_items": [...],
                "priority": "string",
                "sentiment": "string"
            }
        }
    """
    data = request.get_json()
    
    if not data.get('firebase_uid'):
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    # Get email
    email = Email.query.get(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    # Verify ownership
    email_account = EmailAccount.query.get(email.account_id)
    if not email_account or email_account.user_id != data['firebase_uid']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Check if summary already exists
    existing_summary = EmailSummary.query.filter_by(email_id=email_id).first()
    if existing_summary:
        return jsonify({
            'message': 'Summary already exists',
            'summary': existing_summary.to_dict()
        }), 200
    
    # Fetch email body from Gmail
    gmail_service = create_gmail_service(
        email_account.access_token,
        email_account.refresh_token
    )
    body = gmail_service.get_message_body(email.message_id)
    
    # Use text body, fallback to HTML if no text
    body_text = body['text'] if body['text'] else body['html']
    
    if not body_text or len(body_text.strip()) < 50:
        return jsonify({'error': 'Email content too short to summarize'}), 400
    
    # Generate summary using AI
    ai_service = get_ai_service()
    summary_data = ai_service.summarize_email(
        email.subject,
        email.sender_name or email.sender_email,
        body_text
    )
    
    # Save summary to database
    email_summary = EmailSummary(
        email_id=email_id,
        summary_text=summary_data['summary_text'],
        key_points=summary_data.get('key_points', []),
        action_items=summary_data.get('action_items', []),
        priority=summary_data.get('priority', 'medium'),
        sentiment=summary_data.get('sentiment', 'neutral'),
        model_used=summary_data.get('model_used', 'unknown')
    )
    
    db.session.add(email_summary)
    db.session.commit()
    
    return jsonify({
        'message': 'Summary generated successfully',
        'summary': email_summary.to_dict()
    }), 201


@email_bp.route('/email/<int:email_id>/category', methods=['PUT'])
@handle_errors
def update_category(email_id):
    """
    Update email category
    
    Request Body:
        {
            "firebase_uid": "string",
            "category": "string"
        }
    
    Response:
        {
            "message": "string",
            "email": {...}
        }
    """
    data = request.get_json()
    
    if not data.get('firebase_uid') or not data.get('category'):
        return jsonify({'error': 'firebase_uid and category are required'}), 400
    
    # Get email
    email = Email.query.get(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    # Verify ownership
    email_account = EmailAccount.query.get(email.account_id)
    if not email_account or email_account.user_id != data['firebase_uid']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Update category
    email.category = data['category']
    db.session.commit()
    
    return jsonify({
        'message': 'Category updated successfully',
        'email': email.to_dict()
    }), 200


@email_bp.route('/email/<int:email_id>/toggle-star', methods=['PUT'])
@handle_errors
def toggle_star(email_id):
    """
    Star or unstar an email
    
    Request Body:
        {
            "firebase_uid": "string",
            "starred": boolean
        }
    
    Response:
        {
            "message": "string",
            "is_starred": boolean
        }
    """
    data = request.get_json()
    
    if not data.get('firebase_uid'):
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    # Get email
    email = Email.query.get(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    # Verify ownership
    email_account = EmailAccount.query.get(email.account_id)
    if not email_account or email_account.user_id != data['firebase_uid']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Toggle star in Gmail
    starred = data.get('starred', True)
    gmail_service = create_gmail_service(
        email_account.access_token,
        email_account.refresh_token
    )
    
    success = gmail_service.toggle_star(email.message_id, starred)
    
    if success:
        # Update local database
        email.is_starred = starred
        db.session.commit()
        
        return jsonify({
            'message': 'Star toggled successfully',
            'is_starred': starred
        }), 200
    else:
        return jsonify({'error': 'Failed to toggle star in Gmail'}), 500


@email_bp.route('/email/<int:email_id>/mark-read', methods=['PUT'])
@handle_errors
def mark_read(email_id):
    """
    Mark email as read or unread
    
    Request Body:
        {
            "firebase_uid": "string",
            "is_read": boolean
        }
    
    Response:
        {
            "message": "string",
            "is_read": boolean
        }
    """
    data = request.get_json()
    
    if not data.get('firebase_uid'):
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    # Get email
    email = Email.query.get(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    # Verify ownership
    email_account = EmailAccount.query.get(email.account_id)
    if not email_account or email_account.user_id != data['firebase_uid']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Mark as read/unread in Gmail
    is_read = data.get('is_read', True)
    gmail_service = create_gmail_service(
        email_account.access_token,
        email_account.refresh_token
    )
    
    if is_read:
        success = gmail_service.mark_as_read(email.message_id)
    else:
        success = gmail_service.mark_as_unread(email.message_id)
    
    if success:
        # Update local database
        email.is_read = is_read
        db.session.commit()
        
        return jsonify({
            'message': 'Read status updated successfully',
            'is_read': is_read
        }), 200
    else:
        return jsonify({'error': 'Failed to update read status in Gmail'}), 500


@email_bp.route('/email/categories', methods=['GET'])
@handle_errors
def get_categories():
    """
    Get all available email categories
    
    Response:
        {
            "categories": [
                {
                    "slug": "string",
                    "name": "string",
                    "color": "string",
                    "icon": "string"
                }
            ]
        }
    """
    return jsonify({
        'categories': get_all_categories()
    }), 200


@email_bp.route('/email/stats', methods=['GET'])
@handle_errors
def get_email_stats():
    """
    Get email statistics for user
    
    Query Parameters:
        firebase_uid: string (required)
    
    Response:
        {
            "total_emails": int,
            "unread_count": int,
            "starred_count": int,
            "category_counts": {...},
            "last_sync": "datetime"
        }
    """
    firebase_uid = request.args.get('firebase_uid')
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    # Get email account
    email_account = EmailAccount.query.filter_by(user_id=firebase_uid).first()
    if not email_account:
        return jsonify({'error': 'Gmail account not connected'}), 404
    
    # Get counts
    total_emails = Email.query.filter_by(account_id=email_account.id).count()
    unread_count = Email.query.filter_by(account_id=email_account.id, is_read=False).count()
    starred_count = Email.query.filter_by(account_id=email_account.id, is_starred=True).count()
    
    # Get category breakdown
    from sqlalchemy import func
    category_counts = dict(
        db.session.query(Email.category, func.count(Email.id))
        .filter_by(account_id=email_account.id)
        .group_by(Email.category)
        .all()
    )
    
    return jsonify({
        'total_emails': total_emails,
        'unread_count': unread_count,
        'starred_count': starred_count,
        'category_counts': category_counts,
        'last_sync': email_account.last_sync_at.isoformat() if email_account.last_sync_at else None,
        'email_address': email_account.email_address
    }), 200


@email_bp.route('/email/account-status', methods=['GET'])
@handle_errors
def get_account_status():
    """
    Check if user has Gmail connected
    
    Query Parameters:
        firebase_uid: string (required)
    
    Response:
        {
            "connected": boolean,
            "email_address": "string" (if connected),
            "last_sync": "datetime" (if connected)
        }
    """
    firebase_uid = request.args.get('firebase_uid')
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    email_account = EmailAccount.query.filter_by(user_id=firebase_uid).first()
    
    if email_account:
        return jsonify({
            'connected': True,
            'email_address': email_account.email_address,
            'last_sync': email_account.last_sync_at.isoformat() if email_account.last_sync_at else None
        }), 200
    else:
        return jsonify({
            'connected': False
        }), 200


@email_bp.route('/email/test', methods=['GET'])
def test_endpoint():
    """Health check endpoint"""
    return jsonify({
        'message': 'Email Summarizer API is working!',
        'status': 'success'
    }), 200