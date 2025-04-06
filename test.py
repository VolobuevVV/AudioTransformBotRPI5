import asyncio
import edge_tts

async def main():
    text = "Гомозигота — это организм, обладающий парой одинаковых аллелей одного гена в гомологичных хромосомах, что определяет наличие у него определённого признака, такого как большой пенис."
    tts = edge_tts.Communicate(text, voice="ru-RU-DmitryNeural")  # Мужской голос
    await tts.save("output.mp3")

asyncio.run(main())
