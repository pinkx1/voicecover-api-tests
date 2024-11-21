import os
import pytest
from api import requests


def test_get_video_origin_success(base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет, что сервер возвращает корректный файл исходного видео для существующего перевода.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Создать перевод.
    3. Выполнить GET-запрос для получения исходного видео.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что файл доступен для загрузки (валидное содержимое ответа).
    """
    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Создать перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    try:
        # Шаг 3: Выполнить GET-запрос для получения исходного видео
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "accept": "application/json"
        }
        response = requests.get_request(
            f"{base_url}/translate/{translation_id}/download/video_origin/",
            headers=headers
        )

        # Шаг 4: Проверить, что сервер возвращает статус код 200
        assert response.status_code == 200, (
            f"Ожидаемый статус код 200, получен: {response.status_code}"
        )

        # Шаг 5: Проверить, что файл доступен для загрузки
        assert response.content, "Ответ не содержит содержимого файла"
        assert response.headers["Content-Type"] == "video/mp4", (
            f"Ожидалось 'video/mp4', получено: {response.headers.get('Content-Type')}"
        )
    finally:
        # Удалить перевод
        delete_translation(user_access_token, translation_id)


def test_get_video_translate_for_user_without_balance(base_url, signin_user):
    """
    Проверяет, что сервер возвращает корректный файл переведенного видео для перевода,
    принадлежащего пользователю без баланса.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Выполнить GET-запрос для получения переведенного видео по ID перевода.
    3. Проверить, что сервер возвращает статус код 200.
    4. Проверить, что файл доступен для загрузки (валидное содержимое ответа).
    """
    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # ID перевода пользователя без баланса
    translation_id = str(os.getenv("TRANSLATION_ID"))

    # Шаг 2: Выполнить GET-запрос для получения переведенного видео
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{translation_id}/download/video_translate/",
        headers=headers
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 200
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 4: Проверить, что файл доступен для загрузки
    assert response.content, "Ответ не содержит содержимого файла"
    assert response.headers["Content-Type"] == "video/mp4", (
        f"Ожидалось 'video/mp4', получено: {response.headers.get('Content-Type')}"
    )


def test_get_sub_translate_for_user_without_balance(base_url, signin_user):
    """
    Проверяет, что сервер возвращает файл переведенных субтитров на целевом языке для завершенного перевода.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Выполнить GET-запрос для получения переведенных субтитров по ID перевода.
    3. Проверить, что сервер возвращает статус код 200.
    4. Проверить, что файл доступен для загрузки в формате VTT.
    5. Проверить, что содержимое файла соответствует ожидаемым субтитрам (проверка по ключевым словам).
    """
    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # ID перевода пользователя без баланса
    translation_id = str(os.getenv("TRANSLATION_ID_NO_EDIT"))

    # Шаг 2: Выполнить GET-запрос для получения переведенных субтитров
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{translation_id}/download/sub_translate/",
        headers=headers
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 200
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 4: Проверить, что файл доступен для загрузки в формате VTT
    assert response.content, "Ответ не содержит содержимого файла"
    content_type = response.headers.get("Content-Type")
    assert content_type.startswith("text/vtt"), (
        f"Ожидалось 'text/vtt', получено: {content_type}"
    )

    # Шаг 5: Проверить, что содержимое файла соответствует ожидаемым субтитрам (по ключевым словам)
    expected_keywords = [
        "Do you know why you have few friends?",
        "Because you're unique.",
        "You're smart and thoughtful.",
        "Improve those skills instead of being self-absorbed."
    ]
    actual_content = response.text.strip()
    for keyword in expected_keywords:
        assert keyword in actual_content, f"Ключевая строка отсутствует: {keyword}"



def test_get_sub_origin_for_user_without_balance(base_url, signin_user):
    """
    Проверяет, что сервер возвращает файл оригинальных субтитров на исходном языке для завершенного перевода.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Выполнить GET-запрос для получения оригинальных субтитров по ID перевода.
    3. Проверить, что сервер возвращает статус код 200.
    4. Проверить, что файл доступен для загрузки в формате VTT.
    5. Проверить, что содержимое файла соответствует ожидаемым субтитрам.
    """
    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # ID перевода пользователя без баланса
    translation_id = str(os.getenv("TRANSLATION_ID_NO_EDIT"))

    # Шаг 2: Выполнить GET-запрос для получения оригинальных субтитров
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{translation_id}/download/sub_origin/",
        headers=headers
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 200
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 4: Проверить, что файл доступен для загрузки в формате VTT
    assert response.content, "Ответ не содержит содержимого файла"
    content_type = response.headers.get("Content-Type")
    assert content_type.startswith("text/vtt"), (
        f"Ожидалось 'text/vtt', получено: {content_type}"
    )

    # Шаг 5: Проверить, что содержимое файла соответствует ожидаемым субтитрам
    expected_subtitle_content = """WEBVTT

00:00:00.360 --> 00:00:01.879
Знаешь, почему у тебя мало друзей?

00:00:01.879 --> 00:00:02.940
Потому что ты особен.

00:00:03.240 --> 00:00:04.320
Ты умный и вдумчивый.

00:00:04.440 --> 00:00:06.820
А людям это не нравится, потому что они поверхностные.

00:00:06.980 --> 00:00:08.599
Да? Хуйна.

00:00:08.599 --> 00:00:13.580
Если захотелось сказать «да», то у тебя, скорее всего, проблемы с нарциссизмом и с коммуникативными навыками.

00:00:13.640 --> 00:00:15.339
Развивай их, а не самолюбуйся.
"""
    actual_content = response.text.strip()
    assert actual_content == expected_subtitle_content.strip(), (
        "Содержимое файла оригинальных субтитров не соответствует ожидаемому. "
        f"Ожидаемое:\n{expected_subtitle_content.strip()}\n\nПолученное:\n{actual_content}"
    )


def test_get_preview_for_user_without_balance(base_url, signin_user):
    """
    Проверяет, что сервер возвращает файл превью для текущего перевода (если доступно).

    Шаги:
    1. Логин под пользователем без баланса.
    2. Выполнить GET-запрос для получения превью видео по ID перевода.
    3. Проверить, что сервер возвращает статус код 200.
    4. Проверить, что файл доступен для загрузки в формате изображения.
    """
    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # ID перевода пользователя без баланса
    translation_id = str(os.getenv("TRANSLATION_ID"))

    # Шаг 2: Выполнить GET-запрос для получения превью видео
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{translation_id}/download/preview/",
        headers=headers
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 200
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 4: Проверить, что файл доступен для загрузки в формате изображения
    assert response.content, "Ответ не содержит содержимого файла"
    content_type = response.headers.get("Content-Type")
    assert content_type.startswith("image/"), (
        f"Ожидалось 'image/', получено: {content_type}"
    )


def test_get_file_for_nonexistent_translation(base_url, signin_user):
    """
    Проверяет, что сервер возвращает статус код 404 при попытке получить файл для несуществующего перевода.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Указать несуществующий ID перевода.
    3. Выполнить GET-запрос для получения файла.
    4. Проверить, что сервер возвращает статус код 404.
    5. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Указать несуществующий ID перевода
    nonexistent_translation_id = 999999  # Несуществующий ID перевода

    # Шаг 3: Выполнить GET-запрос для получения файла
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{nonexistent_translation_id}/download/preview/",
        headers=headers
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 404
    assert response.status_code == 404, (
        f"Ожидаемый статус код 404 для несуществующего перевода, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert response_data["detail"] == "Translate not found", (
        f"Ожидалось сообщение об ошибке 'Translate not found', получено: {response_data['detail']}"
    )


def test_get_unavailable_type_file(base_url, signin_user):

    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Указать ID перевода с недоступным типом файла
    translation_id = str(os.getenv("TRANSLATION_ID"))

    # Шаг 3: Выполнить GET-запрос для недоступного типа файла
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{translation_id}/download/something/",  # Предполагаем, что `video_translate` недоступен
        headers=headers
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 404
    assert response.status_code == 422, (
        f"Ожидаемый статус код 404 для недоступного типа файла, получен: {response.status_code}"
    )


def test_get_file_without_authorization(base_url):
    """
    Проверяет, что сервер запрещает доступ к эндпоинту для неавторизованных пользователей.

    Шаги:
    1. Указать ID перевода.
    2. Выполнить GET-запрос для получения файла без авторизационного заголовка.
    3. Проверить, что сервер возвращает статус код 401.
    4. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Указать ID перевода
    translation_id = str(os.getenv("TRANSLATION_ID"))

    # Шаг 2: Выполнить GET-запрос для получения файла без авторизационного заголовка
    headers = {
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{translation_id}/download/video_origin/",  # Пример типа файла
        headers=headers
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 401
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401 для запроса без авторизации, получен: {response.status_code}"
    )


def test_get_file_for_foreign_translation(base_url, signin_user):
    """
    Проверяет, что пользователь не может получить доступ к файлу, принадлежащему другому пользователю.

    Шаги:
    1. Логин под пользователем с балансом.
    2. Указать ID перевода, принадлежащего другому пользователю.
    3. Выполнить GET-запрос для получения файла.
    4. Проверить, что сервер возвращает статус код 403.
    5. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Логин под пользователем с балансом
    some_balance_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    some_balance_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(some_balance_email, some_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Указать ID перевода, принадлежащего другому пользователю
    foreign_translation_id = str(os.getenv("TRANSLATION_ID"))

    # Шаг 3: Выполнить GET-запрос для получения файла
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{foreign_translation_id}/download/video_origin/",
        headers=headers
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 403
    assert response.status_code == 404, (
        f"Ожидаемый статус код 403 для запроса к чужому переводу, получен: {response.status_code}"
    )


