from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    """Represents a financial transaction (income or expense)."""
    id: Optional[int]
    chat_id: int
    date: datetime
    type: str  # 'income' or 'expense'
    category: str
    amount: float
    source: str = 'manual'  # 'manual', 'ocr', etc.
    
    def is_income(self) -> bool:
        return self.type.lower() == 'income'
    
    def is_expense(self) -> bool:
        return self.type.lower() == 'expense'


@dataclass
class Budget:
    """Represents a budget for a specific category."""
    id: Optional[int]
    chat_id: int
    category: str
    limit: float
    period: str  # 'daily', 'weekly', 'monthly'
    current_amount: float = 0.0
    
    
@dataclass
class Summary:
    """Represents financial summary data."""
    total_income: float
    total_expense: float
    balance: float
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None