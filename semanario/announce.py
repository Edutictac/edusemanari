"""Avisa en los grupos participantes de que hay un número publicado."""

import argparse
import json
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


def compose_message(numero, url, *, group=None, week=None, language="es",
                    numeros_dir=NUMEROS_DIR):
    """Usa el resumen editorial del grupo; los números antiguos conservan su aviso."""
    if language not in ("es", "va"):
        raise ValueError("El idioma del aviso debe ser es o va")
    notice_file = Path(numeros_dir) / week / "avisos.json" if week else None
    if notice_file is None or not notice_file.exists():
        return (
            f"EduSetmanari, número {numero}\n"
            "Nueva edición en castellano y valenciano / "
            "Nova edició en castellà i valencià:\n"
            f"{url}"
        )
    notices = json.loads(notice_file.read_text(encoding="utf-8"))
    profile = notices.get("grupos", {}).get(group, notices.get("general", {}))
    content = profile.get(language)
    if not isinstance(content, dict):
        raise ValueError(f"Falta el aviso en {language} para @{group}")
    intro, bullets = content.get("intro"), content.get("puntos")
    if (not isinstance(intro, str) or not intro.strip()
            or not isinstance(bullets, list) or not 1 <= len(bullets) <= 3
            or not all(isinstance(item, str) and item.strip() for item in bullets)):
        raise ValueError(f"El aviso para @{group} necesita introducción y de 1 a 3 puntos")
    fields = front_matter(Path(numeros_dir) / week / "_index.md")
    published = date.fromisoformat(fields["date"][:10])
    months = (
        "enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre"
        if language == "es" else
        "gener febrer març abril maig juny juliol agost setembre octubre novembre desembre"
    ).split()
    weekdays = (
        "Lunes Martes Miércoles Jueves Viernes Sábado Domingo"
        if language == "es" else
        "Dilluns Dimarts Dimecres Dijous Divendres Dissabte Diumenge"
    ).split()
    month = months[published.month - 1]
    connector = "d’" if language == "va" and month[0] in "aeiou" else "de "
    when = f"{weekdays[published.weekday()]}, {published.day} {connector}{month} de {published.year}"
    available = ("En castellano y valenciano." if language == "es"
                 else "En castellà i valencià.")
    message = (
        f"EduSetmanari · Núm. {numero}\n{when}\n\n{intro.strip()}\n\n"
        + "\n".join(f"• {item.strip()}" for item in bullets)
        + f"\n\n{available}\n👉 {url}"
    )
    if len(message.encode("utf-16-le")) // 2 > 4096:
        raise ValueError(f"El aviso para @{group} supera el límite de Telegram")
    return message


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
    groups = config["announce_groups"]
    if not groups:
        raise ValueError("Configura announce_groups con los grupos participantes")
    # Validar todos los textos antes de consultar credenciales o enviar el primero.
    messages = {
        group: compose_message(
            numero, url, group=group, week=week,
            language=config.get("announce_language", "es"), numeros_dir=numeros_dir,
        )
        for group in groups
    }
    if dry_run:
        for group, message in messages.items():
            print(f"[dry-run] @{group}\n{message}\n")
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
        payload = {"chat_id": resolve_chat_id(db, group), "text": messages[group]}
        thread_id = config.get("announce_threads", {}).get(group)
        if thread_id is not None:
            payload["message_thread_id"] = thread_id
        try:
            result = api.call("sendMessage", payload, 20)
        except TelegramError as exc:
            LOG.error("No se pudo avisar a @%s: %s", group, exc)
            failed.append(group)
            continue
        if isinstance(result, dict) and isinstance(result.get("message_id"), int):
            set_state(db, f"announced_message:{week}:{group}", result["message_id"])
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
