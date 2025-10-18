"""Reminder system for the bot."""
import logging
from datetime import datetime, time
from typing import Dict
from telegram import Update
from telegram.ext import ContextTypes, JobQueue

from bot.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)


class ReminderManager:
    """Manages automated reminders for the bot."""
    
    def __init__(self, job_queue: JobQueue):
        self.job_queue = job_queue
        self.reminder_jobs: Dict[int, list] = {}  # chat_id -> list of job objects
    
    def schedule_daily_reminder(self, chat_id: int, hour: int = 18, minute: int = 0):
        """Schedule a daily reminder for a chat."""
        # Remove existing jobs for this chat
        self.remove_chat_reminders(chat_id)
        
        # Create a new job
        job = self.job_queue.run_daily(
            self._send_daily_reminder,
            time(hour=hour, minute=minute),
            chat_id=chat_id,
            name=f"daily_reminder_{chat_id}"
        )
        
        # Store the job reference
        if chat_id not in self.reminder_jobs:
            self.reminder_jobs[chat_id] = []
        self.reminder_jobs[chat_id].append(job)
        
        logger.info(f"Scheduled daily reminder for chat {chat_id} at {hour}:{minute:02d}")
    
    def schedule_budget_notifications(self, chat_id: int, hour: int = 20, minute: int = 0):
        """Schedule a daily budget notification for a chat."""
        # Remove existing budget notification jobs for this chat
        self.remove_budget_notifications(chat_id)
        
        # Create a new job
        job = self.job_queue.run_daily(
            self._send_budget_notification,
            time(hour=hour, minute=minute),
            chat_id=chat_id,
            name=f"budget_notification_{chat_id}"
        )
        
        # Store the job reference with a different key
        if chat_id not in self.reminder_jobs:
            self.reminder_jobs[chat_id] = []
        self.reminder_jobs[chat_id].append(job)
        
        logger.info(f"Scheduled budget notification for chat {chat_id} at {hour}:{minute:02d}")
    
    def remove_chat_reminders(self, chat_id: int):
        """Remove all reminders for a specific chat."""
        if chat_id in self.reminder_jobs:
            for job in self.reminder_jobs[chat_id]:
                if not job.removed:
                    job.schedule_removal()
            del self.reminder_jobs[chat_id]
    
    def remove_budget_notifications(self, chat_id: int):
        """Remove budget notifications for a specific chat (if we differentiate them)."""
        # For now, we'll just remove all jobs for this chat
        self.remove_chat_reminders(chat_id)
    
    async def _send_daily_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        """Send a daily reminder to record expenses."""
        chat_id = context.job.chat_id
        
        try:
            # Check if the user has any transactions today
            today_summary = TransactionService.get_daily_summary(chat_id, datetime.now())
            
            if today_summary.total_expense == 0 and today_summary.total_income == 0:
                # No transactions today, send reminder
                message = (
                    "⏰ Recordatorio diario:\n\n"
                    "No has registrado ningún movimiento hoy. "
                    "¿Quieres registrar un gasto o ingreso?"
                )
            elif today_summary.total_expense == 0:
                # Has income but no expenses, remind about expenses
                message = (
                    "⏰ Recordatorio diario:\n\n"
                    f"Hoy has registrado ${today_summary.total_income:,.2f} de ingresos, "
                    "¿Has registrado tus gastos de hoy?"
                )
            else:
                # Has expenses, send friendly reminder
                message = (
                    "⏰ Recordatorio diario:\n\n"
                    f"Hoy has gastado ${today_summary.total_expense:,.2f}. "
                    "¿Quieres registrar algún otro movimiento?"
                )
            
            await context.bot.send_message(chat_id=chat_id, text=message)
            
        except Exception as e:
            logger.error(f"Error sending daily reminder to {chat_id}: {e}")
    
    async def _send_budget_notification(self, context: ContextTypes.DEFAULT_TYPE):
        """Send a daily budget status notification."""
        chat_id = context.job.chat_id
        
        try:
            # Get budget status
            budgets_status = TransactionService.get_budget_status(chat_id)
            
            if not budgets_status:
                # No budgets set, suggest setting one
                message = (
                    "📊 Recordatorio de presupuesto:\n\n"
                    "No tienes presupuestos establecidos. "
                    "Considera crear uno con /presupuesto para controlar tus gastos."
                )
            else:
                # Check for any exceeded budgets
                exceeded_budgets = [(budget, spent, exceeded) for budget, spent, exceeded in budgets_status if exceeded]
                approaching_budgets = [
                    (budget, spent, exceeded) 
                    for budget, spent, exceeded in budgets_status 
                    if not exceeded and (spent / budget.limit) >= 0.8
                ]
                
                messages = []
                
                if exceeded_budgets:
                    messages.append("🚨 <b>Presupuestos Excedidos:</b>")
                    for budget, spent, _ in exceeded_budgets:
                        messages.append(
                            f"  • {budget.category.capitalize()}: "
                            f"Excedido por ${(spent - budget.limit):,.2f} "
                            f"(${spent:,.2f} de ${budget.limit:,.2f})"
                        )
                
                if approaching_budgets:
                    messages.append("\n⚠️ <b>Presupuestos Cerca del Límite:</b>")
                    for budget, spent, _ in approaching_budgets:
                        messages.append(
                            f"  • {budget.category.capitalize()}: "
                            f"{(spent / budget.limit) * 100:.1f}% utilizado "
                            f"(${spent:,.2f} de ${budget.limit:,.2f})"
                        )
                
                if not exceeded_budgets and not approaching_budgets:
                    messages.append("✅ Todos los presupuestos están dentro de los límites.")
                
                message = "📊 <b>Estado de Presupuestos</b>\n\n" + "\n".join(messages)
            
            await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')
            
        except Exception as e:
            logger.error(f"Error sending budget notification to {chat_id}: {e}")