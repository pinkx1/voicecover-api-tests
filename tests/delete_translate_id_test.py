from api import requests
import os
from dotenv import load_dotenv

load_dotenv()


def authorize_user(base_url, email, password):
    payload = {"username": email, "password": password}
    response = requests.post_request(f"{base_url}/auth/signin", data=payload)
    assert response.status_code == 200, (
        f"Ошибка авторизации пользователя: {response.status_code}, {response.text}"
    )
    return response.json()["access_token"]


def upload_test_video(user_access_token, add_translation):
    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.abspath(os.path.join(current_dir, "..", "data", "man_talking.mp4"))
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"
    return add_translation(user_access_token, test_video_path)


def delete_translation_request(base_url, translation_id, headers):
    response = requests.delete_request(f"{base_url}/translate/{translation_id}", headers=headers)
    return response


def test_successful_translation_deletion(base_url, add_translation, delete_translation):
    static_user_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    static_user_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user_access_token = authorize_user(base_url, static_user_email, static_user_password)

    translation = upload_test_video(user_access_token, add_translation)
    translation_id = translation["id"]

    headers = {"accept": "application/json", "Authorization": f"Bearer {user_access_token}"}
    response = delete_translation_request(base_url, translation_id, headers)

    assert response.status_code == 200, f"Ожидаемый статус код 200, получен: {response.status_code}, тело: {response.text}"
    assert response.json().get("success") is True, "Ожидается {'success': True}"

    response_after_delete = requests.get_request(f"{base_url}/translate/{translation_id}", headers=headers)
    assert response_after_delete.status_code == 404, "Ожидаемый статус код 404 для удалённого перевода"


def test_delete_translation_with_invalid_id(base_url):
    static_user_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    static_user_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user_access_token = authorize_user(base_url, static_user_email, static_user_password)

    invalid_translation_id = "abc"
    headers = {"accept": "application/json", "Authorization": f"Bearer {user_access_token}"}
    response = delete_translation_request(base_url, invalid_translation_id, headers)

    assert response.status_code == 422, f"Ожидаемый статус код 422, получен: {response.status_code}, тело: {response.text}"
    response_data = response.json()
    assert "detail" in response_data, "Ответ должен содержать ключ 'detail'"
    assert isinstance(response_data["detail"], list), "Ожидаемый формат ошибок: список"
    assert response_data["detail"][0]["msg"] == "Input should be a valid integer, unable to parse string as an integer"


def test_delete_nonexistent_translation(base_url):
    static_user_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    static_user_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user_access_token = authorize_user(base_url, static_user_email, static_user_password)

    nonexistent_translation_id = 999999
    headers = {"accept": "application/json", "Authorization": f"Bearer {user_access_token}"}
    response = delete_translation_request(base_url, nonexistent_translation_id, headers)

    assert response.status_code == 404, f"Ожидаемый статус код 404, получен: {response.status_code}, тело: {response.text}"
    assert response.json().get("detail") == "Not found", "Ответ должен содержать 'Not found'"


def test_user_cannot_delete_other_user_translation(base_url, create_user_with_login, add_translation, delete_translation):
    user = create_user_with_login
    user_access_token = user["access_token"]

    translation = upload_test_video(user_access_token, add_translation)
    translation_id = translation["id"]

    static_user_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    static_user_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    static_user_token = authorize_user(base_url, static_user_email, static_user_password)

    headers = {"accept": "application/json", "Authorization": f"Bearer {static_user_token}"}
    response = delete_translation_request(base_url, translation_id, headers)

    assert response.status_code == 404, f"Ожидаемый статус код 404, получен: {response.status_code}, тело: {response.text}"

    delete_translation(user_access_token, translation_id)


def test_delete_translation_without_authorization(base_url, create_user_with_login, add_translation, delete_translation):
    user = create_user_with_login
    user_access_token = user["access_token"]

    translation = upload_test_video(user_access_token, add_translation)
    translation_id = translation["id"]

    headers = {"accept": "application/json"}
    response = delete_translation_request(base_url, translation_id, headers)

    assert response.status_code == 401, f"Ожидаемый статус код 401, получен: {response.status_code}, тело: {response.text}"

    delete_translation(user_access_token, translation_id)


def test_admin_can_delete_any_translation(base_url, create_user_with_login, add_translation, delete_user):
    user = create_user_with_login
    user_access_token = user["access_token"]
    user_id = user["id"]

    translation = upload_test_video(user_access_token, add_translation)
    translation_id = translation["id"]

    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin_access_token = authorize_user(base_url, admin_email, admin_password)

    headers = {"accept": "application/json", "Authorization": f"Bearer {admin_access_token}"}
    response = delete_translation_request(base_url, translation_id, headers)

    assert response.status_code == 200, f"Ожидаемый статус код 200, получен: {response.status_code}, тело: {response.text}"
    assert response.json().get("success") is True, "Ожидается {'success': True}"

    delete_user(user_id)
