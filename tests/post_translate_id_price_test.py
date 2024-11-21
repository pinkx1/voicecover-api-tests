import os
import pytest
from api import requests


def test_calculate_price_with_balance_correct_request(base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет расчет стоимости перевода на аккаунте с балансом и значение параметра need_money = False.

    Шаги:
    1. Логин под пользователем с балансом.
    2. Проверить баланс и пополнить его через администратора, если он недостаточный.
    3. Создать перевод для расчета стоимости.
    4. Выполнить запрос на расчет стоимости перевода.
    5. Проверить, что сервер возвращает статус код 200.
    6. Проверить, что поле need_money в ответе равно False.
    7. Удалить созданный перевод.
    """
    # Шаг 1: Логин под пользователем с балансом
    some_balance_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    some_balance_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(some_balance_email, some_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Проверить баланс пользователя через GET /user/me/
    headers_user = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }

    response_user = requests.get_request(
        f"{base_url}/user/me/",
        headers=headers_user
    )
    assert response_user.status_code == 200, (
        f"Не удалось получить информацию о пользователе, статус код: {response_user.status_code}"
    )
    user_data = response_user.json()
    current_balance = user_data.get("balance", 0)
    user_id = user_data.get("id")

    # Если баланс недостаточный, пополнить через администратора
    if current_balance < 1000:
        # Логин под администратором
        admin_email = os.getenv("ADMIN_USER_EMAIL")
        admin_password = os.getenv("ADMIN_USER_PASSWORD")
        admin = signin_user(admin_email, admin_password)
        admin_access_token = admin["access_token"]

        headers_admin = {
            "Authorization": f"Bearer {admin_access_token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        top_up_payload = {
            "user_id": user_id,
            "type_transaction": "credit",
            "amount": 1000
        }

        response_top_up = requests.post_request(
            f"{base_url}/transaction/",
            headers=headers_admin,
            json=top_up_payload
        )
        assert response_top_up.status_code == 200, (
            f"Не удалось пополнить баланс через администратора, статус код: {response_top_up.status_code}"
        )

    # Шаг 3: Создать перевод
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    try:
        # Шаг 4: Выполнить запрос на расчет стоимости перевода
        payload = {
            "language": "en",
            "save_origin_voice": True,
            "has_logo": False,
            "notification": True,
            "voice_clone": True,
            "lipsync": True,
            "subtitle_download": True,
            "subtitle_on_video": True,
            "subtitle_edit": True,
            "voice_gender": "f-af-1",
            "voice_count": 0
        }

        headers_user["Content-Type"] = "application/json"

        response = requests.post_request(
            f"{base_url}/translate/{translation_id}/price/",
            headers=headers_user,
            json=payload
        )

        # Шаг 5: Проверить, что сервер возвращает статус код 200
        assert response.status_code == 200, (
            f"Ожидаемый статус код 200, получен: {response.status_code}"
        )

        # Шаг 6: Проверить, что поле need_money = False
        response_data = response.json()
        assert "need_money" in response_data, "Ответ не содержит ключ 'need_money'"
        assert response_data["need_money"] is False, (
            f"Ожидалось, что поле 'need_money' будет False, получено: {response_data['need_money']}"
        )
    finally:
        # Шаг 7: Удалить перевод
        delete_translation(user_access_token, translation_id)


def test_calculate_price_without_balance_correct_request(base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет расчет стоимости перевода на аккаунте без баланса и значение параметра need_money = True.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Создать перевод для расчета стоимости.
    3. Выполнить запрос на расчет стоимости перевода.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что поле need_money в ответе равно True.
    6. Удалить созданный перевод.
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
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    try:
        # Шаг 3: Выполнить запрос на расчет стоимости перевода
        payload = {
            "language": "en",
            "save_origin_voice": True,
            "has_logo": False,
            "notification": True,
            "voice_clone": True,
            "lipsync": True,
            "subtitle_download": True,
            "subtitle_on_video": True,
            "subtitle_edit": True,
            "voice_gender": "f-af-1",
            "voice_count": 0
        }

        headers_user = {
            "Authorization": f"Bearer {user_access_token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.post_request(
            f"{base_url}/translate/{translation_id}/price/",
            headers=headers_user,
            json=payload
        )

        # Шаг 4: Проверить, что сервер возвращает статус код 200
        assert response.status_code == 200, (
            f"Ожидаемый статус код 200, получен: {response.status_code}"
        )

        # Шаг 5: Проверить, что поле need_money = True
        response_data = response.json()
        assert "need_money" in response_data, "Ответ не содержит ключ 'need_money'"
        assert response_data["need_money"] is True, (
            f"Ожидалось, что поле 'need_money' будет True, получено: {response_data['need_money']}"
        )
    finally:
        # Шаг 6: Удалить перевод
        delete_translation(user_access_token, translation_id)


def test_calculate_price_free_plan(base_url, signin_user, add_translation, delete_translation):
    """
    Проверяет расчет стоимости перевода для опций, доступных в бесплатном тарифе.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Создать перевод для расчета стоимости.
    3. Выполнить запрос на расчет стоимости перевода с опциями бесплатного тарифа.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что поле price равно "0.00".
    6. Удалить созданный перевод.
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
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(user_access_token, test_video_path)
    translation_id = translation["id"]

    try:
        # Шаг 3: Выполнить запрос на расчет стоимости перевода с опциями бесплатного тарифа
        payload = {
            "language": "en",
            "save_origin_voice": False,  # Бесплатная опция
            "has_logo": True,  # Бесплатная опция
            "notification": False,  # Бесплатная опция
            "voice_clone": False,  # Бесплатная опция
            "lipsync": False,  # Бесплатная опция
            "subtitle_download": True,  # Бесплатная опция
            "subtitle_on_video": False,  # Бесплатная опция
            "subtitle_edit": False,  # Бесплатная опция
            "voice_gender": None,  # Бесплатная опция
            "voice_count": 1  # Бесплатная опция
        }

        headers_user = {
            "Authorization": f"Bearer {user_access_token}",
            "accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.post_request(
            f"{base_url}/translate/{translation_id}/price/",
            headers=headers_user,
            json=payload
        )

        # Шаг 4: Проверить, что сервер возвращает статус код 200
        assert response.status_code == 200, (
            f"Ожидаемый статус код 200, получен: {response.status_code}"
        )

        # Шаг 5: Проверить, что поле price = "0.00"
        response_data = response.json()
        assert "price" in response_data, "Ответ не содержит ключ 'price'"
        assert response_data["price"] == "0.00", (
            f"Ожидалось, что поле 'price' будет равно '0.00', получено: {response_data['price']}"
        )
    finally:
        # Шаг 6: Удалить перевод
        delete_translation(user_access_token, translation_id)


def test_calculate_price_with_invalid_translation_id(base_url, signin_user):
    """
    Проверяет реакцию сервера на запрос расчета стоимости с некорректным ID перевода.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Указать некорректный ID перевода (например, 999999).
    3. Выполнить запрос на расчет стоимости.
    4. Проверить, что сервер возвращает статус код 404.
    5. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Указать некорректный ID перевода
    invalid_translation_id = 999999

    # Шаг 3: Выполнить запрос на расчет стоимости
    payload = {
        "language": "en",
        "save_origin_voice": True,
        "has_logo": False,
        "notification": True,
        "voice_clone": True,
        "lipsync": True,
        "subtitle_download": True,
        "subtitle_on_video": True,
        "subtitle_edit": True,
        "voice_gender": "f-af-1",
        "voice_count": 0
    }

    headers_user = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.post_request(
        f"{base_url}/translate/{invalid_translation_id}/price/",
        headers=headers_user,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 404
    assert response.status_code == 404, (
        f"Ожидаемый статус код 404 для некорректного ID, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что тело ответа содержит описание ошибки
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert response_data["detail"] == "Not found", (
        f"Ожидалось сообщение об ошибке 'Not found', получено: {response_data['detail']}"
    )


def test_calculate_price_without_authorization(base_url):
    """
    Проверяет реакцию сервера на запрос расчета стоимости без авторизации.

    Шаги:
    1. Указать ID существующего перевода.
    2. Выполнить запрос на расчет стоимости без заголовка авторизации.
    3. Проверить, что сервер возвращает статус код 401.
    4. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Указать ID существующего перевода
    translation_id = str(os.getenv("TRANSLATION_ID"))

    # Шаг 2: Выполнить запрос на расчет стоимости без заголовка авторизации
    payload = {
        "language": "en",
        "save_origin_voice": True,
        "has_logo": False,
        "notification": True,
        "voice_clone": True,
        "lipsync": True,
        "subtitle_download": True,
        "subtitle_on_video": True,
        "subtitle_edit": True,
        "voice_gender": "f-af-1",
        "voice_count": 0
    }

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/price/",
        headers=headers,
        json=payload
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 401
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )
