import sqlite3
import threading
from contextlib import contextmanager
from typing import List, Optional
from datetime import datetime, timedelta

from bot.models.transaction import Transaction, Budget
from config.settings import DB_NAME


class DatabaseConnection:
    """Thread-safe database connection manager."""
    
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path
        self._local = threading.local()
        
    @contextmanager
    def get_connection(self):
        """Get a thread-local database connection."""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(self.db_path)
            self._local.connection.row_factory = sqlite3.Row
        try:
            yield self._local.connection
        except Exception:
            self._local.connection.rollback()
            raise
        else:
            self._local.connection.commit()


class TransactionDB:
    """Database operations for transactions."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        self._init_tables()
        
    def _init_tables(self):
        """Initialize database tables."""
        with self.db.get_connection() as conn:
            # Transactions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    amount REAL NOT NULL,
                    source TEXT DEFAULT 'manual'
                )
            """)
            
            # Budgets table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    limit_amount REAL NOT NULL,
                    period TEXT NOT NULL,
                    current_amount REAL DEFAULT 0.0,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_chat_id ON transactions(chat_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_budgets_chat_id ON budgets(chat_id)")
            
    def add_transaction(self, transaction: Transaction) -> int:
        """Add a new transaction to the database."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (chat_id, date, type, category, amount, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                transaction.chat_id,
                transaction.date.isoformat(),
                transaction.type,
                transaction.category,
                transaction.amount,
                transaction.source
            ))
            return cursor.lastrowid
    
    def get_transaction_by_id(self, transaction_id: int, chat_id: int) -> Optional[Transaction]:
        """Get a specific transaction by ID and chat ID."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE id = ? AND chat_id = ?
            """, (transaction_id, chat_id))
            
            row = cursor.fetchone()
            if row:
                return Transaction(
                    id=row['id'],
                    chat_id=row['chat_id'],
                    date=datetime.fromisoformat(row['date']),
                    type=row['type'],
                    category=row['category'],
                    amount=row['amount'],
                    source=row['source']
                )
            return None
    
    def get_transactions_by_chat_id(self, chat_id: int, 
                                   limit: Optional[int] = None,
                                   offset: Optional[int] = None) -> List[Transaction]:
        """Get all transactions for a specific chat."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM transactions WHERE chat_id = ? ORDER BY date DESC"
            params = [chat_id]
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
                
            if offset:
                query += " OFFSET ?"
                params.append(offset)
                
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                Transaction(
                    id=row['id'],
                    chat_id=row['chat_id'],
                    date=datetime.fromisoformat(row['date']),
                    type=row['type'],
                    category=row['category'],
                    amount=row['amount'],
                    source=row['source']
                ) for row in rows
            ]
    
    def get_transactions_by_date_range(self, chat_id: int, start_date: datetime, 
                                     end_date: datetime) -> List[Transaction]:
        """Get transactions within a specific date range."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE chat_id = ? AND date BETWEEN ? AND ?
                ORDER BY date DESC
            """, (chat_id, start_date.isoformat(), end_date.isoformat()))
            
            rows = cursor.fetchall()
            return [
                Transaction(
                    id=row['id'],
                    chat_id=row['chat_id'],
                    date=datetime.fromisoformat(row['date']),
                    type=row['type'],
                    category=row['category'],
                    amount=row['amount'],
                    source=row['source']
                ) for row in rows
            ]
    
    def get_transactions_by_category(self, chat_id: int, category: str) -> List[Transaction]:
        """Get all transactions for a specific category."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE chat_id = ? AND category = ?
                ORDER BY date DESC
            """, (chat_id, category))
            
            rows = cursor.fetchall()
            return [
                Transaction(
                    id=row['id'],
                    chat_id=row['chat_id'],
                    date=datetime.fromisoformat(row['date']),
                    type=row['type'],
                    category=row['category'],
                    amount=row['amount'],
                    source=row['source']
                ) for row in rows
            ]
    
    def get_transactions_by_type(self, chat_id: int, transaction_type: str) -> List[Transaction]:
        """Get all transactions of a specific type."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE chat_id = ? AND type = ?
                ORDER BY date DESC
            """, (chat_id, transaction_type))
            
            rows = cursor.fetchall()
            return [
                Transaction(
                    id=row['id'],
                    chat_id=row['chat_id'],
                    date=datetime.fromisoformat(row['date']),
                    type=row['type'],
                    category=row['category'],
                    amount=row['amount'],
                    source=row['source']
                ) for row in rows
            ]
    
    def update_transaction_amount(self, transaction_id: int, chat_id: int, new_amount: float) -> bool:
        """Update the amount of a transaction."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE transactions 
                SET amount = ? 
                WHERE id = ? AND chat_id = ?
            """, (new_amount, transaction_id, chat_id))
            
            return cursor.rowcount > 0
    
    def delete_transaction(self, transaction_id: int, chat_id: int) -> bool:
        """Delete a transaction."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ? AND chat_id = ?", 
                          (transaction_id, chat_id))
            return cursor.rowcount > 0
    
    def get_daily_summary(self, chat_id: int, date: datetime) -> tuple[float, float, float]:
        """Get daily summary for a specific date."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total income for the day
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) 
                FROM transactions 
                WHERE chat_id = ? AND type = 'income' AND date LIKE ?
            """, (chat_id, f"{date.date().isoformat()}%"))
            income = cursor.fetchone()[0]
            
            # Get total expenses for the day
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) 
                FROM transactions 
                WHERE chat_id = ? AND type = 'expense' AND date LIKE ?
            """, (chat_id, f"{date.date().isoformat()}%"))
            expense = cursor.fetchone()[0]
            
            return income, expense, income - expense
    
    def get_expenses_by_category(self, chat_id: int, start_date: datetime = None, 
                               end_date: datetime = None) -> List[tuple[str, float]]:
        """Get total expenses grouped by category."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            if start_date and end_date:
                cursor.execute("""
                    SELECT category, SUM(amount) 
                    FROM transactions 
                    WHERE chat_id = ? AND type = 'expense' AND date BETWEEN ? AND ?
                    GROUP BY category
                """, (chat_id, start_date.isoformat(), end_date.isoformat()))
            else:
                cursor.execute("""
                    SELECT category, SUM(amount) 
                    FROM transactions 
                    WHERE chat_id = ? AND type = 'expense'
                    GROUP BY category
                """, (chat_id,))
            
            return [(row[0], row[1]) for row in cursor.fetchall()]
    
    def get_income_vs_expense_by_day(self, chat_id: int, days: int) -> List[tuple[str, str, float]]:
        """Get income vs expense grouped by day for the last X days."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            start_date = (datetime.now() - timedelta(days=days)).date().isoformat()
            
            cursor.execute("""
                SELECT date(date) as day, type, SUM(amount) 
                FROM transactions 
                WHERE chat_id = ? AND date >= ? 
                GROUP BY date(date), type
                ORDER BY date(date)
            """, (chat_id, start_date))
            
            return [(row[0], row[1], row[2]) for row in cursor.fetchall()]


class BudgetDB:
    """Database operations for budgets."""
    
    def __init__(self, db_connection: DatabaseConnection):
        self.db = db_connection
        
    def add_budget(self, budget: Budget) -> int:
        """Add a new budget."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO budgets 
                (chat_id, category, limit_amount, period, current_amount, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                budget.chat_id,
                budget.category,
                budget.limit,
                budget.period,
                budget.current_amount,
                datetime.now().isoformat()
            ))
            return cursor.lastrowid
    
    def get_budget_by_id(self, budget_id: int, chat_id: int) -> Optional[Budget]:
        """Get a specific budget by ID and chat ID."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM budgets 
                WHERE id = ? AND chat_id = ?
            """, (budget_id, chat_id))
            
            row = cursor.fetchone()
            if row:
                return Budget(
                    id=row['id'],
                    chat_id=row['chat_id'],
                    category=row['category'],
                    limit=row['limit_amount'],
                    period=row['period'],
                    current_amount=row['current_amount']
                )
            return None
    
    def get_budget_by_category(self, chat_id: int, category: str) -> Optional[Budget]:
        """Get budget for a specific category."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM budgets 
                WHERE chat_id = ? AND category = ?
            """, (chat_id, category))
            
            row = cursor.fetchone()
            if row:
                return Budget(
                    id=row['id'],
                    chat_id=row['chat_id'],
                    category=row['category'],
                    limit=row['limit_amount'],
                    period=row['period'],
                    current_amount=row['current_amount']
                )
            return None
            
    def get_all_budgets(self, chat_id: int) -> List[Budget]:
        """Get all budgets for a chat."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM budgets 
                WHERE chat_id = ?
            """, (chat_id,))
            
            rows = cursor.fetchall()
            return [
                Budget(
                    id=row['id'],
                    chat_id=row['chat_id'],
                    category=row['category'],
                    limit=row['limit_amount'],
                    period=row['period'],
                    current_amount=row['current_amount']
                ) for row in rows
            ]
    
    def update_budget_amount(self, budget_id: int, chat_id: int, new_amount: float) -> bool:
        """Update the current amount of a budget."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE budgets 
                SET current_amount = ? 
                WHERE id = ? AND chat_id = ?
            """, (new_amount, budget_id, chat_id))
            
            return cursor.rowcount > 0
    
    def delete_budget(self, budget_id: int, chat_id: int) -> bool:
        """Delete a budget."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM budgets WHERE id = ? AND chat_id = ?", 
                          (budget_id, chat_id))
            return cursor.rowcount > 0


# Global database instances
db_connection = DatabaseConnection()
transaction_db = TransactionDB(db_connection)
budget_db = BudgetDB(db_connection)