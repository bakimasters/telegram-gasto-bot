import logging
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from bot.database.connection import transaction_db, budget_db
from bot.models.transaction import Transaction, Budget, Summary
from bot.utils.constants import TRANSACTION_TYPES, BUDGET_PERIODS
from bot.utils.validators import validate_amount, validate_category, validate_budget_period


logger = logging.getLogger(__name__)


class TransactionService:
    """Business logic for transaction operations."""
    
    @staticmethod
    def add_transaction(chat_id: int, type: str, category: str, amount: float, 
                      source: str = 'manual') -> Transaction:
        """Add a new transaction with validation."""
        # Validate inputs
        if not validate_amount(amount):
            raise ValueError("Amount must be a positive number")
        
        if not validate_category(category):
            raise ValueError("Category cannot be empty")
        
        if type not in TRANSACTION_TYPES:
            raise ValueError(f"Transaction type must be one of: {', '.join(TRANSACTION_TYPES)}")
        
        # Create transaction object
        transaction = Transaction(
            id=None,
            chat_id=chat_id,
            date=datetime.now(),
            type=type,
            category=category,
            amount=amount,
            source=source
        )
        
        # Save to database
        transaction_id = transaction_db.add_transaction(transaction)
        transaction.id = transaction_id
        
        # Update budget if this is an expense
        if type.lower() == 'expense':
            TransactionService._update_budget_for_expense(transaction)
        
        return transaction
    
    @staticmethod
    def _update_budget_for_expense(transaction: Transaction):
        """Update budget when an expense is added."""
        try:
            # Get the budget for this category
            budget = budget_db.get_budget_by_category(transaction.chat_id, transaction.category)
            if budget:
                # Calculate new current_amount based on the budget period
                current_period_spent = TransactionService._get_current_period_spending(
                    transaction.chat_id, transaction.category, budget.period
                )
                
                # Update the budget's current amount
                budget_db.update_budget_amount(budget.id, transaction.chat_id, current_period_spent)
                
                # Check if budget is exceeded
                if current_period_spent > budget.limit:
                    logger.info(f"Budget exceeded for {transaction.chat_id} in category {transaction.category}")
        except Exception as e:
            logger.error(f"Error updating budget for expense: {e}")
    
    @staticmethod
    def _get_current_period_spending(chat_id: int, category: str, period: str) -> float:
        """Get the total spending for the current period in a category."""
        now = datetime.now()
        start_date = now
        
        if period == 'daily':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'weekly':
            start_date = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        elif period == 'monthly':
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Get all expenses for this category in the current period
        with transaction_db.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(amount) 
                FROM transactions 
                WHERE chat_id = ? AND category = ? AND type = 'expense' AND date >= ?
            """, (chat_id, category, start_date.isoformat()))
            
            result = cursor.fetchone()[0]
            return result if result else 0.0
    
    @staticmethod
    def get_transaction_by_id(transaction_id: int, chat_id: int) -> Optional[Transaction]:
        """Get a transaction by its ID and chat ID."""
        return transaction_db.get_transaction_by_id(transaction_id, chat_id)
    
    @staticmethod
    def get_transactions_by_chat_id(chat_id: int, 
                                   limit: Optional[int] = None,
                                   offset: Optional[int] = None) -> List[Transaction]:
        """Get all transactions for a chat."""
        return transaction_db.get_transactions_by_chat_id(chat_id, limit, offset)
    
    @staticmethod
    def get_transactions_by_date_range(chat_id: int, start_date: datetime, 
                                     end_date: datetime) -> List[Transaction]:
        """Get transactions within a date range."""
        return transaction_db.get_transactions_by_date_range(chat_id, start_date, end_date)
    
    @staticmethod
    def get_daily_summary(chat_id: int, date: datetime) -> Summary:
        """Get daily summary for a specific date."""
        income, expense, balance = transaction_db.get_daily_summary(chat_id, date)
        return Summary(
            total_income=income,
            total_expense=expense,
            balance=balance,
            period_start=date.replace(hour=0, minute=0, second=0, microsecond=0),
            period_end=date.replace(hour=23, minute=59, second=59, microsecond=999999)
        )
    
    @staticmethod
    def get_weekly_summary(chat_id: int) -> Summary:
        """Get weekly summary."""
        start_date = (datetime.now() - timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.now()
        
        transactions = transaction_db.get_transactions_by_date_range(chat_id, start_date, end_date)
        
        total_income = sum(t.amount for t in transactions if t.is_income())
        total_expense = sum(t.amount for t in transactions if t.is_expense())
        
        return Summary(
            total_income=total_income,
            total_expense=total_expense,
            balance=total_income - total_expense,
            period_start=start_date,
            period_end=end_date
        )
    
    @staticmethod
    def get_monthly_summary(chat_id: int) -> Summary:
        """Get monthly summary."""
        start_date = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = datetime.now()
        
        transactions = transaction_db.get_transactions_by_date_range(chat_id, start_date, end_date)
        
        total_income = sum(t.amount for t in transactions if t.is_income())
        total_expense = sum(t.amount for t in transactions if t.is_expense())
        
        return Summary(
            total_income=total_income,
            total_expense=total_expense,
            balance=total_income - total_expense,
            period_start=start_date,
            period_end=end_date
        )
    
    @staticmethod
    def get_expenses_by_category(chat_id: int, start_date: datetime = None, 
                               end_date: datetime = None) -> List[Tuple[str, float]]:
        """Get total expenses grouped by category."""
        return transaction_db.get_expenses_by_category(chat_id, start_date, end_date)
    
    @staticmethod
    def update_transaction_amount(transaction_id: int, chat_id: int, new_amount: float) -> bool:
        """Update transaction amount."""
        if not validate_amount(new_amount):
            raise ValueError("Amount must be a positive number")
        
        success = transaction_db.update_transaction_amount(transaction_id, chat_id, new_amount)
        if success and new_amount > 0:
            # If the transaction is an expense, update the budget
            transaction = transaction_db.get_transaction_by_id(transaction_id, chat_id)
            if transaction and transaction.type.lower() == 'expense':
                TransactionService._update_budget_for_expense(transaction)
        
        return success
    
    @staticmethod
    def delete_transaction(transaction_id: int, chat_id: int) -> bool:
        """Delete a transaction."""
        # If this was an expense, we should update the budget accordingly
        transaction = transaction_db.get_transaction_by_id(transaction_id, chat_id)
        if transaction and transaction.type.lower() == 'expense':
            # We need to adjust the budget, but this is complex logic that requires adjustment
            # For now, we'll just delete the transaction
            pass
        
        return transaction_db.delete_transaction(transaction_id, chat_id)


class BudgetService:
    """Business logic for budget operations."""
    
    @staticmethod
    def add_budget(chat_id: int, category: str, limit: float, period: str) -> Budget:
        """Add a new budget with validation."""
        if not validate_category(category):
            raise ValueError("Category cannot be empty")
        
        if not validate_amount(limit):
            raise ValueError("Budget limit must be a positive number")
        
        if period not in BUDGET_PERIODS:
            raise ValueError(f"Budget period must be one of: {', '.join(BUDGET_PERIODS)}")
        
        # Check if budget already exists for this category
        existing_budget = budget_db.get_budget_by_category(chat_id, category)
        if existing_budget:
            raise ValueError(f"Budget already exists for category: {category}")
        
        # Create budget object
        budget = Budget(
            id=None,
            chat_id=chat_id,
            category=category,
            limit=limit,
            period=period
        )
        
        # Save to database and return updated object
        budget_id = budget_db.add_budget(budget)
        budget.id = budget_id
        
        # Update with current spending
        current_spending = TransactionService._get_current_period_spending(chat_id, category, period)
        budget.current_amount = current_spending
        budget_db.update_budget_amount(budget_id, chat_id, current_spending)
        
        return budget
    
    @staticmethod
    def get_budget_by_category(chat_id: int, category: str) -> Optional[Budget]:
        """Get budget for a specific category."""
        return budget_db.get_budget_by_category(chat_id, category)
    
    @staticmethod
    def get_all_budgets(chat_id: int) -> List[Budget]:
        """Get all budgets for a chat."""
        return budget_db.get_all_budgets(chat_id)
    
    @staticmethod
    def update_budget_amount(budget_id: int, chat_id: int, new_amount: float) -> bool:
        """Update budget current amount."""
        if not validate_amount(new_amount):
            raise ValueError("Amount must be a positive number")
        
        return budget_db.update_budget_amount(budget_id, chat_id, new_amount)
    
    @staticmethod
    def delete_budget(budget_id: int, chat_id: int) -> bool:
        """Delete a budget."""
        return budget_db.delete_budget(budget_id, chat_id)
    
    @staticmethod
    def get_budget_status(chat_id: int) -> List[Tuple[Budget, float, bool]]:
        """Get status for all budgets including current spending and whether limit is exceeded."""
        budgets = budget_db.get_all_budgets(chat_id)
        status_list = []
        
        for budget in budgets:
            current_spending = TransactionService._get_current_period_spending(
                chat_id, budget.category, budget.period
            )
            
            # Update the budget's current amount in the database
            budget_db.update_budget_amount(budget.id, chat_id, current_spending)
            
            budget.current_amount = current_spending
            is_exceeded = current_spending > budget.limit
            status_list.append((budget, current_spending, is_exceeded))
        
        return status_list