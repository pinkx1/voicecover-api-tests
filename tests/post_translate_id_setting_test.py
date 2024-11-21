import os
import pytest
from api import requests


def test_successful_setting_and_start_translation_with_balance_check(
        base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет, что авторизованный пользователь с достаточным балансом может успешно
    применить корректные настройки и запустить перевод. Если баланс меньше 1000, он пополняется.

    Шаги:
    1. Авторизоваться под пользователем.
    2. Проверить баланс пользователя. Если меньше 1000, пополнить баланс.
    3. Загрузить перевод.
    4. Установить настройки перевода.
    5. Проверить, что сервер возвращает статус код 200.
    6. Проверить, что настройки обновлены корректно.
    7. Удалить перевод.
    """
    # Шаг 1: Авторизоваться под пользователем
    user_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    user_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)
    user_access_token = user["access_token"]
    user_id = user["user_id"]

    # Шаг 2: Проверить баланс пользователя
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }
    balance_response = requests.get_request(
        f"{base_url}/user/me/",
        headers=headers
    )

    user_data = balance_response.json()
    current_balance = user_data.get("balance", 0)
    if current_balance < 1000:
        top_up_payload = {
            "user_id": user_id,
            "type_transaction": "debit",
            "amount": 10000
        }
        top_up_response = requests.post_request(
            f"{base_url}/transaction/",
            headers=headers,
            json=top_up_payload
        )
        assert top_up_response.status_code == 200, (
            f"Ожидаемый статус код 200 для пополнения баланса, получен: {top_up_response.status_code}"
        )

    # Шаг 3: Загрузить перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 4: Установить настройки перевода
    settings_payload = {
        "language": "en",
        "save_origin_voice": True,
        "has_logo": False,
        "notification": True,
        "voice_clone": True,
        "lipsync": False,
        "subtitle_download": True,
        "subtitle_on_video": False,
        "subtitle_edit": True,
        "voice_gender": "f-af-1",
        "voice_count": 1
    }
    settings_response = requests.post_request(
        f"{base_url}/translate/{translation_id}/setting/",
        headers=headers,
        json=settings_payload
    )
    assert settings_response.status_code == 200, (
        f"Ожидаемый статус код 200 для успешного применения настроек, получен: {settings_response.status_code}"
    )

    # Шаг 5: Проверить, что настройки обновлены корректно
    response_data = settings_response.json()
    for key, value in settings_payload.items():
        assert response_data[key] == value, (
            f"Настройка {key} должна быть обновлена. Ожидалось: {value}, Получено: {response_data[key]}"
        )

    # Шаг 6: Удалить перевод
    delete_translation(user_access_token, translation_id)


def test_translation_settings_insufficient_balance(
    base_url, signin_user, add_translation, delete_translation
):
    """
    Проверяет попытку запуска перевода с недостаточным балансом.

    Шаги:
    1. Логин под пользователем с недостаточным балансом.
    2. Загрузка перевода.
    3. Попытка настройки и запуска перевода.
    4. Проверка, что сервер возвращает статус код 400 (Bad Request).
    """

    # Шаг 1: Логин под пользователем с недостаточным балансом
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Загрузка перевода
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 3: Попытка настройки и запуска перевода
    settings_payload = {
        "language": "en",
        "save_origin_voice": True,
        "has_logo": False,
        "notification": True,
        "voice_clone": True,
        "lipsync": False,
        "subtitle_download": True,
        "subtitle_on_video": False,
        "subtitle_edit": True,
        "voice_gender": "f-af-1",
        "voice_count": 1
    }
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/setting/",
        headers=headers,
        json=settings_payload
    )

    # Шаг 4: Проверка, что сервер возвращает статус код 400
    assert response.status_code == 400, (
        f"Ожидаемый статус код 400 (Bad Request), получен: {response.status_code}"
    )
    response_data = response.json()
    assert response_data == {"detail": "Not enough money"}, (
        f"Некорректное тело ответа: {response_data}"
    )

    # Удаление перевода
    delete_translation(user_access_token, translation_id)


def test_admin_start_translation_with_other_user_data(
    base_url, create_user_with_login, add_translation, delete_translation, signin_user
):
    """
    Проверяет, что администратор может выполнить запрос с настройками перевода другого пользователя,
    включая проверку и пополнение баланса администратора.

    Шаги:
    1. Логин под обычным пользователем.
    2. Загрузка перевода пользователем.
    3. Логин под администратором.
    4. Проверка и пополнение баланса администратора.
    5. Администратор успешно запускает перевод другого пользователя.
    6. Проверка успешного ответа от сервера.
    7. Удаление перевода.
    """

    # Шаг 1: Логин под обычным пользователем
    some_balance_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    some_balance_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(some_balance_email, some_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Загрузка перевода пользователем
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 3: Логин под администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    # Шаг 4: Проверка и пополнение баланса администратора
    headers = {"Authorization": f"Bearer {admin_access_token}", "accept": "application/json"}
    balance_response = requests.get_request(f"{base_url}/user/me/", headers=headers)
    assert balance_response.status_code == 200, (
        f"Не удалось получить баланс администратора: {balance_response.status_code}"
    )
    admin_balance = balance_response.json().get("balance", 0)

    if admin_balance < 1000:
        top_up_payload = {
            "user_id": admin["user_id"],
            "type_transaction": "debit",
            "amount": 10000
        }
        top_up_response = requests.post_request(
            f"{base_url}/transaction/",
            headers=headers,
            json=top_up_payload
        )
        assert top_up_response.status_code == 200, (
            f"Не удалось пополнить баланс администратора: {top_up_response.status_code}"
        )

    # Шаг 5: Администратор запускает перевод другого пользователя
    settings_payload = {
        "language": "en",
        "save_origin_voice": True,
        "has_logo": False,
        "notification": True,
        "voice_clone": True,
        "lipsync": False,
        "subtitle_download": True,
        "subtitle_on_video": False,
        "subtitle_edit": True,
        "voice_gender": "f-af-1",
        "voice_count": 1
    }
    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/setting/",
        headers=headers,
        json=settings_payload
    )

    # Шаг 6: Проверка успешного ответа
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )
    response_data = response.json()
    assert response_data["id"] == translation_id, "ID перевода в ответе не совпадает с ожидаемым"

    # Шаг 7: Удаление перевода
    delete_translation(user_access_token, translation_id)


def test_set_translation_settings_with_nonexistent_id(base_url, signin_user):
    """
    Проверяет реакцию сервера на запрос установки настроек с несуществующим ID перевода.

    Шаги:
    1. Логин под пользователем с балансом.
    2. Выполнить запрос с несуществующим ID перевода.
    3. Проверить, что сервер возвращает статус код 404.
    """

    # Шаг 1: Логин под пользователем с балансом
    some_balance_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    some_balance_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(some_balance_email, some_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Выполнить запрос с несуществующим ID перевода
    nonexistent_translation_id = 999999
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }
    settings_payload = {
        "language": "en",
        "save_origin_voice": True,
        "has_logo": False,
        "notification": True,
        "voice_clone": True,
        "lipsync": False,
        "subtitle_download": True,
        "subtitle_on_video": False,
        "subtitle_edit": True,
        "voice_gender": "f-af-1",
        "voice_count": 1
    }
    response = requests.post_request(
        f"{base_url}/translate/{nonexistent_translation_id}/setting/",
        headers=headers,
        json=settings_payload
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 404
    assert response.status_code == 404, (
        f"Ожидаемый статус код 404, получен: {response.status_code}"
    )
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит описание ошибки"


def test_set_translation_settings_with_invalid_id(base_url, signin_user):
    """
    Проверяет реакцию сервера на запрос установки настроек с некорректным ID перевода.

    Шаги:
    1. Логин под пользователем с балансом.
    2. Выполнить запрос с некорректным ID перевода (например, "abc").
    3. Проверить, что сервер возвращает статус код 422.
    """

    # Шаг 1: Логин под пользователем с балансом
    some_balance_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    some_balance_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(some_balance_email, some_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Выполнить запрос с некорректным ID перевода
    invalid_translation_id = "abc"
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }
    settings_payload = {
        "language": "en",
        "save_origin_voice": True,
        "has_logo": False,
        "notification": True,
        "voice_clone": True,
        "lipsync": False,
        "subtitle_download": True,
        "subtitle_on_video": False,
        "subtitle_edit": True,
        "voice_gender": "f-af-1",
        "voice_count": 1
    }
    response = requests.post_request(
        f"{base_url}/translate/{invalid_translation_id}/setting/",
        headers=headers,
        json=settings_payload
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит описание ошибки"


def test_set_translation_settings_response_structure(base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет структуру ответа при успешной установке настроек перевода.

    Шаги:
    1. Логин под пользователем с балансом.
    2. Загрузить перевод.
    3. Установить настройки перевода.
    4. Проверить структуру и типы данных в ответе сервера.
    5. Удалить перевод.
    """

    # Шаг 1: Логин под пользователем с балансом
    some_balance_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    some_balance_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(some_balance_email, some_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Загрузить перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 3: Установить настройки перевода
    settings_payload = {
        "language": "en",
        "save_origin_voice": False,
        "has_logo": True,
        "notification": False,
        "voice_clone": True,
        "lipsync": False,
        "subtitle_download": True,
        "subtitle_on_video": False,
        "subtitle_edit": False,
        "voice_gender": "f-af-1",
        "voice_count": 0
    }
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/setting/",
        headers=headers,
        json=settings_payload
    )
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )
    response_data = response.json()

    # Шаг 4: Проверить структуру и типы данных в ответе сервера
    expected_structure = {
        "language": str,
        "save_origin_voice": bool,
        "has_logo": bool,
        "notification": bool,
        "voice_clone": bool,
        "lipsync": bool,
        "subtitle_download": bool,
        "subtitle_on_video": bool,
        "subtitle_edit": bool,
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
        "preview": (str, type(None))
    }

    for key, expected_type in expected_structure.items():
        assert key in response_data, f"Ключ {key} отсутствует в ответе сервера"
        assert isinstance(response_data[key], expected_type), (
            f"Ключ {key} имеет неверный тип. Ожидалось: {expected_type}, получено: {type(response_data[key])}"
        )


    # Шаг 5: Удалить перевод
    delete_translation(user_access_token, translation_id)


@pytest.mark.xfail(reason="Баг на бэкенде: сервер возвращает 500 при частично заполненных настройках")
def test_set_translation_partial_settings(base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет, что сервер корректно обрабатывает запрос с частичным заполнением настроек.

    Шаги:
    1. Логин под пользователем с балансом.
    2. Загрузить перевод.
    3. Отправить запрос на установку настроек с частично заполненным телом.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что для отсутствующих полей применяются значения по умолчанию.
    6. Удалить перевод.
    """

    # Шаг 1: Логин под пользователем с балансом
    some_balance_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    some_balance_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(some_balance_email, some_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Загрузить перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 3: Отправить запрос на установку настроек с частично заполненным телом
    partial_settings_payload = {
        "language": "en",
        "save_origin_voice": None,
        "has_logo": None,
        "notification": False,
        "voice_clone": True
        # Остальные поля не указаны (будут интерпретированы как отсутствующие)
    }
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/setting/",
        headers=headers,
        json=partial_settings_payload
    )
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )
    response_data = response.json()

    # Шаг 4: Проверить значения по умолчанию для отсутствующих полей
    default_values = {
        "save_origin_voice": False,
        "has_logo": False,
        "lipsync": False,
        "subtitle_download": False,
        "subtitle_on_video": False,
        "subtitle_edit": False,
        "voice_gender": None,
        "voice_count": 0,
        "current_task": None,
        "feedback": None
    }

    for key, default_value in default_values.items():
        if key not in partial_settings_payload or partial_settings_payload[key] is None:
            assert response_data[key] == default_value, (
                f"Для поля {key} ожидалось значение по умолчанию {default_value}, "
                f"получено: {response_data[key]}"
            )
        else:
            assert response_data[key] == partial_settings_payload[key], (
                f"Для поля {key} ожидалось значение {partial_settings_payload[key]}, "
                f"получено: {response_data[key]}"
            )

    # Шаг 5: Удалить перевод
    delete_translation(user_access_token, translation_id)


def test_set_translation_invalid_language(base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет, что сервер возвращает ошибку при указании некорректного значения языка.

    Шаги:
    1. Логин под пользователем с балансом.
    2. Загрузить перевод.
    3. Отправить запрос на установку настроек с некорректным значением языка.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки.
    6. Удалить перевод.
    """

    # Шаг 1: Логин под пользователем с балансом
    some_balance_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    some_balance_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(some_balance_email, some_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Загрузить перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 3: Отправить запрос на установку настроек с некорректным значением языка
    invalid_language_payload = {
        "language": "invalid",  # Некорректное значение языка
        "save_origin_voice": False,
        "has_logo": True,
        "notification": False,
        "voice_clone": True,
        "lipsync": False,
        "subtitle_download": True,
        "subtitle_on_video": False,
        "subtitle_edit": False,
        "voice_gender": "f-af-1",
        "voice_count": 0
    }
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/setting/",
        headers=headers,
        json=invalid_language_payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422 для некорректного языка, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"

    # Проверка структуры ошибки
    error_detail = response_data["detail"]
    assert isinstance(error_detail, list), "Поле 'detail' должно быть списком"
    assert len(error_detail) > 0, "Поле 'detail' не должно быть пустым"
    language_error = next((err for err in error_detail if "language" in err["loc"]), None)
    assert language_error is not None, "Ошибка в поле 'language' не найдена"
    assert language_error["msg"].startswith("Input should be"), (
        f"Ожидалось сообщение об ошибке 'Input should be ...', получено: {language_error['msg']}"
    )
    assert language_error["type"] == "enum", "Тип ошибки должен быть 'enum'"

    # Шаг 6: Удалить перевод
    delete_translation(user_access_token, translation_id)


def test_set_translation_invalid_voice_clone(base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет, что сервер возвращает ошибку при указании некорректного значения для voice_clone.

    Шаги:
    1. Логин под пользователем с балансом.
    2. Загрузить перевод.
    3. Отправить запрос на установку настроек с некорректным значением voice_clone.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки.
    6. Удалить перевод.
    """

    # Шаг 1: Логин под пользователем с балансом
    some_balance_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    some_balance_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(some_balance_email, some_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Загрузить перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 3: Отправить запрос на установку настроек с некорректным значением voice_clone
    invalid_voice_clone_payload = {
        "language": "en",
        "save_origin_voice": False,
        "has_logo": True,
        "notification": False,
        "voice_clone": "invalid_value",  # Некорректное значение для voice_clone
        "lipsync": False,
        "subtitle_download": True,
        "subtitle_on_video": False,
        "subtitle_edit": False,
        "voice_gender": "f-af-1",
        "voice_count": 0
    }
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/setting/",
        headers=headers,
        json=invalid_voice_clone_payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422 для некорректного значения voice_clone, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки
    response_data = response.json()

    # Проверка структуры ошибки
    error_detail = response_data["detail"]
    assert isinstance(error_detail, list), "Поле 'detail' должно быть списком"
    assert len(error_detail) > 0, "Поле 'detail' не должно быть пустым"
    voice_clone_error = next((err for err in error_detail if "voice_clone" in err["loc"]), None)
    assert voice_clone_error is not None, "Ошибка в поле 'voice_clone' не найдена"
    assert voice_clone_error["msg"] == "Input should be a valid boolean, unable to interpret input", (
        f"Ожидалось сообщение об ошибке 'Input should be a valid boolean, unable to interpret input', получено: {voice_clone_error['msg']}"
    )
    assert voice_clone_error["type"] == "bool_parsing", "Тип ошибки должен быть 'bool_parsing'"

    # Шаг 6: Удалить перевод
    delete_translation(user_access_token, translation_id)


def test_set_translation_invalid_voice_gender(base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет, что сервер возвращает ошибку при указании некорректного значения для voice_gender.

    Шаги:
    1. Логин под пользователем с балансом.
    2. Загрузить перевод.
    3. Отправить запрос на установку настроек с некорректным значением voice_gender.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки.
    6. Удалить перевод.
    """

    # Шаг 1: Логин под пользователем с балансом
    some_balance_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    some_balance_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(some_balance_email, some_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Загрузить перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 3: Отправить запрос на установку настроек с некорректным значением voice_gender
    invalid_voice_gender_payload = {
        "language": "en",
        "save_origin_voice": False,
        "has_logo": True,
        "notification": False,
        "voice_clone": True,
        "lipsync": False,
        "subtitle_download": True,
        "subtitle_on_video": False,
        "subtitle_edit": False,
        "voice_gender": "invalid_gender",  # Некорректное значение для voice_gender
        "voice_count": 0
    }
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/setting/",
        headers=headers,
        json=invalid_voice_gender_payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422 для некорректного значения voice_gender, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"

    # Проверка структуры ошибки
    error_detail = response_data["detail"]
    assert isinstance(error_detail, list), "Поле 'detail' должно быть списком"
    assert len(error_detail) > 0, "Поле 'detail' не должно быть пустым"
    voice_gender_error = next((err for err in error_detail if "voice_gender" in err["loc"]), None)
    assert voice_gender_error is not None, "Ошибка в поле 'voice_gender' не найдена"
    assert voice_gender_error["msg"] == "Input should be a valid voice gender", (
        f"Ожидалось сообщение об ошибке 'Input should be a valid voice gender', получено: {voice_gender_error['msg']}"
    )
    assert voice_gender_error["type"] == "type_error.enum", "Тип ошибки должен быть 'type_error.enum'"

    # Шаг 6: Удалить перевод
    delete_translation(user_access_token, translation_id)


def test_set_translation_invalid_voice_gender(base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет, что сервер возвращает ошибку при указании некорректного значения для voice_gender.

    Шаги:
    1. Логин под пользователем с балансом.
    2. Загрузить перевод.
    3. Отправить запрос на установку настроек с некорректным значением voice_gender.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки.
    6. Удалить перевод.
    """

    # Шаг 1: Логин под пользователем с балансом
    some_balance_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    some_balance_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(some_balance_email, some_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Загрузить перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 3: Отправить запрос на установку настроек с некорректным значением voice_gender
    invalid_voice_gender_payload = {
        "language": "en",
        "save_origin_voice": False,
        "has_logo": True,
        "notification": False,
        "voice_clone": True,
        "lipsync": False,
        "subtitle_download": True,
        "subtitle_on_video": False,
        "subtitle_edit": False,
        "voice_gender": "invalid_gender",  # Некорректное значение для voice_gender
        "voice_count": 0
    }
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/setting/",
        headers=headers,
        json=invalid_voice_gender_payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422 для некорректного значения voice_gender, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"

    # Проверка структуры ошибки
    error_detail = response_data["detail"]
    assert isinstance(error_detail, list), "Поле 'detail' должно быть списком"
    assert len(error_detail) > 0, "Поле 'detail' не должно быть пустым"
    voice_gender_error = next((err for err in error_detail if "voice_gender" in err["loc"]), None)
    assert voice_gender_error is not None, "Ошибка в поле 'voice_gender' не найдена"

    # Проверка сообщения об ошибке
    assert "Input should be" in voice_gender_error["msg"], (
        f"Ожидалось сообщение, содержащее 'Input should be', получено: {voice_gender_error['msg']}"
    )
    assert "voice_gender" in str(voice_gender_error["loc"]), (
        f"Ожидалось упоминание 'voice_gender' в 'loc', получено: {voice_gender_error['loc']}"
    )

    # Шаг 6: Удалить перевод
    delete_translation(user_access_token, translation_id)


def test_invalid_http_method_on_settings_endpoint(base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет, что сервер возвращает ошибку при использовании некорректного HTTP-метода (GET вместо POST).

    Шаги:
    1. Логин под пользователем с балансом.
    2. Загрузить перевод.
    3. Отправить запрос на установку настроек с использованием метода GET.
    4. Проверить, что сервер возвращает статус код 405.
    5. Удалить перевод.
    """

    # Шаг 1: Логин под пользователем с балансом
    some_balance_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    some_balance_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(some_balance_email, some_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Загрузить перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 3: Отправить запрос на установку настроек с использованием метода GET
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
    }
    response = requests.get_request(
        f"{base_url}/translate/{translation_id}/setting/",
        headers=headers
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 405
    assert response.status_code == 405, (
        f"Ожидаемый статус код 405 для некорректного метода, получен: {response.status_code}"
    )

    # Шаг 5: Удалить перевод
    delete_translation(user_access_token, translation_id)


def test_translation_with_free_settings(base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет, что перевод с бесплатными параметрами выполняется успешно даже при отсутствии средств на балансе.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Загрузить перевод.
    3. Отправить запрос на установку бесплатных параметров.
    4. Проверить, что сервер возвращает статус код 200.
    5. Удалить перевод.
    """

    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Загрузить перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    # Шаг 3: Отправить запрос на установку бесплатных параметров
    free_settings_payload = {
        "language": "en",
        "save_origin_voice": False,
        "has_logo": True,
        "notification": False,
        "voice_clone": True,
        "lipsync": False,
        "subtitle_download": True,
        "subtitle_on_video": False,
        "subtitle_edit": False,
        "voice_gender": None,
        "voice_count": 1
    }
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/setting/",
        headers=headers,
        json=free_settings_payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 200
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200 для перевода с бесплатными параметрами, получен: {response.status_code}"
    )

    # Шаг 5: Удалить перевод
    delete_translation(user_access_token, translation_id)
