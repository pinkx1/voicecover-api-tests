import os
import pytest
from api import requests
import time


def test_upload_valid_subtitle_string(base_url, signin_user):
    """
    Проверяет успешную передачу корректного содержимого субтитров в формате VTT с уникальным текстом.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Сформировать содержимое VTT-файла как строку с уникальным текстом.
    3. Передать содержимое строки в запрос.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что тело ответа содержит корректные ссылки на субтитры.
    6. Сделать GET-запрос и проверить содержимое sub_origin.
    """

    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # ID перевода
    translation_id = int(os.getenv("TRANSLATION_ID"))

    # Шаг 2: Генерация содержимого VTT-файла с уникальным текстом
    unique_id = int(time.time())  # Используем текущую метку времени для уникальности
    subtitle_content = f"""WEBVTT

1
00:00:00.000 --> 00:00:02.000
Welcome to the video. Unique ID: {unique_id}

2
00:00:02.001 --> 00:00:05.000
These are sample subtitles with ID: {unique_id}.
"""

    payload = {
        "id": translation_id,
        "vtt": subtitle_content  # Передача содержимого VTT как строки
    }

    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    # Шаг 3: Выполнить запрос на обновление субтитров
    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/rusub/",
        headers=headers,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 200
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит корректные ссылки на субтитры
    response_data = response.json()
    assert "id" in response_data, "Ответ не содержит ключ 'id'"
    assert response_data["id"] == translation_id, (
        f"Ожидалось, что ID перевода останется {translation_id}, получен: {response_data['id']}"
    )
    assert "sub_origin" in response_data, "Ответ не содержит ключ 'sub_origin'"
    assert response_data["sub_origin"] is not None, "Поле 'sub_origin' не должно быть пустым"

    # Проверить, что поле 'subtitle_on_video' не изменилось
    assert response_data["subtitle_on_video"] is False, (
        f"Поле 'subtitle_on_video' должно оставаться False, но получено: {response_data['subtitle_on_video']}"
    )

    # Шаг 6: Выполнить GET-запрос для проверки содержимого sub_origin
    get_response = requests.get_request(
        f"{base_url}/translate/{translation_id}/rusub/",
        headers={"Authorization": f"Bearer {user_access_token}"}
    )

    assert get_response.status_code == 200, (
        f"Ожидаемый статус код 200 для GET-запроса, получен: {get_response.status_code}"
    )

    # Проверить содержимое sub_origin
    sub_origin_content = get_response.json().get("vtt")
    assert sub_origin_content == subtitle_content, (
        f"Содержимое sub_origin не соответствует отправленным данным. "
        f"Ожидалось: {subtitle_content}, получено: {sub_origin_content}"
    )


@pytest.mark.xfail(reason="Сервер возвращает 500 вместо 404 при несуществующем ID перевода")
def test_upload_subtitle_with_invalid_translation_id(base_url, signin_user):
    """
    Проверяет реакцию сервера на передачу субтитров для несуществующего ID перевода.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Сформировать содержимое VTT-файла как строку.
    3. Указать некорректный ID перевода (например, 999999999).
    4. Передать содержимое строки в запрос.
    5. Проверить, что сервер возвращает статус код 404.
    6. Проверить, что тело ответа содержит описание ошибки.
    """

    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Некорректный ID перевода
    invalid_translation_id = 999999999

    # Шаг 2: Генерация содержимого VTT-файла
    subtitle_content = """WEBVTT

1
00:00:00.000 --> 00:00:02.000
This translation ID does not exist.

2
00:00:02.001 --> 00:00:05.000
Please check the ID and try again.
"""

    payload = {
        "id": invalid_translation_id,
        "vtt": subtitle_content  # Передача содержимого VTT как строки
    }

    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    # Шаг 3: Выполнить запрос
    response = requests.post_request(
        f"{base_url}/translate/{invalid_translation_id}/rusub/",
        headers=headers,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 404
    assert response.status_code == 404, (
        f"Ожидаемый статус код 404 для некорректного ID перевода, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert response_data["detail"] == "Translation not found", (
        f"Ожидалось сообщение об ошибке 'Translation not found', получено: {response_data['detail']}"
    )


def test_upload_subtitle_with_non_numeric_id(base_url, signin_user):
    """
    Проверяет реакцию сервера на передачу субтитров с некорректным значением ID (нечисловое значение).

    Шаги:
    1. Логин под пользователем без баланса.
    2. Сформировать содержимое VTT-файла как строку.
    3. Указать некорректное значение ID (например, 'abc').
    4. Передать содержимое строки в запрос.
    5. Проверить, что сервер возвращает статус код 422.
    6. Проверить, что тело ответа содержит описание ошибки.
    """

    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Некорректное значение ID перевода
    invalid_translation_id = "abc"

    # Шаг 2: Генерация содержимого VTT-файла
    subtitle_content = """WEBVTT

1
00:00:00.000 --> 00:00:02.000
This is an invalid ID test.

2
00:00:02.001 --> 00:00:05.000
The ID should be numeric.
"""

    payload = {
        "id": invalid_translation_id,
        "vtt": subtitle_content  # Передача содержимого VTT как строки
    }

    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    # Шаг 3: Выполнить запрос
    response = requests.post_request(
        f"{base_url}/translate/{invalid_translation_id}/rusub/",
        headers=headers,
        json=payload
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
        error["loc"] == ["body", "id"] and error["type"] == "int_parsing"
        for error in response_data["detail"]
    ), "Ответ не содержит ожидаемую ошибку в поле 'id'"


def test_upload_subtitle_without_authorization(base_url):
    """
    Проверяет реакцию сервера на передачу субтитров без авторизации.

    Шаги:
    1. Сформировать содержимое VTT-файла как строку.
    2. Указать ID существующего перевода.
    3. Выполнить запрос без заголовка авторизации.
    4. Проверить, что сервер возвращает статус код 401.
    5. Проверить, что тело ответа содержит описание ошибки.
    """

    # ID существующего перевода
    translation_id = str(os.getenv("TRANSLATION_ID"))

    # Шаг 1: Генерация содержимого VTT-файла
    subtitle_content = """WEBVTT

1
00:00:00.000 --> 00:00:02.000
Unauthorized access test.

2
00:00:02.001 --> 00:00:05.000
This request should fail.
"""

    payload = {
        "id": translation_id,
        "vtt": subtitle_content  # Передача содержимого VTT как строки
    }

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
        # Без заголовка Authorization
    }

    # Шаг 2: Выполнить запрос
    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/rusub/",
        headers=headers,
        json=payload
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 401
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )

    # Шаг 4: Проверить, что тело ответа содержит описание ошибки
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert response_data["detail"] == "Not authenticated", (
        f"Ожидалось сообщение 'Not authenticated', получено: {response_data['detail']}"
    )


@pytest.mark.xfail(reason="Сервер возвращает 500 вместо 403 (баг)")
def test_upload_subtitle_for_foreign_translation(base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет, что пользователь с ролью `user` не может передать субтитры для перевода, принадлежащего другому пользователю.

    Шаги:
    1. Логин под пользователем с балансом.
    2. Создать перевод этим пользователем.
    3. Логин под другим пользователем без баланса.
    4. Сформировать содержимое VTT-файла как строку.
    5. Выполнить запрос на добавление субтитров в перевод, созданный другим пользователем.
    6. Проверить, что сервер возвращает статус код 403.
    7. Проверить, что тело ответа содержит описание ошибки.
    8. Удалить созданный перевод.
    """

    # Шаг 1: Логин под пользователем с балансом
    some_balance_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    some_balance_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    balance_user = signin_user(some_balance_email, some_balance_password)
    balance_user_access_token = balance_user["access_token"]

    # Шаг 2: Создать перевод этим пользователем
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)

    translation = add_translation(balance_user_access_token, test_video_path)
    translation_id = translation["id"]

    try:
        # Шаг 3: Логин под другим пользователем без баланса
        empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
        empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
        empty_balance_user = signin_user(empty_balance_email, empty_balance_password)
        empty_balance_user_access_token = empty_balance_user["access_token"]

        # Шаг 4: Генерация содержимого VTT-файла
        subtitle_content = f"""WEBVTT

1
00:00:00.000 --> 00:00:02.000
This is a foreign translation test.

2
00:00:02.001 --> 00:00:05.000
Access should be denied.
"""

        payload = {
            "id": translation_id,
            "vtt": subtitle_content  # Передача содержимого VTT как строки
        }

        headers = {
            "Authorization": f"Bearer {empty_balance_user_access_token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        # Шаг 5: Выполнить запрос
        response = requests.post_request(
            f"{base_url}/translate/{translation_id}/rusub/",
            headers=headers,
            json=payload
        )

        # Шаг 6: Проверить, что сервер возвращает статус код 403
        assert response.status_code == 403, (
            f"Ожидаемый статус код 403, получен: {response.status_code}"
        )

        # Шаг 7: Проверить, что тело ответа содержит описание ошибки
        response_data = response.json()
        assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
        assert response_data["detail"] == "Permission denied", (
            f"Ожидалось сообщение 'Permission denied', получено: {response_data['detail']}"
        )
    finally:
        # Шаг 8: Удалить созданный перевод
        delete_translation(balance_user_access_token, translation_id)


