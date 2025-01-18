import telebot
from config import TOKENDu, TOKENOpenAI
from openai import OpenAI
from gtts import gTTS
import os
import uuid
import requests
import io
from pydub import AudioSegment
import speech_recognition as sr


# Инициализация клиента OpenAI
client = OpenAI(
    api_key=TOKENOpenAI,  # Замените на ваш ключ API
    base_url="https://api.proxyapi.ru/openai/v1",
)

# Инициализация бота с токеном
bot = telebot.TeleBot(TOKENDu)  # Замените на ваш токен бота


@bot.message_handler(content_types=['text'])
def handle_text_message(message):
    user_input = message.text
    process_message(message.chat.id, user_input)


@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    try:
        # Получаем файл голосового сообщения
        voice_file = bot.get_file(message.voice.file_id)
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
                process_message(message.chat.id, user_input)
            except sr.UnknownValueError:
                bot.send_message(message.chat.id,
                                 "Entschuldigung, ich konnte die Sprachnachricht nicht erkennen.")  # Изменено на немецкий
            except sr.RequestError as e:
                bot.send_message(message.chat.id, "Fehler beim Zugriff auf den Erkennungsdienst.")  # Изменено на немецкий

        # Удаляем временный файл

        os.remove("temp.wav")

    except requests.exceptions.ConnectionError:
        bot.send_message(message.chat.id, 'Ошибка сети. Пожалуйста, проверьте подключение к интернету.')
    except Exception as e:
        bot.send_message(message.chat.id, f'Произошла ошибка: {str(e)}')

def process_message(chat_id, user_input):
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
        with open(audio_file_name, 'rb') as audio_file:
            bot.send_voice(chat_id, audio_file)

        # Удаление аудиофайла после отправки
        os.remove(audio_file_name)

        # Дублирование голосового ответа текстом
        url = f'https://api.telegram.org/bot{bot.token}/sendMessage'

        # Параметры для запроса
        payload = {
            'chat_id': chat_id,
            'text': assistant_response
        }

        # Отправка POST-запроса
        response = requests.post(url, data=payload)

    except requests.exceptions.ConnectionError:
        bot.send_message(chat_id, 'Ошибка сети. Пожалуйста, проверьте подключение к интернету.')
    except Exception as e:
        bot.send_message(chat_id, f'Произошла ошибка: {str(e)}')


if __name__ == "__main__":
    # Запуск бота
    bot.polling(none_stop=True)