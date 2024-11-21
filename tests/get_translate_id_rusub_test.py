import os
import pytest
from api import requests


def test_get_subtitles_for_existing_translation(base_url, signin_user):
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    translation_id = int(os.getenv("TRANSLATION_ID"))

    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{translation_id}/rusub/",
        headers=headers
    )

    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    response_data = response.json()
    assert "id" in response_data, "Ответ не содержит ключ 'id'"
    assert response_data["id"] == translation_id, (
        f"Ожидалось, что ID перевода будет {translation_id}, получен: {response_data['id']}"
    )
    assert "vtt" in response_data, "Ответ не содержит ключ 'vtt'"
    assert isinstance(response_data["vtt"], str), (
        f"Ожидалось, что 'vtt' будет строкой, но получено: {type(response_data['vtt'])}"
    )
    assert response_data["vtt"].startswith("WEBVTT"), (
        "Содержимое 'vtt' должно начинаться с 'WEBVTT', получено: {response_data['vtt'][:10]}"
    )


@pytest.mark.xfail(reason="Баг: сервер возвращает статус код 500 вместо ожидаемого 404")
def test_get_subtitles_for_nonexistent_translation(base_url, signin_user):
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    nonexistent_translation_id = 999999999

    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{nonexistent_translation_id}/rusub/",
        headers=headers
    )

    assert response.status_code == 404, (
        f"Ожидаемый статус код 404 для несуществующего ID, получен: {response.status_code}"
    )

    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert response_data["detail"] == "Subtitle not found", (
        f"Ожидалось сообщение 'Subtitle not found', получено: {response_data['detail']}"
    )


def test_get_subtitles_with_invalid_id(base_url, signin_user):
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]

    invalid_translation_id = "abc"

    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json"
    }

    response = requests.get_request(
        f"{base_url}/translate/{invalid_translation_id}/rusub/",
        headers=headers
    )

    assert response.status_code == 422, (
        f"Ожидаемый статус код 422 для некорректного значения ID, получен: {response.status_code}"
    )

    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert isinstance(response_data["detail"], list), "Поле 'detail' должно быть списком"
    assert any(
        error["loc"] == ["path", "id"] and error["type"] == "int_parsing"
        for error in response_data["detail"]
    ), "Ответ не содержит ожидаемую ошибку в поле 'id'"


def test_get_subtitles_without_authorization(base_url):
    existing_translation_id = str(os.getenv("TRANSLATION_ID"))

    headers = {
        "accept": "application/json"  # Токен авторизации отсутствует
    }

    response = requests.get_request(
        f"{base_url}/translate/{existing_translation_id}/rusub/",
        headers=headers
    )

    assert response.status_code == 401, (
        f"Ожидаемый статус код 401 для запроса без авторизации, получен: {response.status_code}"
    )

    response_data = response.json()
    assert "detail" in response_data, "Ответ не содержит ключ 'detail' с описанием ошибки"
    assert response_data["detail"] == "Not authenticated", (
        f"Ожидалось сообщение об ошибке 'Not authenticated', получено: {response_data['detail']}"
    )


@pytest.mark.xfail(reason="Баг: сервер возвращает статус код 500 вместо ожидаемого 404")
def test_get_subtitles_for_foreign_translation(base_url, signin_user, add_translation, delete_translation):
    some_balance_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    some_balance_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    balance_user = signin_user(some_balance_email, some_balance_password)
    balance_user_access_token = balance_user["access_token"]

    current_dir = os.path.dirname(__file__)
    test_video_path = os.path.join(current_dir, "..", "data", "man_talking.mp4")
    test_video_path = os.path.abspath(test_video_path)
    assert os.path.exists(test_video_path), f"Файл {test_video_path} не найден"

    translation = add_translation(balance_user_access_token, test_video_path)
    translation_id = translation["id"]

    try:
        empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
        empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
        empty_balance_user = signin_user(empty_balance_email, empty_balance_password)
        empty_balance_user_access_token = empty_balance_user["access_token"]

        headers = {
            "Authorization": f"Bearer {empty_balance_user_access_token}",
            "accept": "application/json"
        }

        response = requests.get_request(
            f"{base_url}/translate/{translation_id}/rusub/",
            headers=headers
        )

        assert response.status_code == 403, (
            f"Ожидаемый статус код 403 для доступа к чужому переводу, получен: {response.status_code}"
        )

    finally:
        delete_translation(balance_user_access_token, translation_id)


def test_incorrect_http_method_delete(base_url, signin_user):
    empty_balance_email = os.getenv("EMPTY_BALANCE_USER_EMAIL")
    empty_balance_password = os.getenv("EMPTY_BALANCE_USER_PASSWORD")
    user = signin_user(empty_balance_email, empty_balance_password)
    user_access_token = user["access_token"]
    translation_id = str(os.getenv("TRANSLATION_ID"))

    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
    }

    response = requests.delete_request(
        f"{base_url}/translate/{translation_id}/rusub/",
        headers=headers
    )

    assert response.status_code == 405, (
        f"Ожидаемый статус код 405, получен: {response.status_code}"
    )
