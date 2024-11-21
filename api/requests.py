import requests

from utils.attach import response_logging, response_attaching, request_attaching


def get_request(url, params=None, headers=None, data=None):
    response = requests.get(
        url=url,
        params=params,
        headers=headers,
        data=data
    )
    response_logging(response)
    response_attaching(response)
    return response


def post_request(url, json=None, data=None, headers=None, files=None):
    default_headers = {
        "accept": "application/json",
        "Content-Type": "application/json" if json else "application/x-www-form-urlencoded"
    }
    if headers:
        default_headers.update(headers)

    response = requests.post(
        url=url,
        headers=default_headers if not files else headers,
        json=json,
        data=data,
        files=files
    )
    request_attaching(response)
    response_logging(response)
    response_attaching(response)
    return response


def delete_request(url, params=None, headers=None):
    response = requests.delete(
        url=url,
        params=params,
        headers=headers
    )
    response_logging(response)
    response_attaching(response)
    return response


def patch_request(url, json, headers=None):
    # Устанавливаем заголовки по умолчанию
    default_headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    # Если переданы дополнительные заголовки, объединяем их с дефолтными
    if headers:
        default_headers.update(headers)

    # Выполняем PATCH-запрос
    response = requests.patch(
        url=url,
        headers=default_headers,
        json=json
    )
    request_attaching(response)
    response_logging(response)
    response_attaching(response)
    return response
