import os
import pytest
from api import requests


def test_update_user_with_valid_data_as_admin(base_url, signin_user, create_user_with_login, delete_user):
    """
    Проверяет, что администратор может успешно обновить данные пользователя при передаче валидного тела запроса.

    Шаги:
    1. Создать нового пользователя через фикстуру `create_user_with_login`.
    2. Логин под администратором.
    3. Обновить данные созданного пользователя.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что данные пользователя в ответе соответствуют обновленным данным.
    6. Удалить созданного пользователя.
    """
    # Шаг 1: Создать нового пользователя
    new_user = create_user_with_login
    user_id = new_user["id"]

    # Шаг 2: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    try:
        # Шаг 3: Обновить данные созданного пользователя
        headers = {
            "Authorization": f"Bearer {admin_access_token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        update_payload = {
            "firstname": "UpdatedFirstName",
            "lastname": "UpdatedLastName",
            "phone": "+1234567890",
            "telegram": "@updated_telegram",
            "avatar": "updated_avatar_url"
        }
        update_response = requests.patch_request(
            f"{base_url}/user/{user_id}",
            headers=headers,
            json=update_payload
        )

        # Шаг 4: Проверить, что сервер возвращает статус код 200
        assert update_response.status_code == 200, (
            f"Ожидаемый статус код 200, получен: {update_response.status_code}"
        )

        # Шаг 5: Проверить, что данные пользователя в ответе соответствуют обновленным данным
        updated_user = update_response.json()
        for key, value in update_payload.items():
            assert updated_user[key] == value, (
                f"Поле {key} имеет значение {updated_user[key]}, ожидалось {value}"
            )

    finally:
        # Шаг 6: Удалить созданного пользователя
        delete_user(user_id)


def test_update_partial_user_data_as_admin(base_url, signin_user, create_user_with_login, delete_user):
    """
    Проверяет, что администратор может обновить только часть данных пользователя,
    оставив остальные поля неизменными.

    Шаги:
    1. Создать нового пользователя через фикстуру `create_user_with_login`.
    2. Логин под администратором.
    3. Обновить только часть данных созданного пользователя.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что обновленные поля изменились, а неизмененные остались прежними.
    6. Удалить созданного пользователя.
    """
    # Шаг 1: Создать нового пользователя
    new_user = create_user_with_login
    user_id = new_user["id"]
    original_data = {
        "lastname": "Test",
        "firstname": "User",
        "role": "user",
        "email": new_user["email"],
        "balance": 0,
        "is_active": True,
        "phone": None,
        "telegram": None,
        "avatar": None
    }

    # Шаг 2: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    try:
        # Шаг 3: Обновить только часть данных созданного пользователя
        headers = {
            "Authorization": f"Bearer {admin_access_token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        partial_update_payload = {
            "firstname": "UpdatedFirstName"
        }

        update_response = requests.patch_request(
            f"{base_url}/user/{user_id}",
            headers=headers,
            json=partial_update_payload
        )
        assert update_response.status_code == 200, (
            f"Ожидаемый статус код 200, получен: {update_response.status_code}"
        )

        updated_data = update_response.json()

        # Шаг 4: Проверить, что обновленные поля изменились
        assert updated_data["firstname"] == "UpdatedFirstName", (
            f"Поле firstname должно быть обновлено, получено: {updated_data['firstname']}"
        )

        # Шаг 5: Проверить, что неизмененные поля остались прежними
        assert updated_data["lastname"] == original_data["lastname"], (
            f"Поле lastname не должно быть изменено, получено: {updated_data['lastname']}"
        )
        assert updated_data["email"] == original_data["email"], (
            f"Поле email не должно быть изменено, получено: {updated_data['email']}"
        )
        assert updated_data["role"] == original_data["role"], (
            f"Поле role не должно быть изменено, получено: {updated_data['role']}"
        )
        assert updated_data["balance"] == original_data["balance"], (
            f"Поле balance не должно быть изменено, получено: {updated_data['balance']}"
        )
        assert updated_data["is_active"] == original_data["is_active"], (
            f"Поле is_active не должно быть изменено, получено: {updated_data['is_active']}"
        )
        assert updated_data["phone"] == original_data["phone"], (
            f"Поле phone не должно быть изменено, получено: {updated_data['phone']}"
        )
        assert updated_data["telegram"] == original_data["telegram"], (
            f"Поле telegram не должно быть изменено, получено: {updated_data['telegram']}"
        )
        assert updated_data["avatar"] == original_data["avatar"], (
            f"Поле avatar не должно быть изменено, получено: {updated_data['avatar']}"
        )
    finally:
        # Шаг 6: Удалить созданного пользователя
        delete_user(user_id)


@pytest.mark.xfail(reason="Баг на бэкенде: сервер некорректно обрабатывает некорректные значения в полях role, is_active, email")
def test_update_user_with_invalid_data_as_admin(base_url, signin_user, create_user_with_login, delete_user):
    """
    Проверяет, что сервер корректно отклоняет запрос с некорректными значениями в полях:
    - `role` (например, `invalid_role`),
    - `is_active` (например, строка вместо boolean),
    - `email` (например, `invalid-email`).

    Шаги:
    1. Создать нового пользователя через фикстуру `create_user_with_login`.
    2. Логин под администратором.
    3. Выполнить запрос с некорректными значениями полей.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибок.
    6. Удалить созданного пользователя.
    """
    # Шаг 1: Создать нового пользователя
    new_user = create_user_with_login
    user_id = new_user["id"]

    # Шаг 2: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    try:
        # Шаг 3: Выполнить запрос с некорректными значениями полей
        headers = {
            "Authorization": f"Bearer {admin_access_token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        invalid_payloads = [
            {"role": "invalid_role"},                # Некорректное значение role
            {"is_active": "not_a_boolean"},          # Некорректное значение is_active
            {"email": "invalid-email"}               # Некорректное значение email
        ]

        for payload in invalid_payloads:
            response = requests.patch_request(
                f"{base_url}/user/{user_id}",
                headers=headers,
                json=payload
            )

            # Шаг 4: Проверить, что сервер возвращает статус код 422
            assert response.status_code == 422, (
                f"Ожидаемый статус код 422, получен: {response.status_code} при данных: {payload}"
            )

            # Шаг 5: Проверить, что тело ответа содержит описание ошибок
            response_data = response.json()
            assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
            assert isinstance(response_data["detail"], list), "Поле 'detail' должно быть списком"

            # Проверка на конкретные ошибки
            if "role" in payload:
                assert any(
                    error["loc"][-1] == "role" and error["type"] == "enum"
                    for error in response_data["detail"]
                ), "Ответ не содержит ожидаемую ошибку о некорректном значении role"
            elif "is_active" in payload:
                assert any(
                    error["loc"][-1] == "is_active" and error["type"] == "bool_parsing"
                    for error in response_data["detail"]
                ), "Ответ не содержит ожидаемую ошибку о некорректном значении is_active"
            elif "email" in payload:
                assert any(
                    error["loc"][-1] == "email" and error["type"] == "value_error"
                    for error in response_data["detail"]
                ), "Ответ не содержит ожидаемую ошибку о некорректном значении email"

    finally:
        # Шаг 6: Удалить созданного пользователя
        delete_user(user_id)


@pytest.mark.xfail(reason="Пятисотит в ответе")
def test_update_nonexistent_user_as_admin(base_url, signin_user):
    """
    Проверяет, что сервер корректно обрабатывает запрос на обновление данных несуществующего пользователя.

    Шаги:
    1. Логин под администратором.
    2. Указать несуществующий ID пользователя.
    3. Выполнить PATCH-запрос для обновления данных.
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

    # Шаг 3: Выполнить PATCH-запрос
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    update_payload = {
        "firstname": "NonExistent",
        "lastname": "User"
    }
    response = requests.patch_request(
        f"{base_url}/user/{nonexistent_user_id}",
        headers=headers,
        json=update_payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 404
    assert response.status_code == 404, (
        f"Ожидаемый статус код 404, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит сообщение об ошибке
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с сообщением об ошибке"
    assert response_data["detail"] == "User not found", (
        f"Ожидаемое сообщение об ошибке: 'User not found', полученное: {response_data['detail']}"
    )


def test_update_user_without_authorization(base_url, create_user_with_login, delete_user):
    """
    Проверяет, что сервер отклоняет запрос на обновление данных пользователя без авторизации.

    Шаги:
    1. Создать нового пользователя через фикстуру `create_user_with_login`.
    2. Выполнить PATCH-запрос для обновления данных без передачи заголовка авторизации.
    3. Проверить, что сервер возвращает статус код 401.
    4. Удалить созданного пользователя.
    """
    # Шаг 1: Создать нового пользователя
    new_user = create_user_with_login
    user_id = new_user["id"]

    try:
        # Шаг 2: Выполнить PATCH-запрос без авторизации
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        update_payload = {
            "firstname": "Unauthorized",
            "lastname": "Request"
        }
        response = requests.patch_request(
            f"{base_url}/user/{user_id}",
            headers=headers,
            json=update_payload
        )

        # Шаг 3: Проверить, что сервер возвращает статус код 401
        assert response.status_code == 401, (
            f"Ожидаемый статус код 401, получен: {response.status_code}"
        )

    finally:
        # Шаг 4: Удалить созданного пользователя
        delete_user(user_id)


def test_update_user_as_static_user(base_url, signin_user, create_user_with_login, delete_user):
    """
    Проверяет, что пользователь с ролью `user` не может обновить данные другого пользователя.

    Шаги:
    1. Создать пользователя.
    2. Авторизоваться под другим статичным пользователем.
    3. Выполнить PATCH-запрос для обновления данных созданного пользователя.
    4. Проверить, что сервер возвращает статус код 403.
    5. Удалить созданного пользователя.
    """
    # Шаг 1: Создать пользователя
    target_user = create_user_with_login
    target_user_id = target_user["id"]

    # Шаг 2: Авторизоваться под статичным пользователем
    static_user_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    static_user_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    static_user = signin_user(static_user_email, static_user_password)
    static_user_token = static_user["access_token"]

    try:
        # Шаг 3: Выполнить PATCH-запрос под статичным пользователем
        headers = {
            "Authorization": f"Bearer {static_user_token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        update_payload = {
            "firstname": "Unauthorized",
            "lastname": "Attempt"
        }
        response = requests.patch_request(
            f"{base_url}/user/{target_user_id}",
            headers=headers,
            json=update_payload
        )

        # Шаг 4: Проверить, что сервер возвращает статус код 403
        assert response.status_code == 403, (
            f"Ожидаемый статус код 403, получен: {response.status_code}"
        )
    finally:
        # Шаг 5: Удалить созданного пользователя
        delete_user(target_user_id)


def test_update_user_with_immutable_id(base_url, signin_user, create_user_with_login, delete_user):
    """
    Проверяет, что сервер корректно обрабатывает запрос с попыткой изменения поля `id`.

    Шаги:
    1. Создать пользователя через фикстуру `create_user_with_login`.
    2. Авторизоваться под администратором.
    3. Выполнить PATCH-запрос для изменения поля `id`.
    4. Проверить, что сервер игнорирует изменение этого поля.
    5. Удалить созданного пользователя.
    """
    # Шаг 1: Создать пользователя
    target_user = create_user_with_login
    target_user_id = target_user["id"]

    # Шаг 2: Авторизоваться под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_token = admin["access_token"]

    try:
        # Шаг 3: Попытка изменить поле `id`
        headers = {
            "Authorization": f"Bearer {admin_token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        update_payload = {"id": 999}  # Попытка изменить ID
        response = requests.patch_request(
            f"{base_url}/user/{target_user_id}",
            headers=headers,
            json=update_payload
        )

        assert response.status_code in {200, 422}, (
            f"Ожидаемый статус код 200 или 422, получен: {response.status_code}"
        )

        response_data = response.json()
        assert response_data["id"] == target_user_id, (
            f"Поле `id` должно быть неизменным. Ожидаемое: {target_user_id}, полученное: {response_data['id']}"
        )

    finally:
        # Шаг 5: Удалить пользователя
        delete_user(target_user_id)


