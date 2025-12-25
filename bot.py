import os
import PyPDF2
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import time
# Bot token received from BotFather
TOKEN = '7760848974:AAGBdFxeyv20zZuY5tC52e_myAUkhIsNUdU'

# Function to check if the password works for the PDF
def try_password(pdf_path, password):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        if pdf_reader.decrypt(password):
            return True
    return False

# Function for brute force cracking
def brute_force_crack(pdf_path):
    for i in range(10000):  # Iterate from 0000 to 9999
        password = f"{i:04d}"  # Format as a 4-digit number (e.g., "0001", "0012", ..., "9999")
        if try_password(pdf_path, password):
            return password
    return None

# Handler for /start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome to Cracker! Please upload your password-protected PDF file and I will try to crack the password using brute-force from 0000 to 9999.")

# Handler for /help command (if you'd like to add help)
def help_command(update: Update, context: CallbackContext):
    update.message.reply_text("Send me a password-protected PDF file, and I will attempt to crack it using brute-force. It will try all 4-digit combinations from 0000 to 9999.")

# Handler for file upload
def handle_file(update: Update, context: CallbackContext):
    file = update.message.document
    if file.mime_type == 'application/pdf':
        # Download the file
        file_path = file.get_file().download()
        update.message.reply_text("File received! Starting the password cracking process... Please wait.")

        # Perform brute-force cracking
        password = brute_force_crack(file_path)

        # Notify the user with the result
        if password:
            update.message.reply_text(f"Password found: {password}")
        else:
            update.message.reply_text("Sorry, I couldn't find the password.")
        
        # Clean up the file after processing
        os.remove(file_path)
    else:
        update.message.reply_text("Please upload a valid PDF file.")

# Function to handle errors
def error(update: Update, context: CallbackContext):
    print(f"Error: {context.error}")

# Main function to run the bot
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add handlers for commands and messages
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('help', help_command))
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type('application/pdf'), handle_file))
    dispatcher.add_error_handler(error)

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
