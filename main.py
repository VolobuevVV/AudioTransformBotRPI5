from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pydub import AudioSegment
import os

BOT_TOKEN = '8101388926:AAEjCS7kwSp8EitsYo8m11rT4SeQzUsSf4M'

def start(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    update.message.reply_text(f'Привет, {user_name}! 😊 Отправь мне голосовое сообщение, и я изменю его тон. 🎶 '
                              'Разработчик - Владимир Волобуев @volobuevv 👨‍💻')

def voice(update: Update, context: CallbackContext):
    file = update.message.voice.get_file()
    file_path = "voice.ogg"
    file.download(file_path)

    sound = AudioSegment.from_ogg(file_path)
    octaves = -0.5  # понижение тональности
    new_sample_rate = int(sound.frame_rate * (2 ** octaves))
    sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})

    sound = sound.set_frame_rate(44100)
    sound = sound.set_channels(1)

    output_ogg_path = "voice_lowered.ogg"
    output_mp3_path = "voice_lowered.mp3"
    output_wav_path = "voice_lowered.wav"

    sound.export(output_ogg_path, format="ogg")
    sound.export(output_mp3_path, format="mp3")
    sound.export(output_wav_path, format="wav")

    # Отправляем измененный голос
    with open(output_ogg_path, 'rb') as f:
        update.message.reply_voice(voice=InputFile(f), caption="Вот твой голос с пониженным тоном!")

    # Отправляем файлы для скачивания
    with open(output_ogg_path, 'rb') as f:
        update.message.reply_document(document=InputFile(f), caption="Скачай OGG файл")

    with open(output_mp3_path, 'rb') as f:
        update.message.reply_document(document=InputFile(f), caption="Скачай MP3 файл")

    with open(output_wav_path, 'rb') as f:
        update.message.reply_document(document=InputFile(f), caption="Скачай WAV файл")

    # Удаляем временные файлы
    os.remove(file_path)
    os.remove(output_ogg_path)
    os.remove(output_mp3_path)
    os.remove(output_wav_path)

def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.voice, voice))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
