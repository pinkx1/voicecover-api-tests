import os
import pytest
from api import requests


def test_get_user_with_valid_id_as_admin(base_url, signin_user):
    """
    Проверяет, что администратор может получить данные пользователя по корректному ID.

    Шаги:
    1. Логин под администратором.
    2. Указать корректный ID пользователя.
    3. Выполнить GET-запрос для получения данных пользователя.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что тело ответа соответствует ожидаемой схеме.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать корректный ID пользователя
    user_id = 1  # Замените на существующий ID пользователя

    # Шаг 3: Выполнить GET-запрос
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json"
    }
    response = requests.get_request(
        f"{base_url}/user/{user_id}",
        headers=headers
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 200
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа соответствует ожидаемой схеме
    response_data = response.json()
    expected_keys = {
        "lastname", "firstname", "avatar", "email", "role", "phone",
        "telegram", "telegram_chatid", "balance", "is_active", "id",
        "created_at", "last_login", "utm"
    }
    assert expected_keys.issubset(response_data.keys()), (
        f"Ответ не содержит всех ожидаемых ключей: {expected_keys - response_data.keys()}"
    )


def test_get_user_with_nonexistent_id_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер корректно обрабатывает запрос с несуществующим ID пользователя.

    Шаги:
    1. Логин под администратором.
    2. Указать несуществующий ID пользователя.
    3. Выполнить GET-запрос для получения данных пользователя.
    4. Проверить, что сервер возвращает статус код 404.
    5. Проверить, что тело ответа содержит сообщение об ошибке.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать несуществующий ID пользователя
    nonexistent_user_id = 12345678

    # Шаг 3: Выполнить GET-запрос
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json"
    }
    response = requests.get_request(
        f"{base_url}/user/{nonexistent_user_id}",
        headers=headers
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 404
    assert response.status_code == 404, (
        f"Ожидаемый статус код 404, получен: {response.status_code}"
    )


def test_get_user_with_invalid_id_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос с некорректным значением ID пользователя.

    Шаги:
    1. Логин под администратором.
    2. Указать некорректное значение ID (строка вместо числа).
    3. Выполнить GET-запрос для получения данных пользователя.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать некорректное значение ID
    invalid_user_id = "abc"

    # Шаг 3: Выполнить GET-запрос
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json"
    }
    response = requests.get_request(
        f"{base_url}/user/{invalid_user_id}",
        headers=headers
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert isinstance(response_data["detail"], list), "Поле 'detail' должно быть списком"
    assert any(
        error["loc"] == ["path", "id"] and error["type"] == "int_parsing"
        for error in response_data["detail"]
    ), "Ответ не содержит ожидаемую ошибку о некорректном значении ID"


def test_get_user_without_authorization(base_url):
    """
    Проверяет, что сервер отклоняет запрос, если администратор не авторизован.

    Шаги:
    1. Указать корректный ID пользователя.
    2. Выполнить GET-запрос без заголовка Authorization.
    3. Проверить, что сервер возвращает статус код 401.
    """
    # Шаг 1: Указать корректный ID пользователя
    user_id = 1  # Замените на существующий ID

    # Шаг 2: Выполнить GET-запрос без заголовка Authorization
    headers = {
        "accept": "application/json"
    }
    response = requests.get_request(
        f"{base_url}/user/{user_id}",
        headers=headers
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 401
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )


def test_get_deleted_user_returns_404(base_url, signin_user, delete_user):
    """
    Проверяет, что сервер возвращает 404 при запросе данных удаленного пользователя.

    Шаги:
    1. Логин под администратором.
    2. Создать нового пользователя.
    3. Удалить созданного пользователя.
    4. Выполнить GET-запрос для получения данных удаленного пользователя.
    5. Проверить, что сервер возвращает статус код 404.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Создать нового пользователя
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    new_user_payload = {
        "email": "deleted_user_test@example.com",
        "role": "user",
        "is_active": True,
        "password": "SecurePass123!"
    }
    create_response = requests.post_request(
        f"{base_url}/user/",
        headers=headers,
        json=new_user_payload
    )
    assert create_response.status_code == 200, (
        f"Не удалось создать пользователя, статус код: {create_response.status_code}"
    )
    new_user = create_response.json()
    user_id = new_user["id"]

    # Шаг 3: Удалить созданного пользователя через фикстуру delete_user
    delete_user(user_id)

    # Шаг 4: Выполнить GET-запрос для получения данных удаленного пользователя
    get_response = requests.get_request(
        f"{base_url}/user/{user_id}",
        headers=headers
    )

    # Шаг 5: Проверить, что сервер возвращает статус код 404
    assert get_response.status_code == 404, (
        f"Ожидаемый статус код 404, получен: {get_response.status_code}"
    )
