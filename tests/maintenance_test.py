import pytest
from api import requests


def test_maintenance_not_in_mode(base_url):
    response = requests.get_request(base_url + '/maintenance')
    assert response.status_code == 200, "Ожидается статус код 200"
    assert response.json().get('maintenance') in [True, False], "Ожидается значение 'maintenance': True или False"


def test_maintenance_incorrect_path(base_url):
    response = requests.get_request(base_url + '/maintenanc')  # Ошибка в пути
    assert response.status_code == 404, "Ожидается статус код 404"


def test_maintenance_invalid_method(base_url):
    response = requests.delete_request(base_url + '/maintenance')  # Используем POST вместо GET
    assert response.status_code == 405, "Ожидается статус код 405"
