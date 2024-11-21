import logging
from curlify import to_curl
from requests import Response


def response_logging(response: Response):
    logging.info("Request: " + response.request.url)

    if response.request.body:
        if isinstance(response.request.body, bytes):
            logging.info("[INFO] Тело запроса содержит бинарные данные и не будет декодировано.")
        else:
            logging.info("Request body: " + str(response.request.body))

    logging.info(f"Status code: {response.status_code}")

    try:
        logging.info("Response body: " + response.text)
    except Exception as e:
        logging.error(f"[ERROR] Ошибка при логировании тела ответа: {e}")


def request_attaching(response: Response):
    try:
        if response.request.body and isinstance(response.request.body, bytes):
            logging.info("[INFO] Пропущена генерация cURL для запроса с бинарным телом (binary data).")
            return

        curl = to_curl(response.request)
        logging.info(curl)

    except Exception as e:
        logging.error(f"[ERROR] Ошибка при генерации cURL: {e}")

    logging.info(f'Status code: {response.status_code}')


def response_attaching(response: Response):
    logging.info("Request URL: " + response.request.url)

    if response.request.body:
        if isinstance(response.request.body, bytes):
            logging.info("[INFO] Тело запроса содержит бинарные данные и не будет декодировано.")
        else:
            logging.info("Request Body: " + str(response.request.body))

    logging.info(f"Status Code: {response.status_code}")

    try:
        logging.info("Response Body: " + response.text)
    except Exception as e:
        logging.error(f"[ERROR] Ошибка при логировании тела ответа: {e}")
