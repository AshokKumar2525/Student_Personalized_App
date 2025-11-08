from flask import Blueprint, request, jsonify
from app import db
from app.models.scholarships import Scholarship, ScholarshipCriteria, UserScholarshipPreference, user_saved_scholarships
from app.models.users import User
from datetime import datetime
from sqlalchemy import and_, or_

scholarship_bp = Blueprint('scholarships', __name__)

@scholarship_bp.route('/scholarships/preferences', methods=['POST'])
def save_preferences():
    """Save or update user scholarship preferences"""
    try:
        data = request.get_json()
        firebase_uid = data.get('firebase_uid')
        
        if not firebase_uid:
            return jsonify({'error': 'firebase_uid is required'}), 400
        
        user = User.query.filter_by(id=firebase_uid).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        preferences = UserScholarshipPreference.query.filter_by(user_id=user.id).first()
        
        if preferences:
            preferences.branch = data.get('branch')
            preferences.current_year = data.get('current_year')
            preferences.gender = data.get('gender')
            preferences.skills = data.get('skills', [])
            preferences.preferred_countries = data.get('preferred_countries', [])
            preferences.preferred_types = data.get('preferred_types', [])
            preferences.min_amount = data.get('min_amount')
        else:
            preferences = UserScholarshipPreference(
                user_id=user.id,
                branch=data.get('branch'),
                current_year=data.get('current_year'),
                gender=data.get('gender'),
                skills=data.get('skills', []),
                preferred_countries=data.get('preferred_countries', []),
                preferred_types=data.get('preferred_types', []),
                min_amount=data.get('min_amount')
            )
            db.session.add(preferences)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Preferences saved successfully',
            'preferences': {
                'branch': preferences.branch,
                'current_year': preferences.current_year,
                'gender': preferences.gender,
                'skills': preferences.skills,
                'preferred_countries': preferences.preferred_countries,
                'preferred_types': preferences.preferred_types,
                'min_amount': preferences.min_amount
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to save preferences: {str(e)}'}), 500

@scholarship_bp.route('/scholarships/preferences/<firebase_uid>', methods=['GET'])
def get_preferences(firebase_uid):
    """Get user scholarship preferences"""
    try:
        user = User.query.filter_by(id=firebase_uid).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        preferences = UserScholarshipPreference.query.filter_by(user_id=user.id).first()
        
        if not preferences:
            return jsonify({'has_preferences': False}), 200
        
        return jsonify({
            'has_preferences': True,
            'preferences': {
                'branch': preferences.branch,
                'current_year': preferences.current_year,
                'gender': preferences.gender,
                'skills': preferences.skills or [],
                'preferred_countries': preferences.preferred_countries or [],
                'preferred_types': preferences.preferred_types or [],
                'min_amount': preferences.min_amount
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get preferences: {str(e)}'}), 500

@scholarship_bp.route('/scholarships/search', methods=['POST'])
def search_scholarships():
    """Search scholarships based on user preferences"""
    try:
        data = request.get_json()
        firebase_uid = data.get('firebase_uid')
        
        if not firebase_uid:
            return jsonify({'error': 'firebase_uid is required'}), 400
        
        user = User.query.filter_by(id=firebase_uid).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        preferences = UserScholarshipPreference.query.filter_by(user_id=user.id).first()
        
        query = Scholarship.query.filter(Scholarship.is_active == True)
        query = query.filter(Scholarship.application_deadline >= datetime.now().date())
        
        if preferences:
            if preferences.branch:
                query = query.filter(
                    or_(
                        Scholarship.eligible_branches.contains([preferences.branch]),
                        Scholarship.eligible_branches == None
                    )
                )
            
            if preferences.current_year:
                query = query.filter(
                    or_(
                        Scholarship.eligible_years.contains([preferences.current_year]),
                        Scholarship.eligible_years == None
                    )
                )
            
            if preferences.gender:
                query = query.filter(
                    or_(
                        Scholarship.eligible_genders.contains([preferences.gender]),
                        Scholarship.eligible_genders == None
                    )
                )
            
            if preferences.preferred_countries:
                query = query.filter(
                    Scholarship.country.in_(preferences.preferred_countries)
                )
            
            if preferences.preferred_types:
                query = query.filter(
                    Scholarship.scholarship_type.in_(preferences.preferred_types)
                )
        
        scholarships = query.order_by(Scholarship.application_deadline).all()
        
        saved_ids = set()
        if user.saved_scholarships:
            saved_ids = {s.id for s in user.saved_scholarships}
        
        result = []
        for scholarship in scholarships:
            result.append({
                'id': scholarship.id,
                'title': scholarship.title,
                'description': scholarship.description,
                'provider': scholarship.provider,
                'amount': scholarship.amount,
                'currency': scholarship.currency,
                'application_deadline': scholarship.application_deadline.isoformat(),
                'website_url': scholarship.website_url,
                'country': scholarship.country,
                'scholarship_type': scholarship.scholarship_type,
                'eligible_branches': scholarship.eligible_branches or [],
                'eligible_years': scholarship.eligible_years or [],
                'eligible_genders': scholarship.eligible_genders or [],
                'required_skills': scholarship.required_skills or [],
                'is_saved': scholarship.id in saved_ids
            })
        
        return jsonify({
            'scholarships': result,
            'total': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to search scholarships: {str(e)}'}), 500

@scholarship_bp.route('/scholarships/save', methods=['POST'])
def save_scholarship():
    """Save a scholarship for later"""
    try:
        data = request.get_json()
        firebase_uid = data.get('firebase_uid')
        scholarship_id = data.get('scholarship_id')
        
        if not all([firebase_uid, scholarship_id]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        user = User.query.filter_by(id=firebase_uid).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        scholarship = Scholarship.query.get(scholarship_id)
        if not scholarship:
            return jsonify({'error': 'Scholarship not found'}), 404
        
        if scholarship not in user.saved_scholarships:
            user.saved_scholarships.append(scholarship)
            db.session.commit()
            return jsonify({'message': 'Scholarship saved successfully'}), 200
        else:
            return jsonify({'message': 'Scholarship already saved'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to save scholarship: {str(e)}'}), 500

@scholarship_bp.route('/scholarships/unsave', methods=['POST'])
def unsave_scholarship():
    """Remove a saved scholarship"""
    try:
        data = request.get_json()
        firebase_uid = data.get('firebase_uid')
        scholarship_id = data.get('scholarship_id')
        
        if not all([firebase_uid, scholarship_id]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        user = User.query.filter_by(id=firebase_uid).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        scholarship = Scholarship.query.get(scholarship_id)
        if not scholarship:
            return jsonify({'error': 'Scholarship not found'}), 404
        
        if scholarship in user.saved_scholarships:
            user.saved_scholarships.remove(scholarship)
            db.session.commit()
            return jsonify({'message': 'Scholarship removed successfully'}), 200
        else:
            return jsonify({'message': 'Scholarship not in saved list'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to unsave scholarship: {str(e)}'}), 500

@scholarship_bp.route('/scholarships/saved/<firebase_uid>', methods=['GET'])
def get_saved_scholarships(firebase_uid):
    """Get all saved scholarships for a user"""
    try:
        user = User.query.filter_by(id=firebase_uid).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        result = []
        for scholarship in user.saved_scholarships:
            result.append({
                'id': scholarship.id,
                'title': scholarship.title,
                'description': scholarship.description,
                'provider': scholarship.provider,
                'amount': scholarship.amount,
                'currency': scholarship.currency,
                'application_deadline': scholarship.application_deadline.isoformat(),
                'website_url': scholarship.website_url,
                'country': scholarship.country,
                'scholarship_type': scholarship.scholarship_type,
                'is_saved': True
            })
        
        return jsonify({
            'scholarships': result,
            'total': len(result)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get saved scholarships: {str(e)}'}), 500

@scholarship_bp.route('/scholarships/<scholarship_id>', methods=['GET'])
def get_scholarship_details(scholarship_id):
    """Get detailed information about a specific scholarship"""
    try:
        scholarship = Scholarship.query.get(scholarship_id)
        if not scholarship:
            return jsonify({'error': 'Scholarship not found'}), 404
        
        criteria = ScholarshipCriteria.query.filter_by(scholarship_id=scholarship.id).first()
        
        result = {
            'id': scholarship.id,
            'title': scholarship.title,
            'description': scholarship.description,
            'provider': scholarship.provider,
            'amount': scholarship.amount,
            'currency': scholarship.currency,
            'application_deadline': scholarship.application_deadline.isoformat(),
            'website_url': scholarship.website_url,
            'country': scholarship.country,
            'scholarship_type': scholarship.scholarship_type,
            'eligible_branches': scholarship.eligible_branches or [],
            'eligible_years': scholarship.eligible_years or [],
            'eligible_genders': scholarship.eligible_genders or [],
            'required_skills': scholarship.required_skills or [],
            'criteria': None
        }
        
        if criteria:
            result['criteria'] = {
                'min_gpa': criteria.min_gpa,
                'min_percentage': criteria.min_percentage,
                'max_family_income': criteria.max_family_income,
                'income_currency': criteria.income_currency
            }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get scholarship details: {str(e)}'}), 500

@scholarship_bp.route('/scholarships/test', methods=['GET'])
def test_endpoint():
    return jsonify({'message': 'Scholarship API is working!', 'status': 'success'})