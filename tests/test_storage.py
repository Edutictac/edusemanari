import sqlite3
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from semanario.storage import connect, ingest_update, last_update_id, purge_old, week_messages


class StorageTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = connect(str(Path(self.temp.name) / "test.sqlite3"))

    def tearDown(self):
        self.db.close()
        self.temp.cleanup()

    def message(self, update_id, group="edutictac", text="Hola", edited=False):
        key = "edited_message" if edited else "message"
        return {
            "update_id": update_id,
            key: {
                "message_id": 10,
                "date": int(datetime(2026, 11, 2, 8, tzinfo=ZoneInfo("Europe/Madrid")).timestamp()),
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

    def test_channel_post_is_collected_from_allowed_channel(self):
        update = self.message(4, group="cv_tic", text="Noticia")
        update["channel_post"] = update.pop("message")
        update["channel_post"]["chat"]["type"] = "channel"
        self.assertTrue(ingest_update(self.db, update, {"edutictac", "cv_tic"}))
        rows = week_messages(self.db, date(2026, 11, 2), ZoneInfo("Europe/Madrid"))
        self.assertEqual(rows[0]["link"], "https://t.me/cv_tic/10")


if __name__ == "__main__":
    unittest.main()
