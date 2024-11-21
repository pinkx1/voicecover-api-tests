from dotenv import load_dotenv

from api import requests
import time
from utils.mailsac import get_latest_email
load_dotenv()


def get_activation_code(email):
    activation_code = None
    for attempt in range(30):
        email_content = get_latest_email(email)
        if email_content:
            for link in email_content.get("links", []):
                if "https://voicecover.ru/auth/activate?activate_code=" in link:
                    activation_code = link.split("=")[1]
                    break
        if activation_code:
            break
        time.sleep(2)
    return activation_code


def test_activate_user_success(base_url, create_user, delete_user):
    email, password = create_user["email"], create_user["password"]

    activation_code = get_activation_code(email)

    activation_response = requests.get_request(f"{base_url}/auth/activate?activate_code={activation_code}")
    assert activation_response.status_code == 200
    assert activation_response.json() == {"success": True}

    signin_payload = {"username": email, "password": password}
    signin_response = requests.post_request(base_url + '/auth/signin', data=signin_payload)
    assert signin_response.status_code == 200
    user_id = signin_response.json()["user"]["id"]
    delete_user(user_id)


def test_activate_user_with_invalid_code(base_url, cleanup_new_user):
    invalid_activation_code = "invalid-code-123"
    activation_response = requests.get_request(f"{base_url}/auth/activate?activate_code={invalid_activation_code}")

    # Проверка статуса кода
    assert activation_response.status_code == 400, (
        f"Ожидается статус код 400 для некорректного кода активации, "
        f"получен: {activation_response.status_code}"
    )

    # Проверка структуры и содержимого ответа
    response_data = activation_response.json()
    expected_message = "Incorrect activate code"

    assert "detail" in response_data, "Ожидается наличие поля 'detail' в ответе"
    assert response_data["detail"] == expected_message, (
        f"Ожидается: {expected_message}, получено: {response_data['detail']}"
    )


def test_activate_user_without_code(base_url):
    activation_response = requests.get_request(f"{base_url}/auth/activate")

    assert activation_response.status_code == 422, "Ожидается статус код 422 для отсутствующего параметра activate_code"

    response_data = activation_response.json()
    expected_detail = [
        {
            "loc": ["query", "activate_code"],
            "msg": "Field required",
            "type": "missing",
            "input": None,
            "url": "https://errors.pydantic.dev/2.1/v/missing"
        }
    ]

    assert "detail" in response_data, "Ожидается наличие поля 'detail' в ответе"
    assert response_data["detail"] == expected_detail, (
        f"Ожидается: {expected_detail}, получено: {response_data['detail']}"
    )


def test_activate_user_with_empty_code(base_url):
    activation_response = requests.get_request(f"{base_url}/auth/activate?activate_code=")

    assert activation_response.status_code == 400, (
        f"Ожидается статус код 400 для пустого значения параметра activate_code, "
        f"получен: {activation_response.status_code}"
    )

    response_data = activation_response.json()
    expected_message = "Incorrect activate code"

    assert "detail" in response_data, "Ожидается наличие поля 'detail' в ответе"
    assert response_data["detail"] == expected_message, (
        f"Ожидается: {expected_message}, получено: {response_data['detail']}"
    )


def test_repeated_activation_attempt(base_url, create_user, delete_user):
    user = create_user
    email = user["email"]
    password = user["password"]

    # Получаем код активации из почты
    activation_code = get_activation_code(email)

    # Выполняем первую активацию
    first_activation_response = requests.get_request(f"{base_url}/auth/activate?activate_code={activation_code}")
    assert first_activation_response.status_code == 200, "Первая активация должна быть успешной"

    # Получаем ID пользователя через авторизацию
    signin_payload = {"username": email, "password": password}
    signin_response = requests.post_request(base_url + '/auth/signin', data=signin_payload)
    assert signin_response.status_code == 200, "Ожидается успешная авторизация после активации"
    user_id = signin_response.json()["user"]["id"]

    # Пытаемся повторно активировать того же пользователя
    second_activation_response = requests.get_request(f"{base_url}/auth/activate?activate_code={activation_code}")

    # Проверяем статус код
    assert second_activation_response.status_code == 400, (
        f"Ожидается статус код 400 для повторной активации, "
        f"получен: {second_activation_response.status_code}"
    )

    # Проверяем структуру и содержимое ответа
    response_data = second_activation_response.json()
    expected_response = {"detail": "Incorrect activate code"}
    assert response_data == expected_response, (
        f"Ожидается сообщение: {expected_response}, получено: {response_data}"
    )

    # Удаляем пользователя
    delete_user(user_id)
