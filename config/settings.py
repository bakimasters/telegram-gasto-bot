import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Bot Configuration
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in environment variables")

# Database Configuration
DB_NAME = os.getenv("DB_NAME", "movimientos.db")

# Chart Configuration
CHART_WIDTH = int(os.getenv("CHART_WIDTH", "800"))
CHART_HEIGHT = int(os.getenv("CHART_HEIGHT", "600"))

# Budget Configuration
DEFAULT_BUDGET_NOTIFICATION_HOUR = int(os.getenv("BUDGET_NOTIFICATION_HOUR", "20"))
DEFAULT_BUDGET_NOTIFICATION_MINUTE = int(os.getenv("BUDGET_NOTIFICATION_MINUTE", "0"))

# Reminder Configuration
DEFAULT_REMINDER_HOUR = int(os.getenv("REMINDER_HOUR", "18"))
DEFAULT_REMINDER_MINUTE = int(os.getenv("REMINDER_MINUTE", "0"))