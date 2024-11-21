import os
import pytest
from api import requests


def test_create_payment_successfully_with_amount(base_url, signin_user):
    """
    Проверяет, что авторизованный пользователь может успешно создать платеж, указав только `amount`.
    Ожидается, что сервер возвращает статус код 200 и корректный URL в ответе.
    """
    # Шаг 1: Авторизоваться под пользователем
    user_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    user_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)
    user_access_token = user["access_token"]

    # Шаг 2: Выполнить POST-запрос на создание платежа
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {"amount": 100}
    response = requests.post_request(f"{base_url}/user/create_payment/", headers=headers, json=payload)

    # Шаг 3: Проверить статус код
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 4: Проверить тело ответа
    response_data = response.json()
    assert "id" in response_data, "Ответ не содержит поле `id`"
    assert "url" in response_data, "Ответ не содержит поле `url`"

    # Проверить, что поле `url` содержит валидный URL
    import re
    url_regex = re.compile(
        r'^(?:http|https)://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    assert re.match(url_regex, response_data["url"]), (
        f"Поле `url` содержит некорректный URL: {response_data['url']}"
    )


def test_create_payment_successfully_with_amount_and_code(base_url, signin_user):
    """
    Проверяет, что авторизованный пользователь может успешно создать платеж, указав оба параметра: `amount` и `code`.
    Ожидается, что сервер возвращает статус код 200 и корректный URL в ответе.
    """
    # Шаг 1: Авторизоваться под пользователем
    user_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    user_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)
    user_access_token = user["access_token"]

    # Шаг 2: Выполнить POST-запрос на создание платежа
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {"amount": 100, "code": "discount123"}
    response = requests.post_request(f"{base_url}/user/create_payment/", headers=headers, json=payload)

    # Шаг 3: Проверить статус код
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 4: Проверить тело ответа
    response_data = response.json()
    assert "id" in response_data, "Ответ не содержит поле `id`"
    assert "url" in response_data, "Ответ не содержит поле `url`"

    # Проверить, что поле `url` содержит валидный URL
    import re
    url_regex = re.compile(
        r'^(?:http|https)://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    assert re.match(url_regex, response_data["url"]), (
        f"Поле `url` содержит некорректный URL: {response_data['url']}"
    )


@pytest.mark.xfail(reason="Сервер возвращает 500 вместо 422 при отрицательном значении `amount`")
def test_create_payment_with_invalid_amount(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос на создание платежа, если `amount` задан отрицательным значением.
    Ожидается, что сервер возвращает статус код 422 и сообщение об ошибке.
    """
    # Шаг 1: Авторизоваться под пользователем
    user_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    user_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)
    user_access_token = user["access_token"]

    # Шаг 2: Выполнить POST-запрос на создание платежа с отрицательным `amount`
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {"amount": -100}
    response = requests.post_request(f"{base_url}/user/create_payment/", headers=headers, json=payload)

    # Шаг 3: Проверить статус код
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )

    # Шаг 4: Проверить сообщение об ошибке
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит поле `detail` с описанием ошибки"
    error_details = response_data["detail"]
    assert isinstance(error_details, list), "`detail` должно быть списком"
    assert any(
        error.get("msg") for error in error_details
    ), f"Ответ не содержит ожидаемое сообщение об ошибке: {response_data}"


def test_create_payment_without_amount(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос на создание платежа,
    если обязательный параметр `amount` отсутствует.
    Ожидается, что сервер возвращает статус код 422 и сообщение об ошибке.
    """
    # Шаг 1: Авторизоваться под пользователем
    user_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    user_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)
    user_access_token = user["access_token"]

    # Шаг 2: Выполнить POST-запрос на создание платежа без параметра `amount`
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    payload = {"code": "discount123"}
    response = requests.post_request(f"{base_url}/user/create_payment/", headers=headers, json=payload)

    # Шаг 3: Проверить статус код
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )

    # Шаг 4: Проверить сообщение об ошибке
    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит поле `detail` с описанием ошибки"
    error_details = response_data["detail"]
    assert isinstance(error_details, list), "`detail` должно быть списком"
    assert any(
        error.get("msg") for error in error_details
    ), f"Ответ не содержит ожидаемое сообщение об ошибке: {response_data}"


def test_create_payment_without_authorization(base_url):
    """
    Проверяет, что сервер отклоняет запрос на создание платежа от неавторизованного пользователя.
    Ожидается, что сервер возвращает статус код 401 (Unauthorized).
    """
    # Шаг 1: Подготовить тело запроса
    payload = {"amount": 100}

    # Шаг 2: Выполнить POST-запрос без заголовка авторизации
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.post_request(f"{base_url}/user/create_payment/", headers=headers, json=payload)

    # Шаг 3: Проверить статус код
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )


def test_create_payment_with_empty_body(base_url, signin_user):
    """
    Проверяет, что сервер отклоняет запрос на создание платежа с пустым телом запроса.
    Ожидается, что сервер возвращает статус код 422 (Validation Error).
    """
    # Шаг 1: Авторизоваться под пользователем
    user_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    user_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)
    user_access_token = user["access_token"]

    # Шаг 2: Выполнить POST-запрос с пустым телом
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json",
    }
    response = requests.post_request(f"{base_url}/user/create_payment/", headers=headers, json={})

    # Шаг 3: Проверить статус код
    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )
