# spa-server/app/routes/finance_routes.py
from flask import Blueprint, request, jsonify
from app import db
from app.models.finance_tracker import Transaction, Budget, FinanceSetting
from datetime import datetime
from sqlalchemy import func, extract

finance_bp = Blueprint('finance', __name__)

@finance_bp.route('/finance/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions for a user"""
    try:
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 10))
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        transactions = Transaction.query.filter_by(user_id=user_id)\
            .order_by(Transaction.date.desc())\
            .limit(limit)\
            .all()
        
        return jsonify({
            'transactions': [
                {
                    'id': t.id,
                    'title': t.title,
                    'amount': t.amount,
                    'type': t.type,
                    'category': t.category,
                    'account': t.account,
                    'date': t.date.isoformat(),
                    'notes': t.notes,
                    'created_at': t.created_at.isoformat(),
                    'updated_at': t.updated_at.isoformat()
                } for t in transactions
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@finance_bp.route('/finance/transactions', methods=['POST'])
def create_transaction():
    """Create a new transaction"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'title', 'amount', 'type', 'account', 'date']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        transaction = Transaction(
            user_id=data['user_id'],
            title=data['title'],
            amount=float(data['amount']),
            type=data['type'],
            category=data.get('category'),
            account=data['account'],
            date=datetime.fromisoformat(data['date'].replace('Z', '+00:00')),
            notes=data.get('notes')
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Transaction created successfully',
            'transaction': {
                'id': transaction.id,
                'title': transaction.title,
                'amount': transaction.amount,
                'type': transaction.type,
                'category': transaction.category,
                'account': transaction.account,
                'date': transaction.date.isoformat(),
                'notes': transaction.notes,
                'created_at': transaction.created_at.isoformat(),
                'updated_at': transaction.updated_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@finance_bp.route('/finance/transactions/<int:transaction_id>', methods=['PUT'])
def update_transaction(transaction_id):
    """Update an existing transaction"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        # Update fields
        if 'title' in data:
            transaction.title = data['title']
        if 'amount' in data:
            transaction.amount = float(data['amount'])
        if 'type' in data:
            transaction.type = data['type']
        if 'category' in data:
            transaction.category = data['category']
        if 'account' in data:
            transaction.account = data['account']
        if 'date' in data:
            transaction.date = datetime.fromisoformat(data['date'].replace('Z', '+00:00'))
        if 'notes' in data:
            transaction.notes = data['notes']
        
        transaction.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Transaction updated successfully',
            'transaction': {
                'id': transaction.id,
                'title': transaction.title,
                'amount': transaction.amount,
                'type': transaction.type,
                'category': transaction.category,
                'account': transaction.account,
                'date': transaction.date.isoformat(),
                'notes': transaction.notes,
                'created_at': transaction.created_at.isoformat(),
                'updated_at': transaction.updated_at.isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@finance_bp.route('/finance/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    """Delete a transaction"""
    try:
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
        
        transaction = Transaction.query.filter_by(id=transaction_id, user_id=user_id).first()
        if not transaction:
            return jsonify({'error': 'Transaction not found'}), 404
        
        db.session.delete(transaction)
        db.session.commit()
        
        return jsonify({'message': 'Transaction deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@finance_bp.route('/finance/summary', methods=['GET'])
def get_summary():
    """Get monthly summary with income, expenses, and category breakdown"""
    try:
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not all([user_id, start_date, end_date]):
            return jsonify({'error': 'user_id, start_date, and end_date are required'}), 400
        
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # Get income and expenses
        income = db.session.query(func.sum(Transaction.amount))\
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == 'income',
                Transaction.date >= start,
                Transaction.date <= end
            ).scalar() or 0
        
        expense = db.session.query(func.sum(Transaction.amount))\
            .filter(
                Transaction.user_id == user_id,
                Transaction.type == 'expense',
                Transaction.date >= start,
                Transaction.date <= end
            ).scalar() or 0
        
        # Get category-wise expenses
        category_expenses = db.session.query(
            Transaction.category,
            func.sum(Transaction.amount)
        ).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            Transaction.date >= start,
            Transaction.date <= end
        ).group_by(Transaction.category).all()
        
        # Get account balances (sum of all transactions per account)
        cash_balance = db.session.query(
            func.sum(
                func.case(
                    (Transaction.type == 'income', Transaction.amount),
                    else_=-Transaction.amount
                )
            )
        ).filter(
            Transaction.user_id == user_id,
            Transaction.account == 'cash'
        ).scalar() or 0
        
        online_balance = db.session.query(
            func.sum(
                func.case(
                    (Transaction.type == 'income', Transaction.amount),
                    else_=-Transaction.amount
                )
            )
        ).filter(
            Transaction.user_id == user_id,
            Transaction.account.in_(['card', 'savings'])
        ).scalar() or 0
        
        return jsonify({
            'total_income': float(income),
            'total_expense': float(expense),
            'savings': float(income - expense),
            'cash_balance': float(cash_balance),
            'online_balance': float(online_balance),
            'category_expenses': {
                cat: float(amt) for cat, amt in category_expenses if cat
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@finance_bp.route('/finance/budgets', methods=['GET'])
def get_budgets():
    """Get budgets for a specific month"""
    try:
        user_id = request.args.get('user_id')
        month = request.args.get('month')  # Format: YYYY-MM
        
        if not all([user_id, month]):
            return jsonify({'error': 'user_id and month are required'}), 400
        
        budgets = Budget.query.filter_by(user_id=user_id, month=month).all()
        
        return jsonify({
            'budgets': [
                {
                    'id': b.id,
                    'category': b.category,
                    'amount': b.amount,
                    'month': b.month
                } for b in budgets
            ]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@finance_bp.route('/finance/budgets', methods=['POST'])
def set_budget():
    """Set or update budget for a category"""
    try:
        data = request.get_json()
        
        required_fields = ['user_id', 'category', 'amount', 'month']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if budget already exists
        existing_budget = Budget.query.filter_by(
            user_id=data['user_id'],
            category=data['category'],
            month=data['month']
        ).first()
        
        if existing_budget:
            existing_budget.amount = float(data['amount'])
            existing_budget.updated_at = datetime.utcnow()
        else:
            budget = Budget(
                user_id=data['user_id'],
                category=data['category'],
                amount=float(data['amount']),
                month=data['month']
            )
            db.session.add(budget)
        
        db.session.commit()
        
        return jsonify({'message': 'Budget set successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@finance_bp.route('/finance/test', methods=['GET'])
def test_endpoint():
    return jsonify({'message': 'Finance Tracker API is working!', 'status': 'success'})