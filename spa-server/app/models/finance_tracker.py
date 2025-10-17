from app import db
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Float, Text, CheckConstraint, Index

# ======================
# FINANCE TRACKER TABLES (3 tables)
# ======================

class Transaction(db.Model):
    """Stores all income and expense records"""
    __tablename__ = 'transactions'
    __table_args__ = (
        CheckConstraint('type IN (\'income\', \'expense\')', name='check_transaction_type'),
        CheckConstraint('account IN (\'cash\', \'card\', \'savings\')', name='check_transaction_account'),
        CheckConstraint('amount >= 0', name='check_transaction_amount_positive'),
        Index('idx_transaction_user', 'user_id'),
        Index('idx_transaction_date', 'date'),
        Index('idx_transaction_type', 'type')
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(String(100), nullable=False)
    amount = db.Column(Float, nullable=False)
    type = db.Column(String(10), nullable=False)  # 'income' or 'expense'
    category = db.Column(String(50))
    account = db.Column(String(10), nullable=False)  # 'cash', 'card', or 'savings'
    date = db.Column(DateTime, nullable=False)
    notes = db.Column(Text)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='transactions')

class Budget(db.Model):
    """Stores the monthly budget for the user"""
    __tablename__ = 'budgets'
    __table_args__ = (
        Index('idx_budget_user_month', 'user_id', 'month'),
    )

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, index=True)
    month = db.Column(String(7), nullable=False)  # Format: YYYY-MM
    amount = db.Column(Float, nullable=False)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='budgets')

class FinanceSetting(db.Model):
    """Stores finance-related app settings"""
    __tablename__ = 'finance_settings'

    id = db.Column(Integer, primary_key=True)
    user_id = db.Column(String(36), ForeignKey('users.id'), nullable=False, unique=True, index=True)
    currency = db.Column(String(3), default='INR')
    default_account = db.Column(String(10), default='cash')  # 'cash', 'card', or 'savings'
    budget_notifications = db.Column(Boolean, default=True)
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', back_populates='settings')
