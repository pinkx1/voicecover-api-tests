import pytest
from api import requests
import os
import time
from dotenv import load_dotenv
from utils.mailsac import get_latest_email
import re
load_dotenv()


def test_reset_password_success(base_url, create_user, delete_user, activate_user, signin_user):
    user = create_user
    email = user["email"]
    password = user["password"]
    activate_user(email)
    user_data = signin_user(email, password)
    user_id = user_data["user_id"]
    payload = email
    reset_password_response = requests.post_request(base_url + '/auth/reset_password', data=payload)

    assert reset_password_response.status_code == 200, "Ожидается статус код 200 для успешного сброса пароля"
    response_data = reset_password_response.json()
    assert response_data == {"success": True}, "Ожидается тело ответа: {'success': True}"

    delete_user(user_id)


def test_reset_password_unregistered_email(base_url):
    unregistered_email = "unregistered_email@example.com"

    reset_password_response = requests.post_request(base_url + '/auth/reset_password', data=unregistered_email)

    assert reset_password_response.status_code == 404, "Ожидается статус код 404 для незарегистрированного email"
    response_data = reset_password_response.json()
    expected_detail = "User not found"
    assert response_data["detail"] == expected_detail, f"Ожидается сообщение: {expected_detail}, получено: {response_data['detail']}"


def test_reset_password_missing_email(base_url):
    reset_password_response = requests.post_request(base_url + '/auth/reset_password', json={})

    assert reset_password_response.status_code == 422, "Ожидается статус код 422 для отсутствующего email"

    response_data = reset_password_response.json()
    expected_detail = [
        {
            "type": "value_error",
            "loc": ["body"],
            "msg": "value is not a valid email address: The email address is not valid. It must have exactly one @-sign.",
            "input": "{}",
            "ctx": {
                "reason": "The email address is not valid. It must have exactly one @-sign."
            }
        }
    ]
    assert response_data["detail"] == expected_detail, f"Ожидается: {expected_detail}, получено: {response_data['detail']}"


def test_reset_password_empty_email(base_url):
    payload = {"email": ""}
    reset_password_response = requests.post_request(base_url + '/auth/reset_password', json=payload)

    assert reset_password_response.status_code == 422, "Ожидается статус код 422 для пустого значения email"

    response_data = reset_password_response.json()
    expected_detail = [
        {
            "type": "string_type",
            "loc": ["body"],
            "msg": "Input should be a valid string",
            "input": {"email": ""},
            "url": "https://errors.pydantic.dev/2.1/v/string_type"
        }
    ]
    assert "detail" in response_data, "Ожидается наличие поля 'detail' в ответе"
    assert response_data["detail"] == expected_detail, f"Ожидается: {expected_detail}, получено: {response_data['detail']}"


def test_old_password_invalid_after_reset(base_url, create_user, delete_user, activate_user, signin_user):
    user = create_user
    email = user["email"]
    old_password = user["password"]
    activate_user(email)
    user_data = signin_user(email, old_password)
    user_id = user_data["user_id"]

    reset_password_response = requests.post_request(
        base_url + '/auth/reset_password',
        data=email
    )

    assert reset_password_response.status_code == 200, "Ожидается успешный сброс пароля"
    assert reset_password_response.json() == {"success": True}, "Ожидается тело ответа: {'success': True}"

    old_password_signin_response = requests.post_request(
        base_url + '/auth/signin',
        data={"username": email, "password": old_password}
    )

    assert old_password_signin_response.status_code in [401, 403], "Ожидается статус код 401 или 403 для недействительного пароля"
    response_data = old_password_signin_response.json()
    assert "detail" in response_data, "Ожидается наличие поля 'detail' в ответе"
    assert response_data["detail"] in ["Invalid credentials", "Unauthorized"], f"Ожидается сообщение об ошибке авторизации, получено: {response_data['detail']}"

    delete_user(user_id=user_id)


def test_new_password_functionality(base_url, create_user, delete_user, activate_user, signin_user):
    user = create_user
    email = user["email"]
    old_password = user["password"]
    activate_user(email)
    user_data = signin_user(email, old_password)
    user_id = user_data["user_id"]

    reset_password_response = requests.post_request(
        base_url + '/auth/reset_password',
        data=email
    )

    assert reset_password_response.status_code == 200, "Ожидается успешный сброс пароля"
    mailsac_api_key = os.getenv("MAILSAC_API_KEY")

    new_password = None
    for attempt in range(30):
        email_content = get_latest_email(email)
        if email_content and email_content["subject"] == "Сброс пароля на Voicecover":
            message_id = email_content["_id"]
            response = requests.get_request(
                f"https://mailsac.com/api/text/{email}/{message_id}",
                headers={"Mailsac-Key": mailsac_api_key}
            )
            plaintext = response.text

            match = re.search(r"Новый пароль:\s*(\S+)", plaintext)
            if match:
                new_password = match.group(1)
                break

        time.sleep(2)

    assert new_password is not None, "Не удалось извлечь новый пароль из письма"

    signin_payload = {"username": email, "password": new_password}
    signin_response = requests.post_request(base_url + '/auth/signin', data=signin_payload)
    assert signin_response.status_code == 200, "Ожидается успешный сброс пароля"
    delete_user(user_id)