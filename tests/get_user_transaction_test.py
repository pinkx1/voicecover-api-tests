import os
import pytest
from api import requests


def test_get_transactions_successfully(base_url, signin_user, add_balance):
    """
    Проверяет, что статичный пользователь может успешно получить список своих транзакций.

    Шаги:
    1. Авторизоваться под статичным пользователем.
    2. Пополнить баланс пользователя через фикстуру `add_balance` на 1.
    3. Выполнить GET-запрос к эндпоинту `/user/transactions/`.
    4. Проверить, что сервер возвращает статус код 200.
    5. Проверить, что транзакция отображается в списке транзакций с корректной структурой.
    """
    # Шаг 1: Авторизоваться под статичным пользователем
    user_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    user_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)

    # Используем user_id вместо id
    assert "user_id" in user, "В ответе signin_user отсутствует ключ 'user_id'"
    user_id = user["user_id"]
    user_access_token = user["access_token"]

    # Шаг 2: Пополнить баланс пользователя на 1
    amount = 1.0
    add_balance(user_id, amount)

    # Шаг 3: Выполнить GET-запрос
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
    }
    response = requests.get_request(f"{base_url}/user/transactions/", headers=headers)

    # Шаг 4: Проверить статус код
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 5: Проверить структуру списка транзакций
    transactions = response.json()
    assert isinstance(transactions, list), "Ответ должен быть списком транзакций"
    assert len(transactions) > 0, "Список транзакций пустой, ожидалось хотя бы одно пополнение"

    # Проверить, что транзакция пополнения баланса отображается корректно
    assert any(
        t["user_id"] == user_id and t["amount"] == amount and t["type_transaction"] == "credit"
        for t in transactions
    ), "Транзакция пополнения баланса отсутствует в списке транзакций"


def test_transactions_pagination(base_url, signin_user, add_balance):
    """
    Проверяет, что параметры offset и limit корректно обрабатываются:
    - offset смещает начало списка,
    - limit ограничивает количество возвращаемых элементов.

    Шаги:
    1. Авторизоваться под статичным пользователем.
    2. Пополнить баланс пользователя через фикстуру `add_balance` несколько раз.
    3. Выполнить GET-запрос к эндпоинту `/user/transactions/` с параметрами `offset` и `limit`.
    4. Проверить, что сервер возвращает корректный список в пределах указанных параметров.
    """
    # Шаг 1: Авторизоваться под статичным пользователем
    user_email = os.getenv("SOME_BALANCE_USER_EMAIL")
    user_password = os.getenv("SOME_BALANCE_USER_PASSWORD")
    user = signin_user(user_email, user_password)
    user_id = user["user_id"]
    user_access_token = user["access_token"]

    # Шаг 2: Пополнить баланс пользователя несколько раз
    for _ in range(5):
        add_balance(user_id, 1.0)  # Добавляем несколько транзакций

    # Шаг 3: Выполнить GET-запрос с параметрами offset и limit
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "accept": "application/json",
    }
    offset = 2
    limit = 2
    response = requests.get_request(
        f"{base_url}/user/transactions/?offset={offset}&limit={limit}", headers=headers
    )

    # Шаг 4: Проверить статус код
    assert response.status_code == 200, (
        f"Ожидаемый статус код 200, получен: {response.status_code}"
    )

    # Шаг 5: Проверить, что список соответствует указанным параметрам
    transactions = response.json()
    assert isinstance(transactions, list), "Ответ должен быть списком транзакций"
    assert len(transactions) == limit, (
        f"Ожидаемое количество транзакций: {limit}, получено: {len(transactions)}"
    )

    # Проверить, что offset смещает начало списка
    all_transactions_response = requests.get_request(
        f"{base_url}/user/transactions/", headers=headers
    )
    all_transactions = all_transactions_response.json()
    assert transactions[0] == all_transactions[offset], (
        f"Транзакция с offset={offset} не совпадает с ожидаемой. "
        f"Получено: {transactions[0]}, ожидалось: {all_transactions[offset]}"
    )


def test_empty_transactions_list(base_url, signin_user, create_user_with_login, delete_user):
    """
    Проверяет, что сервер корректно обрабатывает запрос, если у пользователя нет транзакций.

    Шаги:
    1. Создать временного пользователя через фикстуру `create_user_with_login`.
    2. Выполнить GET-запрос к эндпоинту `/user/transactions/`.
    3. Проверить, что сервер возвращает статус код 200.
    4. Проверить, что список транзакций пустой.
    5. Удалить созданного пользователя.
    """
    # Шаг 1: Создать временного пользователя
    temp_user = create_user_with_login
    user_id = temp_user["id"]
    user_access_token = temp_user["access_token"]

    try:
        # Шаг 2: Выполнить GET-запрос
        headers = {
            "Authorization": f"Bearer {user_access_token}",
            "accept": "application/json",
        }
        response = requests.get_request(f"{base_url}/user/transactions/", headers=headers)

        # Шаг 3: Проверить статус код
        assert response.status_code == 200, (
            f"Ожидаемый статус код 200, получен: {response.status_code}"
        )

        # Шаг 4: Проверить, что список транзакций пустой
        transactions = response.json()
        assert isinstance(transactions, list), "Ответ должен быть списком транзакций"
        assert len(transactions) == 0, f"Список транзакций должен быть пустым, получено: {transactions}"
    finally:
        # Шаг 5: Удалить временного пользователя
        delete_user(user_id)


def test_get_transactions_without_authorization(base_url):
    """
    Проверяет, что сервер отклоняет запрос на получение списка транзакций от неавторизованного пользователя.

    Шаги:
    1. Выполнить GET-запрос к эндпоинту `/user/transactions/` без токена авторизации.
    2. Проверить, что сервер возвращает статус код 401.
    """
    # Шаг 1: Выполнить GET-запрос без авторизации
    headers = {"accept": "application/json"}  # Без токена авторизации
    response = requests.get_request(f"{base_url}/user/transactions/", headers=headers)

    # Шаг 2: Проверить, что сервер возвращает статус код 401
    assert response.status_code == 401, (
        f"Ожидаемый статус код 401, получен: {response.status_code}"
    )
