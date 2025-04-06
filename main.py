from telegram import Update, InputFile, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pydub import AudioSegment
import os
import whisper

BOT_TOKEN = '8101388926:AAEjCS7kwSp8EitsYo8m11rT4SeQzUsSf4M'

# Предзагрузка моделей
preloaded_models = {
    'tiny': whisper.load_model('tiny'),
    'base': whisper.load_model('base'),
    'small': whisper.load_model('small'),
}

user_models = {}

def start(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    keyboard = [['Изменить голос', 'Преобразовать голос в текст']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        f'Привет, {user_name}! 😊 Отправь мне голосовое сообщение, и я сделаю с ним что-нибудь интересное!\n'
        'Разработчик - Владимир Волобуев @volobuevv 👨‍💻',
        reply_markup=reply_markup
    )
    context.user_data.clear()

def handle_text(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == 'Преобразовать голос в текст':
        context.user_data['action'] = 'recognize'
        keyboard = [['tiny', 'base', 'small'], ['Назад']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("Выбери модель для распознавания речи", reply_markup=reply_markup)

    elif text in ['tiny', 'base', 'small'] and context.user_data.get('action') == 'recognize':
        user_models[user_id] = text
        update.message.reply_text(f'Выбрана модель: {text}\nТеперь отправь голосовое сообщение 🎙')

    elif text == 'Изменить голос':
        context.user_data['action'] = 'transform'
        update.message.reply_text("Отправь голосовое сообщение")

    elif text == 'Назад':
        context.user_data.pop('action', None)
        keyboard = [['Изменить голос', 'Преобразовать голос в текст']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("Возвращаемся назад\nВыбери действие", reply_markup=reply_markup)

def transcribe_audio(audio_file, model_name):
    model = preloaded_models[model_name]
    result = model.transcribe(audio_file, language="ru")
    return result["text"]

def voice(update: Update, context: CallbackContext):
    action = context.user_data.get('action')
    user_id = update.message.from_user.id
    model_name = user_models.get(user_id, 'tiny')

    if not action:
        update.message.reply_text("Сначала выбери действие с помощью кнопок")
        return

    # Сообщение о начале процесса
    message = update.message.reply_text(
        "🌀 Ожидайте... Распознаю голосовое сообщение.",
        parse_mode=ParseMode.MARKDOWN
    )

    # Загружаем и обрабатываем голосовое сообщение
    file = update.message.voice.get_file()
    file_path = "voice.ogg"
    file.download(file_path)

    if action == 'transform':
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
            update.message.reply_voice(voice=InputFile(f), caption="Вот твой голос с пониженным тоном")

        with open(output_wav_path, 'rb') as f:
            update.message.reply_document(document=InputFile(f))

        os.remove(output_ogg_path)
        os.remove(output_wav_path)

    elif action == 'recognize':
        text = transcribe_audio(file_path, model_name)
        update.message.reply_text(text)

    os.remove(file_path)

    # Удаляем сообщение ожидания
    message.delete()

    context.user_data.clear()  # Очистим данные пользователя после завершения

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
