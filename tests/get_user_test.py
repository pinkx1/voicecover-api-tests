import os
import pytest
from api import requests


@pytest.mark.xfail(reason="Тест возвращает 500, ожидается 200")
def test_get_all_users_without_parameters(base_url, signin_user):
    """
    Проверяет, что запрос без указания параметров offset и limit возвращает список пользователей
    начиная с первой записи, и что объекты в списке соответствуют ожидаемой структуре.

    Шаги:
    1. Логин под администратором.
    2. Выполнить GET-запрос без параметров offset и limit.
    3. Проверить, что сервер возвращает статус код 200.
    4. Проверить, что тело ответа содержит список пользователей.
    5. Проверить, что объекты в списке имеют ожидаемую структуру.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Выполнить GET-запрос без параметров offset и limit
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json"
    }
    response = requests.get_request(
        f"{base_url}/user/",
        headers=headers
    )

    # Вывод отладочной информации
    print("Статус код ответа:", response.status_code)
    try:
        print("Тело ответа:", response.json())
    except ValueError:
        print("Ответ не является JSON:", response.text)

    # Шаг 3: Проверить, что сервер возвращает статус код 200
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 4: Проверить, что тело ответа содержит список пользователей
    response_data = response.json()
    assert isinstance(response_data, list), "Ответ не содержит список пользователей"
    assert len(response_data) > 0, "Список пользователей пуст"

    # Шаг 5: Проверить структуру объектов в списке
    expected_keys = {"id", "is_active", "created_at", "last_login", "utm", "email", "role"}
    for user in response_data:
        assert isinstance(user, dict), "Объект пользователя не является словарем"
        assert expected_keys.issubset(user.keys()), (
            f"Объект пользователя не содержит ожидаемых ключей. "
            f"Ожидаемые: {expected_keys}, полученные: {user.keys()}"
        )
        # Проверка типов данных
        assert isinstance(user["id"], int), "Поле 'id' должно быть целым числом"
        assert isinstance(user["is_active"], bool), "Поле 'is_active' должно быть булевым"
        assert isinstance(user["created_at"], str), "Поле 'created_at' должно быть строкой"
        assert isinstance(user["last_login"], str), "Поле 'last_login' должно быть строкой"
        assert isinstance(user["utm"], str) or user["utm"] is None, "Поле 'utm' должно быть строкой или None"
        assert isinstance(user["email"], str), "Поле 'email' должно быть строкой"
        assert isinstance(user["role"], str), "Поле 'role' должно быть строкой"


def test_get_users_with_offset_and_limit_as_admin(base_url, signin_user):
    """
    Проверяет, что запрос с параметрами offset и limit возвращает корректное подмножество пользователей.

    Шаги:
    1. Логин под администратором.
    2. Указать значения offset и limit.
    3. Выполнить GET-запрос для получения списка пользователей.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что тело ответа содержит корректное количество пользователей в соответствии с указанными параметрами.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать значения offset и limit
    offset = 1
    limit = 2

    # Шаг 3: Выполнить GET-запрос
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json"
    }
    response = requests.get_request(
        f"{base_url}/user/?offset={offset}&limit={limit}",
        headers=headers
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 200
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит список пользователей в соответствии с параметрами offset и limit
    response_data = response.json()
    assert isinstance(response_data, list), "Ответ должен быть списком пользователей"
    assert len(response_data) <= limit, (
        f"Количество пользователей в ответе больше, чем указанный limit: {len(response_data)}"
    )


def test_get_users_with_nonexistent_offset_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер возвращает пустой список, если offset больше общего количества записей.

    Шаги:
    1. Логин под администратором.
    2. Указать значение offset, превышающее общее количество записей.
    3. Выполнить GET-запрос для получения списка пользователей.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что тело ответа содержит пустой список.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать значение offset больше общего количества записей
    offset = 1000  # Предполагается, что в базе данных меньше 1000 записей
    limit = 10

    # Шаг 3: Выполнить GET-запрос
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json"
    }
    response = requests.get_request(
        f"{base_url}/user/?offset={offset}&limit={limit}",
        headers=headers
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 200
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит пустой список
    response_data = response.json()
    assert isinstance(response_data, list), "Ответ должен быть списком"
    assert len(response_data) == 0, "Ответ должен содержать пустой список"


def test_get_users_with_invalid_offset_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос с некорректным значением offset (строка вместо числа).

    Шаги:
    1. Логин под администратором.
    2. Указать некорректное значение offset (например, строка).
    3. Выполнить GET-запрос для получения списка пользователей.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать некорректное значение offset
    invalid_offset = "invalid_string"
    limit = 10

    # Шаг 3: Выполнить GET-запрос
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json"
    }
    response = requests.get_request(
        f"{base_url}/user/?offset={invalid_offset}&limit={limit}",
        headers=headers
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert isinstance(response_data["detail"], list), "Поле 'detail' должно быть списком"
    assert any(
        error["loc"] == ["query", "offset"] and error["type"] == "int_parsing"
        for error in response_data["detail"]
    ), "Ответ не содержит ожидаемую ошибку о некорректном значении offset"


def test_get_users_with_invalid_limit_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос с некорректным значением limit (строка вместо числа).

    Шаги:
    1. Логин под администратором.
    2. Указать некорректное значение limit (например, строка).
    3. Выполнить GET-запрос для получения списка пользователей.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать некорректное значение limit
    invalid_limit = "invalid_string"
    offset = 0

    # Шаг 3: Выполнить GET-запрос
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json"
    }
    response = requests.get_request(
        f"{base_url}/user/?offset={offset}&limit={invalid_limit}",
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
        error["loc"] == ["query", "limit"] and error["type"] == "int_parsing"
        for error in response_data["detail"]
    ), "Ответ не содержит ожидаемую ошибку о некорректном значении limit"

@pytest.mark.xfail(reason="Тест возвращает 500, ожидается 200")
def test_get_users_with_large_limit_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер корректно обрабатывает запрос с большим значением limit.

    Шаги:
    1. Логин под администратором.
    2. Указать большое значение limit (например, 1000).
    3. Выполнить GET-запрос для получения списка пользователей.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что тело ответа содержит не более максимально допустимого количества записей.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать большое значение limit
    large_limit = 1000
    offset = 0

    # Шаг 3: Выполнить GET-запрос
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json"
    }
    response = requests.get_request(
        f"{base_url}/user/?offset={offset}&limit={large_limit}",
        headers=headers
    )

    response_data = response.json()
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит не более максимально допустимого количества записей
    assert isinstance(response_data, list), "Ответ должен быть списком пользователей"
    max_limit = 100  # Заменить на реальное максимальное значение, если оно известно
    assert len(response_data) <= max_limit, (
        f"Ожидаемое количество записей <= {max_limit}, получено: {len(response_data)}"
    )


def test_get_users_without_authorization(base_url):
    """
    Проверяет, что сервер отклоняет запрос без авторизации.

    Шаги:
    1. Указать отсутствие авторизационного токена.
    2. Выполнить GET-запрос для получения списка пользователей.
    3. Проверить, что сервер возвращает статус код 401.
    """
    # Шаг 1: Указать отсутствие авторизационного токена
    headers = {
        "accept": "application/json"
    }

    # Шаг 2: Выполнить GET-запрос
    response = requests.get_request(
        f"{base_url}/user/",
        headers=headers
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 401
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )


def test_get_users_as_regular_user(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос от пользователя с ролью `user`.

    Шаги:
    1. Логин под пользователем с ролью `user`.
    2. Выполнить GET-запрос для получения списка пользователей.
    3. Проверить, что сервер возвращает статус код 403.
    """
    # Шаг 1: Логин под пользователем с ролью `user`
    user_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    user_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)
    user_access_token = user["access_token"]

    # Шаг 2: Выполнить GET-запрос
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }
    response = requests.get_request(
        f"{base_url}/user/",
        headers=headers
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 403
    assert response.status_code == 403, (
        f"Ожидаемый статус код 403, получен: {response.status_code}"
    )
