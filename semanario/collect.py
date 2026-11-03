"""Escucha actualizaciones de un bot dedicado mediante long polling."""

import argparse
import logging
import subprocess
import time

import requests

from .storage import connect, ingest_update, last_update_id, load_config, purge_old


LOG = logging.getLogger(__name__)


class TelegramError(Exception):
    """Error sin URL ni token en su representación."""


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
        except (requests.RequestException, ValueError) as exc:
            # requests puede incluir la URL con el token en el error original.
            raise TelegramError(f"No se pudo completar {method}") from None


def run(config):
    try:
        token = subprocess.run(
            ["pass", "show", config["token_pass_entry"]],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise SystemExit("No se pudo leer el token desde pass") from None
    if not token:
        raise SystemExit("La entrada de pass está vacía")
    api = TelegramAPI(token)
    me = api.call("getMe", {}, 20)
    expected = config.get("bot_username", "").lstrip("@").lower()
    if expected and me["username"].lower() != expected:
        raise SystemExit("El token no corresponde al bot configurado")
    if not me.get("can_read_all_group_messages"):
        raise SystemExit("Desactiva el modo de privacidad del bot en BotFather")
    db = connect(config["database"])
    purge_old(db, config["retention_days"])
    LOG.info("Bot iniciado; escuchando %d grupos", len(config["groups"]))
    next_purge = time.monotonic() + 24 * 60 * 60
    while True:
        try:
            updates = api.call(
                "getUpdates",
                {
                    "offset": last_update_id(db) + 1,
                    "timeout": 45,
                    "limit": 100,
                    "allowed_updates": [
                        "message", "edited_message", "channel_post", "edited_channel_post"
                    ],
                },
                55,
            )
            for update in updates:
                ingest_update(db, update, config["groups"])
            if time.monotonic() >= next_purge:
                purge_old(db, config["retention_days"])
                next_purge = time.monotonic() + 24 * 60 * 60
        except TelegramError:
            LOG.warning("Error al consultar Telegram; se reintentará")
            time.sleep(10)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    run(load_config(args.config))


if __name__ == "__main__":
    main()
