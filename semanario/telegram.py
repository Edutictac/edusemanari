"""Acceso mínimo a la API de Telegram sin exponer el token."""

import subprocess

import requests


class TelegramError(Exception):
    """Error sin URL ni token en su representación."""


class TokenError(Exception):
    """No se pudo obtener el token del bot."""


def read_token(entry):
    try:
        result = subprocess.run(
            ["pass", "show", entry],
            check=True, capture_output=True, text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise TokenError("No se pudo leer el token desde pass") from None
    token = result.stdout.strip()
    if not token:
        raise TokenError("La entrada de pass está vacía")
    return token


class TelegramAPI:
    def __init__(self, token):
        self.url = f"https://api.telegram.org/bot{token}/"
        self.session = requests.Session()

    def call(self, method, payload, timeout):
        try:
            response = self.session.post(self.url + method, json=payload, timeout=timeout)
            response.raise_for_status()
            body = response.json()
            if not body.get("ok"):
                raise TelegramError(f"Telegram rechazó {method}")
            return body["result"]
        except (requests.RequestException, ValueError):
            # requests puede incluir la URL con el token en el error original.
            raise TelegramError(f"No se pudo completar {method}") from None
