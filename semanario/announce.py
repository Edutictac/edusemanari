"""Avisa en los grupos participantes de que hay un número publicado."""

import argparse
import logging
import re
import time
from datetime import date
from pathlib import Path

import requests

from .storage import connect, get_state, load_config, set_state
from .telegram import TelegramAPI, TelegramError, TokenError, read_token


LOG = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent.parent
NUMEROS_DIR = BASE_DIR / "web" / "content" / "numeros"
FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*(?:\n|\Z)", re.S)


def front_matter(path):
    text = Path(path).read_text(encoding="utf-8")
    match = FRONT_MATTER.search(text)
    if not match:
        raise ValueError(f"Sin cabecera YAML: {path}")
    fields = {}
    for line in match.group(1).splitlines():
        if line.startswith((" ", "\t", "-")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    return fields


def is_draft(path):
    return front_matter(path).get("draft", "").lower() == "true"


def latest_week(numeros_dir=NUMEROS_DIR):
    weeks = []
    for folder in Path(numeros_dir).iterdir():
        if not folder.is_dir() or not (folder / "_index.md").exists():
            continue
        try:
            day = date.fromisoformat(folder.name)
        except ValueError:
            continue
        if day.weekday() != 0:
            continue
        weeks.append(folder.name)
    if not weeks:
        raise ValueError("No hay ningún número")
    latest = max(weeks)
    if is_draft(Path(numeros_dir) / latest / "_index.md"):
        raise ValueError(
            f"El número {latest} sigue en borrador; quita draft: true antes de avisar"
        )
    return latest


def issue_number(week, numeros_dir=NUMEROS_DIR):
    day = date.fromisoformat(week)
    if day.weekday() != 0:
        raise ValueError("La semana debe empezar en lunes")
    index = Path(numeros_dir) / week / "_index.md"
    if not index.exists():
        raise ValueError(f"No existe el número {week}")
    fields = front_matter(index)
    if fields.get("draft", "").lower() == "true":
        raise ValueError(f"El número {week} sigue en borrador")
    numero = fields.get("numero", "").strip()
    if not numero:
        raise ValueError(f"El número {week} no tiene campo numero")
    return numero


def compose_message(numero, url):
    return (
        f"EduSemanari, número {numero}\n"
        "Nueva edición en castellano y valenciano / "
        "Nova edició en castellà i valencià:\n"
        f"{url}"
    )


def wait_for_url(url, seconds):
    if seconds <= 0:
        return True
    deadline = time.monotonic() + seconds
    while True:
        try:
            response = requests.get(url, timeout=20)
            if 200 <= response.status_code < 400:
                return True
        except requests.RequestException:
            pass
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return False
        LOG.info("La web todavía no responde; reintento en 15 s")
        time.sleep(min(15, remaining))


def resolve_chat_id(db, group):
    row = db.execute(
        """SELECT chat_id FROM messages WHERE group_username=?
           ORDER BY sent_at DESC LIMIT 1""",
        (group,),
    ).fetchone()
    return row["chat_id"] if row else f"@{group}"


def announce(config, week=None, dry_run=False, force=False, wait=300,
             numeros_dir=NUMEROS_DIR):
    week = week or latest_week(numeros_dir)
    numero = issue_number(week, numeros_dir)
    url = f"{config['site_url']}/numeros/{week}/"
    message = compose_message(numero, url)
    groups = config["announce_groups"]
    if not groups:
        raise ValueError("Configura announce_groups con los grupos participantes")
    if dry_run:
        print(f"[dry-run] {message}")
        print(f"[dry-run] grupos: {', '.join('@' + group for group in groups)}")
        return
    if not wait_for_url(url, wait):
        raise ValueError(f"La web no responde en {url}; no se envía el aviso")
    try:
        token = read_token(config["token_pass_entry"])
    except TokenError as exc:
        raise ValueError(str(exc)) from None
    api = TelegramAPI(token)
    db = connect(config["database"])
    failed = []
    sent = 0
    for group in groups:
        key = f"announced:{week}:{group}"
        if not force and get_state(db, key):
            LOG.info("Aviso ya enviado a @%s; se omite", group)
            continue
        try:
            api.call(
                "sendMessage",
                {"chat_id": resolve_chat_id(db, group), "text": message},
                20,
            )
        except TelegramError as exc:
            LOG.error("No se pudo avisar a @%s: %s", group, exc)
            failed.append(group)
            continue
        set_state(db, key, int(time.time()))
        LOG.info("Aviso enviado a @%s", group)
        sent += 1
    if failed:
        raise ValueError("No se pudo avisar a: " + ", ".join(f"@{g}" for g in failed))
    LOG.info("Avisos completados (%d enviados)", sent)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--week", help="Lunes del número: AAAA-MM-DD")
    parser.add_argument("--dry-run", action="store_true", help="Muestra el aviso sin enviarlo")
    parser.add_argument("--force", action="store_true", help="Repite avisos ya enviados")
    parser.add_argument(
        "--wait", type=int, default=300,
        help="Segundos para esperar a que la web responda (0 = no esperar)",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = load_config(args.config)
    try:
        announce(
            config, week=args.week, dry_run=args.dry_run,
            force=args.force, wait=args.wait,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from None


if __name__ == "__main__":
    main()
