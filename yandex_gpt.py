import os
import requests
import json
import logging
import time
from config import *


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


def create_prompt(user_id):
    try:
        prompt = ''
        return prompt
    except Exception as e:
        logging.error(f"Ошибка создания промта {e}")
        print(e)


def create_new_token():
    """Создание нового токена"""
    metadata_url = "http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}

    token_dir = os.path.dirname(TOKEN_PATH)
    if not os.path.exists(token_dir):
        os.makedirs(token_dir)

    try:
        response = requests.get(metadata_url, headers=headers)
        if response.status_code == 200:
            token_data = response.json()
            # Добавляем время истечения токена к текущему времени
            token_data['expires_at'] = time.time() + token_data['expires_in']
            with open(TOKEN_PATH, "w") as token_file:
                json.dump(token_data, token_file)
            logging.info("Token created")
        else:
            logging.error(f"Failed to retrieve token. Status code: {response.status_code}")
    except Exception as e:
        logging.error(f"An error occurred while retrieving token: {e}")


def get_creds():
    """Получение токена и folder_id из yandex cloud command line interface"""

    with open(TOKEN_PATH, 'r') as f:
        d = json.load(f)
        token = d["access_token"]

    with open(FOLDER_ID_PATH, 'r') as f:
        folder_id = f.read().strip()

    return token, folder_id

