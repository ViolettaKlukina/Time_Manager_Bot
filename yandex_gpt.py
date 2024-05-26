import requests
import logging
from config import *
import os
import json
import time

logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты - дружелюбный помощник по планированию.'
                                            'Отвечай пользователю только по вопросам, связанными с планированием, тайм-менеджментом и так же используя системы планирвоания: '
                                            'Канбан,'
                                            'МАТРИЦА ЭЙЗЕНХАУЭРА,'
                                            'Распределение задач на месяца и недели.'
                                            'Отвечай одним-тремя предложениями, кратко и по делу.'}]


def count_gpt_tokens(messages):
    iam_token, folder_id = get_creds()
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion"
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'modelUri': f"gpt://{folder_id}/yandexgpt-lite",
        "messages": messages
    }
    try:
        return len(requests.post(url=url, json=data, headers=headers).json()['tokens'])
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return 0


def count_tokens_in_dialogue(messages: list) -> int:
    try:
        token, folder_id = get_creds()
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        data = {
           "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
           "maxTokens": MAX_TOKENS,
           "messages": []
        }

        for row in messages:
            if row["content"]:
                data["messages"].append(
                    {
                        "role": row["role"],
                        "text": row["content"]
                    }
                )
        resp = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/tokenizeCompletion",
            json=data,
            headers=headers
        )
        if resp.status_code == 200:
            return len(
                resp.json()["tokens"]
            )
        print(resp.text)
    except Exception as e:
        logging.error(f"Ошибка токинезации {e}")
        print(e)
        return 0


def create_new_token():
    metadata_url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}

    token_dir = os.path.dirname(TOKEN_PATH)
    if not os.path.exists(token_dir):
        os.makedirs(token_dir)

    try:
        response = requests.get(metadata_url, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            token_data['expires_at'] = time.time() + token_data['expires_in']
            with open(TOKEN_PATH, "w") as token_file:
                json.dump(token_data, token_file)
            logging.info("Token created")
        else:
            logging.error(f"Failed to retrieve token. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"An error occurred while retrieving token: {e}")


def ask_gpt(messages):
    iam_token, folder_id = get_creds()
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        'Authorization': f'Bearer {iam_token}',
        'Content-Type': 'application/json'
    }
    data = {
        'modelUri': f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.7,
            "maxTokens": MAX_TOKENS
        },
        "messages": [
            {
                'role': 'user',
                'text': messages.text
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        # проверяем статус код
        if response.status_code != 200:
            return False, f"Ошибка GPT. Статус-код: {response.status_code}", None
        # если всё успешно - считаем количество токенов, потраченных на ответ, возвращаем статус, ответ, и количество токенов в ответе
        answer = response.json()['result']['alternatives'][0]['message']['text']
        tokens = count_tokens_in_dialogue(answer)
        return True, answer, tokens
    except Exception as e:
        logging.error(e)  # если ошибка - записываем её в логи
        return False, "Ошибка при обращении к GPT",  None


def get_creds():
    """Получение токена и folder_id из yandex cloud command line interface"""
    with open(TOKEN_PATH, 'r') as f:
        d = json.load(f)
        iam_token = d["access_token"]

    with open(FOLDER_ID_PATH, 'r') as f:
        folder_id = f.read().strip()

    return iam_token, folder_id

