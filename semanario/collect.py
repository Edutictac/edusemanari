"""Escucha actualizaciones de un bot dedicado mediante long polling."""

import argparse
import logging
import time

from .storage import connect, ingest_update, last_update_id, load_config, purge_old
from .telegram import TelegramAPI, TelegramError, TokenError, read_token


LOG = logging.getLogger(__name__)


def run(config):
    try:
        token = read_token(config["token_pass_entry"])
    except TokenError as exc:
        raise SystemExit(str(exc)) from None
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
