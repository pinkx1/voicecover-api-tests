import pytest
from api import requests
from utils.mailsac import generate_unique_email


def test_signup_success(base_url, cleanup_new_user):
    email = generate_unique_email()
    password = "Password123!"
    payload = {"email": email, "password": password, "utm": "test-utm"}
    response = requests.post_request(base_url + '/auth/signup', json=payload)

    assert response.status_code == 200, "Ожидается статус код 200"
    assert response.json() == {"success": True}, "Ожидается тело ответа {'success': True}"

    cleanup_new_user(email, password)()


def test_signup_invalid_email(base_url):
    invalid_email = "invalidemail.com"
    password = "Password123!"
    payload = {"email": invalid_email, "password": password, "utm": "test-utm"}
    response = requests.post_request(base_url + '/auth/signup', json=payload)

    assert response.status_code == 422, "Ожидается статус код 422 для некорректного email"


def test_signup_without_utm(base_url, cleanup_new_user):
    email = generate_unique_email()
    password = "Password123!"
    payload = {"email": email, "password": password}  # Параметр utm отсутствует
    response = requests.post_request(base_url + '/auth/signup', json=payload)

    assert response.status_code == 200, "Ожидается статус код 200"
    assert response.json() == {"success": True}, "Ожидается тело ответа {'success': True}"

    cleanup_new_user(email, password)()


def test_signup_without_email(base_url):
    password = "Password123!"
    payload = {"password": password, "utm": "test-utm"}  # Параметр email отсутствует
    response = requests.post_request(base_url + '/auth/signup', json=payload)
    error_details = response.json().get("detail", [])
    email_error = next((error for error in error_details if "email" in error.get("loc", [])), None)

    assert email_error.get("msg") == "Field required", "Ожидается сообщение 'Field required'"
    assert response.status_code == 422, "Ожидается статус код 422 для отсутствующего email"


def test_signup_without_password(base_url):
    email = "testuser@example.com"
    payload = {"email": email, "utm": "test-utm"}
    response = requests.post_request(base_url + '/auth/signup', json=payload)

    error_details = response.json().get("detail", [])
    password_error = next((error for error in error_details if "password" in error.get("loc", [])), None)

    assert password_error.get("msg") == "Field required", "Ожидается сообщение 'Field required'"
    assert response.status_code == 422, "Ожидается статус код 422 для отсутствующего password"


def test_signup_empty_email(base_url):
    email = ""
    password = "Password123!"
    payload = {"email": email, "password": password, "utm": "test-utm"}
    response = requests.post_request(base_url + '/auth/signup', json=payload)
    error_details = response.json().get("detail", [])

    assert response.status_code == 422, "Ожидается статус код 422 для пустого email"


def test_signup_empty_password(base_url):
    email = "testuser@example.com"
    password = ""
    payload = {"email": email, "password": password, "utm": "test-utm"}
    response = requests.post_request(base_url + '/auth/signup', json=payload)
    error_details = response.json().get("detail", [])

    assert response.status_code == 422, "Ожидается статус код 422 для пустого password"


def test_signup_existing_email(base_url, cleanup_new_user_no_activation, activate_user):
    email = generate_unique_email()
    password = "Password123!"

    payload = {"email": email, "password": password, "utm": "test-utm"}
    first_response = requests.post_request(base_url + '/auth/signup', json=payload)
    assert first_response.status_code == 200, "Ожидается успешная регистрация первого пользователя"
    activate_user(email)

    second_response = requests.post_request(base_url + '/auth/signup', json=payload)
    assert second_response.status_code == 400, "Ожидается статус код 409 для повторной регистрации с тем же email"

    error_details = second_response.json().get("detail", "")
    assert isinstance(error_details, str), "Ожидается строковое сообщение в 'detail'"
    assert "User with this email exist" in error_details

    cleanup_new_user_no_activation(email, password)()


def test_signup_empty_request_body(base_url):
    payload = {}
    response = requests.post_request(base_url + '/auth/signup', json=payload)
    error_details = response.json().get("detail", [])

    assert response.status_code == 422, "Ожидается статус код 422 для пустого тела запроса"
    assert any("Input should be a valid dictionary" in error.get("msg", "") for error in error_details), \
        "Ожидается сообщение: 'Input should be a valid dictionary or object to extract fields from'"


def test_registration_with_password_too_short(base_url):
    email = generate_unique_email()
    password = "12345"  # Короче 6 символов
    payload = {"email": email, "password": password, "utm": "test-utm"}

    response = requests.post_request(base_url + "/auth/signup", json=payload)

    assert response.status_code == 422, f"Ожидался статус код 422, получен: {response.status_code}"
    response_data = response.json()
    assert "detail" in response_data, "Ожидалось сообщение об ошибке валидации"
    assert any("password" in error["loc"] for error in response_data["detail"]), (
        "Сообщение об ошибке должно указывать на параметр 'password'"
    )


def test_registration_with_password_min_length(base_url, cleanup_new_user_no_activation):
    email = generate_unique_email()
    password = "123456"  # Ровно 6 символов
    payload = {"email": email, "password": password, "utm": "test-utm"}

    response = requests.post_request(base_url + "/auth/signup", json=payload)

    assert response.status_code == 200, f"Ожидался статус код 200, получен: {response.status_code}"
    response_data = response.json()
    assert response_data == {"success": True}, f"Ожидался ответ: {{'success': True}}, получен: {response_data}"

    cleanup_user = cleanup_new_user_no_activation(email, password)
    cleanup_user()


def test_registration_with_password_max_length(base_url, cleanup_new_user_no_activation):
    email = generate_unique_email()
    password = "12345678901234567890"  # Ровно 20 символов
    payload = {"email": email, "password": password, "utm": "test-utm"}

    response = requests.post_request(base_url + "/auth/signup", json=payload)

    assert response.status_code == 200, f"Ожидался статус код 200, получен: {response.status_code}"
    response_data = response.json()
    assert response_data == {"success": True}, f"Ожидался ответ: {{'success': True}}, получен: {response_data}"

    cleanup_user = cleanup_new_user_no_activation(email, password)
    cleanup_user()


def test_registration_with_password_too_long(base_url):
    email = generate_unique_email()
    password = "123456789012345678901"  # Больше 20 символов
    payload = {"email": email, "password": password, "utm": "test-utm"}

    response = requests.post_request(base_url + "/auth/signup", json=payload)

    assert response.status_code == 422, f"Ожидался статус код 422, получен: {response.status_code}"
    response_data = response.json()
    assert "detail" in response_data, "Ожидалось сообщение об ошибке валидации"
    assert any("password" in error["loc"] for error in response_data["detail"]), (
        "Сообщение об ошибке должно указывать на параметр 'password'"
    )