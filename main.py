from telegram import Update, InputFile, ReplyKeyboardMarkup, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pydub import AudioSegment
import os
import whisper
import asyncio
import edge_tts

BOT_TOKEN = '8101388926:AAEjCS7kwSp8EitsYo8m11rT4SeQzUsSf4M'

# Используется только модель 'small' для распознавания
preloaded_models = {
    'small': whisper.load_model('small'),
}

TEXT_TO_VOICE_PATH = "tts_output.ogg"

def start(update: Update, context: CallbackContext):
    user_name = update.message.from_user.first_name
    keyboard = [['Изменить голос (понизить тон)', 'Преобразовать голос в текст'], ['Преобразовать текст в голос', 'Преобразовать голос в голос']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    update.message.reply_text(
        f'Привет, {user_name}! 😊 Отправь мне голосовое сообщение, и я сделаю с ним что-нибудь интересное!',
        reply_markup=reply_markup
    )
    context.user_data.clear()

def handle_text(update: Update, context: CallbackContext):
    text = update.message.text
    user_id = update.message.from_user.id

    if text == 'Преобразовать голос в текст':
        context.user_data['action'] = 'recognize'
        update.message.reply_text("Отправь голосовое сообщение 🎙")

    elif text == 'Изменить голос (понизить тон)':
        context.user_data['action'] = 'transform'
        update.message.reply_text("Отправь голосовое сообщение")

    elif text == 'Преобразовать текст в голос':
        context.user_data['action'] = 'tts'
        update.message.reply_text("Голос для озвучки выбран: Дмитрий. Теперь отправь текст для озвучки.")

    elif text == 'Преобразовать голос в голос':
        context.user_data['action'] = 'voice_to_voice'
        update.message.reply_text("Голос для озвучки выбран: Дмитрий. Отправь голосовое сообщение.")

    elif text == 'Назад':
        context.user_data.pop('action', None)
        keyboard = [['Изменить голос (понизить тон)', 'Преобразовать голос в текст'], ['Преобразовать текст в голос', 'Преобразовать голос в голос']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        update.message.reply_text("Выбери действие", reply_markup=reply_markup)

    elif context.user_data.get('action') == 'tts':
        # Голос Дмитрий установлен по умолчанию
        context.user_data['voice'] = 'ru-RU-DmitryNeural'
        asyncio.run(text_to_speech(update, text, context))
        context.user_data.clear()

def transcribe_audio(audio_file, model_name):
    # Используется модель 'small' по умолчанию для распознавания
    model = preloaded_models['small']
    result = model.transcribe(audio_file, language="ru")
    return result["text"]

async def text_to_speech(update: Update, text: str, context: CallbackContext):
    # Голос Дмитрий выбран по умолчанию
    voice = 'ru-RU-DmitryNeural'
    tts = edge_tts.Communicate(text, voice=voice)
    await tts.save(TEXT_TO_VOICE_PATH)

    with open(TEXT_TO_VOICE_PATH, 'rb') as f:
        update.message.reply_voice(voice=InputFile(f), caption="Вот озвучка твоего текста")

    os.remove(TEXT_TO_VOICE_PATH)

async def voice_to_voice(update: Update, file_path: str, context: CallbackContext):
    text = transcribe_audio(file_path, 'small')  # Используем модель 'small' для распознавания
    voice = 'ru-RU-DmitryNeural'  # Голос Дмитрий выбран по умолчанию

    tts = edge_tts.Communicate(text, voice=voice)
    await tts.save(TEXT_TO_VOICE_PATH)

    with open(TEXT_TO_VOICE_PATH, 'rb') as f:
        update.message.reply_voice(voice=InputFile(f), caption="Вот озвучка твоего текста из голосового сообщения")

    os.remove(TEXT_TO_VOICE_PATH)

def voice(update: Update, context: CallbackContext):
    action = context.user_data.get('action')

    if not action:
        update.message.reply_text("Сначала выбери действие с помощью кнопок")
        return

    message = update.message.reply_text("Распознаю голосовое сообщение...", parse_mode=ParseMode.MARKDOWN)

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
        # Используется модель 'small' для распознавания
        text = transcribe_audio(file_path, 'small')
        context.user_data['action'] = 'tts'
        context.user_data['text'] = text
        update.message.reply_text(f"Текст: {text}\nТеперь отправь текст для озвучки")

    elif action == 'voice_to_voice':
        asyncio.run(voice_to_voice(update, file_path, context))

    os.remove(file_path)
    message.delete()

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
