"""
Email Summarizer Routes - Fixed and Optimized
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

# Simple in-memory cache
_cache = {}
CACHE_EXPIRY = 300  # 5 minutes

def get_cached(key):
    """Get cached value if not expired"""
    if key in _cache:
        data, expiry = _cache[key]
        if datetime.utcnow() < expiry:
            return data
        del _cache[key]
    return None

def set_cache(key, value, seconds=CACHE_EXPIRY):
    """Set cache with expiry"""
    _cache[key] = (value, datetime.utcnow() + timedelta(seconds=seconds))

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


def update_account_tokens(account, gmail_service):
    """Update account tokens if they were refreshed"""
    updated = gmail_service.get_updated_credentials()
    if updated:
        account.access_token = updated['access_token']
        if updated.get('refresh_token'):
            account.refresh_token = updated['refresh_token']
        if updated.get('token_expiry'):
            account.token_expires_at = datetime.fromisoformat(updated['token_expiry'])
        account.updated_at = datetime.utcnow()
        db.session.commit()
        print("✅ Account tokens updated")


@email_bp.route('/email/connect', methods=['POST'])
@handle_errors
def connect_gmail():
    """Connect Gmail account"""
    data = request.get_json()
    
    required = ['firebase_uid', 'access_token']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    user = User.query.filter_by(id=data['firebase_uid']).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    existing_account = EmailAccount.query.filter_by(user_id=user.id).first()
    
    try:
        gmail_service = create_gmail_service(
            data['access_token'],
            data.get('refresh_token')
        )
        email_address = gmail_service.get_user_email()
    except Exception as e:
        return jsonify({'error': f'Failed to connect to Gmail: {str(e)}'}), 400
    
    if existing_account:
        existing_account.access_token = data['access_token']
        existing_account.refresh_token = data.get('refresh_token')
        existing_account.email_address = email_address
        if data.get('token_expires_at'):
            try:
                existing_account.token_expires_at = datetime.fromisoformat(data['token_expires_at'])
            except:
                existing_account.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        existing_account.updated_at = datetime.utcnow()
        db.session.commit()
        
        set_cache(f"account_status:{user.id}", None, 0)
        
        return jsonify({
            'message': 'Gmail account updated',
            'email_address': existing_account.email_address,
            'account_id': existing_account.id
        }), 200
    
    email_account = EmailAccount(
        user_id=user.id,
        email_address=email_address,
        access_token=data['access_token'],
        refresh_token=data.get('refresh_token'),
        token_expires_at=datetime.utcnow() + timedelta(hours=1),
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
    """Fast sync - only last 5 days + starred/important"""
    data = request.get_json()
    
    if not data.get('firebase_uid'):
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    email_account = EmailAccount.query.filter_by(
        user_id=data['firebase_uid'],
        is_active=True
    ).first()
    
    if not email_account:
        return jsonify({'error': 'Gmail account not connected'}), 404
    
    gmail_service = create_gmail_service(
        email_account.access_token,
        email_account.refresh_token
    )
    
    update_account_tokens(email_account, gmail_service)
    ai_service = get_ai_service()
    
    # Delete old emails (>5 days, not starred)
    if data.get('delete_old', True):
        cutoff_date = datetime.utcnow() - timedelta(days=5)
        Email.query.filter(
            Email.account_id == email_account.id,
            Email.email_date < cutoff_date,
            Email.is_starred == False
        ).delete()
        db.session.commit()
    
    # Fetch emails: last 5 days OR starred OR important
    max_results = min(data.get('max_results', 50), 100)  # Reduced to 50
    days_back = data.get('days_back', 5)
    after_date = (datetime.utcnow() - timedelta(days=days_back)).strftime('%Y/%m/%d')
    
    query = f'(after:{after_date} OR is:starred OR is:important) in:inbox'
    
    result = gmail_service.fetch_emails(max_results=max_results, query=query)
    emails_data = result['emails']
    
    synced_count = 0
    existing_ids = {e.message_id for e in Email.query.filter_by(account_id=email_account.id).all()}
    
    for email_data in emails_data:
        if email_data['message_id'] in existing_ids:
            continue
        
        category = ai_service.categorize_email(
            email_data['subject'],
            email_data['sender_email'],
            email_data['snippet']
        )
        
        if email_data.get('is_important'):
            category = 'important'
        
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
    
    # Update last sync time (UTC)
    email_account.last_sync_at = datetime.utcnow()
    
    history_id = gmail_service.get_history_id()
    if history_id:
        email_account.sync_token = str(history_id)
    
    db.session.commit()
    
    # Clear cache
    set_cache(f"emails_list:{data['firebase_uid']}", None, 0)
    set_cache(f"email_stats:{data['firebase_uid']}", None, 0)
    
    return jsonify({
        'message': 'Emails synced successfully',
        'synced_count': synced_count
    }), 200


@email_bp.route('/email/list', methods=['GET'])
@handle_errors
def list_emails():
    """Get emails with proper filtering and caching"""
    firebase_uid = request.args.get('firebase_uid')
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    cache_key = f"emails_list:{firebase_uid}:{request.args.get('category', 'all')}:{request.args.get('is_read', 'all')}:{request.args.get('is_starred', 'all')}:{request.args.get('page', 1)}"
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached), 200
    
    email_account = EmailAccount.query.filter_by(user_id=firebase_uid).first()
    if not email_account:
        return jsonify({'error': 'Gmail account not connected'}), 404
    
    query = Email.query.filter_by(account_id=email_account.id)
    
    # Apply filters correctly
    category = request.args.get('category')
    if category:
        query = query.filter_by(category=category)
    
    is_read = request.args.get('is_read')
    if is_read is not None:
        read_value = is_read.lower() == 'true'
        query = query.filter_by(is_read=read_value)
    
    is_starred = request.args.get('is_starred')
    if is_starred is not None:
        starred_value = is_starred.lower() == 'true'
        query = query.filter_by(is_starred=starred_value)
    
    page = int(request.args.get('page', 1))
    per_page = min(int(request.args.get('per_page', 50)), 100)
    
    query = query.order_by(Email.email_date.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    emails_data = [email.to_dict() for email in pagination.items]
    
    result = {
        'emails': emails_data,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev,
        'categories': get_all_categories()
    }
    
    set_cache(cache_key, result, 180)  # 3 minutes
    
    return jsonify(result), 200


@email_bp.route('/email/<int:email_id>', methods=['GET'])
@handle_errors
def get_email_detail(email_id):
    """Get email detail with body, links, and attachments"""
    firebase_uid = request.args.get('firebase_uid')
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    include_body = request.args.get('include_body', 'false').lower() == 'true'
    
    email = Email.query.get(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    email_account = EmailAccount.query.get(email.account_id)
    if not email_account or email_account.user_id != firebase_uid:
        return jsonify({'error': 'Access denied'}), 403
    
    response_data = {'email': email.to_dict()}
    
    if include_body:
        cache_key = f"email_body:{email_id}"
        cached_body = get_cached(cache_key)
        
        if cached_body:
            response_data.update(cached_body)
        else:
            gmail_service = create_gmail_service(
                email_account.access_token,
                email_account.refresh_token
            )
            
            update_account_tokens(email_account, gmail_service)
            
            # Get full message with attachments info
            full_message = gmail_service.get_message_with_attachments(email.message_id)
            
            body_data = {
                'body_text': full_message['body']['text'],
                'body_html': full_message['body']['html'],
                'attachments': full_message['attachments'],
                'links': full_message['links']
            }
            
            response_data.update(body_data)
            set_cache(cache_key, body_data, 600)  # 10 minutes
    
    return jsonify(response_data), 200


@email_bp.route('/email/<int:email_id>/summarize', methods=['POST'])
@handle_errors
def summarize_email(email_id):
    """Generate Gemini summary"""
    data = request.get_json()
    
    if not data.get('firebase_uid'):
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    email = Email.query.get(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    email_account = EmailAccount.query.get(email.account_id)
    if not email_account or email_account.user_id != data['firebase_uid']:
        return jsonify({'error': 'Access denied'}), 403
    
    # Check existing summary
    existing_summary = EmailSummary.query.filter_by(email_id=email_id).first()
    if existing_summary:
        return jsonify({
            'message': 'Summary already exists',
            'summary': existing_summary.to_dict()
        }), 200
    
    # Get body from cache or Gmail
    cache_key = f"email_body:{email_id}"
    cached_body = get_cached(cache_key)
    
    if cached_body:
        body_text = cached_body['body_text']
    else:
        gmail_service = create_gmail_service(
            email_account.access_token,
            email_account.refresh_token
        )
        update_account_tokens(email_account, gmail_service)
        
        body = gmail_service.get_message_body(email.message_id)
        body_text = body['text'] if body['text'] else body['html']
    
    if not body_text or len(body_text.strip()) < 50:
        return jsonify({'error': 'Email content too short to summarize'}), 400
    
    # Generate summary
    ai_service = get_ai_service()
    summary_data = ai_service.summarize_email(
        email.subject,
        email.sender_name or email.sender_email,
        body_text[:10000]  # Limit for Gemini
    )
    
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


@email_bp.route('/email/<int:email_id>/mark-read', methods=['PUT'])
@handle_errors
def mark_read(email_id):
    """Mark email as read - syncs with Gmail"""
    data = request.get_json()
    
    if not data.get('firebase_uid'):
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    email = Email.query.get(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    email_account = EmailAccount.query.get(email.account_id)
    if not email_account or email_account.user_id != data['firebase_uid']:
        return jsonify({'error': 'Access denied'}), 403
    
    is_read = data.get('is_read', True)
    
    # Update local DB immediately
    email.is_read = is_read
    db.session.commit()
    
    # Clear cache
    set_cache(f"emails_list:{data['firebase_uid']}", None, 0)
    set_cache(f"email_stats:{data['firebase_uid']}", None, 0)
    
    # Sync with Gmail in background (don't wait)
    try:
        gmail_service = create_gmail_service(
            email_account.access_token,
            email_account.refresh_token
        )
        update_account_tokens(email_account, gmail_service)
        
        if is_read:
            gmail_service.mark_as_read(email.message_id)
        else:
            gmail_service.mark_as_unread(email.message_id)
    except Exception as e:
        print(f"Gmail sync error (non-critical): {e}")
    
    return jsonify({
        'message': 'Read status updated',
        'is_read': is_read
    }), 200


@email_bp.route('/email/<int:email_id>', methods=['DELETE'])
@handle_errors
def delete_email(email_id):
    """Delete email - FIXED to work properly"""
    firebase_uid = request.args.get('firebase_uid')
    
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    email = Email.query.get(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    email_account = EmailAccount.query.get(email.account_id)
    if not email_account or email_account.user_id != firebase_uid:
        return jsonify({'error': 'Access denied'}), 403
    
    # Delete from local DB immediately
    db.session.delete(email)
    db.session.commit()
    
    # Clear cache
    set_cache(f"emails_list:{firebase_uid}", None, 0)
    set_cache(f"email_stats:{firebase_uid}", None, 0)
    
    # Delete from Gmail in background
    try:
        gmail_service = create_gmail_service(
            email_account.access_token,
            email_account.refresh_token
        )
        update_account_tokens(email_account, gmail_service)
        gmail_service.delete_message(email.message_id)
        print(f"✅ Email {email_id} deleted from Gmail")
    except Exception as e:
        print(f"Gmail delete error (non-critical): {e}")
    
    return jsonify({'message': 'Email deleted successfully'}), 200


@email_bp.route('/email/<int:email_id>/toggle-star', methods=['PUT'])
@handle_errors
def toggle_star(email_id):
    """Toggle star"""
    data = request.get_json()
    
    if not data.get('firebase_uid'):
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    email = Email.query.get(email_id)
    if not email:
        return jsonify({'error': 'Email not found'}), 404
    
    email_account = EmailAccount.query.get(email.account_id)
    if not email_account or email_account.user_id != data['firebase_uid']:
        return jsonify({'error': 'Access denied'}), 403
    
    starred = data.get('starred', True)
    
    email.is_starred = starred
    db.session.commit()
    
    set_cache(f"emails_list:{data['firebase_uid']}", None, 0)
    
    try:
        gmail_service = create_gmail_service(
            email_account.access_token,
            email_account.refresh_token
        )
        update_account_tokens(email_account, gmail_service)
        gmail_service.toggle_star(email.message_id, starred)
    except Exception as e:
        print(f"Gmail sync error: {e}")
    
    return jsonify({
        'message': 'Star toggled successfully',
        'is_starred': starred
    }), 200


@email_bp.route('/email/stats', methods=['GET'])
@handle_errors
def get_email_stats():
    """Get email statistics"""
    firebase_uid = request.args.get('firebase_uid')
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    cache_key = f"email_stats:{firebase_uid}"
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached), 200
    
    email_account = EmailAccount.query.filter_by(user_id=firebase_uid).first()
    if not email_account:
        return jsonify({'error': 'Gmail account not connected'}), 404
    
    total_emails = Email.query.filter_by(account_id=email_account.id).count()
    unread_count = Email.query.filter_by(account_id=email_account.id, is_read=False).count()
    starred_count = Email.query.filter_by(account_id=email_account.id, is_starred=True).count()
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = Email.query.filter(
        Email.account_id == email_account.id,
        Email.email_date >= today_start
    ).count()
    
    from sqlalchemy import func
    category_counts = dict(
        db.session.query(Email.category, func.count(Email.id))
        .filter_by(account_id=email_account.id)
        .group_by(Email.category)
        .all()
    )
    
    result = {
        'total_emails': total_emails,
        'unread_count': unread_count,
        'starred_count': starred_count,
        'today_count': today_count,
        'category_counts': category_counts,
        'last_sync': email_account.last_sync_at.isoformat() if email_account.last_sync_at else None,
        'email_address': email_account.email_address
    }
    
    set_cache(cache_key, result, 120)
    
    return jsonify(result), 200


@email_bp.route('/email/account-status', methods=['GET'])
@handle_errors
def get_account_status():
    """Get account status"""
    firebase_uid = request.args.get('firebase_uid')
    if not firebase_uid:
        return jsonify({'error': 'firebase_uid is required'}), 400
    
    cache_key = f"account_status:{firebase_uid}"
    cached = get_cached(cache_key)
    if cached:
        return jsonify(cached), 200
    
    email_account = EmailAccount.query.filter_by(user_id=firebase_uid).first()
    
    if email_account:
        result = {
            'connected': True,
            'email_address': email_account.email_address,
            'last_sync': email_account.last_sync_at.isoformat() if email_account.last_sync_at else None
        }
    else:
        result = {'connected': False}
    
    set_cache(cache_key, result, 300)
    
    return jsonify(result), 200


@email_bp.route('/email/categories', methods=['GET'])
@handle_errors
def get_categories():
    """Get all categories"""
    return jsonify({'categories': get_all_categories()}), 200


@email_bp.route('/email/test', methods=['GET'])
def test_endpoint():
    """Health check"""
    return jsonify({
        'message': 'Email Summarizer API is working!',
        'status': 'success'
    }), 200