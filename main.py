import torch
from telegram import Update, InputFile, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pydub import AudioSegment
import os
import whisper

BOT_TOKEN = '8101388926:AAEjCS7kwSp8EitsYo8m11rT4SeQzUsSf4M'

user_models = {}
loaded_models = {
    "tiny": whisper.load_model("tiny"),
    "base": whisper.load_model("base"),
    "small": whisper.load_model("small")
}

def main_menu_keyboard():
    return ReplyKeyboardMarkup([['Преобразовать голос', 'Распознать голос']], resize_keyboard=True)

def model_selection_keyboard():
    return ReplyKeyboardMarkup([['tiny', 'base', 'small'], ['Назад']], resize_keyboard=True)

def back_keyboard():
    return ReplyKeyboardMarkup([['Назад']], resize_keyboard=True)

def start(update: Update, context: CallbackContext):
    context.user_data.clear()
    user_name = update.message.from_user.first_name
    update.message.reply_text(f'Привет, {user_name}! 😊 Выбери одну из опций:', reply_markup=main_menu_keyboard())

def handle_text(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.message.from_user.id
    step = context.user_data.get("step")

    if text == 'Распознать голос':
        context.user_data['step'] = 'select_model'
        update.message.reply_text("Выбери модель Whisper для распознавания:", reply_markup=model_selection_keyboard())

    elif text in ['tiny', 'base', 'small'] and step == 'select_model':
        user_models[user_id] = text
        context.user_data['model'] = text
        context.user_data['step'] = 'awaiting_recognition_voice'
        update.message.reply_text(f"Выбрана модель: {text}. Теперь отправь голосовое сообщение 🧠", reply_markup=back_keyboard())

    elif text == 'Преобразовать голос':
        context.user_data['step'] = 'awaiting_transform_voice'
        update.message.reply_text("Отправь голосовое сообщение 🎵", reply_markup=back_keyboard())

    elif text == 'Назад':
        if step == 'awaiting_recognition_voice':
            context.user_data['step'] = 'select_model'
            update.message.reply_text("Выбери модель Whisper для распознавания:", reply_markup=model_selection_keyboard())
        elif step == 'select_model' or step == 'awaiting_transform_voice':
            context.user_data.clear()
            update.message.reply_text("Возвращаемся в главное меню:", reply_markup=main_menu_keyboard())
        else:
            update.message.reply_text("Ты уже в главном меню 😊", reply_markup=main_menu_keyboard())

    else:
        update.message.reply_text("Я не понимаю эту команду 😅 Пожалуйста, используй кнопки.")

def transcribe_audio(audio_file, model_name):
    model = loaded_models[model_name]
    result = model.transcribe(audio_file, language="ru")
    return result["text"]

def voice(update: Update, context: CallbackContext):
    step = context.user_data.get('step')
    user_id = update.message.from_user.id
    model_name = user_models.get(user_id, 'tiny')

    file = update.message.voice.get_file()
    file_path = "voice.ogg"
    file.download(file_path)

    if step == 'awaiting_transform_voice':
        sound = AudioSegment.from_ogg(file_path)
        octaves = -0.5
        new_sample_rate = int(sound.frame_rate * (2 ** octaves))
        sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
        sound = sound.set_frame_rate(44100).set_channels(1)

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

    elif step == 'awaiting_recognition_voice':
        text = transcribe_audio(file_path, model_name)
        update.message.reply_text(text)

    else:
        update.message.reply_text("Сначала выбери действие с помощью кнопок.")

    os.remove(file_path)

    context.user_data.clear()
    update.message.reply_text("Выбери следующее действие:", reply_markup=main_menu_keyboard())

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
