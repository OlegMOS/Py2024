import requests
from config import YANDEX_TRANSLATE_API_KEY

YANDEX_TRANSLATE_API_KEY = YANDEX_TRANSLATE_API_KEY
YANDEX_TRANSLATE_URL = "https://translate.yandex.net/api/v1.5/tr.json/translate"

def check_token(api_key):
    params = {
        'key': api_key,
        'text': 'Привет',
        'lang': 'ru-en'
    }
    response = requests.get(YANDEX_TRANSLATE_URL, params=params)
    return response.json()

result = check_token(YANDEX_TRANSLATE_API_KEY)
print(result)