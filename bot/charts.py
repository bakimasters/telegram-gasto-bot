"""Chart generation utilities for the bot."""
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import io
from datetime import datetime
from typing import List, Tuple

from bot.services.transaction_service import TransactionService


def generate_expense_pie_chart(chat_id: int) -> io.BytesIO:
    """Generate a pie chart of expenses by category."""
    # Get expenses by category
    expenses_by_category = TransactionService.get_expenses_by_category(chat_id)
    
    if not expenses_by_category:
        return None
    
    categories = [item[0] for item in expenses_by_category]
    amounts = [item[1] for item in expenses_by_category]
    
    # Create the pie chart
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title("Gastos por Categoría")
    
    # Save to BytesIO
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return buf


def generate_income_expense_bar_chart(chat_id: int, days: int = 7) -> io.BytesIO:
    """Generate a bar chart comparing income vs expenses for the last X days."""
    # Get income vs expense data
    data = TransactionService.get_income_vs_expense_by_day(chat_id, days)
    
    if not data:
        return None
    
    # Process data to separate dates, income, and expenses
    date_map = {}
    for date_str, type_str, amount in data:
        if date_str not in date_map:
            date_map[date_str] = {'income': 0, 'expense': 0}
        if type_str == 'income':
            date_map[date_str]['income'] = amount
        else:
            date_map[date_str]['expense'] = amount
    
    dates = sorted(date_map.keys())
    income_vals = [date_map[date]['income'] for date in dates]
    expense_vals = [date_map[date]['expense'] for date in dates]
    
    # Create the bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Set positions and width for bars
    x = range(len(dates))
    width = 0.35
    
    # Create bars
    ax.bar([i - width/2 for i in x], income_vals, width, label='Ingresos', color='g')
    ax.bar([i + width/2 for i in x], expense_vals, width, label='Gastos', color='r')
    
    # Add labels and title
    ax.set_ylabel('Monto')
    ax.set_title(f'Ingresos vs. Gastos - Últimos {days} días')
    ax.set_xticks(x)
    ax.set_xticklabels([datetime.fromisoformat(d).strftime('%d/%m') for d in dates], rotation=45)
    ax.legend()
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Save to BytesIO
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return buf


def generate_monthly_trend_chart(chat_id: int) -> io.BytesIO:
    """Generate a line chart showing monthly income and expense trends."""
    # Get all transactions for the chat
    transactions = TransactionService.get_transactions_by_chat_id(chat_id)
    
    if not transactions:
        return None
    
    # Group transactions by month
    monthly_data = {}
    for transaction in transactions:
        month_key = transaction.date.strftime('%Y-%m')
        if month_key not in monthly_data:
            monthly_data[month_key] = {'income': 0, 'expense': 0}
        
        if transaction.type.lower() == 'income':
            monthly_data[month_key]['income'] += transaction.amount
        else:
            monthly_data[month_key]['expense'] += transaction.amount
    
    # Sort and prepare data for plotting
    sorted_months = sorted(monthly_data.keys())
    months = [datetime.strptime(m, '%Y-%m').strftime('%m/%y') for m in sorted_months]
    income_values = [monthly_data[m]['income'] for m in sorted_months]
    expense_values = [monthly_data[m]['expense'] for m in sorted_months]
    
    # Create the line chart
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.plot(months, income_values, label='Ingresos', marker='o', color='g')
    ax.plot(months, expense_values, label='Gastos', marker='o', color='r')
    
    # Add labels and title
    ax.set_ylabel('Monto')
    ax.set_title('Tendencia Mensual de Ingresos y Gastos')
    plt.xticks(rotation=45)
    ax.legend()
    
    # Adjust layout
    plt.tight_layout()
    
    # Save to BytesIO
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)
    
    return buf