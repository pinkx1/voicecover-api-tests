import os
import pytest
from api import requests


def test_get_translation_count_admin_all(base_url, create_admin):
    admin = create_admin
    access_token = admin["access_token"]

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/count/?my=false", headers=headers)

    assert response.status_code == 200, f"Ожидаемый статус код 200, получен: {response.status_code}"

    response_data = response.json()
    assert isinstance(response_data, int), f"Ожидалось число в ответе, получено: {response_data}"


def test_get_translation_count_admin_own(base_url, create_admin, add_translation, delete_translation, delete_user):
    admin = create_admin
    access_token = admin["access_token"]
    admin_id = admin["id"]

    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation_ids = []
    num_translations = 3

    for i in range(num_translations):
        translation = add_translation(access_token, test_video_path)
        translation_ids.append(translation["id"])

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/count/?my=true", headers=headers)

    assert response.status_code == 200, f"Ожидаемый статус код 200, получен: {response.status_code}"

    response_data = response.json()
    assert isinstance(response_data, int), f"Ожидалось число в ответе, получено: {response_data}"
    assert response_data == len(translation_ids), (
        f"Ожидалось количество переводов {len(translation_ids)}, получено: {response_data}"
    )

    for translation_id in translation_ids:
        delete_translation(access_token, translation_id)

    delete_user(admin_id)


def test_get_translation_count_user(base_url, create_user_with_login, add_translation, delete_translation, delete_user):
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    access_token = user["access_token"]
    user_id = user["id"]

    # Шаг 2: Загрузка переводов
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation_ids = []
    num_translations = 3  # Количество переводов для проверки

    for i in range(num_translations):
        translation = add_translation(access_token, test_video_path)
        translation_ids.append(translation["id"])

    # Шаг 3: Запрос количества переводов с my=false
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response_my_false = requests.get_request(f"{base_url}/translate/count/?my=false", headers=headers)

    # Шаг 4: Запрос количества переводов с my=true
    response_my_true = requests.get_request(f"{base_url}/translate/count/?my=true", headers=headers)

    # Шаг 5: Проверка статус-кода
    assert response_my_false.status_code == 200, f"Ожидаемый статус код 200, получен: {response_my_false.status_code}"
    assert response_my_true.status_code == 200, f"Ожидаемый статус код 200, получен: {response_my_true.status_code}"

    # Шаг 6: Проверка тела ответа
    response_data_my_false = response_my_false.json()
    response_data_my_true = response_my_true.json()
    assert isinstance(response_data_my_false, int), f"Ожидалось число в ответе, получено: {response_data_my_false}"
    assert isinstance(response_data_my_true, int), f"Ожидалось число в ответе, получено: {response_data_my_true}"
    assert response_data_my_false == len(translation_ids), (
        f"Ожидалось количество переводов {len(translation_ids)}, получено: {response_data_my_false}"
    )
    assert response_data_my_true == len(translation_ids), (
        f"Ожидалось количество переводов {len(translation_ids)}, получено: {response_data_my_true}"
    )

    # Шаг 7: Удаление переводов
    for translation_id in translation_ids:
        delete_translation(access_token, translation_id)

    # Шаг 8: Удаление аккаунта пользователя
    delete_user(user_id)


def test_get_translation_count_without_my(base_url, create_user_with_login, add_translation, delete_translation, delete_user):
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    access_token = user["access_token"]
    user_id = user["id"]

    # Шаг 2: Загрузка переводов
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation_ids = []
    num_translations = 3

    for i in range(num_translations):
        translation = add_translation(access_token, test_video_path)
        translation_ids.append(translation["id"])

    # Шаг 3: Запрос количества переводов без параметра my
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/count/", headers=headers)

    # Шаг 4: Проверка статус-кода
    assert response.status_code == 200, f"Ожидаемый статус код 200, получен: {response.status_code}"

    # Шаг 5: Проверка тела ответа
    response_data = response.json()
    assert isinstance(response_data, int), f"Ожидалось число в ответе, получено: {response_data}"
    assert response_data == len(translation_ids), (
        f"Ожидалось количество переводов {len(translation_ids)}, получено: {response_data}"
    )

    # Шаг 6: Удаление переводов
    for translation_id in translation_ids:
        delete_translation(access_token, translation_id)

    # Шаг 7: Удаление аккаунта пользователя
    delete_user(user_id)


def test_translation_count_without_authorization(base_url):
    """
    Проверяет, что сервер запрещает доступ к эндпоинту без авторизации.

    Шаги:
    1. Выполняется запрос к эндпоинту /translate/count/ без заголовка Authorization.
    2. Проверяется, что сервер возвращает статус код 401 (Unauthorized).
    """
    # Шаг 1: Выполнение запроса без авторизации
    headers = {
        "accept": "application/json"
    }
    response = requests.get_request(f"{base_url}/translate/count/", headers=headers)

    # Шаг 2: Проверка статус-кода
    assert response.status_code == 401, f"Ожидаемый статус код 401, получен: {response.status_code}"


def test_translation_count_with_invalid_my_parameter(base_url, create_user_with_login, delete_user):
    """
    Проверяет реакцию сервера на некорректное значение параметра my.

    Шаги:
    1. Создаётся новый аккаунт пользователя.
    2. Выполняется запрос с некорректным значением параметра my (например, my=invalid).
    3. Проверяется, что сервер возвращает статус код 422 (Validation Error).
    4. Проверяется, что тело ответа содержит описание ошибки.
    5. Удаляется созданный аккаунт пользователя.
    """
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    access_token = user["access_token"]
    user_id = user["id"]

    # Шаг 2: Выполнение запроса с некорректным параметром my
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/count/?my=invalid", headers=headers)

    # Шаг 3: Проверка статус-кода
    assert response.status_code == 422, f"Ожидаемый статус код 422, получен: {response.status_code}"

    # Шаг 4: Проверка тела ответа
    response_data = response.json()
    assert "detail" in response_data, f"Ожидалось описание ошибки в ответе, получено: {response_data}"

    # Шаг 5: Удаление аккаунта пользователя
    delete_user(user_id)
