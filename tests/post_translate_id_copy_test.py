import os
import pytest
from api import requests


def test_copy_translation_with_feedback(base_url, create_user_with_login, add_translation, delete_translation):
    """
    Проверяет успешное копирование перевода по корректному ID, включая поле feedback.

    Шаги:
    1. Создать пользователя.
    2. Загрузить перевод.
    3. Создать feedback для перевода.
    4. Выполнить запрос копирования перевода.
    5. Проверить, что сервер возвращает статус код 200.
    6. Проверить корректность полей в копии (измененные и неизмененные).
    7. Удалить копию и оригинальный перевод.
    """
    # Шаг 1: Создать пользователя
    user = create_user_with_login
    user_access_token = user["access_token"]

    # Шаг 2: Загрузить перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)

    original_translation = add_translation(user_access_token, test_video_path)
    original_id = original_translation["id"]

    # Шаг 3: Создать feedback для перевода
    feedback_value = 5
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    feedback_response = requests.post_request(
        f"{base_url}/translate/{original_id}/feedback/",
        headers=headers,
        json=feedback_value
    )
    assert feedback_response.status_code == 200, (
        f"Ожидаемый статус код 200 для создания feedback, получен: {feedback_response.status_code}"
    )

    # Шаг 4: Выполнить запрос копирования перевода
    copy_response = requests.post_request(
        f"{base_url}/translate/{original_id}/copy/",
        headers=headers
    )
    assert copy_response.status_code == 200, (
        f"Ожидаемый статус код 200 для копирования перевода, получен: {copy_response.status_code}"
    )
    copy_translation = copy_response.json()

    # Шаг 5: Проверить корректность полей
    # Поля, которые должны оставаться неизменными между оригиналом и копией
    for field in [
        "language",
        "save_origin_voice",
        "has_logo",
        "notification",
        "voice_clone",
        "lipsync",
        "subtitle_download",
        "subtitle_on_video",
        "subtitle_edit",
        "voice_gender",
        "voice_count",
        "video",
        "owner"
    ]:
        assert copy_translation[field] == original_translation[field], (
            f"Поле {field} должно совпадать между оригиналом и копией"
        )

    # Поля, которые должны отличаться
    assert copy_translation["id"] != original_translation["id"], "ID копии должен отличаться от оригинала"
    assert copy_translation["feedback"] is None, "Поле feedback должно быть сброшено в None в копии"

    # Шаг 6: Удалить копию и оригинальный перевод
    delete_translation(user_access_token, copy_translation["id"])
    delete_translation(user_access_token, original_id)


def test_copy_translation_with_nonexistent_id(base_url, create_user_with_login):
    """
    Проверяет, что сервер возвращает статус код 404 при попытке создать копию перевода с несуществующим ID.

    Шаги:
    1. Создать пользователя.
    2. Выполнить запрос копирования перевода с несуществующим ID.
    3. Проверить, что сервер возвращает статус код 404.
    """
    # Шаг 1: Создать пользователя
    user = create_user_with_login
    user_access_token = user["access_token"]

    # Шаг 2: Выполнить запрос копирования перевода с несуществующим ID
    nonexistent_id = 999999
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }
    copy_response = requests.post_request(
        f"{base_url}/translate/{nonexistent_id}/copy/",
        headers=headers
    )

    # Шаг 3: Проверить ответ
    assert copy_response.status_code == 404, (
        f"Ожидаемый статус код 404 (Not Found), получен: {copy_response.status_code}"
    )
    response_body = copy_response.json()
    assert response_body["detail"] == "Not found"


def test_copy_translation_from_other_user(
    base_url, create_user_with_login, add_translation, delete_translation
):
    """
    Проверяет, что пользователь с ролью `user` не может создать копию задания,
    принадлежащего другому пользователю.

    Шаги:
    1. Создать первого пользователя и загрузить перевод.
    2. Авторизоваться вторым пользователем (данные из env).
    3. Выполнить запрос на создание копии перевода первым пользователем вторым пользователем.
    4. Проверить, что сервер возвращает статус код 404.
    """
    # Шаг 1: Создать первого пользователя и загрузить перевод
    first_user = create_user_with_login
    first_user_access_token = first_user["access_token"]

    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)

    original_translation = add_translation(first_user_access_token, test_video_path)
    original_id = original_translation["id"]

    # Шаг 2: Авторизоваться вторым пользователем
    empty_user_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_user_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    signin_payload = {"username": empty_user_email, "password": empty_user_password}
    empty_user_signin_response = requests.post_request(
        f"{base_url}/auth/signin", data=signin_payload
    )
    assert empty_user_signin_response.status_code == 200, (
        f"Ошибка авторизации второго пользователя: {empty_user_signin_response.status_code}"
    )
    empty_user_access_token = empty_user_signin_response.json()["access_token"]

    # Шаг 3: Выполнить запрос на создание копии перевода
    headers = {
        "Authorization": f"Bearer {empty_user_access_token}",
        "accept": "application/json"
    }
    copy_response = requests.post_request(
        f"{base_url}/translate/{original_id}/copy/",
        headers=headers
    )

    # Шаг 4: Проверить ответ
    assert copy_response.status_code == 404, (
        f"Ожидаемый статус код 404 (Not Found), получен: {copy_response.status_code}"
    )

    # Удалить оригинальный перевод
    delete_translation(first_user_access_token, original_id)


def test_copy_translation_with_invalid_id(base_url, create_user_with_login):
    """
    Проверяет, что сервер возвращает ошибку при попытке создания копии задания с некорректным ID.

    Шаги:
    1. Авторизоваться пользователем.
    2. Выполнить запрос на создание копии задания с некорректным ID (например, 'abc').
    3. Проверить, что сервер возвращает статус код 422.
    4. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Авторизоваться пользователем
    user = create_user_with_login
    user_access_token = user["access_token"]

    # Шаг 2: Выполнить запрос на создание копии задания с некорректным ID
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }
    invalid_id = "abc"
    copy_response = requests.post_request(
        f"{base_url}/translate/{invalid_id}/copy/",
        headers=headers
    )

    # Шаг 3: Проверить ответ
    assert copy_response.status_code == 422, (
        f"Ожидаемый статус код 422 (Validation Error), получен: {copy_response.status_code}"
    )
    response_body = copy_response.json()
    assert "detail" in response_body, "Тело ответа должно содержать ключ 'detail'"
    assert isinstance(response_body["detail"], list), "Поле 'detail' должно быть списком"
    assert response_body["detail"][0]["msg"] == "Input should be a valid integer, unable to parse string as an integer"


def test_copy_translation_without_authorization(base_url):
    """
    Проверяет, что сервер запрещает доступ к эндпоинту без авторизации.

    Шаги:
    1. Выполнить запрос на создание копии задания без указания токена авторизации.
    2. Проверить, что сервер возвращает статус код 401 (Unauthorized).
    3. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Выполнить запрос на создание копии задания без токена
    headers = {
        "accept": "application/json"
    }
    translation_id = 1  # Используется ID, который мог бы существовать
    copy_response = requests.post_request(
        f"{base_url}/translate/{translation_id}/copy/",
        headers=headers
    )

    # Шаг 2: Проверить ответ
    assert copy_response.status_code == 401, (
        f"Ожидаемый статус код 401 (Unauthorized), получен: {copy_response.status_code}"
    )
    response_body = copy_response.json()
    assert "detail" in response_body, "Тело ответа должно содержать ключ 'detail'"
    assert response_body["detail"] == "Not authenticated", (
        f"Сообщение об ошибке не совпадает. Получено: {response_body['detail']}"
    )


def test_response_structure_and_types_for_successful_copy(base_url, create_user_with_login, add_translation, delete_translation):
    """
    Проверяет, что тело ответа при успешном создании копии задания
    содержит все ключи и значения с правильными типами данных в соответствии с ожидаемой схемой.

    Шаги:
    1. Создать пользователя.
    2. Загрузить перевод.
    3. Выполнить запрос на создание копии задания.
    4. Проверить структуру и типы данных в ответе.
    5. Удалить копию и оригинальный перевод.
    """
    # Шаг 1: Создать пользователя
    user = create_user_with_login
    user_access_token = user["access_token"]

    # Шаг 2: Загрузить перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    original_translation = add_translation(user_access_token, test_video_path)
    original_id = original_translation["id"]

    # Шаг 3: Выполнить запрос на создание копии задания
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }
    copy_response = requests.post_request(
        f"{base_url}/translate/{original_id}/copy/",
        headers=headers
    )
    assert copy_response.status_code == 200, (
        f"Ожидаемый статус код 200 для копирования перевода, получен: {copy_response.status_code}"
    )
    copy_translation = copy_response.json()

    # Шаг 4: Проверить структуру и типы данных в ответе
    expected_schema = {
        "language": (str, type(None)),
        "save_origin_voice": (bool, type(None)),
        "has_logo": (bool, type(None)),
        "notification": (bool, type(None)),
        "voice_clone": (bool, type(None)),
        "lipsync": (bool, type(None)),
        "subtitle_download": (bool, type(None)),
        "subtitle_on_video": (bool, type(None)),
        "subtitle_edit": (bool, type(None)),
        "current_task": (str, type(None)),
        "voice_gender": (str, type(None)),
        "voice_count": (int, type(None)),
        "feedback": (int, type(None)),
        "id": int,
        "owner": dict,
        "video": dict,
        "transaction": (dict, type(None)),
        "sub_origin": (str, type(None)),
        "sub_translate": (str, type(None)),
        "video_origin": (str, type(None)),
        "video_translate": (str, type(None)),
        "preview": (str, type(None)),
    }

    for key, expected_type in expected_schema.items():
        assert key in copy_translation, f"Ключ '{key}' отсутствует в ответе"
        assert isinstance(copy_translation[key], expected_type), (
            f"Поле '{key}' имеет некорректный тип. Ожидаемый: {expected_type}, "
            f"Полученный: {type(copy_translation[key])}"
        )

    # Проверка вложенных объектов
    assert isinstance(copy_translation["owner"], dict), "Поле 'owner' должно быть объектом"
    assert isinstance(copy_translation["video"], dict), "Поле 'video' должно быть объектом"
    if copy_translation["transaction"] is not None:
        assert isinstance(copy_translation["transaction"], dict), "Поле 'transaction' должно быть объектом, если оно задано"

    # Шаг 5: Удалить копию и оригинальный перевод
    copy_id = copy_translation["id"]
    delete_translation(user_access_token, copy_id)
    delete_translation(user_access_token, original_id)
