import pytest
from api import requests
import os
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


def test_update_token_success(base_url, create_user_with_login, delete_user):
    user = create_user_with_login
    email = user["email"]
    access_token = user["access_token"]
    user_id = user["id"]

    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        update_token_response = requests.post_request(f"{base_url}/auth/update_token", headers=headers)
        response_data = update_token_response.json()

        assert update_token_response.status_code == 200, (
            f"Ожидается статус код 200, получен: {update_token_response.status_code}"
        )
        assert "access_token" in response_data, "Ожидается наличие 'access_token' в ответе"
        assert "refresh_token" in response_data, "Ожидается наличие 'refresh_token' в ответе"
        assert "user" in response_data, "Ожидается наличие данных пользователя в ответе"
        assert response_data["user"]["email"] == email, "Email пользователя не совпадает с ожидаемым"

    finally:
        delete_user(user_id)


def test_new_access_token_is_different(base_url, create_user_with_login, delete_user):
    user = create_user_with_login
    old_access_token = user["access_token"]
    user_id = user["id"]

    try:
        headers = {"Authorization": f"Bearer {old_access_token}"}
        time.sleep(1)

        update_token_response = requests.post_request(f"{base_url}/auth/update_token", headers=headers)
        response_data = update_token_response.json()
        new_access_token = response_data["access_token"]

        assert update_token_response.status_code == 200, (
            f"Ожидается статус код 200, получен: {update_token_response.status_code}"
        )
        assert new_access_token != old_access_token, "Ожидается, что новый access_token отличается от старого"

    finally:
        delete_user(user_id)


def test_token_expiry_dates(base_url, create_user_with_login, delete_user):
    user = create_user_with_login
    access_token = user["access_token"]
    user_id = user["id"]

    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        time.sleep(1)
        update_token_response = requests.post_request(f"{base_url}/auth/update_token", headers=headers)
        response_data = update_token_response.json()
        access_expiry = response_data["access_token_expired_at"]
        refresh_expiry = response_data["refresh_token_expired_at"]
        access_expiry_date = datetime.fromisoformat(access_expiry.replace("Z", "+00:00"))
        refresh_expiry_date = datetime.fromisoformat(refresh_expiry.replace("Z", "+00:00"))
        now = datetime.utcnow()

        assert update_token_response.status_code == 200, (
            f"Ожидается статус код 200, получен: {update_token_response.status_code}"
        )
        assert access_expiry_date > now, "Ожидается, что 'access_token_expired_at' будет в будущем"
        assert refresh_expiry_date > now, "Ожидается, что 'refresh_token_expired_at' будет в будущем"

    finally:
        delete_user(user_id)


def test_new_access_token_compatibility(base_url, create_user_with_login, delete_user):
    user = create_user_with_login
    email = user["email"]
    access_token = user["access_token"]
    user_id = user["id"]

    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        time.sleep(1)
        update_token_response = requests.post_request(f"{base_url}/auth/update_token", headers=headers)
        response_data = update_token_response.json()
        new_access_token = response_data["access_token"]
        new_headers = {"Authorization": f"Bearer {new_access_token}"}
        assert update_token_response.status_code == 200, (
            f"Ожидается статус код 200, получен: {update_token_response.status_code}"
        )
        protected_response = requests.get_request(f"{base_url}/user/me/", headers=new_headers)
        assert protected_response.status_code == 200, (
            f"Ожидается статус код 200, получен: {protected_response.status_code}"
        )
        response_data = protected_response.json()
        assert "email" in response_data, "Ожидается наличие 'email' в ответе"
        assert response_data["email"] == email, "Email пользователя не совпадает с ожидаемым"

    finally:
        delete_user(user_id)


def test_protected_endpoint_without_authorization(base_url):
    protected_response = requests.get_request(f"{base_url}/user/me/")

    assert protected_response.status_code == 401, (
        f"Ожидается статус код 401, получен: {protected_response.status_code}"
    )


def test_protected_endpoint_with_invalid_token(base_url):
    invalid_access_token = "Bearer invalid.token.value"
    headers = {"Authorization": invalid_access_token}

    protected_response = requests.get_request(f"{base_url}/user/me/", headers=headers)

    assert protected_response.status_code in [401, 403], (
        f"Ожидается статус код 401 или 403, получен: {protected_response.status_code}"
    )


def test_update_token_with_invalid_http_method(base_url, create_user_with_login, delete_user):
    user = create_user_with_login
    access_token = user["access_token"]
    user_id = user["id"]
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        delete_response = requests.delete_request(f"{base_url}/auth/update_token", headers=headers)
        assert delete_response.status_code == 405, (
            f"Ожидается статус код 405, получен: {delete_response.status_code}"
        )
    finally:
        delete_user(user_id)


@pytest.mark.xfail(reason="Тут баг, нужен фикс")
def test_old_access_token_invalid_after_update(base_url, create_user_with_login, delete_user):
    user = create_user_with_login
    old_access_token = user["access_token"]
    user_id = user["id"]
    try:
        headers_with_old_access = {"Authorization": f"Bearer {old_access_token}"}
        headers = {"Authorization": f"Bearer {old_access_token}"}
        time.sleep(2)  # Небольшая задержка для синхронизации токенов
        update_token_response = requests.post_request(f"{base_url}/auth/update_token", headers=headers)
        assert update_token_response.status_code == 200, (
            f"Ожидается статус код 200, получен: {update_token_response.status_code}"
        )

        protected_response_with_old_access = requests.get_request(
            f"{base_url}/user/me/", headers=headers_with_old_access
        )
        assert protected_response_with_old_access.status_code == 401, (
            f"Ожидается статус код 401, получен: {protected_response_with_old_access.status_code}"
        )
    finally:
        delete_user(user_id)