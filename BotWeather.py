import asyncio
import requests
import aiohttp
import certifi
import ssl
import os
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from datetime import datetime, timedelta

from config import TOKEN, ACCUWEATHER_API_KEY

# Храним время последнего сообщения
last_message_time = None
n_time = 1
time_diff_all = timedelta(0)  # Инициализируем как timedelta

# Создаем Dispatcher здесь, перед использованием декораторов
dp = Dispatcher()


def get_weather(city="Chelyabinsk"):
    # Получаем ключ для города
    location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={ACCUWEATHER_API_KEY}&q={city}"
    response = requests.get(location_url)

    if response.status_code == 200:
        location_data = response.json()

        if location_data and isinstance(location_data, list) and len(location_data) > 0:
            location_key = location_data[0]['Key']

            # Получаем прогноз погоды
            weather_url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={ACCUWEATHER_API_KEY}&language=ru"
            weather_response = requests.get(weather_url)

            if weather_response.status_code == 200:
                weather_data = weather_response.json()

                if weather_data and isinstance(weather_data, list) and len(weather_data) > 0:
                    weather = weather_data[0]
                    return f"Температура: {weather['Temperature']['Metric']['Value']}°C\n" \
                           f"Состояние: {weather['WeatherText']}"
            elif weather_response.status_code == 404:
                return None  # Возвращаем None для статуса 404

    return "Не удалось получить данные о погоде."


@dp.message(Command('help'))
async def help_command(message: Message):
    await message.answer(
        "Этот бот умеет выполнять команды:\n/start - Запуск бота\n/help - Помощь\n/weather - Узнать погоду в Челябинске")


@dp.message(CommandStart())
async def start_command(message: Message):
    global last_message_time, time_diff_all, n_time
    # Храним время последнего сообщения
    last_message_time = None
    n_time = 1
    time_diff_all = timedelta(0)

    await message.answer(
        "Привет! Я бот, который показывает погоду!\nИспользуйте команду /weather для получения прогноза погоды.")


@dp.message(Command('weather'))
async def weather_command(message: Message):
    global last_message_time, time_diff_all, n_time
    current_time = datetime.now()

    if last_message_time is not None:
        if n_time % 2 == 0:
            time_diff = current_time - last_message_time
            time_diff_all += time_diff  # Добавляем timedelta
            await message.answer(
                f"Прошло времени с последнего сообщения: {round(time_diff.total_seconds() / 60)} минут(-а/ы).")
            await message.answer(
                f"Всего прошло времени с последнего start: {round(time_diff_all.total_seconds() / 60)} минут(-а/ы).")
        else:
            time_diff = 0
            await message.answer("Таймер включен (105+60)!")
    else:
        await message.answer("Таймер включен (105+60)!")

    n_time = n_time + 1
    last_message_time = current_time

    weather_info = get_weather()
    await message.answer(weather_info)


async def create_bot():
    # Настройка SSL для Telegram
    ssl_ca_path = certifi.where()
    telegram_ssl_context = ssl.create_default_context(cafile=ssl_ca_path)

    # Создаем безопасный коннектор для Telegram
    telegram_connector = aiohttp.TCPConnector(ssl=telegram_ssl_context)

    # Инициализируем бота с безопасным коннектором
    bot = Bot(token=TOKEN, connector=telegram_connector)
    return bot, telegram_connector


async def main():
    # Создаем бота с безопасным коннектором
    bot, connector = await create_bot()

    try:
        print("Бот погоды запущен!")
        print(f"Используемые SSL сертификаты: {certifi.where()}")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await connector.close()


if __name__ == "__main__":
    # Проверка подключения к Telegram с SSL
    try:
        ssl_ca_path = certifi.where()
        telegram_session = requests.Session()
        telegram_session.verify = ssl_ca_path
        test_resp = telegram_session.get("https://api.telegram.org", timeout=10)
        print(f"Тест подключения к Telegram: {'Успешно' if test_resp.ok else 'Ошибка'} - код {test_resp.status_code}")
    except Exception as e:
        print(f"Ошибка теста подключения к Telegram: {str(e)}")

    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())