"""Chart command handlers."""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from bot.charts import generate_expense_pie_chart, generate_income_expense_bar_chart, generate_monthly_trend_chart

logger = logging.getLogger(__name__)


async def chart_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /grafico command."""
    chat_id = update.effective_chat.id
    
    # Check if there are arguments to specify the type of chart
    if context.args:
        chart_type = context.args[0].lower()
    else:
        chart_type = 'all'  # default to show all charts
    
    if chart_type == 'gastos' or chart_type == 'expenses':
        await _send_expense_pie_chart(update, context)
    elif chart_type == 'ingresos' or chart_type == 'income':
        await _send_income_expense_chart(update, context, days=7)
    elif chart_type == 'tendencia' or chart_type == 'trend':
        await _send_monthly_trend_chart(update, context)
    elif chart_type == 'todo' or chart_type == 'all':
        await _send_all_charts(update, context)
    else:
        # Show all charts by default
        await _send_all_charts(update, context)


async def _send_expense_pie_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send expense pie chart."""
    chat_id = update.effective_chat.id
    
    chart_data = generate_expense_pie_chart(chat_id)
    
    if chart_data:
        await update.message.reply_photo(
            photo=chart_data,
            caption="📊 Distribución de Gastos por Categoría"
        )
    else:
        await update.message.reply_text(
            "❌ No hay datos suficientes para generar el gráfico de gastos por categoría."
        )


async def _send_income_expense_chart(update: Update, context: ContextTypes.DEFAULT_TYPE, days: int = 7):
    """Send income vs expense bar chart."""
    chat_id = update.effective_chat.id
    
    chart_data = generate_income_expense_bar_chart(chat_id, days)
    
    if chart_data:
        await update.message.reply_photo(
            photo=chart_data,
            caption=f"📊 Ingresos vs. Gastos (Últimos {days} días)"
        )
    else:
        await update.message.reply_text(
            f"❌ No hay datos suficientes para generar el gráfico de ingresos vs. gastos."
        )


async def _send_monthly_trend_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send monthly trend chart."""
    chat_id = update.effective_chat.id
    
    chart_data = generate_monthly_trend_chart(chat_id)
    
    if chart_data:
        await update.message.reply_photo(
            photo=chart_data,
            caption="📊 Tendencia Mensual de Ingresos y Gastos"
        )
    else:
        await update.message.reply_text(
            "❌ No hay datos suficientes para generar el gráfico de tendencia mensual."
        )


async def _send_all_charts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send all available charts."""
    chat_id = update.effective_chat.id
    
    # Send expense pie chart
    chart_data = generate_expense_pie_chart(chat_id)
    if chart_data:
        await update.message.reply_photo(
            photo=chart_data,
            caption="📊 Distribución de Gastos por Categoría"
        )
    else:
        await update.message.reply_text(
            "❌ No hay datos suficientes para generar el gráfico de gastos por categoría."
        )
    
    # Send income vs expense chart
    chart_data = generate_income_expense_bar_chart(chat_id)
    if chart_data:
        await update.message.reply_photo(
            photo=chart_data,
            caption="📊 Ingresos vs. Gastos (Últimos 7 días)"
        )
    else:
        await update.message.reply_text(
            "❌ No hay datos suficientes para generar el gráfico de ingresos vs. gastos."
        )
    
    # Send monthly trend chart
    chart_data = generate_monthly_trend_chart(chat_id)
    if chart_data:
        await update.message.reply_photo(
            photo=chart_data,
            caption="📊 Tendencia Mensual de Ingresos y Gastos"
        )
    else:
        await update.message.reply_text(
            "❌ No hay datos suficientes para generar el gráfico de tendencia mensual."
        )