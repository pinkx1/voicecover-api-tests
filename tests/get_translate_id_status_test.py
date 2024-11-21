import os
import pytest
from api import requests


def test_get_status_for_new_translation(base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет, что статус нового перевода корректно возвращается после настройки перевода.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Создать бесплатный перевод.
    3. Настроить перевод с бесплатными параметрами (это инициирует процесс).
    4. Выполнить GET-запрос для получения статуса перевода.
    5. Проверить, что сервер возвращает статус код 200.
    6. Проверить, что тело ответа содержит корректный статус.
    """
    # Ожидаемые статусы
    valid_statuses = [
        "Накладываются субтитры",
        "Обработка видео",
        "Обработка субтитров",
        "Подтверждение субтитров",
        "Формирование голоса",
        "Формирование видео",
        "Завершено"
    ]

    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Создать перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    try:
        # Шаг 3: Настроить перевод
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        payload_settings = {
            "language": "en",
            "save_origin_voice": True,
            "has_logo": True,
            "notification": False,
            "voice_clone": False,
            "lipsync": False,
            "subtitle_download": True,
            "subtitle_on_video": False,
            "subtitle_edit": False,
            "voice_gender": None,
            "voice_count": 0
        }

        response_settings = requests.post_request(
            f"{base_url}/translate/{translation_id}/setting/",
            headers=headers,
            json=payload_settings
        )
        assert response_settings.status_code == 200, (
            f"Не удалось настроить перевод, статус код: {response_settings.status_code}"
        )

        # Шаг 4: Выполнить GET-запрос для получения статуса перевода
        response_status = requests.get_request(
            f"{base_url}/translate/{translation_id}/status/",
            headers=headers
        )

        # Шаг 5: Проверить, что сервер возвращает статус код 200
        assert response_status.status_code == 200, (
            f"Ожидаемый статус код 200, получен: {response_status.status_code}"
        )

        # Шаг 6: Проверить статус перевода
        response_data = response_status.json()
        assert "status" in response_data, "Ответ не содержит ключ 'status'"
        assert response_data["status"] in valid_statuses, (
            f"Неожиданный статус перевода: {response_data['status']}. Ожидаемые статусы: {valid_statuses}"
        )
    finally:
        # Удалить перевод после теста
        delete_translation(user_access_token, translation_id)


def test_get_status_for_nonexistent_translation(base_url, signin_user):
    """
    Проверяет реакцию сервера на запрос статуса для несуществующего ID задачи.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Указать несуществующий ID перевода.
    3. Выполнить GET-запрос для получения статуса перевода.
    4. Проверить, что сервер возвращает статус код 404.
    5. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Указать несуществующий ID перевода
    nonexistent_translation_id = 999999  # ID, которого точно нет в базе данных

    # Шаг 3: Выполнить GET-запрос для получения статуса перевода
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{nonexistent_translation_id}/status/",
        headers=headers
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 404
    assert response.status_code == 404, (
        f"Ожидаемый статус код 404 для несуществующего ID, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert response_data["detail"] == "Not found", (
        f"Ожидалось сообщение об ошибке 'Not found', получено: {response_data['detail']}"
    )


def test_get_status_with_invalid_id(base_url, signin_user):
    """
    Проверяет реакцию сервера на запрос статуса с некорректным значением ID (например, 'abc').

    Шаги:
    1. Логин под пользователем без баланса.
    2. Указать некорректное значение ID (например, 'abc').
    3. Выполнить GET-запрос для получения статуса перевода.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Указать некорректное значение ID
    invalid_translation_id = "abc"  # Некорректное значение ID

    # Шаг 3: Выполнить GET-запрос для получения статуса перевода
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{invalid_translation_id}/status/",
        headers=headers
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422 для некорректного значения ID, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert isinstance(response_data["detail"], list), "Поле 'detail' должно быть списком"
    assert any(
        error["loc"] == ["path", "id"] and error["type"] == "int_parsing"
        for error in response_data["detail"]
    ), "Ответ не содержит ожидаемую ошибку в поле 'id'"


def test_get_status_without_authorization(base_url):
    """
    Проверяет реакцию сервера на запрос статуса без авторизации.

    Шаги:
    1. Указать существующий ID перевода.
    2. Выполнить GET-запрос без авторизационного заголовка.
    3. Проверить, что сервер возвращает статус код 401.
    4. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Указать существующий ID перевода
    translation_id = str(os.getenv("TRANSLATION_ID"))

    # Шаг 2: Выполнить GET-запрос без авторизационного заголовка
    headers = {
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{translation_id}/status/",
        headers=headers
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 401
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401 для запроса без авторизации, получен: {response.status_code}"
    )

    # Шаг 4: Проверить, что тело ответа содержит описание ошибки
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert response_data["detail"] == "Not authenticated", (
        f"Ожидаемое описание ошибки 'Not authenticated', получено: {response_data['detail']}"
    )


def test_get_status_for_foreign_task_as_admin(base_url, signin_user):
    """
    Проверяет, что администратор может получить статус чужой задачи.

    Шаги:
    1. Логин под администратором.
    2. Указать ID перевода, принадлежащего другому пользователю.
    3. Выполнить GET-запрос для получения статуса перевода.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что тело ответа содержит корректный статус задачи.
    """
    # Шаг 1: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 2: Указать ID перевода, принадлежащего другому пользователю
    translation_id = str(os.getenv("TRANSLATION_ID"))

    # Шаг 3: Выполнить GET-запрос для получения статуса перевода
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{translation_id}/status/",
        headers=headers
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 200
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200 для получения статуса чужой задачи, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит корректный статус задачи
    response_data = response.json()
    assert "status" in response_data, "Ответ не содержит ключ 'status'"
    assert response_data["status"] in [
        "Накладываются субтитры",
        "Обработка видео",
        "Обработка субтитров",
        "Подтверждение субтитров",
        "Формирование голоса",
        "Формирование видео",
        "Завершено",
        "Неизвестно"
    ], f"Некорректный статус задачи: {response_data['status']}"


