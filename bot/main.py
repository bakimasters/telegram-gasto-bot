"""Main application entry point for the expense bot."""
import logging
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)

# Import handlers
from bot.handlers.start_handler import start_handler, help_handler
from bot.handlers.transaction_handlers import (
    income_handler, expense_handler, balance_handler,
    enter_amount, select_category, enter_custom_category,
    confirm_transaction, cancel_transaction
)
from bot.handlers.summary_handlers import summary_handler
from bot.handlers.export_handlers import export_csv_handler, export_xlsx_handler
from bot.handlers.chart_handlers import chart_handler
from bot.handlers.budget_handlers import (
    budget_handler, budgets_list_handler,
    enter_budget_amount, enter_budget_category,
    select_budget_period, confirm_budget, cancel_budget
)
from bot.services.reminder_service import ReminderManager
from config.settings import TELEGRAM_TOKEN

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
ENTERING_AMOUNT, SELECTING_CATEGORY, CONFIRMING_TRANSACTION = range(3)
ENTERING_BUDGET_AMOUNT, SELECTING_BUDGET_PERIOD, CONFIRMING_BUDGET = range(3, 6)


def create_application():
    """Create and configure the Telegram bot application."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Initialize reminder manager
    reminder_manager = ReminderManager(application.job_queue)
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(CommandHandler("ingreso", income_handler))
    application.add_handler(CommandHandler("gasto", expense_handler))
    application.add_handler(CommandHandler("balance", balance_handler))
    application.add_handler(CommandHandler("resumen", summary_handler))
    application.add_handler(CommandHandler("exportar", export_csv_handler))
    application.add_handler(CommandHandler("grafico", chart_handler))
    application.add_handler(CommandHandler("presupuesto", budget_handler))
    application.add_handler(CommandHandler("presupuestos", budgets_list_handler))
    
    # Add conversation handler for transactions
    transaction_conv_handler = ConversationHandler(
        entry_points=[
            # Commands that start the conversation would go here
            # For now, we handle commands directly
        ],
        states={
            ENTERING_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_amount)
            ],
            SELECTING_CATEGORY: [
                CallbackQueryHandler(select_category, pattern=r'^cat:'),
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_custom_category)
            ],
            CONFIRMING_TRANSACTION: [
                CallbackQueryHandler(confirm_transaction, pattern=r'^confirm:'),
                CallbackQueryHandler(cancel_transaction, pattern=r'^cancel:')
            ]
        },
        fallbacks=[
            # Add fallback handlers if needed
        ]
    )
    
    # Add conversation handler for budgets
    budget_conv_handler = ConversationHandler(
        entry_points=[
            # Commands that start the budget conversation would go here
        ],
        states={
            ENTERING_BUDGET_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_budget_amount)
            ],
            SELECTING_BUDGET_PERIOD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_budget_category),
            ],
            CONFIRMING_BUDGET: [
                CallbackQueryHandler(select_budget_period, pattern=r'^period:'),
                CallbackQueryHandler(confirm_budget, pattern=r'^confirm:'),
                CallbackQueryHandler(cancel_budget, pattern=r'^cancel:')
            ]
        },
        fallbacks=[
            # Add fallback handlers if needed
        ]
    )
    
    # Add the conversation handlers
    application.add_handler(transaction_conv_handler)
    application.add_handler(budget_conv_handler)
    
    # Add message handler for text messages (for direct transaction entry)
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text_message
        )
    )
    
    # Add callback query handler for inline keyboards
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Schedule daily reminders for all users (this would typically be done per user when they start)
    # For now, we'll just set up the reminder manager
    
    return application, reminder_manager


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages that might be transactions."""
    text = update.message.text.strip().lower()
    chat_id = update.effective_chat.id
    
    # Check if message is in the format "gasto 50.00 comida" or "ingreso 100.00 salario"
    parts = text.split()
    if len(parts) >= 3 and parts[0] in ['gasto', 'ingreso', 'expense', 'income']:
        transaction_type = 'expense' if parts[0] in ['gasto', 'expense'] else 'income'
        try:
            # Extract amount (last part) and category (everything in between)
            amount_str = parts[-1].replace(',', '.')
            category = ' '.join(parts[1:-1])
            
            amount = float(amount_str)
            
            # Import here to avoid circular imports
            from bot.services.transaction_service import TransactionService
            from bot.utils.validators import validate_amount, validate_category
            
            if not validate_amount(amount):
                await update.message.reply_text("❌ Monto inválido. Debe ser un número positivo.")
                return
            
            if not validate_category(category):
                await update.message.reply_text("❌ Categoría inválida.")
                return
            
            # Add the transaction
            transaction = TransactionService.add_transaction(
                chat_id=chat_id,
                type=transaction_type,
                category=category,
                amount=amount
            )
            
            transaction_name = "Gasto" if transaction_type == 'expense' else "Ingreso"
            await update.message.reply_text(
                f"✅ ¡{transaction_name} de ${amount:,.2f} en '{category.capitalize()}' registrado correctamente!"
            )
            
        except ValueError:
            await update.message.reply_text(
                "❌ Por favor, usa el formato: gasto/ingreso [monto] [categoría]"
            )
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            await update.message.reply_text("❌ Ocurrió un error al procesar el movimiento.")
    else:
        await update.message.reply_text(
            "❌ Formato no reconocido. Usa: gasto/ingreso [monto] [categoría]\n"
            "O usa los comandos /gasto o /ingreso"
        )


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle callback queries from inline keyboards."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    # Route to appropriate handler based on callback data
    if data.startswith('cat:'):
        await select_category(update, context)
    elif data.startswith('period:'):
        await select_budget_period(update, context)
    elif data.startswith('confirm:'):
        # Determine if this is for budget creation or transaction
        parts = data.split(':', 2)
        if len(parts) >= 2:
            action = parts[1]
            if action.startswith('budget'):
                await confirm_budget(update, context)
            else:
                await confirm_transaction(update, context)
    elif data.startswith('cancel:'):
        # Determine if this is for budget or transaction
        if 'budget' in data:
            await cancel_budget(update, context)
        else:
            await cancel_transaction(update, context)
    else:
        # Handle other callback queries
        await query.edit_message_text(text=f"Callback received: {data}")


def main():
    """Run the bot."""
    logger.info("Starting expense bot...")
    
    application, reminder_manager = create_application()
    
    # Run the bot until Ctrl-C is pressed
    application.run_polling()
    
    logger.info("Expense bot stopped.")


if __name__ == '__main__':
    main()