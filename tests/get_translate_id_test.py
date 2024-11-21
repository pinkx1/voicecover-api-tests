import os
import time

import pytest
from api import requests


def test_get_translation_by_id(base_url, create_user_with_login, create_admin, add_translation, delete_translation, delete_user):
    """
    Проверяет получение перевода по корректному ID.

    Шаги:
    1. Создаётся аккаунт пользователя.
    2. Создаётся аккаунт администратора.
    3. Пользователем создаётся перевод.
    4. Проверяется, что пользователь имеет доступ к своему переводу.
    5. Проверяется, что администратор имеет доступ к переводу пользователя.
    6. Удаляются созданные перевод, пользователь и администратор.
    """
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    user_access_token = user["access_token"]
    user_id = user["id"]

    # Шаг 2: Создание администратора
    admin = create_admin
    admin_access_token = admin["access_token"]
    admin_id = admin["id"]

    # Шаг 3: Пользователь создаёт перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 4: Проверка доступа пользователя к переводу
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_access_token}"
    }
    user_response = requests.get_request(f"{base_url}/translate/{translation_id}", headers=headers)
    assert user_response.status_code == 200, (
        f"Ожидаемый статус код 200 для пользователя, получен: {user_response.status_code}"
    )
    user_response_data = user_response.json()
    assert user_response_data["id"] == translation_id, "ID перевода в ответе не совпадает с ожидаемым"

    # Шаг 5: Проверка доступа администратора к переводу
    headers["Authorization"] = f"Bearer {admin_access_token}"
    admin_response = requests.get_request(f"{base_url}/translate/{translation_id}", headers=headers)
    assert admin_response.status_code == 200, (
        f"Ожидаемый статус код 200 для администратора, получен: {admin_response.status_code}"
    )
    admin_response_data = admin_response.json()
    assert admin_response_data["id"] == translation_id, "ID перевода в ответе не совпадает с ожидаемым"

    # Шаг 6: Удаление перевода и пользователей
    delete_translation(user_access_token, translation_id)
    delete_user(user_id)
    delete_user(admin_id)


def test_get_translation_with_invalid_id(base_url, create_user_with_login, delete_user):
    """
    Проверяет, что сервер корректно обрабатывает запрос с некорректным значением ID.

    Шаги:
    1. Создаётся аккаунт пользователя.
    2. Выполняется запрос с некорректным значением ID (например, 'abc').
    3. Проверяется, что сервер возвращает статус код 422 и описание ошибки.
    4. Удаляется созданный пользователь.
    """
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    access_token = user["access_token"]
    user_id = user["id"]

    # Шаг 2: Выполнение запроса с некорректным ID
    invalid_id = "abc"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/{invalid_id}", headers=headers)

    # Шаг 3: Проверка ответа
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )
    response_data = response.json()
    assert "detail" in response_data, "В ответе отсутствует описание ошибки"
    assert any(error["loc"][-1] == "id" for error in response_data["detail"]), (
        "В описании ошибки отсутствует указание на параметр 'id'"
    )

    # Шаг 4: Удаление пользователя
    delete_user(user_id)


def test_get_translation_with_nonexistent_id(base_url, create_user_with_login, delete_user):
    """
    Проверяет, что сервер корректно обрабатывает запрос с несуществующим ID.

    Шаги:
    1. Создаётся аккаунт пользователя.
    2. Выполняется запрос с несуществующим значением ID (например, '999999').
    3. Проверяется, что сервер возвращает статус код 404 и описание ошибки.
    4. Удаляется созданный пользователь.
    """
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    access_token = user["access_token"]
    user_id = user["id"]

    # Шаг 2: Выполнение запроса с несуществующим ID
    nonexistent_id = "999999"
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/{nonexistent_id}", headers=headers)

    # Шаг 3: Проверка ответа
    assert response.status_code == 404, (
        f"Ожидаемый статус код 404, получен: {response.status_code}"
    )
    response_data = response.json()
    assert "detail" in response_data, "В ответе отсутствует описание ошибки"
    assert response_data["detail"] == "Not found"

    # Шаг 4: Удаление пользователя
    delete_user(user_id)


def test_user_cannot_access_other_user_translation(
        base_url, create_user_with_login, add_translation, delete_translation, delete_user
):
    """
    Проверяет, что пользователь с ролью `user` не может получить доступ к переводу,
    который принадлежит другому пользователю.

    Шаги:
    1. Создаётся первый пользователь.
    2. Первый пользователь загружает перевод.
    3. Заранее созданный статичный пользователь пытается получить доступ к переводу первого пользователя.
    4. Проверяется, что сервер возвращает статус код 404 (Not Found).
    5. Удаляются созданный перевод и пользователь.
    """
    # Шаг 1: Создание первого пользователя
    first_user = create_user_with_login
    first_user_token = first_user["access_token"]
    first_user_id = first_user["id"]

    # Шаг 2: Первый пользователь загружает перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(first_user_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 3: Заранее созданный пользователь пытается получить доступ к переводу первого пользователя
    static_user_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    static_user_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    signin_payload = {"username": static_user_email, "password": static_user_password}
    signin_response = requests.post_request(f"{base_url}/auth/signin", data=signin_payload)
    assert signin_response.status_code == 200, (
        f"Не удалось авторизовать статичного пользователя: {signin_response.status_code}, {signin_response.text}"
    )
    static_user_token = signin_response.json()["access_token"]

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {static_user_token}",
    }
    response = requests.get_request(f"{base_url}/translate/{translation_id}", headers=headers)

    # Шаг 4: Проверка ответа
    assert response.status_code == 404, (
        f"Ожидаемый статус код 404 (Not Found), получен: {response.status_code}, тело: {response.text}"
    )

    # Шаг 5: Удаление перевода и первого пользователя
    delete_translation(first_user_token, translation_id)
    delete_user(first_user_id)


def test_access_translation_without_authorization(base_url, create_user_with_login, add_translation, delete_translation, delete_user):
    """
    Проверяет, что сервер запрещает доступ к переводу без авторизации.

    Шаги:
    1. Создаётся пользователь.
    2. Пользователем создаётся перевод.
    3. Выполняется запрос к переводу без авторизации.
    4. Проверяется, что сервер возвращает статус код 401 (Unauthorized).
    5. Удаляются созданные перевод и пользователь.
    """
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    user_access_token = user["access_token"]
    user_id = user["id"]

    # Шаг 2: Пользователь создаёт перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 3: Запрос к переводу без авторизации
    response = requests.get_request(f"{base_url}/translate/{translation_id}")

    # Шаг 4: Проверка ответа
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401 (Unauthorized), получен: {response.status_code}, тело: {response.text}"
    )

    # Шаг 5: Удаление перевода и пользователя
    delete_translation(user_access_token, translation_id)
    delete_user(user_id)
