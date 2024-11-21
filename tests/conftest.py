import os
import time
import pytest
from api import requests
from utils.mailsac import generate_unique_email, get_latest_email
from dotenv import load_dotenv
import uuid
load_dotenv()


@pytest.fixture
def base_url():
    return os.getenv('URL')


@pytest.fixture
def create_user(base_url):
    email = generate_unique_email()
    password = "Password123!"
    payload = {"email": email, "password": password, "utm": "test-utm"}
    response = requests.post_request(base_url + '/auth/signup', json=payload)

    if response.status_code != 200:
        raise Exception(f"Ошибка при регистрации пользователя: {response.status_code}, {response.json()}")

    return {"email": email, "password": password}


@pytest.fixture
def activate_user(base_url):
    def _activate_user(email):
        activation_code = None
        for attempt in range(30):
            email_content = get_latest_email(email)
            if email_content:
                for link in email_content.get("links", []):
                    if "https://voicecover.ru/auth/activate?activate_code=" in link:
                        activation_code = link.split("=")[1]
                        break
            if activation_code:
                break
            time.sleep(2)

        if not activation_code:
            raise Exception("Не удалось найти письмо с активацией или код активации")

        response = requests.get_request(f"{base_url}/auth/activate?activate_code={activation_code}")
        if response.status_code != 200:
            raise Exception(f"Ошибка при активации пользователя: {response.status_code}, {response.json()}")

    return _activate_user


@pytest.fixture
def signin_user(base_url):
    def _signin_user(email, password):
        signin_payload = {"username": email, "password": password}
        signin_response = requests.post_request(base_url + '/auth/signin', data=signin_payload)

        if signin_response.status_code != 200:
            raise Exception(
                f"Ошибка при авторизации пользователя: {signin_response.status_code}, {signin_response.json()}"
            )

        response_data = signin_response.json()
        if "user" not in response_data:
            raise KeyError(f"Ответ API не содержит ключ 'user': {response_data}")

        return {
            "user_id": response_data["user"]["id"],
            "access_token": response_data["access_token"],
            "refresh_token": response_data["refresh_token"],
        }

    return _signin_user


@pytest.fixture
def delete_user(base_url):
    """
    Фикстура для удаления пользователя по его ID.
    """
    def _delete_user(user_id):
        admin_email = os.getenv("ADMIN_EMAIL")
        admin_password = os.getenv("ADMIN_PASSWORD")
        payload = {"username": admin_email, "password": admin_password}

        # Авторизация под администратором
        admin_response = requests.post_request(base_url + '/auth/signin', data=payload)

        if admin_response.status_code != 200:
            raise Exception(f"Ошибка при входе под администратором: {admin_response.status_code}, {admin_response.json()}")

        admin_access_token = admin_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {admin_access_token}", "accept": "application/json"}

        # Удаление пользователя
        response = requests.delete_request(f"{base_url}/user/{user_id}", headers=headers)
        if response.status_code not in [200, 204]:
            raise Exception(f"Ошибка при удалении пользователя: {response.status_code}, {response.json()}")

    return _delete_user


@pytest.fixture
def cleanup_new_user(base_url, activate_user, delete_user):
    def _cleanup_user(email, password):
        activate_user(email)

        def cleanup():
            signin_payload = {"username": email, "password": password}
            signin_response = requests.post_request(base_url + '/auth/signin', data=signin_payload)

            if signin_response.status_code == 200:
                user_id = signin_response.json()["user"]["id"]
                delete_user(user_id)
            else:
                print(f"Не удалось авторизоваться для удаления пользователя: {signin_response.status_code}")

        return cleanup

    return _cleanup_user


@pytest.fixture
def cleanup_new_user_no_activation(base_url, delete_user):
    def _cleanup_user(email, password):
        def cleanup():
            signin_payload = {"username": email, "password": password}
            signin_response = requests.post_request(base_url + '/auth/signin', data=signin_payload)
            if signin_response.status_code == 200:
                user_id = signin_response.json()["user"]["id"]
                delete_user(user_id)
            else:
                print(f"[WARNING] Не удалось авторизовать пользователя {email} для удаления.")
        return cleanup
    return _cleanup_user


@pytest.fixture
def admin_access_token(base_url):
    """
    Фикстура для получения access_token администратора.
    """
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    signin_payload = {"username": admin_email, "password": admin_password}
    response = requests.post_request(f"{base_url}/auth/signin", data=signin_payload)

    if response.status_code != 200:
        raise Exception(f"Ошибка авторизации администратора: {response.status_code}, {response.json()}")

    access_token = response.json().get("access_token")
    if not access_token:
        raise Exception("Не удалось получить токен администратора")

    return access_token


@pytest.fixture
def create_admin(base_url):
    """
    Фикстура для создания администратора через существующего администратора.
    """
    # Авторизация под постоянным администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    signin_payload = {"username": admin_email, "password": admin_password}
    admin_signin_response = requests.post_request(
        f"{base_url}/auth/signin",
        data=signin_payload
    )
    assert admin_signin_response.status_code == 200, (
        f"Не удалось авторизоваться под администратором: {admin_signin_response.text}"
    )
    admin_access_token = admin_signin_response.json()["access_token"]

    # Создание нового администратора
    email = f"admin_{uuid.uuid4().hex}@test.com"
    password = "Password123!"
    payload = {
        "lastname": "Test",
        "firstname": "Admin",
        "email": email,
        "role": "admin",
        "balance": 0,
        "is_active": True,
        "password": password
    }
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    create_response = requests.post_request(
        f"{base_url}/user/",
        json=payload,
        headers=headers
    )
    assert create_response.status_code == 200, (
        f"Не удалось создать администратора: {create_response.text}"
    )

    # Авторизация нового администратора
    signin_payload = {"username": email, "password": password}
    new_admin_signin_response = requests.post_request(
        f"{base_url}/auth/signin",
        data=signin_payload
    )
    assert new_admin_signin_response.status_code == 200, (
        f"Не удалось авторизоваться новым администратором: {new_admin_signin_response.text}"
    )

    new_admin_access_token = new_admin_signin_response.json()["access_token"]
    new_admin_id = create_response.json()["id"]

    return {
        "id": new_admin_id,  # Возвращаем ID нового администратора
        "email": email,
        "password": password,
        "access_token": new_admin_access_token
    }


@pytest.fixture
def add_translation(base_url):
    """
    Фикстура для добавления перевода.
    """

    def _add_translation(access_token, file_path):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "accept": "application/json"
        }

        # Указываем MIME-тип для видео
        mime_type = "video/mp4"  # Замените на подходящий MIME-тип вашего видео
        files = {
            "upload": (os.path.basename(file_path), open(file_path, "rb"), mime_type)
        }

        response = requests.post_request(
            f"{base_url}/translate/upload/",
            headers=headers,
            files=files
        )

        assert response.status_code == 200, (
            f"Ошибка при загрузке видео: {response.status_code}, {response.text}"
        )
        return response.json()

    return _add_translation


@pytest.fixture
def delete_translation(base_url):
    def _delete_translation(access_token, translation_id):
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.delete_request(
            url=f"{base_url}/translate/{translation_id}",
            headers=headers
        )
        assert response.status_code in [200, 204], f"Не удалось удалить перевод: {response.text}"
    return _delete_translation


@pytest.fixture
def create_user_with_login(base_url):
    """
    Фикстура для создания пользователя через администратора и последующей авторизации.
    """
    # Авторизация под постоянным администратором
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    signin_payload = {"username": admin_email, "password": admin_password}
    admin_signin_response = requests.post_request(
        f"{base_url}/auth/signin",
        data=signin_payload
    )
    assert admin_signin_response.status_code == 200, (
        f"Не удалось авторизоваться под администратором: {admin_signin_response.text}"
    )
    admin_access_token = admin_signin_response.json()["access_token"]

    # Создание нового пользователя
    email = f"user_{uuid.uuid4().hex}@test.com"
    password = "Password123!"
    payload = {
        "lastname": "Test",
        "firstname": "User",
        "email": email,
        "role": "user",
        "balance": 0,
        "is_active": True,
        "password": password
    }
    headers = {
        "Authorization": f"Bearer {admin_access_token}",
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    create_response = requests.post_request(
        f"{base_url}/user/",
        json=payload,
        headers=headers
    )
    assert create_response.status_code == 200, (
        f"Не удалось создать пользователя: {create_response.text}"
    )

    # Авторизация нового пользователя
    signin_payload = {"username": email, "password": password}
    new_user_signin_response = requests.post_request(
        f"{base_url}/auth/signin",
        data=signin_payload
    )
    assert new_user_signin_response.status_code == 200, (
        f"Не удалось авторизоваться новым пользователем: {new_user_signin_response.text}"
    )

    new_user_access_token = new_user_signin_response.json()["access_token"]
    new_user_id = create_response.json()["id"]

    return {
        "id": new_user_id,  # Возвращаем ID нового пользователя
        "email": email,
        "password": password,
        "access_token": new_user_access_token
    }


@pytest.fixture
def add_balance(base_url, signin_user):
    """
    Фикстура для пополнения баланса пользователя через администратора.

    Аргументы:
    - base_url: базовый URL API.
    - signin_user: фикстура для входа в систему.

    Возвращает:
    - Функцию для выполнения транзакции с указанными параметрами.
    """
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    admin = signin_user(admin_email, admin_password)
    admin_access_token = admin["access_token"]

    def _add_balance(user_id, amount):
        headers = {
            "Authorization": f"Bearer {admin_access_token}",
            "accept": "application/json",
            "Content-Type": "application/json",
        }
        payload = {
            "user_id": user_id,
            "type_transaction": "credit",
            "amount": amount,
        }
        response = requests.post_request(
            f"{base_url}/transaction/",
            headers=headers,
            json=payload,
        )

        # Проверка успешности выполнения транзакции
        assert response.status_code == 200, (
            f"Не удалось пополнить баланс пользователя: {response.text}"
        )

        return response.json()  # Возвращает данные о транзакции

    return _add_balance


@pytest.fixture
def cleanup_entities(delete_user):
    created_users = []

    def track_user(user_id):
        created_users.append(user_id)

    yield track_user

    for user_id in created_users:
        delete_user(user_id)