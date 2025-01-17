import asyncio
import random
import requests
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, InputFile, FSInputFile
from aiogram.filters import CommandStart, Command
from googletrans import Translator
from gtts import gTTS
import os
from config import TOKEN2
from io import BytesIO

bot = Bot(token=TOKEN2)
dp = Dispatcher()

translator = Translator()

@dp.message(Command('help'))
async def help_command(message: Message):
    await message.answer("Этот бот умеет выполнять команды:\n/start - Запуск бота\n/help - Помощь")

@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer("Привет! Я бот, который сохраняет твои фото, создает голосовое сообщение для перевода твоего текста на немецкий язык. Загрузи фото или напиши здесь текст для перевода:")

@dp.message(F.text)
async def translate_and_speak(message: Message):
    # Перевод текста с русского на немецкий
    translated_text = await translator.translate(message.text, src='auto', dest='de')
    await message.answer(f"Переведенный текст: {translated_text.text}")

    # Генерация голосового сообщения
    audio_file_path = await text_to_speech(translated_text.text)

    # Отправка голосового сообщения
    #with open(audio_file_path, 'rb') as voice:
    #    await message.answer_voice(voice, caption="Вот ваше голосовое сообщение!")
    #audio_file_path = 'tmp/audio_message.ogg'
    voice_file = FSInputFile(audio_file_path)
    await message.answer_voice(voice_file)

    #audio_file_path = 'tmp/audio_message.ogg'
    #with open(audio_file_path, 'rb') as f:
    #    voice_file = BytesIO(f.read())
    #await bot.send_voice(chat_id=message.chat.id, voice=voice_file)

async def text_to_speech(text):
    # Путь для сохранения аудиофайла
    audio_file_path = 'tmp/audio_message.ogg'

    # Генерация аудиофайла
    tts = gTTS(text=text, lang='de')
    tts.save(audio_file_path)

    return audio_file_path

@dp.message(F.photo)  # Убедитесь, что вы импортировали F
async def react_photo(message: Message):
    responses = ['Ого, какая фотка! Сохранил ее. Хочешь написать текст для перевода? Можешь здесь написать:',
                 'Супер! Сохранил фото. Хочешь написать текст для перевода? Можешь здесь написать:',
                 'Сохранил фото. Хочешь написать текст для перевода? Можешь здесь написать:']
    rand_answ = random.choice(responses)
    await message.answer(rand_answ)
    await bot.download(message.photo[-1], destination=f'tmp/{message.photo[-1].file_id}.jpg')

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":  # Исправлено на __name__
    asyncio.run(main())