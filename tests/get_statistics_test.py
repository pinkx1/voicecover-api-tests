import os
import pytest
from api import requests


def test_get_statistics_with_valid_date_range(base_url, signin_user):
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
    }
    params = {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
    }
    response = requests.get_request(f"{base_url}/statistic/", headers=headers, params=params)

    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    expected_response_structure = {
        "users": int,
        "users_total": int,
        "translates": {
            "count": int,
            "amount": (int, float),
        },
        "translates_total": {
            "count": int,
            "amount": (int, float),
        },
        "transactions": int,
        "transactions_total": int,
        "income": {
            "yoomoney": (int, float),
            "admin": (int, float),
        },
        "income_total": {
            "yoomoney": (int, float),
            "admin": (int, float),
        },
    }

    response_data = response.json()

    def validate_structure(data, structure, parent_key=""):
        for key, value_type in structure.items():
            assert key in data, f"Ключ '{key}' отсутствует в ответе (в '{parent_key}')"
            if isinstance(value_type, dict):
                assert isinstance(data[key], dict), (
                    f"Поле '{key}' в '{parent_key}' должно быть объектом."
                )
                validate_structure(data[key], value_type, key)
            else:
                assert isinstance(data[key], value_type), (
                    f"Поле '{key}' в '{parent_key}' имеет неверный тип данных. "
                    f"Ожидаемый: {value_type}, полученный: {type(data[key])}"
                )

    validate_structure(response_data, expected_response_structure)


@pytest.mark.xfail(reason="Сервер возвращает 500 при запросе без указания временного интервала.")
def test_get_statistics_without_date_range(base_url, signin_user):
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
    }
    response = requests.get_request(f"{base_url}/statistic/", headers=headers)
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    expected_response_structure = {
        "users": int,
        "users_total": int,
        "translates": {
            "count": int,
            "amount": (int, float),
        },
        "translates_total": {
            "count": int,
            "amount": (int, float),
        },
        "transactions": int,
        "transactions_total": int,
        "income": {
            "yoomoney": (int, float),
            "admin": (int, float),
        },
        "income_total": {
            "yoomoney": (int, float),
            "admin": (int, float),
        },
    }

    response_data = response.json()

    def validate_structure(data, structure, parent_key=""):
        for key, value_type in structure.items():
            assert key in data, f"Ключ '{key}' отсутствует в ответе (в '{parent_key}')"
            if isinstance(value_type, dict):
                assert isinstance(data[key], dict), (
                    f"Поле '{key}' в '{parent_key}' должно быть объектом."
                )
                validate_structure(data[key], value_type, key)
            else:
                assert isinstance(data[key], value_type), (
                    f"Поле '{key}' в '{parent_key}' имеет неверный тип данных. "
                    f"Ожидаемый: {value_type}, полученный: {type(data[key])}"
                )

    validate_structure(response_data, expected_response_structure)


def test_get_statistics_with_invalid_date_format(base_url, signin_user):
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
    }
    params = {
        "start_date": "01-01-2024",  # Некорректный формат
        "end_date": "31-01-2024",    # Некорректный формат
    }
    response = requests.get_request(f"{base_url}/statistic/", headers=headers, params=params)

    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )


@pytest.mark.xfail(reason="Сервер возвращает 500")
def test_get_statistics_with_missing_start_date(base_url, signin_user):
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
    }
    params = {
        "end_date": "2024-01-31",  # Указан только end_date
    }
    response = requests.get_request(f"{base_url}/statistic/", headers=headers, params=params)

    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    response_data = response.json()
    expected_keys = [
        "users", "users_total", "translates", "translates_total",
        "transactions", "transactions_total", "income", "income_total"
    ]
    for key in expected_keys:
        assert key in response_data, f"Ключ '{key}' отсутствует в ответе"


@pytest.mark.xfail(reason="Сервер возвращает 500")
def test_get_statistics_with_missing_end_date(base_url, signin_user):
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
    }
    params = {
        "start_date": "2024-01-01",  # Указан только start_date
    }
    response = requests.get_request(f"{base_url}/statistic/", headers=headers, params=params)

    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    response_data = response.json()
    expected_keys = [
        "users", "users_total", "translates", "translates_total",
        "transactions", "transactions_total", "income", "income_total"
    ]
    for key in expected_keys:
        assert key in response_data, f"Ключ '{key}' отсутствует в ответе"


@pytest.mark.xfail(reason="Сервер возвращает 200 вместо 422 при некорректном интервале дат")
def test_get_statistics_with_start_date_after_end_date(base_url, signin_user):
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
    }
    params = {
        "start_date": "2024-01-31",  # start_date позже end_date
        "end_date": "2024-01-01",
    }
    response = requests.get_request(f"{base_url}/statistic/", headers=headers, params=params)

    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )

    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert isinstance(response_data["detail"], list), "Поле 'detail' должно быть списком"
    assert any(
        "start_date" in error["loc"] and "end_date" in error["loc"]
        for error in response_data["detail"]
    ), "Ответ не содержит ожидаемого описания ошибки о некорректном интервале дат"


def test_get_statistics_without_authorization(base_url):
    params = {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
    }

    headers = {
        "accept": "application/json",
    }
    response = requests.get_request(f"{base_url}/statistic/", headers=headers, params=params)

    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )


def test_get_statistics_as_regular_user(base_url, signin_user):
    user_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    user_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)
    user_access_token = user["access_token"]

    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
    }
    params = {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
    }
    response = requests.get_request(f"{base_url}/statistic/", headers=headers, params=params)

    assert response.status_code == 403, (
        f"Ожидаемый статус код 403, получен: {response.status_code}"
    )
