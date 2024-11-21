import os
import pytest
from api import requests


def test_get_transaction_count_successfully(base_url, signin_user, add_balance):
    """
    Проверяет, что авторизованный пользователь может получить общее количество своих транзакций.

    Шаги:
    1. Авторизоваться под статичным пользователем.
    2. Пополнить баланс пользователя через фикстуру `add_balance` на 1 (создать одну транзакцию).
    3. Выполнить GET-запрос к эндпоинту `/user/transactions/count/`.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что в ответе возвращается корректное число транзакций.
    """
    # Шаг 1: Авторизоваться под статичным пользователем
    user_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    user_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)
    user_access_token = user["access_token"]

    # Шаг 2: Пополнить баланс пользователя на 1
    add_balance(user["user_id"], 1)

    # Шаг 3: Выполнить GET-запрос
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
    }
    response = requests.get_request(f"{base_url}/user/transactions/count/", headers=headers)

    # Шаг 4: Проверить статус код
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 5: Проверить число транзакций в ответе
    transaction_count = response.json()
    assert isinstance(transaction_count, int), (
        f"Ожидаемый тип ответа: int, получено: {type(transaction_count)}"
    )
    assert transaction_count > 1, "Количество транзакций должно быть больше 0"


def test_get_transaction_count_without_authorization(base_url):
    """
    Проверяет, что сервер отклоняет запрос на получение количества транзакций от неавторизованного пользователя.

    Шаги:
    1. Выполнить GET-запрос к эндпоинту `/user/transactions/count/` без токена авторизации.
    2. Проверить, что сервер возвращает статус код 401.
    """
    # Шаг 1: Выполнить GET-запрос без авторизации
    headers = {"accept": "application/json"}
    response = requests.get_request(f"{base_url}/user/transactions/count/", headers=headers)

    # Шаг 2: Проверить статус код
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )
