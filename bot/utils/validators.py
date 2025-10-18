"""Validation utilities for the bot."""
import re
from typing import Union


def validate_amount(amount: Union[str, float, int]) -> bool:
    """Validate that an amount is a positive number."""
    try:
        float_amount = float(amount)
        return float_amount >= 0
    except (ValueError, TypeError):
        return False


def validate_category(category: str) -> bool:
    """Validate that a category is not empty and has valid characters."""
    if not category or not category.strip():
        return False
    
    # Check if category contains only alphanumeric characters, spaces, and hyphens
    pattern = r'^[a-zA-Z0-9\s\-]+$'
    return bool(re.match(pattern, category.strip()))


def validate_budget_period(period: str) -> bool:
    """Validate that a budget period is valid."""
    from bot.utils.constants import BUDGET_PERIODS
    return period.lower() in BUDGET_PERIODS


def validate_telegram_chat_id(chat_id: Union[str, int]) -> bool:
    """Validate that a chat ID is a valid integer."""
    try:
        int(chat_id)
        return True
    except ValueError:
        return False