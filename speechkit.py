import requests
from yandex_gpt import get_creds, create_new_token
from config import *

iam_token, folder_id = get_creds()


def stt(data):
    params = '&'.join([
        'topic=general',
        f'folder_id={folder_id}',
        'lang=ru-RU'
    ])

    headers = {
        'Authorization': f'Bearer {iam_token}'
    }

    response = requests.post(
        f'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?{params}',
        headers=headers,
        data=data
    )
    if response.status_code == 429:
        create_new_token()
        return stt(data)

    decoded_data = response.json

    if decoded_data('error_code') is None:
        return True, decoded_data('result')
    else:
        return False, 'При запросе в SpeechKit возникла ошибка.'