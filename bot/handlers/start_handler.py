"""Start and help command handlers."""
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from bot.ui.keyboards import get_main_menu_keyboard
from bot.utils.constants import DEFAULT_CATEGORIES

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    chat_id = update.effective_chat.id
    
    # Send welcome message with main menu
    welcome_message = (
        "¡Hola! 👋 Bienvenido a tu bot de control de gastos personal.\n\n"
        "Con este bot podrás:\n"
        "• Registrar ingresos y gastos\n"
        "• Consultar balances y resúmenes\n"
        "• Generar gráficos de finanzas\n"
        "• Establecer presupuestos por categoría\n"
        "• Recibir recordatorios de gasto\n\n"
        "Selecciona una opción del menú o usa los comandos directamente."
    )
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=get_main_menu_keyboard()
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command."""
    help_text = (
        "🤖 <b>Comandos disponibles:</b>\n\n"
        "<b>/start</b> - Iniciar el bot\n"
        "<b>/help</b> - Mostrar este mensaje de ayuda\n"
        "<b>/ingreso</b> [monto] [categoría] - Registrar un ingreso\n"
        "<b>/gasto</b> [monto] [categoría] - Registrar un gasto\n"
        "<b>/balance</b> - Consultar balance total\n"
        "<b>/resumen</b> [día/semana/mes] - Ver resumen de gastos e ingresos\n"
        "<b>/presupuesto</b> [categoría] [monto] [periodo] - Establecer presupuesto\n"
        "<b>/grafico</b> - Generar gráficos de finanzas\n"
        "<b>/exportar</b> - Exportar datos a CSV\n"
        "<b>/borrar</b> [ID] - Eliminar un registro\n\n"
        "<b>Categorías por defecto:</b>\n"
        f"<i>Gastos:</i> {', '.join(DEFAULT_CATEGORIES['expense'])}\n"
        f"<i>Ingresos:</i> {', '.join(DEFAULT_CATEGORIES['income'])}\n\n"
        "Puedes registrar gastos e ingresos directamente con el formato:\n"
        "<i>gasto 50.00 comida</i>\n"
        "<i>ingreso 1000.00 salario</i>"
    )
    
    await update.message.reply_text(help_text, parse_mode='HTML')