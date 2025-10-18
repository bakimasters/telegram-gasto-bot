"""Budget command handlers."""
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.services.transaction_service import BudgetService
from bot.ui.keyboards import get_budget_period_keyboard, get_confirmation_keyboard
from bot.utils.validators import validate_amount, validate_category, validate_budget_period
from bot.utils.constants import BUDGET_PERIODS, DEFAULT_BUDGET_LIMITS

logger = logging.getLogger(__name__)

# Conversation states
ENTERING_BUDGET_AMOUNT, SELECTING_BUDGET_PERIOD, CONFIRMING_BUDGET = range(3)


async def budget_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /presupuesto command."""
    chat_id = update.effective_chat.id
    
    if context.args:
        # Handle command with arguments: /presupuesto comida 500.0 mensual
        if len(context.args) >= 3:
            category = context.args[0].lower()
            try:
                amount = float(context.args[1])
                period = context.args[2].lower()
                
                # Validate inputs
                if not validate_category(category):
                    await update.message.reply_text("❌ Categoría inválida.")
                    return
                
                if not validate_amount(amount):
                    await update.message.reply_text("❌ Monto inválido. Debe ser un número positivo.")
                    return
                
                if not validate_budget_period(period):
                    await update.message.reply_text(f"❌ Período inválido. Usa uno de: {', '.join(BUDGET_PERIODS)}")
                    return
                
                # Add the budget
                budget = BudgetService.add_budget(chat_id, category, amount, period)
                
                await update.message.reply_text(
                    f"✅ ¡Presupuesto establecido para '{category.capitalize()}'!\n"
                    f"• Límite: ${amount:,.2f} por {period}\n"
                    f"• Actualmente gastado: $0.00"
                )
                
            except ValueError:
                await update.message.reply_text(
                    "❌ Por favor, usa el formato: /presupuesto [categoría] [monto] [periodo]\n"
                    f"Períodos válidos: {', '.join(BUDGET_PERIODS)}"
                )
        else:
            await update.message.reply_text(
                "❌ Por favor, usa el formato: /presupuesto [categoría] [monto] [periodo]\n"
                f"Períodos válidos: {', '.join(BUDGET_PERIODS)}"
            )
    else:
        # Start conversation to create budget
        await update.message.reply_text(
            "💰 Para crear un presupuesto, por favor dime:\n"
            "1. La categoría (por ejemplo: comida)\n"
            "2. El monto máximo\n"
            "3. El período (diario, semanal, mensual)"
        )
        return ENTERING_BUDGET_AMOUNT


async def budgets_list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /presupuestos command to list all budgets."""
    chat_id = update.effective_chat.id
    
    # Get all budgets and their status
    budgets_status = BudgetService.get_budget_status(chat_id)
    
    if not budgets_status:
        await update.message.reply_text("❌ No tienes presupuestos establecidos.")
        return
    
    message = "📝 <b>Presupuestos Establecidos</b>\n\n"
    
    for budget, current_spending, is_exceeded in budgets_status:
        status_emoji = "⚠️" if is_exceeded else "✅"
        status_text = " (EXCEDIDO)" if is_exceeded else ""
        
        message += (
            f"{status_emoji} <b>{budget.category.capitalize()}</b>{status_text}\n"
            f"   Límite: ${budget.limit:,.2f} por {budget.period}\n"
            f"   Gastado: ${current_spending:,.2f}\n"
            f"   Restante: ${max(0, budget.limit - current_spending):,.2f}\n\n"
        )
    
    await update.message.reply_text(message, parse_mode='HTML')


async def enter_budget_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle entering budget amount during conversation."""
    message = update.message.text.strip()
    
    try:
        amount = float(message.replace(',', '.'))
        
        if not validate_amount(amount):
            await update.message.reply_text("❌ Monto inválido. Debe ser un número positivo.")
            return ENTERING_BUDGET_AMOUNT
        
        # Store amount in context
        context.user_data['temp_budget_amount'] = amount
        
        # Ask for category
        await update.message.reply_text(
            f"💰 Monto del presupuesto: ${amount:,.2f}\n\n"
            "Ahora, por favor dime la categoría para este presupuesto:"
        )
        
        return SELECTING_BUDGET_PERIOD  # We'll use this state to get the category
        
    except ValueError:
        await update.message.reply_text("❌ Por favor, ingresa un número válido para el monto:")
        return ENTERING_BUDGET_AMOUNT


async def enter_budget_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle entering budget category during conversation."""
    category = update.message.text.strip().lower()
    
    if not validate_category(category):
        await update.message.reply_text("❌ Categoría inválida. Por favor, ingresa una categoría válida:")
        return SELECTING_BUDGET_PERIOD
    
    # Store category in context
    context.user_data['temp_budget_category'] = category
    
    # Ask for budget period
    await update.message.reply_text(
        f"Categoría: {category.capitalize()}\n"
        f"Monto: ${context.user_data['temp_budget_amount']:,.2f}\n\n"
        f"Selecciona el período para este presupuesto:",
        reply_markup=get_budget_period_keyboard()
    )
    
    return CONFIRMING_BUDGET


async def select_budget_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle budget period selection."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith('period:'):
        period = data.split(':', 1)[1]
        
        # Store period in context
        context.user_data['temp_budget_period'] = period
        
        # Confirm budget
        amount = context.user_data['temp_budget_amount']
        category = context.user_data['temp_budget_category']
        
        await query.edit_message_text(
            f"Confirmar presupuesto:\n"
            f"• Categoría: {category.capitalize()}\n"
            f"• Límite: ${amount:,.2f}\n"
            f"• Período: {period}\n\n"
            f"¿Es correcto?",
            reply_markup=get_confirmation_keyboard(f"budget_create", f"{category}:{amount}:{period}")
        )


async def confirm_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle budget confirmation."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    chat_id = query.effective_chat.id
    
    if data.startswith('confirm:'):
        parts = data.split(':', 2)
        if len(parts) >= 3:
            action, budget_data = parts[1], parts[2]
            
            if action == 'budget_create':
                try:
                    category, amount_str, period = budget_data.split(':', 2)
                    amount = float(amount_str)
                    
                    # Add the budget
                    budget = BudgetService.add_budget(chat_id, category, amount, period)
                    
                    await query.edit_message_text(
                        f"✅ ¡Presupuesto establecido para '{category.capitalize()}'!\n"
                        f"• Límite: ${amount:,.2f} por {period}\n"
                        f"• Actualmente gastado: $0.00"
                    )
                    
                    # Clear user data
                    context.user_data.pop('temp_budget_amount', None)
                    context.user_data.pop('temp_budget_category', None)
                    context.user_data.pop('temp_budget_period', None)
                    
                    return ConversationHandler.END
                except (ValueError, IndexError):
                    await query.edit_message_text("❌ Error al procesar el presupuesto.")
                    return ConversationHandler.END
    
    elif data.startswith('cancel:'):
        await query.edit_message_text("❌ Operación cancelada.")
        return ConversationHandler.END


async def cancel_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the budget creation process."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("❌ Operación cancelada.")
    return ConversationHandler.END