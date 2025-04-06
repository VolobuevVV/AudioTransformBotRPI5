import asyncio
import edge_tts

async def main():
    text = "Гомозигота — это организ"
    tts = edge_tts.Communicate(text, voice="ru-RU-SvetlanaNeural")  # Мужской голос
    await tts.save("output.mp3")

asyncio.run(main())
