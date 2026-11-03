"""Persistencia mínima de mensajes de Telegram."""

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


def load_config(path):
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    bot_username = config.get("bot_username", "").lstrip("@").lower()
    if not bot_username or bot_username == "nombre_del_bot_nuevo":
        raise ValueError("Configura bot_username con el bot dedicado")
    config["bot_username"] = bot_username
    entry = config.get("token_pass_entry", "")
    if not entry or entry == "telegram/nombre_del_bot_nuevo":
        raise ValueError("Configura token_pass_entry con la ruta de pass")
    groups = config.get("groups", [])
    if not groups or not all(isinstance(group, str) and group for group in groups):
        raise ValueError("La configuración necesita nombres de grupos públicos")
    config["groups"] = {group.lstrip("@").lower() for group in groups}
    config["timezone"] = ZoneInfo(config.get("timezone", "Europe/Madrid"))
    config["retention_days"] = int(config.get("retention_days", 35))
    if config["retention_days"] < 8:
        raise ValueError("retention_days debe ser al menos 8")
    config["database"] = str((Path(path).resolve().parent / config["database"]).resolve())
    return config


def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS state (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS messages (
            chat_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            group_username TEXT NOT NULL,
            sent_at INTEGER NOT NULL,
            text TEXT NOT NULL,
            edited_at INTEGER,
            PRIMARY KEY (chat_id, message_id)
        );
        CREATE INDEX IF NOT EXISTS messages_sent_at ON messages(sent_at);
        """
    )
    return db


def last_update_id(db):
    row = db.execute("SELECT value FROM state WHERE key='last_update_id'").fetchone()
    return int(row["value"]) if row else 0


def ingest_update(db, update, allowed_groups):
    update_id = update["update_id"]
    message = (
        update.get("edited_message") or update.get("message")
        or update.get("edited_channel_post") or update.get("channel_post")
    )
    accepted = False
    with db:
        if message:
            chat = message.get("chat", {})
            username = (chat.get("username") or "").lower()
            content = message.get("text") or message.get("caption") or ""
            if (
                chat.get("type") in {"group", "supergroup", "channel"}
                and username in allowed_groups
                and content.strip()
            ):
                db.execute(
                    """INSERT INTO messages
                       (chat_id, message_id, group_username, sent_at, text, edited_at)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ON CONFLICT(chat_id, message_id) DO UPDATE SET
                       text=excluded.text, edited_at=excluded.edited_at""",
                    (
                        chat["id"], message["message_id"], username,
                        message["date"], content.strip(), message.get("edit_date"),
                    ),
                )
                accepted = True
        db.execute(
            """INSERT INTO state(key, value) VALUES ('last_update_id', ?)
               ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
            (str(update_id),),
        )
    return accepted


def purge_old(db, days, now=None):
    now = now or datetime.now(timezone.utc)
    cutoff = int((now - timedelta(days=days)).timestamp())
    with db:
        return db.execute("DELETE FROM messages WHERE sent_at < ?", (cutoff,)).rowcount


def week_messages(db, monday, local_timezone):
    if monday.weekday() != 0:
        raise ValueError("La semana debe empezar en lunes")
    start = datetime.combine(monday, datetime.min.time(), local_timezone)
    end = start + timedelta(days=7)
    rows = db.execute(
        """SELECT group_username, message_id, sent_at, text, edited_at
           FROM messages WHERE sent_at >= ? AND sent_at < ?
           ORDER BY sent_at, group_username, message_id""",
        (int(start.timestamp()), int(end.timestamp())),
    ).fetchall()
    return [
        {
            "group": row["group_username"],
            "message_id": row["message_id"],
            "date": datetime.fromtimestamp(row["sent_at"], local_timezone).isoformat(),
            "text": row["text"],
            "link": f"https://t.me/{row['group_username']}/{row['message_id']}",
            "edited": row["edited_at"] is not None,
        }
        for row in rows
    ]
