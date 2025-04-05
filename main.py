from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import os

BOT_TOKEN = '8101388926:AAEjCS7kwSp8EitsYo8m11rT4SeQzUsSf4M'

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Привет! Отправь мне голосовое сообщение, и я изменю его тон')

def voice(update: Update, context: CallbackContext):
    file = update.message.voice.get_file()
    file_path = "voice.ogg"
    file.download(file_path)

    with open(file_path, 'rb') as f:
        update.message.reply_voice(voice=InputFile(f), caption="Вот твой голос без изменений!")

    os.remove(file_path)

def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.voice, voice))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
