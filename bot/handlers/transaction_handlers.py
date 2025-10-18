"""Transaction command handlers."""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from bot.services.transaction_service import TransactionService
from bot.ui.keyboards import get_category_selection_keyboard, get_confirmation_keyboard
from bot.utils.validators import validate_amount, validate_category

logger = logging.getLogger(__name__)

# Conversation states
ENTERING_AMOUNT, SELECTING_CATEGORY, CONFIRMING_TRANSACTION = range(3)


async def income_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /ingreso command."""
    chat_id = update.effective_chat.id
    
    # Check if command has arguments
    if context.args:
        # Handle command with arguments: /ingreso 500 salario
        if len(context.args) >= 2:
            try:
                amount_str = context.args[0]
                category = " ".join(context.args[1:])
                
                if not validate_amount(amount_str):
                    await update.message.reply_text("❌ Monto inválido. Debe ser un número positivo.")
                    return
                
                amount = float(amount_str)
                
                # Validate category
                if not validate_category(category):
                    await update.message.reply_text("❌ Categoría inválida.")
                    return
                
                # Add the transaction
                transaction = TransactionService.add_transaction(
                    chat_id=chat_id,
                    type='income',
                    category=category,
                    amount=amount
                )
                
                await update.message.reply_text(
                    f"✅ ¡Ingreso de ${amount:,.2f} en '{category.capitalize()}' registrado correctamente!"
                )
                
            except ValueError:
                await update.message.reply_text("❌ Por favor, usa el formato: /ingreso [monto] [categoría]")
        else:
            await update.message.reply_text("❌ Por favor, usa el formato: /ingreso [monto] [categoría]")
    else:
        # Start conversation to enter amount
        await update.message.reply_text("💰 Por favor, ingresa el monto del ingreso:")
        return ENTERING_AMOUNT


async def expense_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /gasto command."""
    chat_id = update.effective_chat.id
    
    # Check if command has arguments
    if context.args:
        # Handle command with arguments: /gasto 500 comida
        if len(context.args) >= 2:
            try:
                amount_str = context.args[0]
                category = " ".join(context.args[1:])
                
                if not validate_amount(amount_str):
                    await update.message.reply_text("❌ Monto inválido. Debe ser un número positivo.")
                    return
                
                amount = float(amount_str)
                
                # Validate category
                if not validate_category(category):
                    await update.message.reply_text("❌ Categoría inválida.")
                    return
                
                # Add the transaction
                transaction = TransactionService.add_transaction(
                    chat_id=chat_id,
                    type='expense',
                    category=category,
                    amount=amount
                )
                
                await update.message.reply_text(
                    f"✅ ¡Gasto de ${amount:,.2f} en '{category.capitalize()}' registrado correctamente!"
                )
                
            except ValueError:
                await update.message.reply_text("❌ Por favor, usa el formato: /gasto [monto] [categoría]")
        else:
            await update.message.reply_text("❌ Por favor, usa el formato: /gasto [monto] [categoría]")
    else:
        # Start conversation to enter amount
        await update.message.reply_text("💸 Por favor, ingresa el monto del gasto:")
        return ENTERING_AMOUNT


async def balance_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /balance command."""
    chat_id = update.effective_chat.id
    
    # Get all transactions for the user
    transactions = TransactionService.get_transactions_by_chat_id(chat_id)
    
    total_income = sum(t.amount for t in transactions if t.type.lower() == 'income')
    total_expense = sum(t.amount for t in transactions if t.type.lower() == 'expense')
    balance = total_income - total_expense
    
    await update.message.reply_text(
        f"💰 <b>Balance Total</b>\n\n"
        f"🟢 Ingresos totales: <code>${total_income:,.2f}</code>\n"
        f"🔴 Gastos totales: <code>${total_expense:,.2f}</code>\n"
        f"📊 Balance: <code>${balance:,.2f}</code>",
        parse_mode='HTML'
    )


async def enter_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle entering amount during conversation."""
    message = update.message.text.strip()
    
    try:
        amount = float(message.replace(',', '.'))
        
        if not validate_amount(amount):
            await update.message.reply_text("❌ Monto inválido. Debe ser un número positivo.")
            return ENTERING_AMOUNT
        
        # Store amount in context
        context.user_data['temp_amount'] = amount
        
        # Ask for category
        await update.message.reply_text(
            f"💰 Monto: ${amount:,.2f}\n\n"
            "Selecciona la categoría para este ingreso:",
            reply_markup=get_category_selection_keyboard('income')
        )
        
        return SELECTING_CATEGORY
        
    except ValueError:
        await update.message.reply_text("❌ Por favor, ingresa un número válido para el monto:")
        return ENTERING_AMOUNT


async def select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith('cat:'):
        category = data.split(':', 1)[1]
        
        if category == 'custom':
            # Ask for custom category
            await query.edit_message_text("✍️ Por favor, escribe la categoría:")
            return SELECTING_CATEGORY
        else:
            # Store category in context
            context.user_data['temp_category'] = category
            
            # Confirm transaction
            amount = context.user_data['temp_amount']
            transaction_type = 'income' if 'income' in context.user_data.get('transaction_type', '') else 'expense'
            
            await query.edit_message_text(
                f"Confirmar {transaction_type}:\n"
                f"• Monto: ${amount:,.2f}\n"
                f"• Categoría: {category}\n\n"
                f"¿Es correcto?",
                reply_markup=get_confirmation_keyboard(f"{transaction_type}_transaction", f"{amount}:{category}")
            )
            
            return CONFIRMING_TRANSACTION


async def enter_custom_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle entering custom category."""
    category = update.message.text.strip()
    
    if not validate_category(category):
        await update.message.reply_text("❌ Categoría inválida. Por favor, escribe una categoría válida:")
        return SELECTING_CATEGORY
    
    # Store category in context
    context.user_data['temp_category'] = category
    
    # Confirm transaction
    amount = context.user_data['temp_amount']
    transaction_type = 'income'
    
    await update.message.reply_text(
        f"Confirmar ingreso:\n"
        f"• Monto: ${amount:,.2f}\n"
        f"• Categoría: {category}\n\n"
        f"¿Es correcto?",
        reply_markup=get_confirmation_keyboard(f"{transaction_type}_transaction", f"{amount}:{category}")
    )
    
    return CONFIRMING_TRANSACTION


async def confirm_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle transaction confirmation."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    chat_id = query.effective_chat.id
    
    if data.startswith('confirm:'):
        parts = data.split(':', 2)
        if len(parts) >= 3:
            action, transaction_data = parts[1], parts[2]
            
            if action in ['income_transaction', 'expense_transaction']:
                try:
                    amount_str, category = transaction_data.split(':', 1)
                    amount = float(amount_str)
                    
                    transaction_type = 'income' if 'income' in action else 'expense'
                    
                    # Add the transaction
                    transaction = TransactionService.add_transaction(
                        chat_id=chat_id,
                        type=transaction_type,
                        category=category,
                        amount=amount
                    )
                    
                    await query.edit_message_text(
                        f"✅ ¡{transaction_type.capitalize()} de ${amount:,.2f} en '{category.capitalize()}' registrado correctamente!"
                    )
                    
                    # Clear user data
                    context.user_data.pop('temp_amount', None)
                    context.user_data.pop('temp_category', None)
                    context.user_data.pop('transaction_type', None)
                    
                    return ConversationHandler.END
                except (ValueError, IndexError):
                    await query.edit_message_text("❌ Error al procesar la transacción.")
                    return ConversationHandler.END
    
    elif data.startswith('cancel:'):
        await query.edit_message_text("❌ Operación cancelada.")
        return ConversationHandler.END


async def cancel_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the transaction process."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text("❌ Operación cancelada.")
    return ConversationHandler.END