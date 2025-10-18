"""Keyboard utilities for the bot."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard():
    """Get the main menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton("📥 Ingreso", callback_data="income"),
            InlineKeyboardButton("📤 Gasto", callback_data="expense")
        ],
        [
            InlineKeyboardButton("📊 Resumen", callback_data="summary"),
            InlineKeyboardButton("📈 Gráficos", callback_data="charts")
        ],
        [
            InlineKeyboardButton("💰 Presupuestos", callback_data="budgets"),
            InlineKeyboardButton("⚙️ Configuración", callback_data="settings")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_category_selection_keyboard(transaction_type: str = 'expense'):
    """Get a keyboard for category selection."""
    from bot.utils.constants import DEFAULT_CATEGORIES
    
    categories = DEFAULT_CATEGORIES.get(transaction_type, [])
    
    # Create buttons in rows of 2
    keyboard = []
    for i in range(0, len(categories), 2):
        row = []
        for category in categories[i:i+2]:
            row.append(InlineKeyboardButton(
                category.capitalize(), 
                callback_data=f"cat:{category}"
            ))
        keyboard.append(row)
    
    # Add custom category option
    keyboard.append([InlineKeyboardButton("✍️ Otra categoría", callback_data="cat:custom")])
    
    return InlineKeyboardMarkup(keyboard)


def get_budget_period_keyboard():
    """Get a keyboard for budget period selection."""
    from bot.utils.constants import BUDGET_PERIODS
    
    keyboard = []
    for period in BUDGET_PERIODS:
        keyboard.append([
            InlineKeyboardButton(
                period.capitalize(), 
                callback_data=f"period:{period}"
            )
        ])
    
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard(action: str, data: str = ""):
    """Get a keyboard with confirm/cancel options."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirmar", callback_data=f"confirm:{action}:{data}"),
            InlineKeyboardButton("❌ Cancelar", callback_data=f"cancel:{action}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_summary_period_keyboard():
    """Get a keyboard for summary period selection."""
    keyboard = [
        [
            InlineKeyboardButton("📅 Hoy", callback_data="summary:today"),
            InlineKeyboardButton("📆 Esta semana", callback_data="summary:week")
        ],
        [
            InlineKeyboardButton("🗓️ Este mes", callback_data="summary:month"),
            InlineKeyboardButton("📈 Total", callback_data="summary:total")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)