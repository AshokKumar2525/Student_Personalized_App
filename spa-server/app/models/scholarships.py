from app import db
from datetime import datetime
from sqlalchemy import String, DateTime, Text, Boolean, Date, ForeignKey, Index, Float, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from app.models.utils import generate_uuid

class Scholarship(db.Model):
    """Main scholarship information table"""
    __tablename__ = 'scholarships'
    __table_args__ = (
        Index('idx_scholarship_deadline', 'application_deadline'),
        Index('idx_scholarship_active', 'is_active'),
        Index('idx_scholarship_branches', 'eligible_branches', postgresql_using='gin'),
        Index('idx_scholarship_years', 'eligible_years', postgresql_using='gin'),
        Index('idx_scholarship_genders', 'eligible_genders', postgresql_using='gin'),
        Index('idx_scholarship_skills', 'required_skills', postgresql_using='gin'),
    )

    id = db.Column(String(36), primary_key=True, default=generate_uuid)
    title = db.Column(String(128), nullable=False)
    description = db.Column(Text)
    provider = db.Column(String(128))
    website_url = db.Column(String(512), nullable=False)
    application_deadline = db.Column(Date, nullable=False)
    amount = db.Column(String(64))
    currency = db.Column(String(3))
    is_active = db.Column(Boolean, default=True, nullable=False)

    # Filtering criteria
    eligible_branches = db.Column(ARRAY(String(64)))
    eligible_years = db.Column(ARRAY(Integer))
    eligible_genders = db.Column(ARRAY(String(10)))
    required_skills = db.Column(ARRAY(String(32)))

    # Additional metadata
    country = db.Column(String(64))
    scholarship_type = db.Column(String(32))

    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    criteria = db.relationship('ScholarshipCriteria', back_populates='scholarship',
                               uselist=False)
    saved_by = db.relationship('User', secondary='user_saved_scholarships',
                              back_populates='saved_scholarships')

class ScholarshipCriteria(db.Model):
    """Detailed eligibility criteria for scholarships"""
    __tablename__ = 'scholarship_criteria'

    id = db.Column(Integer, primary_key=True)
    scholarship_id = db.Column(String(36), ForeignKey('scholarships.id'),
                              nullable=False, unique=True)

    # Academic criteria
    min_gpa = db.Column(Float)
    min_percentage = db.Column(Float)

    # Financial criteria
    max_family_income = db.Column(Float)
    income_currency = db.Column(String(3))

    # Relationships
    scholarship = db.relationship('Scholarship', back_populates='criteria')

class UserScholarshipPreference(db.Model):
    """User preferences for scholarship filtering"""
    __tablename__ = 'user_scholarship_preferences'

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, unique=True)

    # Academic information
    branch = db.Column(String(64))
    current_year = db.Column(Integer)
    gender = db.Column(String(10))
    skills = db.Column(ARRAY(String(32)))

    # Preferences
    preferred_countries = db.Column(ARRAY(String(64)))
    preferred_types = db.Column(ARRAY(String(32)))
    min_amount = db.Column(Float)

    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='scholarship_preferences')

# Association table for saved scholarships (many-to-many)
user_saved_scholarships = db.Table(
    'user_saved_scholarships',
    db.Column('user_id', String(36), ForeignKey('users.id'), primary_key=True, index=True),
    db.Column('scholarship_id', String(36), ForeignKey('scholarships.id'), primary_key=True, index=True),
    db.Column('saved_at', DateTime, default=datetime.utcnow, index=True)
)