import os
import pytest
from api import requests


def test_delete_user_successfully_as_admin(base_url, signin_user, create_user_with_login):
    target_user = create_user_with_login
    user_id = target_user["id"]

    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_token = admin["access_token"]

    headers = {
        "Authorization": f"Bearer {admin_token}",
        "accept": "application/json"
    }
    response = requests.delete_request(
        f"{base_url}/user/{user_id}",
        headers=headers
    )

    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    response_data = response.json()
    assert response_data == {"success": True}, (
        f"Ожидаемый ответ: {{'success': True}}, полученный ответ: {response_data}"
    )


def test_delete_nonexistent_user_as_admin(base_url, signin_user):
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_token = admin["access_token"]

    nonexistent_user_id = 12345678  # Указываем ID, которого гарантированно нет в системе
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "accept": "application/json"
    }
    response = requests.delete_request(
        f"{base_url}/user/{nonexistent_user_id}",
        headers=headers
    )

    assert response.status_code == 404, (
        f"Ожидаемый статус код 404, получен: {response.status_code}"
    )


def test_delete_user_with_invalid_id_as_admin(base_url, signin_user):
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_token = admin["access_token"]

    invalid_user_id = "abc"  # Некорректное значение ID
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "accept": "application/json"
    }
    response = requests.delete_request(
        f"{base_url}/user/{invalid_user_id}",
        headers=headers
    )

    assert response.status_code == 422, (
        f"Ожидаемый статус код 422, получен: {response.status_code}"
    )

    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert any(
        error["loc"][-1] == "id" and error["type"] == "int_parsing"
        for error in response_data["detail"]
    ), f"Ожидаемое описание ошибки не найдено: {response_data['detail']}"


def test_delete_user_without_authorization(base_url, create_user_with_login):
    new_user = create_user_with_login
    user_id = new_user["id"]

    response = requests.delete_request(
        f"{base_url}/user/{user_id}",
        headers={"accept": "application/json"}  # Без Authorization
    )

    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )


def test_delete_user_as_regular_user(base_url, signin_user, create_user_with_login):
    new_user = create_user_with_login
    user_id = new_user["id"]

    regular_user_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    regular_user_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    regular_user = signin_user(regular_user_email, regular_user_password)
    regular_user_access_token = regular_user["access_token"]

    headers = {
        "Authorization": f"Bearer {regular_user_access_token}",
        "accept": "application/json"
    }
    response = requests.delete_request(
        f"{base_url}/user/{user_id}",
        headers=headers
    )

    assert response.status_code == 403, (
        f"Ожидаемый статус код 403, получен: {response.status_code}"
    )
