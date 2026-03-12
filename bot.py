import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from gemini_parser import parse_ticket_image, parse_ticket_text
from notion_client_helper import save_ticket

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 Recibí tu ticket, procesando...")
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_bytes = await file.download_as_bytearray()
    ticket_data = await parse_ticket_image(bytes(image_bytes))
    if ticket_data:
        await save_ticket(ticket_data)
        await update.message.reply_text(
            f"✅ Gasto registrado!\n"
            f"🏪 {ticket_data['tienda']}\n"
            f"💰 {ticket_data['moneda']} {ticket_data['total']}\n"
            f"📅 {ticket_data['fecha']}"
        )
    else:
        await update.message.reply_text("❌ No pude leer el ticket, intentá con otra foto.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    await update.message.reply_text("📝 Procesando tu gasto...")
    ticket_data = await parse_ticket_text(text)
    if ticket_data:
        await save_ticket(ticket_data)
        await update.message.reply_text(
            f"✅ Gasto registrado!\n"
            f"🏪 {ticket_data['tienda']}\n"
            f"💰 {ticket_data['moneda']} {ticket_data['total']}\n"
            f"📅 {ticket_data['fecha']}"
        )
    else:
        await update.message.reply_text("❌ No entendí el gasto, intentá de nuevo.")

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("🤖 Bot corriendo...")
    app.run_polling()

if __name__ == "__main__":
    main()