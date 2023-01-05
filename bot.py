from telegram.ext import (
    Updater,
    MessageHandler,
    CommandHandler,
    Filters,
    CallbackContext,
)
from telegram import Update
import logging
import os
import PyPDF3
import pyttsx3
import pdfplumber
from secret import API_KEY


# https://towardsdatascience.com/how-to-deploy-a-telegram-bot-using-heroku-for-free-9436f89575d2
# https://stackoverflow.com/questions/62445753/how-to-send-pdf-file-back-to-user-using-python-telegram-bot - sending file back to user
# https://stackoverflow.com/questions/31096358/how-do-i-download-a-file-or-photo-that-was-sent-to-my-telegram-bot - downloading file sent to bot

PORT = int(os.environ.get('PORT', 5000))
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

print("Bot Started...")
global newFileName


def start_command(update: Update, context: CallbackContext):
    # Starts the conversation.
    update.message.reply_text("""
Welcome to Jun's PDF to MP3 telegram bot!
To use: 
Send the PDF file that you want to convert. Currently, only files up to 20MB are allowed.
""")


def downloader(update: Update, context: CallbackContext):
    # Receives the document and checks if it is valid
    if update.message.document:
        # Download file
        fileName = update.message.document.file_name
        new_file = update.message.effective_attachment.get_file()
        new_file.download(fileName)

        # Acknowledge file received
        update.message.reply_text(f"{fileName} saved successfully")

        # Convert file from PDF to MP3
        pdfToMp3(fileName)

        # Send the file
        document = open("updated.mp3", "rb")
        print(document)
        context.bot.send_document(chat_id=update.effective_chat.id, document=document)


def message_handler(update: Update, context: CallbackContext):
    """Prompts user when user sends a message."""
    text = "Welcome to the Jun's PDF to MP3 bot! Type /start for more instructions!"
    update.message.reply_text(text)


def error(update: Update, context: CallbackContext):
    print(f"Update {update} caused error {context.error}")
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    text = f"Error {context.error}, text Jun Neng to fix it!"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def main():
    updater = Updater(token=API_KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text, message_handler))
    dp.add_handler(MessageHandler(Filters.attachment, downloader))
    dp.add_handler(CommandHandler("start", start_command))
    dp.add_error_handler(error)
    updater.start_webhook(listen="0.0.0.0",
                          port=int(PORT),
                          url_path=API_KEY)
    updater.bot.setWebhook('https://peaceful-brushlands-75600.herokuapp.com' + API_KEY)
    # updater.start_polling()
    updater.idle()


# Run the bot until you press Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.


# Helper function

def pdfToMp3(file): 
    # Create file object and PDF reader object
    book = open(file, 'rb')
    pdfReader = PyPDF3.PdfFileReader(book)

    # Look for number of pages for looping
    pages = pdfReader.numPages

    finalText = ""
    with pdfplumber.open(file) as pdf:
        for i in range(0, pages):
            page = pdf.pages[i]
            text = page.extract_text()
            finalText += text    

    # Convert to MP3 and save as a file
    engine = pyttsx3.init()
    newFileName = "updated.mp3"
    engine.save_to_file(finalText, newFileName)
    engine.runAndWait()


if __name__ == '__main__':
    main()
