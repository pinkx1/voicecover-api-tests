import os
import pytest
from api import requests


def test_update_phone_successfully_with_temp_user(base_url, create_user_with_login, delete_user):
    """
    Проверяет, что поле `phone` может быть успешно обновлено для временного пользователя,
    а остальные поля остаются неизменными.

    Шаги:
    1. Создать временного пользователя через фикстуру `create_user_with_login`.
    2. Выполнить PATCH-запрос для изменения поля `phone`.
    3. Проверить, что сервер возвращает статус код 200.
    4. Проверить, что поле `phone` в ответе обновлено.
    5. Проверить, что остальные поля остались неизменными.
    6. Удалить созданного пользователя через фикстуру `delete_user`.
    """
    # Шаг 1: Создать временного пользователя
    temp_user = create_user_with_login
    user_id = temp_user["id"]
    user_access_token = temp_user["access_token"]

    # Оригинальные данные пользователя
    original_data = {
        "lastname": "Test",
        "firstname": "User",
        "avatar": None,
        "email": temp_user["email"],
        "role": "user",
        "phone": None,
        "telegram": None,
        "telegram_chatid": None,
        "balance": 0.0,
        "is_active": True,
        "id": user_id,
    }

    try:
        # Шаг 2: Выполнить PATCH-запрос для изменения поля `phone`
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        update_payload = {
            "phone": "+1234567890",  # Новое значение для поля `phone`
        }
        response = requests.patch_request(
            f"{base_url}/user/me/", headers=headers, json=update_payload
        )

        # Шаг 3: Проверить статус код
        assert response.status_code == 200, (
            f"Ожидаемый статус код 200, получен: {response.status_code}"
        )

        # Шаг 4: Проверить, что поле `phone` в ответе обновлено
        response_data = response.json()
        assert "phone" in response_data, "Поле `phone` отсутствует в ответе"
        assert response_data["phone"] == "+1234567890", (
            f"Поле `phone` не обновлено. Ожидаемое: +1234567890, "
            f"полученное: {response_data['phone']}"
        )

        # Шаг 5: Проверить, что остальные поля остались неизменными
        for field, expected_value in original_data.items():
            if field == "phone":  # Пропускаем обновленное поле
                continue
            assert field in response_data, f"Поле `{field}` отсутствует в ответе"
            assert response_data[field] == expected_value, (
                f"Поле `{field}` изменилось. Ожидаемое: {expected_value}, "
                f"полученное: {response_data[field]}"
            )
    finally:
        # Шаг 6: Удалить временного пользователя
        delete_user(user_id)


def test_update_telegram_successfully_with_temp_user(base_url, create_user_with_login, delete_user):
    """
    Проверяет, что поле `telegram` может быть успешно обновлено для временного пользователя,
    а остальные поля остаются неизменными.

    Шаги:
    1. Создать временного пользователя через фикстуру `create_user_with_login`.
    2. Выполнить PATCH-запрос для изменения поля `telegram`.
    3. Проверить, что сервер возвращает статус код 200.
    4. Проверить, что поле `telegram` в ответе обновлено.
    5. Проверить, что остальные поля остались неизменными.
    6. Удалить созданного пользователя через фикстуру `delete_user`.
    """
    # Шаг 1: Создать временного пользователя
    temp_user = create_user_with_login
    user_id = temp_user["id"]
    user_access_token = temp_user["access_token"]

    # Оригинальные данные пользователя
    original_data = {
        "lastname": "Test",
        "firstname": "User",
        "avatar": None,
        "email": temp_user["email"],
        "role": "user",
        "phone": None,
        "telegram": None,
        "telegram_chatid": None,
        "balance": 0.0,
        "is_active": True,
        "id": user_id,
    }

    try:
        # Шаг 2: Выполнить PATCH-запрос для изменения поля `telegram`
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        update_payload = {
            "telegram": "@updated_telegram",  # Новое значение для поля `telegram`
        }
        response = requests.patch_request(
            f"{base_url}/user/me/", headers=headers, json=update_payload
        )

        # Шаг 3: Проверить статус код
        assert response.status_code == 200, (
            f"Ожидаемый статус код 200, получен: {response.status_code}"
        )

        # Шаг 4: Проверить, что поле `telegram` в ответе обновлено
        response_data = response.json()
        assert "telegram" in response_data, "Поле `telegram` отсутствует в ответе"
        assert response_data["telegram"] == "@updated_telegram", (
            f"Поле `telegram` не обновлено. Ожидаемое: @updated_telegram, "
            f"полученное: {response_data['telegram']}"
        )

        # Шаг 5: Проверить, что остальные поля остались неизменными
        for field, expected_value in original_data.items():
            if field == "telegram":  # Пропускаем обновленное поле
                continue
            assert field in response_data, f"Поле `{field}` отсутствует в ответе"
            assert response_data[field] == expected_value, (
                f"Поле `{field}` изменилось. Ожидаемое: {expected_value}, "
                f"полученное: {response_data[field]}"
            )
    finally:
        # Шаг 6: Удалить временного пользователя
        delete_user(user_id)


def test_update_lastname_successfully_with_temp_user(base_url, create_user_with_login, delete_user):
    """
    Проверяет, что поле `lastname` может быть успешно обновлено для временного пользователя,
    а остальные поля остаются неизменными.

    Шаги:
    1. Создать временного пользователя через фикстуру `create_user_with_login`.
    2. Выполнить PATCH-запрос для изменения поля `lastname`.
    3. Проверить, что сервер возвращает статус код 200.
    4. Проверить, что поле `lastname` в ответе обновлено.
    5. Проверить, что остальные поля остались неизменными.
    6. Удалить созданного пользователя через фикстуру `delete_user`.
    """
    # Шаг 1: Создать временного пользователя
    temp_user = create_user_with_login
    user_id = temp_user["id"]
    user_access_token = temp_user["access_token"]

    # Оригинальные данные пользователя
    original_data = {
        "lastname": "Test",
        "firstname": "User",
        "avatar": None,
        "email": temp_user["email"],
        "role": "user",
        "phone": None,
        "telegram": None,
        "telegram_chatid": None,
        "balance": 0.0,
        "is_active": True,
        "id": user_id,
    }

    try:
        # Шаг 2: Выполнить PATCH-запрос для изменения поля `lastname`
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        update_payload = {
            "lastname": "UpdatedLastName",  # Новое значение для поля `lastname`
        }
        response = requests.patch_request(
            f"{base_url}/user/me/", headers=headers, json=update_payload
        )

        # Шаг 3: Проверить статус код
        assert response.status_code == 200, (
            f"Ожидаемый статус код 200, получен: {response.status_code}"
        )

        # Шаг 4: Проверить, что поле `lastname` в ответе обновлено
        response_data = response.json()
        assert "lastname" in response_data, "Поле `lastname` отсутствует в ответе"
        assert response_data["lastname"] == "UpdatedLastName", (
            f"Поле `lastname` не обновлено. Ожидаемое: UpdatedLastName, "
            f"полученное: {response_data['lastname']}"
        )

        # Шаг 5: Проверить, что остальные поля остались неизменными
        for field, expected_value in original_data.items():
            if field == "lastname":  # Пропускаем обновленное поле
                continue
            assert field in response_data, f"Поле `{field}` отсутствует в ответе"
            assert response_data[field] == expected_value, (
                f"Поле `{field}` изменилось. Ожидаемое: {expected_value}, "
                f"полученное: {response_data[field]}"
            )
    finally:
        # Шаг 6: Удалить временного пользователя
        delete_user(user_id)


def test_update_firstname_successfully_with_temp_user(base_url, create_user_with_login, delete_user):
    """
    Проверяет, что поле `firstname` может быть успешно обновлено для временного пользователя,
    а остальные поля остаются неизменными.

    Шаги:
    1. Создать временного пользователя через фикстуру `create_user_with_login`.
    2. Выполнить PATCH-запрос для изменения поля `firstname`.
    3. Проверить, что сервер возвращает статус код 200.
    4. Проверить, что поле `firstname` в ответе обновлено.
    5. Проверить, что остальные поля остались неизменными.
    6. Удалить созданного пользователя через фикстуру `delete_user`.
    """
    # Шаг 1: Создать временного пользователя
    temp_user = create_user_with_login
    user_id = temp_user["id"]
    user_access_token = temp_user["access_token"]

    # Оригинальные данные пользователя
    original_data = {
        "lastname": "Test",
        "firstname": "User",
        "avatar": None,
        "email": temp_user["email"],
        "role": "user",
        "phone": None,
        "telegram": None,
        "telegram_chatid": None,
        "balance": 0.0,
        "is_active": True,
        "id": user_id,
    }

    try:
        # Шаг 2: Выполнить PATCH-запрос для изменения поля `firstname`
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        update_payload = {
            "firstname": "UpdatedFirstName",  # Новое значение для поля `firstname`
        }
        response = requests.patch_request(
            f"{base_url}/user/me/", headers=headers, json=update_payload
        )

        # Шаг 3: Проверить статус код
        assert response.status_code == 200, (
            f"Ожидаемый статус код 200, получен: {response.status_code}"
        )

        # Шаг 4: Проверить, что поле `firstname` в ответе обновлено
        response_data = response.json()
        assert "firstname" in response_data, "Поле `firstname` отсутствует в ответе"
        assert response_data["firstname"] == "UpdatedFirstName", (
            f"Поле `firstname` не обновлено. Ожидаемое: UpdatedFirstName, "
            f"полученное: {response_data['firstname']}"
        )

        # Шаг 5: Проверить, что остальные поля остались неизменными
        for field, expected_value in original_data.items():
            if field == "firstname":  # Пропускаем обновленное поле
                continue
            assert field in response_data, f"Поле `{field}` отсутствует в ответе"
            assert response_data[field] == expected_value, (
                f"Поле `{field}` изменилось. Ожидаемое: {expected_value}, "
                f"полученное: {response_data[field]}"
            )
    finally:
        # Шаг 6: Удалить временного пользователя
        delete_user(user_id)


def test_update_avatar_successfully_with_temp_user(base_url, create_user_with_login, delete_user):
    """
    Проверяет, что поле `avatar` может быть успешно обновлено для временного пользователя,
    а остальные поля остаются неизменными.

    Шаги:
    1. Создать временного пользователя через фикстуру `create_user_with_login`.
    2. Выполнить PATCH-запрос для изменения поля `avatar`.
    3. Проверить, что сервер возвращает статус код 200.
    4. Проверить, что поле `avatar` в ответе обновлено.
    5. Проверить, что остальные поля остались неизменными.
    6. Удалить созданного пользователя через фикстуру `delete_user`.
    """
    # Шаг 1: Создать временного пользователя
    temp_user = create_user_with_login
    user_id = temp_user["id"]
    user_access_token = temp_user["access_token"]

    # Оригинальные данные пользователя
    original_data = {
        "lastname": "Test",
        "firstname": "User",
        "avatar": None,
        "email": temp_user["email"],
        "role": "user",
        "phone": None,
        "telegram": None,
        "telegram_chatid": None,
        "balance": 0.0,
        "is_active": True,
        "id": user_id,
    }

    try:
        # Шаг 2: Выполнить PATCH-запрос для изменения поля `avatar`
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        update_payload = {
            "avatar": "https://example.com/new_avatar.png",  # Новое значение для поля `avatar`
        }
        response = requests.patch_request(
            f"{base_url}/user/me/", headers=headers, json=update_payload
        )

        # Шаг 3: Проверить статус код
        assert response.status_code == 200, (
            f"Ожидаемый статус код 200, получен: {response.status_code}"
        )

        # Шаг 4: Проверить, что поле `avatar` в ответе обновлено
        response_data = response.json()
        assert "avatar" in response_data, "Поле `avatar` отсутствует в ответе"
        assert response_data["avatar"] == "https://example.com/new_avatar.png", (
            f"Поле `avatar` не обновлено. Ожидаемое: https://example.com/new_avatar.png, "
            f"полученное: {response_data['avatar']}"
        )

        # Шаг 5: Проверить, что остальные поля остались неизменными
        for field, expected_value in original_data.items():
            if field == "avatar":  # Пропускаем обновленное поле
                continue
            assert field in response_data, f"Поле `{field}` отсутствует в ответе"
            assert response_data[field] == expected_value, (
                f"Поле `{field}` изменилось. Ожидаемое: {expected_value}, "
                f"полученное: {response_data[field]}"
            )
    finally:
        # Шаг 6: Удалить временного пользователя
        delete_user(user_id)


