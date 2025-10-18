"""Summary command handlers."""
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes

from bot.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)


async def summary_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /resumen command."""
    chat_id = update.effective_chat.id
    
    # Check if there are arguments for the summary period
    if context.args:
        period = context.args[0].lower()
    else:
        period = 'today'  # default to today
    
    if period == 'hoy' or period == 'today':
        await _send_daily_summary(update, context)
    elif period == 'semana' or period == 'week':
        await _send_weekly_summary(update, context)
    elif period == 'mes' or period == 'month':
        await _send_monthly_summary(update, context)
    elif period == 'total':
        await _send_total_summary(update, context)
    else:
        await update.message.reply_text(
            "❌ Período inválido. Usa: /resumen [hoy|semana|mes|total]"
        )


async def _send_daily_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send daily summary."""
    chat_id = update.effective_chat.id
    date = datetime.now()
    
    summary = TransactionService.get_daily_summary(chat_id, date)
    
    await update.message.reply_text(
        f"📊 <b>Resumen de Hoy</b> ({date.strftime('%d/%m/%Y')})\n\n"
        f"🟢 Ingresos: <code>${summary.total_income:,.2f}</code>\n"
        f"🔴 Gastos: <code>${summary.total_expense:,.2f}</code>\n"
        f"💰 Balance: <code>${summary.balance:,.2f}</code>",
        parse_mode='HTML'
    )


async def _send_weekly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send weekly summary."""
    chat_id = update.effective_chat.id
    
    summary = TransactionService.get_weekly_summary(chat_id)
    
    # Format dates for display
    start_date = summary.period_start.strftime('%d/%m/%Y')
    end_date = summary.period_end.strftime('%d/%m/%Y')
    
    await update.message.reply_text(
        f"📅 <b>Resumen Semanal</b> ({start_date} - {end_date})\n\n"
        f"🟢 Ingresos: <code>${summary.total_income:,.2f}</code>\n"
        f"🔴 Gastos: <code>${summary.total_expense:,.2f}</code>\n"
        f"💰 Balance: <code>${summary.balance:,.2f}</code>",
        parse_mode='HTML'
    )


async def _send_monthly_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send monthly summary."""
    chat_id = update.effective_chat.id
    
    summary = TransactionService.get_monthly_summary(chat_id)
    
    # Format dates for display
    start_date = summary.period_start.strftime('%d/%m/%Y')
    end_date = summary.period_end.strftime('%d/%m/%Y')
    
    await update.message.reply_text(
        f"🗓️ <b>Resumen Mensual</b> ({start_date} - {end_date})\n\n"
        f"🟢 Ingresos: <code>${summary.total_income:,.2f}</code>\n"
        f"🔴 Gastos: <code>${summary.total_expense:,.2f}</code>\n"
        f"💰 Balance: <code>${summary.balance:,.2f}</code>",
        parse_mode='HTML'
    )


async def _send_total_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send total summary."""
    chat_id = update.effective_chat.id
    
    # Get all transactions to calculate total summary
    transactions = TransactionService.get_transactions_by_chat_id(chat_id)
    
    total_income = sum(t.amount for t in transactions if t.type.lower() == 'income')
    total_expense = sum(t.amount for t in transactions if t.type.lower() == 'expense')
    
    await update.message.reply_text(
        f"📈 <b>Resumen Total</b>\n\n"
        f"🟢 Ingresos totales: <code>${total_income:,.2f}</code>\n"
        f"🔴 Gastos totales: <code>${total_expense:,.2f}</code>\n"
        f"💰 Balance total: <code>${total_income - total_expense:,.2f}</code>",
        parse_mode='HTML'
    )