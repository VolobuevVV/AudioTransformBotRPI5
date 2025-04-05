from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pydub import AudioSegment
import os

BOT_TOKEN = '8101388926:AAEjCS7kwSp8EitsYo8m11rT4SeQzUsSf4M'

def start(update: Update, context: CallbackContext):
    update.message.reply_text('Привет! Отправь мне голосовое сообщение, и я изменю его тон')

def voice(update: Update, context: CallbackContext):
    file = update.message.voice.get_file()
    file_path = "voice.ogg"
    file.download(file_path)

    sound = AudioSegment.from_ogg(file_path)
    octaves = -0.5
    new_sample_rate = int(sound.frame_rate * (2 ** octaves))
    sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})

    sound = sound.set_frame_rate(44100)
    sound = sound.set_channels(1)

    output_path = "voice_lowered.ogg"
    sound.export(output_path, format="ogg")

    with open(output_path, 'rb') as f:
        update.message.reply_voice(voice=InputFile(f), caption="Вот твой голос с пониженным тоном!")

    os.remove(file_path)
    os.remove(output_path)

def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.voice, voice))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
