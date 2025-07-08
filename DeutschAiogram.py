import os
import uuid
import requests
import io
import certifi
import ssl
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment
import speech_recognition as sr
from config import TOKENDu, TOKENOpenAI
import asyncio

# Устанавливаем переменные окружения для SSL
os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

# Настройка SSL-верификации
ssl_ca_path = certifi.where()

# Создаем безопасную сессию requests
requests_session = requests.Session()
requests_session.verify = ssl_ca_path

# Инициализация клиента OpenAI
client = OpenAI(
    api_key=TOKENOpenAI,
    base_url="https://api.proxyapi.ru/openai/v1",
)


async def create_bot():
    # Вариант 1: Стандартная SSL-проверка
    ssl_context = ssl.create_default_context(cafile=ssl_ca_path)

    # Вариант 2: Для тестирования (раскомментировать если вариант 1 не работает)
    # ssl_context = ssl.create_default_context()
    # ssl_context.check_hostname = False
    # ssl_context.verify_mode = ssl.CERT_NONE

    # Создаем коннектор с SSL контекстом
    connector = aiohttp.TCPConnector(ssl=ssl_context)

    # Инициализируем бота с кастомным коннектором
    bot = Bot(token=TOKENDu, connector=connector)
    return bot, connector


async def main():
    bot, connector = await create_bot()
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    async def process_message(chat_id, user_input):
        messages = [{"role": "user", "content": user_input}]

        try:
            chat_completion = client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages
            )
            assistant_response = chat_completion.choices[0].message.content

            tts = gTTS(text=assistant_response, lang='de', slow=False)
            audio_file_name = f"{uuid.uuid4()}.mp3"
            tts.save(audio_file_name)

            await bot.send_audio(chat_id, types.FSInputFile(audio_file_name))
            os.remove(audio_file_name)
            await bot.send_message(chat_id, assistant_response)

        except Exception as e:
            await bot.send_message(chat_id, f'Произошла ошибка: {str(e)}')

    @dp.message(Command("start"))
    async def handle_start_command(message: types.Message):
        await message.answer("Привет! Отправь мне текст или голосовое сообщение.")

    @dp.message(F.text)
    async def handle_text_message(message: types.Message):
        await process_message(message.chat.id, message.text)

    @dp.message(F.voice)
    async def handle_voice_message(message: types.Message):
        try:
            voice_file = await bot.get_file(message.voice.file_id)
            voice_url = f'https://api.telegram.org/file/bot{bot.token}/{voice_file.file_path}'

            # Используем нашу безопасную сессию requests
            voice_response = requests_session.get(voice_url)
            audio_file = io.BytesIO(voice_response.content)

            audio_segment = AudioSegment.from_ogg(audio_file)
            audio_segment.export("temp.wav", format="wav")

            recognizer = sr.Recognizer()
            with sr.AudioFile("temp.wav") as source:
                audio_data = recognizer.record(source)
                try:
                    user_input = recognizer.recognize_google(audio_data, language='de-DE')
                    await process_message(message.chat.id, user_input)
                except sr.UnknownValueError:
                    await message.answer("Entschuldigung, ich konnte die Sprachnachricht nicht erkennen.")
                except sr.RequestError as e:
                    await message.answer(f"Fehler beim Zugriff auf den Erkennungsdienst: {str(e)}")

            os.remove("temp.wav")

        except Exception as e:
            await message.answer(f'Произошла ошибка: {str(e)}')

    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка при работе бота: {e}")
    finally:
        await connector.close()


if __name__ == '__main__':
    # Для Windows устанавливаем правильную политику event loop
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Дополнительные проверки SSL
    print(f"Используемый SSL файл: {certifi.where()}")
    try:
        print(f"Доступ к api.telegram.org: {requests.get('https://api.telegram.org', verify=ssl_ca_path).status_code}")
    except Exception as e:
        print(f"Ошибка проверки доступа: {e}")

    asyncio.run(main())