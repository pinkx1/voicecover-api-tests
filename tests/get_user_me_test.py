import os
import pytest
from api import requests


def test_get_my_data_successfully(base_url, signin_user):
    """
    Проверяет, что авторизованный пользователь может успешно получить свои данные.

    Шаги:
    1. Логин под тестовым пользователем.
    2. Выполнить GET-запрос к эндпоинту `/user/me`.
    3. Проверить, что сервер возвращает статус код 200.
    4. Проверить, что тело ответа соответствует ожидаемой схеме.
    """
    # Шаг 1: Логин под тестовым пользователем
    user_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    user_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)
    user_access_token = user["access_token"]

    # Шаг 2: Выполнить GET-запрос
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
    }
    response = requests.get_request(f"{base_url}/user/me/", headers=headers)

    # Вывод отладочной информации
    print("Статус код ответа:", response.status_code)
    try:
        print("Тело ответа:", response.json())
    except ValueError:
        print("Ответ не является JSON:", response.text)

    # Шаг 3: Проверить статус код
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 4: Проверить схему ответа
    response_data = response.json()
    expected_schema = {
        "lastname": (str, type(None)),
        "firstname": (str, type(None)),
        "avatar": (str, type(None)),
        "email": str,
        "role": str,
        "phone": (str, type(None)),
        "telegram": (str, type(None)),
        "telegram_chatid": (int, type(None)),
        "balance": (float, int),
        "is_active": bool,
        "id": int,
        "created_at": str,
        "last_login": (str, type(None)),
        "utm": (str, type(None)),
    }

    for field, field_type in expected_schema.items():
        assert field in response_data, f"Поле `{field}` отсутствует в ответе"
        assert isinstance(response_data[field], field_type), (
            f"Поле `{field}` имеет неверный тип. "
            f"Ожидаемый: {field_type}, полученный: {type(response_data[field])}"
        )


def test_get_my_data_without_authorization(base_url):
    """
    Проверяет, что сервер отклоняет запрос, если пользователь не авторизован.

    Шаги:
    1. Выполнить GET-запрос к эндпоинту `/user/me` без авторизации.
    2. Проверить, что сервер возвращает статус код 401.
    3. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Выполнить GET-запрос без авторизации
    headers = {
        "accept": "application/json",
    }
    response = requests.get_request(f"{base_url}/user/me", headers=headers)

    # Вывод отладочной информации
    print("Статус код ответа:", response.status_code)
    try:
        print("Тело ответа:", response.json())
    except ValueError:
        print("Ответ не является JSON:", response.text)

    # Шаг 2: Проверить статус код
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )

