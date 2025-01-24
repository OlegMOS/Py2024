import os
import uuid
import requests
import io
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment
import speech_recognition as sr
from config import TOKENDu, TOKENOpenAI
import logging
import asyncio

# Инициализация клиента OpenAI
client = OpenAI(
    api_key=TOKENOpenAI,  # Замените на ваш ключ API
    base_url="https://api.proxyapi.ru/openai/v1",
)

# Настройка логирования
##logging.basicConfig(level=logging.INFO)
##logger = logging.getLogger(__name__)

# Инициализация бота с токеном
bot = Bot(token=TOKENDu)  # Замените на ваш токен бота
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

##async def on_startup(dp):
##    logger.info("Бот запущен!")

async def process_message(chat_id, user_input):
    # Создаем список сообщений
    messages = [
        {"role": "user", "content": user_input}
    ]

    try:
        # Получаем ответ от модели
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo-1106", messages=messages
        )

        # Извлекаем текст ответа
        assistant_response = chat_completion.choices[0].message.content

        # Генерация аудиофайла с помощью gTTS
        tts = gTTS(text=assistant_response, lang='de', slow=False)  # Изменено на немецкий
        audio_file_name = f"{uuid.uuid4()}.mp3"  # Уникальное имя для аудиофайла
        tts.save(audio_file_name)

        # Отправка аудиофайла пользователю
        await bot.send_audio(chat_id, types.FSInputFile(audio_file_name))

        # Удаление аудиофайла после отправки
        os.remove(audio_file_name)

        # Дублирование голосового ответа текстом
        await bot.send_message(chat_id, assistant_response)

    except requests.exceptions.ConnectionError:
        await bot.send_message(chat_id, 'Ошибка сети. Пожалуйста, проверьте подключениек интернету.')
    except Exception as e:
        await bot.send_message(chat_id, f'Произошла ошибка: {str(e)}')

@dp.message(Command("start"))
async def handle_start_command(message: types.Message):
    await message.answer("Привет! Отправь мне текст или голосовое сообщение.")

@dp.message()
async def handle_text_message(message: types.Message):
    user_input = message.text
    await process_message(message.chat.id, user_input)

@dp.message()
async def handle_voice_message(message: types.Message):
    if message.voice:  # Проверяем, является ли сообщение голосовым
        try:
            # Получаем файл голосового сообщения
            voice_file = await bot.get_file(message.voice.file_id)
            voice_url = f'https://api.telegram.org/file/bot{bot.token}/{voice_file.file_path}'

            # Загружаем файл и сохраняем его
            voice_response = requests.get(voice_url)
            audio_file = io.BytesIO(voice_response.content)

            # Конвертация аудиофайла в формат, который можно распознать
            audio_segment = AudioSegment.from_ogg(audio_file)
            audio_segment.export("temp.wav", format="wav")

            # Используйте библиотеку для распознавания речи
            recognizer = sr.Recognizer()
            with sr.AudioFile("temp.wav") as source:
                audio_data = recognizer.record(source)
                try:
                    user_input = recognizer.recognize_google(audio_data, language='de-DE')  # Изменено на немецкий
                    await process_message(message.chat.id, user_input)
                except sr.UnknownValueError:
                    await bot.send_message(message.chat.id, "Entschuldigung, ich konnte die Sprachnachricht nicht erkennen.")  # Изменено на немецкий
                except sr.RequestError as e:
                    await bot.send_message(message.chat.id, "Fehler beim Zugriff auf den Erkennungsdienst.")  # Изменено на немецкий

            # Удаляем временный файл
            os.remove("temp.wav")

        except requests.exceptions.ConnectionError:
            await bot.send_message(chat_id, 'Ошибка сети. Пожалуйста, проверьте подключение к интернету.')
        except Exception as e:
            await bot.send_message(chat_id, f'Произошла ошибка: {str(e)}')

async def main():
    ##await on_startup(dp)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())