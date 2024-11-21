import os
import pytest
from api import requests


def test_get_user_count_as_admin(base_url, signin_user):
    """
    Проверяет, что администратор может успешно получить общее количество пользователей.

    Шаги:
    1. Авторизоваться под администратором.
    2. Выполнить GET-запрос для получения количества пользователей.
    3. Проверить, что сервер возвращает статус код 200.
    4. Проверить, что тело ответа содержит числовое значение.
    """
    # Шаг 1: Авторизоваться под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_token = admin["access_token"]

    # Шаг 2: Выполнить GET-запрос для получения количества пользователей
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "accept": "application/json"
    }
    response = requests.get_request(
        f"{base_url}/user/count/",
        headers=headers
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 200
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 4: Проверить, что тело ответа содержит числовое значение
    response_data = response.json()
    assert isinstance(response_data, int), (
        f"Ожидалось числовое значение, получено: {type(response_data).__name__}"
    )
    assert response_data >= 0, (
        f"Ожидалось неотрицательное значение, получено: {response_data}"
    )


def test_get_user_count_without_authorization(base_url):
    """
    Проверяет, что сервер отклоняет запрос на получение количества пользователей без авторизации.

    Шаги:
    1. Выполнить GET-запрос для получения количества пользователей без указания заголовка авторизации.
    2. Проверить, что сервер возвращает статус код 401.
    3. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Выполнить GET-запрос для получения количества пользователей без авторизации
    response = requests.get_request(f"{base_url}/user/count/")

    # Шаг 2: Проверить, что сервер возвращает статус код 401
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )


def test_get_user_count_as_regular_user(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос на получение количества пользователей,
    если запрос отправлен от имени пользователя с ролью `user`.

    Шаги:
    1. Логин под пользователем с ролью `user`.
    2. Выполнить GET-запрос для получения количества пользователей.
    3. Проверить, что сервер возвращает статус код 403.
    4. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Логин под пользователем с ролью `user`
    user_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    user_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)
    user_access_token = user["access_token"]

    # Шаг 2: Выполнить GET-запрос
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
    }
    response = requests.get_request(f"{base_url}/user/count/", headers=headers)

    # Шаг 3: Проверить, что сервер возвращает статус код 403
    assert response.status_code == 403, (
        f"Ожидаемый статус код 403, получен: {response.status_code}"
    )
