import sqlite3
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from semanario.storage import (
    connect, get_state, ingest_update, last_update_id, purge_old, set_state,
    week_messages,
)


class StorageTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = connect(str(Path(self.temp.name) / "test.sqlite3"))

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def message(self, update_id, group="edutictac", text="Hola", edited=False,
                when=None, message_id=10):
        key = "edited_message" if edited else "message"
        when = when or datetime(2026, 11, 2, 8, tzinfo=ZoneInfo("Europe/Madrid"))
        return {
            "update_id": update_id,
            key: {
                "message_id": message_id,
                "date": int(when.timestamp()),
                "chat": {"id": -1001, "type": "supergroup", "username": group},
                "text": text,
                **({"edit_date": 1793610000} if edited else {}),
            },
        }

    def test_only_allowed_group_and_deduplicates_edits(self):
        self.assertFalse(ingest_update(self.db, self.message(1, "otro"), {"edutictac"}))
        self.assertTrue(ingest_update(self.db, self.message(2), {"edutictac"}))
        self.assertTrue(ingest_update(self.db, self.message(3, text="Corregido", edited=True), {"edutictac"}))
        self.assertEqual(last_update_id(self.db), 3)
        rows = week_messages(self.db, date(2026, 11, 2), ZoneInfo("Europe/Madrid"))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["text"], "Corregido")
        self.assertEqual(rows[0]["link"], "https://t.me/edutictac/10")
        self.assertTrue(rows[0]["edited"])

    def test_week_bounds_and_retention(self):
        self.assertTrue(ingest_update(self.db, self.message(1), {"edutictac"}))
        self.assertEqual(len(week_messages(self.db, date(2026, 11, 2), ZoneInfo("Europe/Madrid"))), 1)
        self.assertEqual(len(week_messages(self.db, date(2026, 11, 9), ZoneInfo("Europe/Madrid"))), 0)
        self.assertEqual(purge_old(self.db, 35, datetime(2027, 1, 1, tzinfo=ZoneInfo("UTC"))), 1)

    def test_week_closes_on_saturday_and_excludes_sunday(self):
        zona = ZoneInfo("Europe/Madrid")
        sabado = datetime(2026, 11, 7, 23, 59, tzinfo=zona)
        domingo = datetime(2026, 11, 8, 0, 1, tzinfo=zona)
        self.assertTrue(ingest_update(
            self.db, self.message(1, text="Sábado", when=sabado, message_id=10), {"edutictac"},
        ))
        self.assertTrue(ingest_update(
            self.db, self.message(2, text="Domingo", when=domingo, message_id=11), {"edutictac"},
        ))
        rows = week_messages(self.db, date(2026, 11, 2), zona)
        self.assertEqual([row["text"] for row in rows], ["Sábado"])
        siguiente = week_messages(self.db, date(2026, 11, 9), zona)
        self.assertEqual([row["text"] for row in siguiente], ["Domingo"])

    def test_week_starts_where_the_previous_one_closed(self):
        zona = ZoneInfo("Europe/Madrid")
        sabado_anterior = datetime(2026, 10, 31, 23, 59, tzinfo=zona)
        domingo = datetime(2026, 11, 1, 0, 1, tzinfo=zona)
        self.assertTrue(ingest_update(
            self.db,
            self.message(1, text="Sábado anterior", when=sabado_anterior, message_id=10),
            {"edutictac"},
        ))
        self.assertTrue(ingest_update(
            self.db,
            self.message(2, text="Domingo", when=domingo, message_id=11),
            {"edutictac"},
        ))
        anterior = week_messages(self.db, date(2026, 10, 26), zona)
        self.assertEqual([row["text"] for row in anterior], ["Sábado anterior"])
        actual = week_messages(self.db, date(2026, 11, 2), zona)
        self.assertEqual([row["text"] for row in actual], ["Domingo"])

    def test_state_helpers(self):
        self.assertIsNone(get_state(self.db, "clave"))
        set_state(self.db, "clave", 42)
        self.assertEqual(get_state(self.db, "clave"), "42")

    def test_channel_post_is_collected_from_allowed_channel(self):
        update = self.message(4, group="cv_tic", text="Noticia")
        update["channel_post"] = update.pop("message")
        update["channel_post"]["chat"]["type"] = "channel"
        self.assertTrue(ingest_update(self.db, update, {"edutictac", "cv_tic"}))
        rows = week_messages(self.db, date(2026, 11, 2), ZoneInfo("Europe/Madrid"))
        self.assertEqual(rows[0]["link"], "https://t.me/cv_tic/10")


if __name__ == "__main__":
    unittest.main()
