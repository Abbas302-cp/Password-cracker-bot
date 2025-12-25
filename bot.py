import os
import threading
import PyPDF2
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# ====== BOT TOKEN ======
TOKEN = os.getenv("7760848974:AAGBdFxeyv20zZuY5tC52e_myAUkhIsNUdU")
if not TOKEN:
    raise RuntimeError("BOT TOKEN not set")

# ====== PDF PASSWORD CHECK ======
def try_password(pdf_path, password):
    try:
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfFileReader(f)
            return reader.decrypt(password)
    except:
        return False

# ====== BACKGROUND CRACKING (THREAD) ======
def crack_pdf_background(update: Update, context: CallbackContext, pdf_path: str):
    chat_id = update.effective_chat.id

    for i in range(10000):
        password = f"{i:04d}"

        if try_password(pdf_path, password):
            context.bot.send_message(
                chat_id=chat_id,
                text=f"✅ Password found: {password}"
            )
            os.remove(pdf_path)
            return

        # progress update every 500 tries
        if i % 500 == 0:
            context.bot.send_message(
                chat_id=chat_id,
                text=f"🔄 Trying: {password}"
            )

    context.bot.send_message(
        chat_id=chat_id,
        text="❌ Password not found (0000–9999)"
    )
    os.remove(pdf_path)

# ====== COMMANDS ======
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🔐 Welcome to PDF Cracker Bot\n\n"
        "📄 Send a password-protected PDF\n"
        "🔢 I will try passwords from 0000 to 9999\n\n"
        "⚠️ Educational use only"
    )

# ====== FILE HANDLER ======
def handle_pdf(update: Update, context: CallbackContext):
    document = update.message.document

    if document.mime_type != "application/pdf":
        update.message.reply_text("❌ Please send a PDF file only")
        return

    file = document.get_file()
    pdf_path = "target.pdf"
    file.download(pdf_path)

    update.message.reply_text("🚀 Cracking started… please wait")

    # start cracking in background thread
    t = threading.Thread(
        target=crack_pdf_background,
        args=(update, context, pdf_path),
        daemon=True
    )
    t.start()

# ====== MAIN ======
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.document, handle_pdf))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
