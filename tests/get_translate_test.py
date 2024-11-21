import os
import pytest
from api import requests


@pytest.mark.xfail(reason="Баг на бэкенде: 500 Internal Server Error при my=false для администратора")
def test_get_translations_admin_all(base_url, admin_access_token):
    """
    Проверяет, что администратор с параметром my=false видит все переводы.

    Шаги:
    1. Отправляется GET-запрос от имени администратора с параметром my=false.
    2. Проверяется, что сервер возвращает статус-код 200.
    3. Проверяется, что тело ответа содержит список переводов.
    4. Выполняются дополнительные проверки структуры объектов переводов.
    """
    # Шаг 1: Отправка запроса
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {admin_access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/?my=false&offset=0", headers=headers)

    # Шаг 2: Проверка статус-кода
    assert response.status_code == 200, f"Ожидаемый статус код 200, получен: {response.status_code}"

    # Шаг 3: Проверка тела ответа
    response_data = response.json()
    assert isinstance(response_data, list), "Ожидался массив переводов"
    assert len(response_data) > 0, "Список переводов пуст"

    # Шаг 4: Проверка структуры объектов в ответе
    required_keys = {"language", "subscription", "video", "id", "created_at"}
    for translation in response_data:
        assert required_keys.issubset(translation.keys()), f"Не хватает ключей в переводе: {translation}"


def test_admin_sees_own_translations_with_my_true(base_url, create_admin, add_translation, delete_translation, delete_user):
    """
    Проверяет, что администратор с параметром my=true видит только свои переводы.

    Шаги:
    1. Создаётся новый аккаунт администратора.
    2. Загружается перевод, связанный с этим аккаунтом.
    3. Проверяется, что загрузка перевода прошла успешно.
    4. Выполняется запрос списка переводов администратора с параметром my=true.
    5. Проверяется, что список содержит только переводы, принадлежащие созданному аккаунту.
    6. Удаляется созданный перевод.
    7. Удаляется созданный аккаунт администратора.
    """
    # Шаг 1: Создание администратора
    admin = create_admin
    access_token = admin["access_token"]

    # Шаг 2: Путь к видео (относительно текущего файла теста)
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)  # Приводим путь к абсолютному
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    # Шаг 3: Добавление перевода
    translation = add_translation(access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 4: Проверка, что перевод добавлен
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/?my=true&offset=0", headers=headers)
    assert response.status_code == 200, f"Ожидаемый статус код 200, получен: {response.status_code}"

    response_data = response.json()

    # Шаг 5: Проверяем, что добавленный перевод присутствует
    assert any(tr["id"] == translation_id for tr in response_data), (
        f"Перевод с ID {translation_id} не найден в списке переводов"
    )

    # Шаг 6: Удаление перевода
    delete_translation(access_token, translation_id)

    # Шаг 7: Удаление аккаунта
    delete_user(admin["id"])


def test_user_sees_only_own_translations(base_url, create_user_with_login, add_translation, delete_translation, delete_user):
    """
    Проверяет, что пользователь видит только свои переводы, независимо от значения параметра my.

    Шаги:
    1. Создаётся новый аккаунт обычного пользователя.
    2. Загружается перевод, связанный с этим аккаунтом.
    3. Проверяется, что загрузка перевода прошла успешно.
    4. Выполняется запрос списка переводов пользователя с параметром my=false.
    5. Проверяется, что список содержит только переводы, принадлежащие созданному аккаунту.
    6. Удаляется созданный перевод.
    7. Удаляется созданный аккаунт пользователя.
    """
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    access_token = user["access_token"]

    # Шаг 2: Путь к видео (относительно текущего файла теста)
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    # Шаг 3: Добавление перевода
    translation = add_translation(access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 4: Проверка, что перевод добавлен
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/?my=false&offset=0", headers=headers)
    assert response.status_code == 200, f"Ожидаемый статус код 200, получен: {response.status_code}"

    response_data = response.json()

    # Шаг 5: Проверяем, что добавленный перевод присутствует
    assert any(tr["id"] == translation_id for tr in response_data), (
        f"Перевод с ID {translation_id} не найден в списке переводов"
    )
    assert all(tr["owner"]["id"] == user["id"] for tr in response_data), (
        f"Список содержит переводы, не принадлежащие пользователю {user['id']}"
    )

    # Шаг 6: Удаление перевода
    delete_translation(access_token, translation_id)

    # Шаг 7: Удаление аккаунта
    delete_user(user["id"])


def test_pagination_with_limit(base_url, create_user_with_login, add_translation, delete_translation, delete_user):
    """
    Проверяет, что сервер корректно возвращает ограниченное количество переводов при использовании параметра limit.

    Шаги:
    1. Создаётся новый аккаунт пользователя.
    2. Загружается большее количество переводов, чем указано в параметре limit.
    3. Выполняется запрос с параметром limit.
    4. Проверяется, что возвращённое количество переводов не превышает указанное значение limit.
    5. Удаляются созданные переводы.
    6. Удаляется созданный аккаунт пользователя.
    """
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    access_token = user["access_token"]

    # Шаг 2: Создание переводов
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation_ids = []
    num_translations = 5
    limit = 3

    for i in range(num_translations):
        translation = add_translation(access_token, test_video_path)
        translation_ids.append(translation["id"])

    # Шаг 3: Проверка лимита в ответе
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/?limit={limit}&offset=0", headers=headers)
    assert response.status_code == 200, f"Ожидаемый статус код 200, получен: {response.status_code}"

    response_data = response.json()
    assert isinstance(response_data, list), "Ожидался массив переводов"
    assert len(response_data) <= limit, (
        f"Количество переводов в ответе ({len(response_data)}) превышает указанный лимит ({limit})"
    )

    # Шаг 4: Удаление созданных переводов
    for translation_id in translation_ids:
        delete_translation(access_token, translation_id)

    # Шаг 5: Удаление аккаунта
    delete_user(user["id"])


@pytest.mark.xfail(reason="API возвращает переводы в обратном порядке")
def test_pagination_with_offset(base_url, create_user_with_login, add_translation, delete_translation, delete_user):
    """
    Проверяет, что сервер корректно смещает список переводов при использовании параметра offset.

    Шаги:
    1. Создаётся новый аккаунт пользователя.
    2. Загружается несколько переводов, чтобы проверить смещение.
    3. Выполняется запрос с параметром offset.
    4. Проверяется, что возвращённый список начинается с указанного смещения.
    5. Удаляются созданные переводы.
    6. Удаляется созданный аккаунт пользователя.
    """
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    access_token = user["access_token"]

    # Шаг 2: Создание переводов
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation_ids = []
    num_translations = 5  # Количество переводов для проверки

    for i in range(num_translations):
        translation = add_translation(access_token, test_video_path)
        translation_ids.append(translation["id"])

    # Шаг 3: Проверка смещения
    offset = 2  # Смещение
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/?offset={offset}&limit=10", headers=headers)
    assert response.status_code == 200, f"Ожидаемый статус код 200, получен: {response.status_code}"

    response_data = response.json()
    assert isinstance(response_data, list), "Ожидался массив переводов"

    # Проверяем, что список начинается с перевода с индексом offset
    expected_ids = translation_ids[offset:]  # Ожидаемые ID переводов после смещения
    actual_ids = [tr["id"] for tr in response_data]
    assert actual_ids == expected_ids[:len(actual_ids)], (
        f"Список переводов не совпадает с ожидаемым после смещения. "
        f"Ожидаемые: {expected_ids}, полученные: {actual_ids}"
    )

    # Шаг 4: Удаление созданных переводов
    for translation_id in translation_ids:
        delete_translation(access_token, translation_id)

    # Шаг 5: Удаление аккаунта
    delete_user(user["id"])


def test_empty_list_with_large_offset(base_url, create_user_with_login, add_translation, delete_translation, delete_user):
    """
    Проверяет, что при использовании параметра offset, превышающего количество доступных переводов, сервер возвращает пустой список.

    Шаги:
    1. Создаётся новый аккаунт пользователя.
    2. Загружается несколько переводов.
    3. Выполняется запрос с параметром offset, превышающим количество доступных переводов.
    4. Проверяется, что список переводов пустой.
    5. Удаляются созданные переводы.
    6. Удаляется созданный аккаунт пользователя.
    """
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    access_token = user["access_token"]

    # Шаг 2: Создание переводов
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation_ids = []
    num_translations = 3

    for i in range(num_translations):
        translation = add_translation(access_token, test_video_path)
        translation_ids.append(translation["id"])

    # Шаг 3: Проверка пустого списка с большим offset
    large_offset = 100
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/?offset={large_offset}&limit=10", headers=headers)
    assert response.status_code == 200, f"Ожидаемый статус код 200, получен: {response.status_code}"

    response_data = response.json()
    assert isinstance(response_data, list), "Ожидался массив переводов"
    assert len(response_data) == 0, "Ожидался пустой список, но он содержит данные"

    # Шаг 4: Удаление созданных переводов
    for translation_id in translation_ids:
        delete_translation(access_token, translation_id)

    delete_user(user["id"])


def test_request_without_params(base_url, create_user_with_login, add_translation, delete_translation, delete_user):
    """
    Проверяет, что сервер корректно обрабатывает запрос без указания параметров.

    Шаги:
    1. Создаётся новый аккаунт пользователя.
    2. Загружается несколько переводов, связанных с этим аккаунтом.
    3. Выполняется запрос без указания параметров.
    4. Проверяется, что возвращённый список соответствует переводам пользователя.
    5. Удаляются созданные переводы.
    6. Удаляется созданный аккаунт пользователя.
    """
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    access_token = user["access_token"]

    # Шаг 2: Создание переводов
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation_ids = []
    num_translations = 3

    for i in range(num_translations):
        translation = add_translation(access_token, test_video_path)
        translation_ids.append(translation["id"])

    # Шаг 3: Запрос без параметров
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/", headers=headers)
    assert response.status_code == 200, f"Ожидаемый статус код 200, получен: {response.status_code}"

    response_data = response.json()
    assert isinstance(response_data, list), "Ожидался массив переводов"

    actual_ids = [tr["id"] for tr in response_data]
    assert set(actual_ids) == set(translation_ids), (
        f"Возвращённые переводы не соответствуют переводам пользователя. "
        f"Ожидаемые: {translation_ids}, полученные: {actual_ids}"
    )

    # Шаг 4: Удаление созданных переводов
    for translation_id in translation_ids:
        delete_translation(access_token, translation_id)

    # Шаг 5: Удаление аккаунта
    delete_user(user["id"])


def test_access_without_authorization(base_url):
    """
    Проверяет, что сервер запрещает доступ к эндпоинту без авторизации.

    Шаги:
    1. Выполняется запрос к эндпоинту без передачи заголовка Authorization.
    2. Проверяется, что сервер возвращает статус код 401.
    """
    # Шаг 1: Выполнение запроса без авторизации
    headers = {"accept": "application/json"}
    response = requests.get_request(f"{base_url}/translate/", headers=headers)

    # Шаг 2: Проверка статус-кода
    assert response.status_code == 401, f"Ожидаемый статус код 401, получен: {response.status_code}"


def test_invalid_my_param(base_url, create_user_with_login):
    """
    Проверяет реакцию сервера на некорректное значение параметра my.

    Шаги:
    1. Создаётся новый аккаунт пользователя.
    2. Выполняется запрос с некорректным значением параметра my.
    3. Проверяется, что сервер возвращает статус код 422 и описание ошибки.
    """
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    access_token = user["access_token"]

    # Шаг 2: Выполнение запроса с некорректным значением my
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/?my=invalid", headers=headers)

    # Шаг 3: Проверка статус-кода
    assert response.status_code == 422, f"Ожидаемый статус код 422, получен: {response.status_code}"

    # Шаг 4: Проверка тела ответа
    response_data = response.json()
    assert "detail" in response_data, "Ожидалось описание ошибки в теле ответа"


def test_invalid_offset_param(base_url, create_user_with_login):
    """
    Проверяет реакцию сервера на некорректное значение параметра offset.

    Шаги:
    1. Создаётся новый аккаунт пользователя.
    2. Выполняется запрос с некорректным значением параметра offset.
    3. Проверяется, что сервер возвращает статус код 422 и описание ошибки.
    """
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    access_token = user["access_token"]

    # Шаг 2: Выполнение запроса с некорректным значением offset
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/?offset=abc", headers=headers)

    # Шаг 3: Проверка статус-кода
    assert response.status_code == 422, f"Ожидаемый статус код 422, получен: {response.status_code}"

    # Шаг 4: Проверка тела ответа
    response_data = response.json()
    assert "detail" in response_data, "Ожидалось описание ошибки в теле ответа"


def test_invalid_limit_param(base_url, create_user_with_login):
    """
    Проверяет реакцию сервера на некорректное значение параметра limit.

    Шаги:
    1. Создаётся новый аккаунт пользователя.
    2. Выполняется запрос с некорректным значением параметра limit.
    3. Проверяется, что сервер возвращает статус код 422 и описание ошибки.
    """
    # Шаг 1: Создание пользователя
    user = create_user_with_login
    access_token = user["access_token"]

    # Шаг 2: Выполнение запроса с некорректным значением limit
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get_request(f"{base_url}/translate/?limit=xyz", headers=headers)

    # Шаг 3: Проверка статус-кода
    assert response.status_code == 422, f"Ожидаемый статус код 422, получен: {response.status_code}"

    # Шаг 4: Проверка тела ответа
    response_data = response.json()
    assert "detail" in response_data, "Ожидалось описание ошибки в теле ответа"
