import asyncio
import requests
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from config import TOKEN, ACCUWEATHER_API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher()


# Функция для получения прогноза погоды
async def get_weather(city="Chelyabinsk"):
    # Получаем ключ для города
    location_url = f"http://dataservice.accuweather.com/locations/v1/cities/search?apikey={ACCUWEATHER_API_KEY}&q={city}"
    response = requests.get(location_url)
    location_data = response.json()

    if location_data and isinstance(location_data, list) and len(location_data) > 0:
        location_key = location_data[0]['Key']

        # Получаем прогноз погоды
        weather_url = f"http://dataservice.accuweather.com/currentconditions/v1/{location_key}?apikey={ACCUWEATHER_API_KEY}&language=ru"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()

        if weather_data and isinstance(weather_data, list) and len(weather_data) > 0:
            weather = weather_data[0]
            return f"Температура: {weather['Temperature']['Metric']['Value']}°C\n" \
                   f"Состояние: {weather['WeatherText']}"

    return "Не удалось получить данные о погоде."


@dp.message(Command('help'))
async def help_command(message: Message):
    await message.answer("Этот бот умеет выполнять команды:\n/start - Запуск бота\n/help - Помощь\n/weather - Узнать погоду в Челябинске")


@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        "Привет! Я бот, который показывает погоду!\nИспользуйте команду /weather для получения прогноза погоды.")


@dp.message(Command('weather'))
async def weather_command(message: Message):
    weather_info = await get_weather()
    await message.answer(weather_info)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())