"""Export command handlers."""
import logging
import io
import csv
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

from bot.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)


async def export_csv_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /exportar command to export transactions to CSV."""
    chat_id = update.effective_chat.id
    
    try:
        # Get all transactions for the user
        transactions = TransactionService.get_transactions_by_chat_id(chat_id)
        
        if not transactions:
            await update.message.reply_text("❌ No tienes transacciones para exportar.")
            return
        
        # Create CSV content
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "ID", "Fecha", "Tipo", "Categoría", "Monto", "Fuente"
        ])
        
        # Write transaction data
        for transaction in transactions:
            writer.writerow([
                transaction.id,
                transaction.date.isoformat(),
                transaction.type,
                transaction.category,
                transaction.amount,
                transaction.source
            ])
        
        # Prepare the CSV file for sending
        output.seek(0)
        csv_bytes = io.BytesIO(output.getvalue().encode('utf-8'))
        csv_bytes.name = f"transacciones_{chat_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        await update.message.reply_document(
            document=csv_bytes,
            caption=f"Archivo CSV con {len(transactions)} transacciones exportadas."
        )
        
        logger.info(f"CSV exported for chat_id {chat_id} with {len(transactions)} transactions")
        
    except Exception as e:
        logger.error(f"Error exporting CSV for chat_id {chat_id}: {e}")
        await update.message.reply_text("❌ Ocurrió un error al exportar las transacciones.")


async def export_xlsx_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle exporting transactions to XLSX format."""
    chat_id = update.effective_chat.id
    
    # Check if openpyxl is installed
    try:
        import openpyxl
    except ImportError:
        await update.message.reply_text(
            "❌ La exportación a XLSX requiere la biblioteca 'openpyxl'. "
            "Por favor, instálala con: pip install openpyxl"
        )
        return
    
    try:
        # Get all transactions for the user
        transactions = TransactionService.get_transactions_by_chat_id(chat_id)
        
        if not transactions:
            await update.message.reply_text("❌ No tienes transacciones para exportar.")
            return
        
        # Create XLSX workbook
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Transacciones"
        
        # Write header
        headers = ["ID", "Fecha", "Tipo", "Categoría", "Monto", "Fuente"]
        sheet.append(headers)
        
        # Write transaction data
        for transaction in transactions:
            sheet.append([
                transaction.id,
                transaction.date.isoformat(),
                transaction.type,
                transaction.category,
                transaction.amount,
                transaction.source
            ])
        
        # Save to BytesIO
        output = io.BytesIO()
        workbook.save(output)
        output.seek(0)
        
        # Prepare the XLSX file for sending
        xlsx_bytes = output
        xlsx_bytes.name = f"transacciones_{chat_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        await update.message.reply_document(
            document=xlsx_bytes,
            caption=f"Archivo XLSX con {len(transactions)} transacciones exportadas."
        )
        
        logger.info(f"XLSX exported for chat_id {chat_id} with {len(transactions)} transactions")
        
    except Exception as e:
        logger.error(f"Error exporting XLSX for chat_id {chat_id}: {e}")
        await update.message.reply_text("❌ Ocurrió un error al exportar las transacciones.")