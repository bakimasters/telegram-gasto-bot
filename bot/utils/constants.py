"""Constants used throughout the bot."""
from datetime import datetime


# Transaction types
TRANSACTION_TYPES = ['income', 'expense']

# Budget periods
BUDGET_PERIODS = ['daily', 'weekly', 'monthly']

# Default categories
DEFAULT_CATEGORIES = {
    'expense': [
        'comida', 'transporte', 'ocio', 'salud', 'educacion', 
        'vivienda', 'ropa', 'otros', 'servicios', 'viajes'
    ],
    'income': [
        'salario', 'freelance', 'inversiones', 'regalo', 
        'otro ingreso', 'negocio', 'alquiler'
    ]
}

# Default budget limits by category (per month)
DEFAULT_BUDGET_LIMITS = {
    'comida': 600.0,
    'transporte': 300.0,
    'ocio': 200.0,
    'salud': 150.0,
    'educacion': 100.0,
    'vivienda': 800.0,
    'ropa': 100.0,
    'servicios': 200.0,
    'viajes': 300.0
}