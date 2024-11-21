import os
import pytest
from api import requests


def test_submit_feedback_with_valid_score(base_url, signin_user):
    """
    Проверяет, что пользователь может успешно отправить отзыв для завершенного перевода
    с корректным значением оценки.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Указать ID завершенного перевода.
    3. Отправить POST-запрос с корректной оценкой (например, 85).
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что параметр feedback в ответе обновился с корректным значением.
    """
    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Указать ID завершенного перевода
    translation_id = str(os.getenv("TRANSLATION_ID"))

    # Шаг 3: Отправить POST-запрос с корректной оценкой
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    feedback_score = 85  # Корректное значение отзыва
    payload = feedback_score

    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/feedback/",
        headers=headers,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 200
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что параметр feedback в ответе обновился
    response_data = response.json()
    assert "feedback" in response_data, "Ответ не содержит параметра 'feedback'"
    assert response_data["feedback"] == feedback_score, (
        f"Ожидалось, что feedback будет равен {feedback_score}, получено: {response_data['feedback']}"
    )


def test_submit_feedback_with_invalid_score(base_url, signin_user):
    """
    Проверяет, что сервер корректно обрабатывает запрос с некорректным значением оценки.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Указать ID завершенного перевода.
    3. Отправить POST-запрос с некорректной оценкой (например, 101).
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Указать ID завершенного перевода
    translation_id = str(os.getenv("TRANSLATION_ID"))

    # Шаг 3: Отправить POST-запрос с некорректной оценкой
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    feedback_score = 101  # Некорректное значение отзыва (вне диапазона)
    payload = feedback_score

    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/feedback/",
        headers=headers,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )


def test_submit_feedback_for_nonexistent_translation(base_url, signin_user):
    """
    Проверяет, что сервер корректно обрабатывает запрос с несуществующим ID перевода.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Указать несуществующий ID перевода.
    3. Отправить POST-запрос с корректной оценкой.
    4. Проверить, что сервер возвращает статус код 404.
    5. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Указать несуществующий ID перевода
    nonexistent_translation_id = 999999  # ID, отсутствующий в базе данных

    # Шаг 3: Отправить POST-запрос с корректной оценкой
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    feedback_score = 80  # Корректное значение оценки
    payload = feedback_score

    response = requests.post_request(
        f"{base_url}/translate/{nonexistent_translation_id}/feedback/",
        headers=headers,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 404
    assert response.status_code == 404, (
        f"Ожидаемый статус код 404, получен: {response.status_code}"
    )


def test_submit_feedback_for_foreign_translation(base_url, signin_user):
    """
    Проверяет, что пользователь не может оставить отзыв для перевода, который ему не принадлежит.

    Шаги:
    1. Логин под пользователем с балансом (не владельцем перевода).
    2. Указать ID перевода, принадлежащего другому пользователю.
    3. Отправить POST-запрос с корректной оценкой.
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

    # Шаг 3: Отправить POST-запрос с корректной оценкой
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    feedback_score = 90  # Корректное значение оценки
    payload = feedback_score

    response = requests.post_request(
        f"{base_url}/translate/{foreign_translation_id}/feedback/",
        headers=headers,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 403
    assert response.status_code == 404, (
        f"Ожидаемый статус код 403, получен: {response.status_code}"
    )


def test_submit_feedback_without_authorization(base_url):
    """
    Проверяет, что сервер запрещает доступ к эндпоинту для отправки отзыва без авторизации.

    Шаги:
    1. Указать ID существующего перевода.
    2. Отправить POST-запрос с корректной оценкой без авторизационного токена.
    3. Проверить, что сервер возвращает статус код 401.
    4. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Указать ID существующего перевода
    translation_id = str(os.getenv("TRANSLATION_ID"))

    # Шаг 2: Отправить POST-запрос с корректной оценкой без авторизационного токена
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    feedback_score = 80  # Корректное значение оценки
    payload = feedback_score

    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/feedback/",
        headers=headers,
        json=payload
    )

    # Шаг 3: Проверить, что сервер возвращает статус код 401
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )


def test_submit_feedback_with_empty_body(base_url, signin_user):
    """
    Проверяет, что сервер корректно обрабатывает запрос с пустым телом при отправке отзыва.

    Шаги:
    1. Логин под пользователем без баланса.
    2. Указать ID существующего перевода.
    3. Отправить POST-запрос с пустым телом.
    4. Проверить, что сервер возвращает статус код 422.
    5. Проверить, что тело ответа содержит описание ошибки.
    """
    # Шаг 1: Логин под пользователем без баланса
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    # Шаг 2: Указать ID существующего перевода
    translation_id = str(os.getenv("TRANSLATION_ID"))  # ID существующего перевода

    # Шаг 3: Отправить POST-запрос с пустым телом
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = None  # Пустое тело запроса

    response = requests.post_request(
        f"{base_url}/translate/{translation_id}/feedback/",
        headers=headers,
        json=payload
    )

    # Шаг 4: Проверить, что сервер возвращает статус код 422
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )
