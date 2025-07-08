from config import TOKEN2
import asyncio
import os
import uuid
import aiohttp
import time
import certifi  # Импортируем certifi для SSL
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from gtts import gTTS
import ssl
import requests
from googletrans import Translator

# Настройка SSL для Telegram
ssl_ca_path = certifi.where()
telegram_ssl_context = ssl.create_default_context(cafile=ssl_ca_path)

# Для Google Translate и gTTS отключаем проверку SSL
google_ssl_context = ssl.create_default_context()
google_ssl_context.check_hostname = False
google_ssl_context.verify_mode = ssl.CERT_NONE

# Создаем небезопасную сессию requests для Google сервисов
unverified_requests_session = requests.Session()
unverified_requests_session.verify = False

# Monkey patching для gTTS - используем небезопасную сессию
import gtts.tts

gtts.tts.requests.get = lambda url, **kwargs: unverified_requests_session.get(url, **kwargs)
gtts.tts.requests.post = lambda url, **kwargs: unverified_requests_session.post(url, **kwargs)

# Инициализируем переводчик
translator = Translator()


async def create_bot():
    # Создаем безопасный коннектор для Telegram
    connector = aiohttp.TCPConnector(ssl=telegram_ssl_context)

    # Инициализируем бота с кастомным коннектором
    bot = Bot(token=TOKEN2, connector=connector)
    return bot, connector


def translate_text_sync(text):
    """Функция для перевода текста на немецкий с помощью googletrans"""
    try:
        # Выполняем перевод
        result = translator.translate(text, dest='de')

        # Возвращаем переведенный текст
        return result.text
    except Exception as e:
        # В случае ошибки возвращаем сообщение об ошибке на немецком
        print(f"Ошибка перевода: {str(e)}")
        return "Übersetzungsfehler - bitte versuchen Sie es später erneut"


async def main():
    bot, connector = await create_bot()
    dp = Dispatcher()

    @dp.message(Command("start"))
    async def start_cmd(message: types.Message):
        await message.answer("Привет! Отправь текст для перевода на немецкий")

    @dp.message(F.text)
    async def handle_text(message: types.Message):
        audio_file = None
        try:
            # Выполняем перевод в отдельном потоке
            start_time = time.time()
            translated_text = await asyncio.to_thread(translate_text_sync, message.text)
            translation_time = time.time() - start_time

            await message.answer(f"Перевод: {translated_text}\n\n⏱ Время перевода: {translation_time:.2f} сек")

            # Генерация аудио
            start_time = time.time()
            audio_file = f"audio_{uuid.uuid4()}.mp3"
            tts = gTTS(text=translated_text, lang='de')
            tts.save(audio_file)
            tts_time = time.time() - start_time

            # Отправка аудио
            with open(audio_file, 'rb') as audio:
                await message.answer_voice(
                    types.BufferedInputFile(audio.read(), filename="translation.ogg"),
                    caption=f"Озвучка перевода ⏱ {tts_time:.2f} сек"
                )

        except asyncio.TimeoutError:
            await message.answer("⏳ Время ожидания перевода истекло. Попробуйте позже.")
        except Exception as e:
            # Подробная диагностика ошибки
            import traceback
            error_trace = traceback.format_exc()
            print(f"Детали ошибки:\n{error_trace}")
            await message.answer(f"⚠️ Fehler: {str(e)}")
        finally:
            if audio_file and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except:
                    pass

    try:
        print("Бот запущен! Используется Google Translate для перевода")
        print(f"Используемые SSL сертификаты для Telegram: {ssl_ca_path}")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await connector.close()


if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Проверка подключения к Telegram с SSL
    try:
        telegram_session = requests.Session()
        telegram_session.verify = ssl_ca_path
        test_resp = telegram_session.get("https://api.telegram.org", timeout=10)
        print(f"Тест подключения к Telegram: {'Успешно' if test_resp.ok else 'Ошибка'} - код {test_resp.status_code}")
    except Exception as e:
        print(f"Ошибка теста подключения к Telegram: {str(e)}")

    # Проверка подключения к Google без SSL
    try:
        test_google = unverified_requests_session.get("https://translate.google.com", timeout=10)
        print(f"Тест подключения к Google: {'Успешно' if test_google.ok else 'Ошибка'} - код {test_google.status_code}")
    except Exception as e:
        print(f"Ошибка теста подключения к Google: {str(e)}")

    asyncio.run(main())