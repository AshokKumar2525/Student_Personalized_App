# spa-server/app/models/finance_tracker.py

from sqlalchemy import Index
from app import db
from datetime import datetime

# ----------------------
# Budget Model
# ----------------------
class Budget(db.Model):
    """Stores the monthly budget for categories"""
    __tablename__ = 'budgets'
    __table_args__ = (
        Index('idx_budget_user_month_category', 'user_id', 'month', 'category'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False)  # Add this field
    month = db.Column(db.String(7), nullable=False)  # Format: YYYY-MM
    amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='budgets')


# ----------------------
# Transaction Model
# ----------------------
class Transaction(db.Model):
    """Stores individual financial transactions"""
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False, index=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    budget = db.relationship('Budget', back_populates='transactions')


# Add back-populates in Budget
Budget.transactions = db.relationship('Transaction', back_populates='budget', cascade='all, delete-orphan')


# ----------------------
# FinanceSetting Model
# ----------------------
class FinanceSetting(db.Model):
    """Stores user-specific finance settings"""
    __tablename__ = 'finance_settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, unique=True)
    currency = db.Column(db.String(10), default='INR')  # Default currency
    notifications_enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='finance_settings')
