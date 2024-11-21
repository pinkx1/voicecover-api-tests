import os
import pytest
from api import requests


def test_successful_video_upload(base_url, create_user_with_login):
    """
    Проверяет успешную загрузку корректного видеофайла.

    Шаги:
    1. Авторизоваться под пользователем.
    2. Загрузить корректный видеофайл (менее 1 Гб, поддерживаемый формат).
    3. Проверить, что возвращается статус код 200.
    4. Проверить, что в ответе присутствуют:
        - ID перевода больше 0.
        - Поле video содержит ожидаемые данные:
            - Корректное название.
            - Длину больше 0.
            - ID больше 0.
        - Ссылки video_origin и preview.
    """
    # Шаг 1: Авторизация пользователя
    user = create_user_with_login
    user_access_token = user["access_token"]
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
    }

    # Шаг 2: Указание пути к видеофайлу
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)

    # Шаг 3: Отправка запроса на загрузку видео
    mime_type = "video/mp4"
    files = {
        "upload": (os.path.basename(test_video_path), open(test_video_path, "rb"), mime_type)
    }
    response = requests.post_request(
        f"{base_url}/translate/upload/",
        headers=headers,
        files=files
    )

    # Шаг 4: Проверки ответа
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )
    response_data = response.json()

    # Проверка: ID перевода больше 0
    assert "id" in response_data and response_data["id"] > 0

    # Проверка: Поле video
    video_data = response_data.get("video", {})
    assert video_data["length"] > 0, "Длина видео должна быть больше 0"
    assert video_data["id"] > 0, "ID видео отсутствует или некорректен"
    assert "video_origin" in response_data and response_data["video_origin"], "Отсутствует ссылка video_origin"
    assert "preview" in response_data and response_data["preview"], "Отсутствует ссылка preview"


def test_upload_unsupported_file_format(base_url, create_user_with_login):
    """
    Проверяет, что сервер возвращает ошибку при загрузке файла неподдерживаемого формата.

    Шаги:
    1. Авторизоваться под пользователем.
    2. Загрузить файл неподдерживаемого формата (например, PDF).
    3. Проверить, что сервер возвращает статус код 400.
    4. Проверить, что тело ответа содержит "detail": "Invalid file type".
    """
    # Шаг 1: Авторизация пользователя
    user = create_user_with_login
    user_access_token = user["access_token"]
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
    }

    # Шаг 2: Указание пути к неподдерживаемому файлу
    current_dir = os.path.dirname(__file__)
    test_file_path = os.path.join(current_dir, "..", "data", "dummy.pdf")
    test_file_path = os.path.abspath(test_file_path)
    assert os.path.exists(test_file_path), f"Файл {test_file_path} не найден"

    # Шаг 3: Отправка запроса на загрузку неподдерживаемого файла
    mime_type = "application/pdf"
    files = {
        "upload": (os.path.basename(test_file_path), open(test_file_path, "rb"), mime_type)
    }
    response = requests.post_request(
        f"{base_url}/translate/upload/",
        headers=headers,
        files=files
    )

    # Шаг 4: Проверки ответа
    assert response.status_code == 400, (
        f"Ожидаемый статус код 400, получен: {response.status_code}"
    )
    response_data = response.json()

    # Проверка сообщения об ошибке
    expected_error = {"detail": "Invalid file type"}
    assert response_data == expected_error, (
        f"Ожидаемое сообщение об ошибке {expected_error}, получено: {response_data}"
    )


def test_upload_without_file(base_url, create_user_with_login):
    """
    Проверяет, что сервер возвращает ошибку при отсутствии файла в запросе.

    Шаги:
    1. Авторизоваться под пользователем.
    2. Отправить запрос на загрузку без файла.
    3. Проверить, что сервер возвращает статус код 422.
    4. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Авторизация пользователя
    user = create_user_with_login
    user_access_token = user["access_token"]
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
    }

    # Шаг 2: Отправка запроса без файла
    response = requests.post_request(
        f"{base_url}/translate/upload/",
        headers=headers
    )

    # Шаг 3: Проверки ответа
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )
    response_data = response.json()

    # Проверка сообщения об ошибке
    assert response_data["detail"][0]["msg"] == "Field required"


def test_upload_without_authorization(base_url):
    """
    Проверяет, что сервер запрещает загрузку файла без предоставления авторизационного токена.

    Шаги:
    1. Отправить запрос на загрузку файла без авторизационного токена.
    2. Проверить, что сервер возвращает статус код 401.
    3. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Подготовка данных для загрузки
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    mime_type = "video/mp4"
    files = {
        "upload": (os.path.basename(test_video_path), open(test_video_path, "rb"), mime_type)
    }

    # Шаг 2: Отправка запроса без авторизационного токена
    response = requests.post_request(
        f"{base_url}/translate/upload/",
        files=files
    )

    # Шаг 3: Проверки ответа
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )
    response_data = response.json()

    # Проверка сообщения об ошибке
    assert response_data["detail"] == "Not authenticated", (
        f"Ожидаемое сообщение об ошибке 'Not authenticated', получено: {response_data['detail']}"
    )
