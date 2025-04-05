import torch
from telegram import Update, InputFile, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pydub import AudioSegment
import os
import whisper

BOT_TOKEN = '8101388926:AAEjCS7kwSp8EitsYo8m11rT4SeQzUsSf4M'

model = whisper.load_model("tiny")

def start(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    keyboard = [['Преобразовать голос', 'Распознать голос']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(f'Привет, {user_name}! 😊 Выбери одну из опций:', reply_markup=reply_markup)

def handle_text(update: Update, context: CallbackContext):
    text = update.message.text
    if text == 'Распознать голос':
        update.message.reply_text("Пожалуйста, отправь голосовое сообщение, и я его распознаю 🧠")
        context.user_data['action'] = 'recognize'
    elif text == 'Преобразовать голос':
        update.message.reply_text("Пожалуйста, отправь голосовое сообщение, и я понижу его тон 🎵")
        context.user_data['action'] = 'transform'
    else:
        update.message.reply_text("Я не понимаю эту команду 😅 Пожалуйста, выбери действие с помощью кнопок.")

def transcribe_audio(audio_file):
    result = model.transcribe(audio_file, language="ru")
    return result["text"]

def convert_audio_format(input_file_path, output_format="wav"):
    sound = AudioSegment.from_ogg(input_file_path)
    sound = sound.set_frame_rate(16000)
    output_path = f"converted.{output_format}"
    sound.export(output_path, format=output_format)
    return output_path

def voice(update: Update, context: CallbackContext):
    action = context.user_data.get('action')
    if not action:
        update.message.reply_text("Сначала выбери действие с помощью кнопок.")
        return

    file = update.message.voice.get_file()
    file_path = "voice.ogg"
    file.download(file_path)

    converted_path = convert_audio_format(file_path)

    if action == 'transform':
        sound = AudioSegment.from_wav(converted_path)
        octaves = -0.5
        new_sample_rate = int(sound.frame_rate * (2 ** octaves))
        sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
        sound = sound.set_frame_rate(16000)

        output_ogg_path = "voice_lowered.ogg"
        output_wav_path = "voice_lowered.wav"
        sound.export(output_ogg_path, format="ogg")
        sound.export(output_wav_path, format="wav")

        with open(output_ogg_path, 'rb') as f:
            update.message.reply_voice(voice=InputFile(f), caption="Вот твой голос с пониженным тоном!")

        with open(output_wav_path, 'rb') as f:
            update.message.reply_document(document=InputFile(f))

        os.remove(output_ogg_path)
        os.remove(output_wav_path)

    elif action == 'recognize':
        text = transcribe_audio(converted_path)
        update.message.reply_text(text)

    os.remove(file_path)
    os.remove(converted_path)

def main():
    updater = Updater(BOT_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.voice, voice))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
