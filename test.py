import whisper

# Загружаем модель
model = whisper.load_model("base")  # Вы можете использовать другие модели: tiny, small, medium, large

def transcribe_audio(audio_file):
    result = model.transcribe(audio_file, language="ru")
    print("Распознанный текст: ", result["text"])

# Использование:
transcribe_audio(r"C:\Users\vladi\Downloads\gs.ogg")
