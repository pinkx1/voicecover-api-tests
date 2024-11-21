import pytest
from api import requests


def test_healthcheck_success(base_url):
    response = requests.get_request(base_url + '/healthcheck')
    assert response.status_code == 200, "Ожидается статус код 200"
    assert response.json() == {'healthchek': True}, "Ожидается тело ответа {'healthcheck': True}"


def test_healthcheck_incorrect_path(base_url):
    response = requests.get_request(base_url + '/healthchek')  # Ошибка в пути
    assert response.status_code == 404, "Ожидается статус код 404"


def test_healthcheck_invalid_method(base_url):
    response = requests.delete_request(base_url + '/healthcheck')  # Используем POST вместо GET
    assert response.status_code == 405, "Ожидается статус код 405"
