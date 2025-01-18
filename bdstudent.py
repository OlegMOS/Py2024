import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from config import TOKEN3

import sqlite3
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import logging


bot = Bot(token=TOKEN3)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

def init_db():
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
	CREATE TABLE IF NOT EXISTS students (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	age INTEGER NOT NULL,
	grade TEXT NOT NULL)
	''')
    conn.commit()
    conn.close()

init_db()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Из какого ты учебного потока?")
    await state.set_state(Form.grade)

@dp.message(Form.grade)
async def grade(message: Message, state:FSMContext):
    await state.update_data(grade=message.text)
    students_user = await state.get_data()

    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO students (name, age, grade) VALUES (?, ?, ?)''', (students_user['name'], students_user['age'],
    students_user['grade']))
    conn.commit()
    conn.close()

    # Получение данных из базы данных для вывода
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM students WHERE name = ?', (students_user['name'],))
    student_data = cur.fetchone()

    if student_data:
        await message.answer(
            f"Данные по студенту сохранены в БД: имя - {student_data[1]}, возраст - {student_data[2]}, поток - {student_data[3]}")
    else:
        await message.answer("Не удалось найти данные студента в базе данных.")

    conn.close()

async def main():
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())