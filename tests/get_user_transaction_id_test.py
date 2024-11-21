import os
import pytest
from api import requests


def test_get_transaction_successfully(base_url, signin_user, add_balance):
    """
    Проверяет, что авторизованный пользователь может получить информацию о своей транзакции по корректному `id`.
    """
    # Шаг 1: Авторизоваться под статичным пользователем
    user_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    user_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)
    user_access_token = user["access_token"]
    user_id = user["user_id"]

    # Шаг 2: Пополнить баланс пользователя на 1
    transaction = add_balance(user_id, 1)

    # Проверка созданной транзакции
    transaction_id = transaction["id"]

    # Шаг 3: Выполнить GET-запрос
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
    }

    response = requests.get_request(f"{base_url}/user/transactions/{transaction_id}", headers=headers)

    # Проверить статус код
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )


def test_get_other_user_transaction_forbidden(base_url, signin_user, add_balance):
    """
    Проверяет, что пользователь не может получить доступ к транзакции другого пользователя.
    Ожидается, что сервер возвращает статус код 403 (Forbidden).
    """
    # Шаг 1: Авторизоваться под первым пользователем
    user1_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    user1_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user1 = signin_user(user1_email, user1_password)

    # Шаг 2: Создать транзакцию для первого пользователя
    transaction = add_balance(user1["user_id"], 1)
    transaction_id = transaction["id"]

    # Шаг 3: Авторизоваться под вторым пользователем
    user2_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    user2_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user2 = signin_user(user2_email, user2_password)
    user2_access_token = user2["access_token"]

    # Шаг 4: Попробовать получить транзакцию первого пользователя
    headers = {
        "Authorization": f"Bearer {user2_access_token}",
        "accept": "application/json",
    }
    response = requests.get_request(f"{base_url}/transaction/{transaction_id}", headers=headers)

    # Шаг 5: Проверить статус код
    assert response.status_code == 403, (
        f"Ожидаемый статус код 403, получен: {response.status_code}"
    )


def test_get_transaction_as_admin(base_url, signin_user, add_balance):
    """
    Проверяет, что администратор может получить информацию о транзакции любого пользователя.
    Ожидается, что сервер возвращает статус код 200 и корректную информацию о транзакции.
    """
    # Шаг 1: Авторизоваться под пользователем
    user_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    user_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)

    # Шаг 2: Создать транзакцию для пользователя
    transaction = add_balance(user["user_id"], 1)
    transaction_id = transaction["id"]

    # Шаг 3: Авторизоваться под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 4: Получить транзакцию
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
    }
    response = requests.get_request(f"{base_url}/transaction/{transaction_id}", headers=headers)

    # Шаг 5: Проверить статус код и данные
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )
    response_data = response.json()
    assert response_data["id"] == transaction_id, "ID транзакции в ответе не совпадает"
    assert response_data["user_id"] == user["user_id"], "ID пользователя в транзакции не совпадает"


def test_get_nonexistent_transaction_not_found(base_url, signin_user):
    """
    Проверяет, что сервер возвращает ошибку при попытке доступа к транзакции с несуществующим `id`.
    Ожидается, что сервер возвращает статус код 404 (Not Found).
    """
    # Шаг 1: Авторизоваться под пользователем
    user_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    user_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)
    user_access_token = user["access_token"]

    # Шаг 2: Попробовать получить несуществующую транзакцию
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
    }
    response = requests.get_request(f"{base_url}/user/transaction/9999999", headers=headers)

    # Шаг 3: Проверить статус код
    assert response.status_code == 404, (
        f"Ожидаемый статус код 404, получен: {response.status_code}"
    )


def test_get_transaction_unauthorized(base_url):
    """
    Проверяет, что сервер отклоняет запрос от неавторизованного пользователя.
    Ожидается, что сервер возвращает статус код 401 (Unauthorized).
    """
    # Шаг 1: Выполнить GET-запрос без авторизации
    headers = {"accept": "application/json"}
    response = requests.get_request(f"{base_url}/transaction/1", headers=headers)

    # Шаг 2: Проверить статус код
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )
