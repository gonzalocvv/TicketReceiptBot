import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from ai_parser import parse_ticket_image, parse_ticket_text, parse_ingreso_text
from notion_client_helper import save_ticket, save_ingreso

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
    caption = update.message.caption or ""
    result = await parse_ticket_image(bytes(image_bytes), caption)
    if result:
        await save_ticket(result["data"])
        msg = f"✅ Gasto registrado!\n🏪 {result['data']['tienda']}\n💰 {result['data']['moneda']} {result['data']['total']}\n📅 {result['data']['fecha']}"
        if result.get("aproximado"):
            msg += "\n⚠️ Se usó un valor aproximado"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("❌ No pude leer el ticket, intentá con otra foto.")

        
async def handle_gasto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("📝 Usá: /gasto <descripción>\nEjemplo: /gasto almacén Don Jorge $350 hoy")
        return
    await update.message.reply_text("📝 Procesando tu gasto...")
    result = await parse_ticket_text(text)
    if result:
        await save_ticket(result["data"])
        msg = f"✅ Gasto registrado!\n🏪 {result['data']['tienda']}\n💰 {result['data']['moneda']} {result['data']['total']}\n📅 {result['data']['fecha']}"
        if result.get("aproximado"):
            msg += "\n⚠️ Se usó un valor aproximado"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("❌ No entendí el gasto, intentá de nuevo.")

async def handle_ingreso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("💰 Usá: /ingreso <descripción>\nEjemplo: /ingreso mensualidad de papá $5000")
        return
    await update.message.reply_text("💰 Procesando tu ingreso...")
    result = await parse_ingreso_text(text)
    if result:
        await save_ingreso(result["data"])
        msg = f"✅ Ingreso registrado!\n📋 {result['data']['concepto']}\n💰 {result['data']['moneda']} {result['data']['monto']}\n📅 {result['data']['fecha']}"
        if result.get("aproximado"):
            msg += "\n⚠️ Se usó un valor aproximado"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("❌ No entendí el ingreso, intentá de nuevo.")

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    app = Application.builder().token(token).build()
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CommandHandler("gasto", handle_gasto))
    app.add_handler(CommandHandler("ingreso", handle_ingreso))
    print("🤖 Bot corriendo...")
    app.run_polling()

if __name__ == "__main__":
    main()