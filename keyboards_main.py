import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove
from config import TOKEN4
from keyboards import create_main_menu, create_links_menu, create_dynamic_menu, create_more_options_menu
from aiogram import F  # Обновленный импорт фильтров
from aiogram.filters import Command

API_TOKEN = TOKEN4

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
router = Router()

async def close_keyboard():
    return ReplyKeyboardRemove()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer("Добро пожаловать!", reply_markup=create_main_menu())

@dp.message(F.text == 'Привет')  # Обновлено
async def farewell_user(message: types.Message):
    await message.answer(f"Привет, {message.from_user.first_name}! Выбери из меню команду", reply_markup=await close_keyboard())

@dp.message(F.text == "Пока")  # Обновленный синтаксис
async def send_farewell(message: types.Message):
    await message.answer(f"Пока, {message.from_user.first_name}!", reply_markup=await close_keyboard())
    # await bot.session.close()  # Закрываем сессию бота
    # await dp.stop_polling()  # Останавливаем диспетчер

@dp.message(Command ('links'))
async def send_links(message: types.Message):
    await message.answer("Выберите ссылку или другую команду из меню:", reply_markup=create_links_menu())

@dp.message(Command ('dynamic'))
async def send_dynamic_buttons(message: types.Message):
    await message.answer("Нажмите кнопку ниже:", reply_markup=create_dynamic_menu())

@dp.callback_query(F.data == "show_more")  # Обновленный синтаксис
async def show_more_options(callback_query: types.CallbackQuery):
    await callback_query.message.edit_reply_markup(reply_markup=create_more_options_menu())

@dp.callback_query(F.data == "option_1")  # Обновленный синтаксис
async def option_one(callback_query: types.CallbackQuery):
    await callback_query.answer("Вы выбрали Опцию 1!")

@dp.callback_query(F.data == "option_2")  # Обновленный синтаксис
async def option_two(callback_query: types.CallbackQuery):
    await callback_query.answer("Вы выбрали Опцию 2!")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":  # Исправлено имя проверки
    asyncio.run(main())