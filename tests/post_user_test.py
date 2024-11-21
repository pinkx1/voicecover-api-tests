import os
import pytest
from api import requests


def test_create_user_with_valid_data_as_admin(base_url, signin_user):
    """
    Проверяет, что администратор может создать пользователя с корректными данными,
    и данные пользователя в ответе совпадают с отправленными.
    """
    # Проверка наличия переменных окружения
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    assert admin_email, "Переменная окружения ADMIN_EMAIL не задана"
    assert admin_password, "Переменная окружения ADMIN_PASSWORD не задана"

    # Логин под администратором
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Данные нового пользователя
    payload = {
        "lastname": "Ivanov",
        "firstname": "Ivan",
        "avatar": "https://example.com/avatar.png",
        "email": "ivanov@example.com",
        "role": "user",
        "phone": "+1234567890",
        "telegram_chatid": None,
        "balance": 0.0,
        "is_active": True,
        "password": "securepassword"
    }

    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    # Создание пользователя
    response = requests.post_request(
        f"{base_url}/user/",
        headers=headers,
        json=payload
    )

    # Проверка ответа
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    response_data = response.json()
    payload.pop("password")
    for key, value in payload.items():
        assert response_data[key] == value, (
            f"Значение '{key}' отличается. Ожидаемое: {value}, "
            f"полученное: {response_data[key]}"
        )


def test_create_user_with_minimal_data_as_admin(base_url, signin_user):
    """
    Проверяет, что администратор может создать пользователя с заполнением только обязательных полей.

    Шаги:
    1. Логин под администратором.
    2. Указать минимально необходимые данные для создания пользователя.
    3. Выполнить POST-запрос для создания нового пользователя.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что тело ответа содержит данные нового пользователя.
    """
    # Проверка наличия переменных окружения
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    assert admin_email, "Переменная окружения ADMIN_EMAIL не задана"
    assert admin_password, "Переменная окружения ADMIN_PASSWORD не задана"

    # Логин под администратором
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Данные нового пользователя с минимально необходимыми полями
    payload = {
        "email": "minimal@example.com",
        "role": "user",
        "is_active": True,
        "password": "minimalpassword"
    }

    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    # Создание пользователя
    response = requests.post_request(
        f"{base_url}/user/",
        headers=headers,
        json=payload
    )

    # Проверка ответа
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    response_data = response.json()
    payload.pop("password")
    for key, value in payload.items():
        assert response_data[key] == value, (
            f"Значение '{key}' отличается. Ожидаемое: {value}, "
            f"полученное: {response_data[key]}"
        )


def test_create_user_without_email_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос на создание пользователя без обязательного поля 'email'.

    Шаги:
    1. Логин под администратором.
    2. Сформировать данные нового пользователя без поля 'email'.
    3. Выполнить POST-запрос для создания нового пользователя.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит информацию о пропущенном поле 'email'.
    """
    # Проверка наличия переменных окружения
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    # Логин под администратором
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Данные нового пользователя без поля 'email'
    payload = {
        "role": "user",
        "is_active": True,
        "password": "password123"
    }

    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    # Попытка создания пользователя
    response = requests.post_request(
        f"{base_url}/user/",
        headers=headers,
        json=payload
    )

    # Проверка ответа
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )

    response_data = response.json()
    assert any(
        error["loc"] == ["body", "email"] and error["type"] == "missing"
        for error in response_data["detail"]
    ), "Ответ не содержит ожидаемой ошибки о пропущенном поле 'email'"


@pytest.mark.xfail(reason="Тест помечен как баг: сервер некорректно обрабатывает отсутствие поля 'role'")
def test_create_user_without_role_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос на создание пользователя без обязательного поля 'role'.

    Шаги:
    1. Логин под администратором.
    2. Сформировать данные нового пользователя без поля 'role'.
    3. Выполнить POST-запрос для создания нового пользователя.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит информацию о пропущенном поле 'role'.
    """
    # Проверка наличия переменных окружения
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    # Логин под администратором
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Данные нового пользователя без поля 'role'
    payload = {
        "email": "test_user@example.com",
        "is_active": True,
        "password": "password123"
    }

    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    # Попытка создания пользователя
    response = requests.post_request(
        f"{base_url}/user/",
        headers=headers,
        json=payload
    )

    # Проверка ответа
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )

    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail'"
    assert isinstance(response_data["detail"], list), "Поле 'detail' должно быть списком"
    assert any(
        error["loc"] == ["body", "role"] and error["type"] == "missing"
        for error in response_data["detail"]
    ), "Ответ не содержит ожидаемой ошибки о пропущенном поле 'role'"


@pytest.mark.xfail(reason="Тест помечен как баг: сервер некорректно обрабатывает отсутствие поля 'role'")
def test_create_user_without_is_active_field_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос, если поле 'is_active' отсутствует в теле запроса.

    Шаги:
    1. Логин под администратором.
    2. Указать данные для всех полей, кроме 'is_active'.
    3. Выполнить POST-запрос для создания нового пользователя.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки, указывающее на отсутствие поля 'is_active'.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать данные для всех полей, кроме 'is_active'
    payload = {
        "email": "testuser5@example.com",
        "role": "user",
        "password": "StrongPassword123!"
    }

    # Шаг 3: Выполнить POST-запрос для создания нового пользователя
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/user/",
        headers=headers,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )


def test_create_user_without_password_field_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос, если поле 'password' отсутствует в теле запроса.

    Шаги:
    1. Логин под администратором.
    2. Указать данные для всех полей, кроме 'password'.
    3. Выполнить POST-запрос для создания нового пользователя.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки, указывающее на отсутствие поля 'password'.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать данные для всех полей, кроме 'password'
    payload = {
        "email": "testuser6@example.com",
        "role": "user",
        "is_active": True
    }

    # Шаг 3: Выполнить POST-запрос для создания нового пользователя
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/user/",
        headers=headers,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )


@pytest.mark.xfail(reason="Сервер не валидирует обязательные поля 'role' и 'is_active' при пустом JSON.")
def test_create_user_with_empty_json_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер корректно обрабатывает запрос с пустым JSON при создании пользователя.

    Шаги:
    1. Логин под администратором.
    2. Указать пустое тело запроса (JSON `{}`).
    3. Выполнить POST-запрос для создания нового пользователя.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки, указывающее на отсутствие обязательных полей.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать пустое тело запроса
    payload = {}

    # Шаг 3: Выполнить POST-запрос для создания нового пользователя
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/user/",
        headers=headers,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert isinstance(response_data["detail"], list), "Поле 'detail' должно быть списком"
    missing_fields = {"email", "role", "is_active", "password"}
    actual_missing = {
        error["loc"][-1]
        for error in response_data["detail"]
        if error["type"] == "missing"
    }
    assert missing_fields.issubset(actual_missing), (
        f"Ожидаемые пропущенные поля: {missing_fields}, полученные: {actual_missing}"
    )


@pytest.mark.xfail(reason="сервер позволяет создавать пользователей с дублирующим email")
def test_create_user_with_duplicate_email_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос на создание пользователя с дублирующим email.

    Шаги:
    1. Логин под администратором.
    2. Указать email, который уже зарегистрирован в системе.
    3. Выполнить POST-запрос для создания пользователя.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки о дублирующемся email.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать дублирующий email
    duplicate_email = "user1337_empty@mail.com"
    payload = {
        "email": duplicate_email,
        "role": "user",
        "is_active": True,
        "password": "SecurePass123!"
    }

    # Шаг 3: Выполнить POST-запрос для создания пользователя
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/user/",
        headers=headers,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки о дублирующемся email
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert any(
        error["loc"] == ["body", "email"] and "already exists" in error["msg"].lower()
        for error in response_data["detail"]
    ), "Ответ не содержит ожидаемую ошибку о дублирующемся email"


def test_create_user_with_invalid_email_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос с некорректным email при создании пользователя.

    Шаги:
    1. Логин под администратором.
    2. Указать некорректное значение поля email.
    3. Выполнить POST-запрос для создания пользователя.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки о некорректном формате email.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать некорректное значение email
    invalid_email = "invalid-email"
    payload = {
        "email": invalid_email,
        "role": "user",
        "is_active": True,
        "password": "SecurePass123!"
    }

    # Шаг 3: Выполнить POST-запрос для создания пользователя
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/user/",
        headers=headers,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки о некорректном формате email
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert any(
        error["loc"] == ["body", "email"] and error["type"] == "value_error"
        for error in response_data["detail"]
    ), (
        "Ответ не содержит ожидаемую ошибку о некорректном email: "
        f"{response_data['detail']}"
    )


def test_create_user_with_invalid_email_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос с некорректным email при создании пользователя.

    Шаги:
    1. Логин под администратором.
    2. Указать некорректное значение поля email.
    3. Выполнить POST-запрос для создания пользователя.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки о некорректном формате email.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать некорректное значение email
    invalid_email = "invalid-email"
    payload = {
        "email": invalid_email,
        "role": "user",
        "is_active": True,
        "password": "SecurePass123!"
    }

    # Шаг 3: Выполнить POST-запрос для создания пользователя
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/user/",
        headers=headers,
        json=payload
    )

    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )


def test_create_user_with_invalid_is_active_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос с некорректным значением поля is_active при создании пользователя.

    Шаги:
    1. Логин под администратором.
    2. Указать некорректное значение поля is_active.
    3. Выполнить POST-запрос для создания пользователя.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки о некорректном значении is_active.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать некорректное значение is_active
    invalid_is_active = "not_a_boolean"  # Некорректное значение
    payload = {
        "email": "new_user@example.com",
        "role": "user",
        "is_active": invalid_is_active,
        "password": "SecurePass123!"
    }

    # Шаг 3: Выполнить POST-запрос для создания пользователя
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/user/",
        headers=headers,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки о некорректном значении is_active
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert any(
        error["loc"] == ["body", "is_active"] and error["type"] == "bool_parsing"
        for error in response_data["detail"]
    ), (
        "Ответ не содержит ожидаемую ошибку о некорректном значении is_active: "
        f"{response_data['detail']}"
    )


def test_create_user_with_empty_password_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос с пустым паролем при создании пользователя.

    Шаги:
    1. Логин под администратором.
    2. Указать пустое значение поля password.
    3. Выполнить POST-запрос для создания пользователя.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки о слишком коротком пароле.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать пустое значение password
    empty_password = ""
    payload = {
        "email": "empty_password_user@example.com",
        "role": "user",
        "is_active": True,
        "password": empty_password
    }

    # Шаг 3: Выполнить POST-запрос для создания пользователя
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/user/",
        headers=headers,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки о слишком коротком пароле
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert any(
        error["loc"] == ["body", "password"] and error["type"] == "string_too_short"
        for error in response_data["detail"]
    ), (
        "Ответ не содержит ожидаемую ошибку о слишком коротком пароле: "
        f"{response_data['detail']}"
    )


def test_create_user_without_authorization(base_url):
    """
    Проверяет, что сервер запрещает запрос на создание пользователя без авторизации.

    Шаги:
    1. Указать данные для создания пользователя.
    2. Выполнить POST-запрос без авторизационного заголовка.
    3. Проверить, что сервер возвращает статус код 401.
    4. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Указать данные для создания пользователя
    payload = {
        "email": "unauthorized_user@example.com",
        "role": "user",
        "is_active": True,
        "password": "SecurePass123!"
    }

    # Шаг 2: Выполнить POST-запрос без авторизационного заголовка
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/user/",
        headers=headers,
        json=payload
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 401
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )


