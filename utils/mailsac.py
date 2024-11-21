import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("MAILSAC_API_KEY")


def generate_unique_email():
    if not API_KEY:
        raise Exception("MAILSAC_API_KEY не найден в .env файле")

    base_email = "testuser"
    domain = "mailsac.com"
    unique_email = f"{base_email}{requests.get('https://www.uuidgenerator.net/api/version4').text.strip()}@{domain}"

    return unique_email


def get_latest_email(email_address):
    """Получает последнее письмо для указанного email через API Mailsac."""
    response = requests.get(
        f"https://mailsac.com/api/addresses/{email_address}/messages",
        headers={"Mailsac-Key": API_KEY}
    )
    if response.status_code != 200:
        raise Exception(f"Ошибка при получении писем: {response.status_code}, {response.text}")

    messages = response.json()
    if messages:
        message_id = messages[0]["_id"]
        message_response = requests.get(
            f"https://mailsac.com/api/addresses/{email_address}/messages/{message_id}",
            headers={"Mailsac-Key": API_KEY}
        )
        if message_response.status_code == 200:
            return message_response.json()
    return None



def get_latest_email_text(email):
    """
    Получить текст последнего письма для указанного email из Mailsac.

    :param email: Email, для которого нужно получить последнее письмо.
    :return: Текст содержимого последнего письма или None, если письма нет.
    """
    if not API_KEY:
        raise ValueError("MAILSAC_API_KEY не найден. Проверьте .env файл.")

    # URL для получения списка сообщений
    messages_url = f"https://mailsac.com/api/addresses/{email}/messages"
    headers = {"Mailsac-Key": API_KEY}

    # Получаем список сообщений
    response = requests.get(messages_url, headers=headers)
    if response.status_code != 200:
        print(f"Ошибка при получении списка сообщений: {response.status_code}, {response.text}")
        return None

    messages = response.json()
    if not messages:
        print("В инбоксе нет сообщений.")
        return None

    # Берем последнее сообщение
    latest_message = messages[0]
    message_id = latest_message["_id"]

    # URL для получения содержимого письма
    email_text_url = f"https://mailsac.com/api/addresses/{email}/messages/{message_id}"
    email_response = requests.get(email_text_url, headers=headers)

    if email_response.status_code != 200:
        print(f"Ошибка при получении тела письма: {email_response.status_code}, {email_response.text}")
        return None

    # Возвращаем текстовое содержимое письма
    email_content = email_response.json()
    return email_content.get("text")
