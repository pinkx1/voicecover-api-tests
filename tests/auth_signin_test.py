import pytest
from api import requests
import os
from dotenv import load_dotenv
from utils.mailsac import generate_unique_email

load_dotenv()


def test_signin_success(base_url):
    email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")

    signin_payload = {"username": email, "password": password}
    signin_response = requests.post_request(base_url + '/auth/signin', data=signin_payload)

    assert signin_response.status_code == 200, "Status code 200 is expected"

    response_data = signin_response.json()
    assert "access_token" in response_data, "It is expected that the response will have an 'access_token'"
    assert "refresh_token" in response_data, “The response is expected to contain 'refresh_token'”
    assert "user" in response_data, "It is expected that the response will contain the user's details"
    assert response_data["user"]["email"] == email, "The user's email is expected to match the one passed in"


def test_signin_unconfirmed_account(base_url, cleanup_new_user, delete_user):
    email = generate_unique_email()
    password = "Password123!"
    payload = {"email": email, "password": password, "utm": "test-utm"}
    signup_response = requests.post_request(base_url + '/auth/signup', json=payload)
    assert signup_response.status_code == 200
    signin_payload = {"username": email, "password": password}
    signin_response = requests.post_request(base_url + '/auth/signin', data=signin_payload)
    response_data = signin_response.json()

    assert signin_response.status_code == 403
    assert response_data["detail"] == "User is not active"

    cleanup_new_user(email, password)()


def test_signin_with_unregistered_email(base_url):
    email = generate_unique_email()
    password = "Password123!"

    signin_payload = {"username": email, "password": password}
    signin_response = requests.post_request(base_url + '/auth/signin', data=signin_payload)
    response_data = signin_response.json()
    assert signin_response.status_code == 404
    assert response_data["detail"] == "User not found"


def test_signin_with_invalid_password(base_url):
    email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    password = "WrongPassword123!"

    signin_payload = {"username": email, "password": password}
    signin_response = requests.post_request(base_url + '/auth/signin', data=signin_payload)
    response_data = signin_response.json()
    assert signin_response.status_code == 403
    assert response_data["detail"] == "Invalid credentials"


def test_signin_with_empty_email(base_url):
    password = "Password123!"
    signin_payload = {"username": "", "password": password}
    signin_response = requests.post_request(base_url + '/auth/signin', data=signin_payload)
    response_data = signin_response.json()
    error_details = response_data.get("detail", [])
    email_error = next((error for error in error_details if "username" in error.get("loc", [])), None)

    assert signin_response.status_code == 422
    assert email_error.get("msg") == "Field required"


def test_signin_with_empty_password(base_url):
    email = "testuser@example.com"

    signin_payload = {"username": email, "password": ""}
    signin_response = requests.post_request(base_url + '/auth/signin', data=signin_payload)
    response_data = signin_response.json()
    error_details = response_data.get("detail", [])
    password_error = next((error for error in error_details if "password" in error.get("loc", [])), None)

    assert signin_response.status_code == 422
    assert password_error.get("msg") == "Field required"


def test_signin_with_empty_request_body(base_url):
    signin_payload = {}
    signin_response = requests.post_request(base_url + '/auth/signin', json=signin_payload)
    response_data = signin_response.json()

    error_details = response_data.get("detail", [])
    username_error = next((error for error in error_details if "username" in error.get("loc", [])), None)
    password_error = next((error for error in error_details if "password" in error.get("loc", [])), None)

    assert signin_response.status_code == 422
    assert username_error.get("msg") == "Field required"
    assert password_error.get("msg") == "Field required"


def test_signin_with_extra_parameter(base_url):
    email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")

    signin_payload = {"username": email, "password": password, "extra_param": "ignored_value"}
    signin_response = requests.post_request(base_url + '/auth/signin', data=signin_payload)
    response_data = signin_response.json()

    assert signin_response.status_code == 200
    assert "access_token" in response_data
    assert "refresh_token" in response_data
    assert "user" in response_data
    assert response_data["user"]["email"] == email
