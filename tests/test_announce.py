import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from semanario.announce import (
    announce, compose_message, issue_number, latest_week,
)


class AnnounceTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.numeros = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def issue(self, week, numero, draft=False):
        folder = self.numeros / week
        folder.mkdir(parents=True)
        draft_line = "draft: true\n" if draft else ""
        (folder / "_index.md").write_text(
            f'---\ntitle: "Número {numero}"\ndate: {week}\nnumero: {numero}\n{draft_line}---\n',
            encoding="utf-8",
        )

    def test_latest_issue_refuses_a_draft(self):
        self.issue("2026-10-26", 0)
        self.assertEqual(latest_week(self.numeros), "2026-10-26")
        self.issue("2026-11-02", 1, draft=True)
        with self.assertRaises(ValueError):
            latest_week(self.numeros)

    def test_issue_number_and_draft_validation(self):
        self.issue("2026-11-02", 1)
        self.assertEqual(issue_number("2026-11-02", self.numeros), "1")
        self.issue("2026-11-09", 2, draft=True)
        with self.assertRaises(ValueError):
            issue_number("2026-11-09", self.numeros)

    def test_message_includes_number_and_url(self):
        message = compose_message(3, "https://example.test/numeros/2026-11-16/")
        self.assertIn("número 3", message)
        self.assertIn("https://example.test/numeros/2026-11-16/", message)

    def test_dry_run_does_not_send(self):
        self.issue("2026-11-02", 1)
        config = {
            "site_url": "https://example.test",
            "announce_groups": ["edutictac", "portaledu"],
        }
        out = io.StringIO()
        with redirect_stdout(out):
            announce(config, week="2026-11-02", dry_run=True, numeros_dir=self.numeros)
        text = out.getvalue()
        self.assertIn("[dry-run]", text)
        self.assertIn("https://example.test/numeros/2026-11-02/", text)
        self.assertIn("@edutictac", text)
        self.assertIn("@portaledu", text)

    def notices(self):
        self.issue("2026-11-02", 1)
        folder = self.numeros / "2026-11-02"
        index = folder / "_index.md"
        index.write_text(index.read_text().replace("date: 2026-11-02", "date: 2026-11-15"))
        def profile(text):
            return {
                "es": {"intro": text, "puntos": [text + " ES"]},
                "va": {"intro": text, "puntos": [text + " VA"]},
            }
        data = {
            "general": profile("General"),
            "grupos": {"aules": profile("Copias de Aules"),
                       "comunitat_lliurex": profile("Acceso a LliureX")},
        }
        (folder / "avisos.json").write_text(json.dumps(data))
        return folder, data

    def test_group_messages_use_publication_date_and_general_fallback(self):
        self.notices()
        def message(group, language="es"):
            return compose_message(1, "https://example.test/numeros/2026-11-02/",
                                   group=group, week="2026-11-02", language=language,
                                   numeros_dir=self.numeros)
        aules = message("aules")
        self.assertIn("Domingo, 15 de noviembre de 2026", aules)
        self.assertIn("• Copias de Aules ES", aules)
        self.assertNotIn("Acceso a LliureX", aules)
        self.assertIn("• Acceso a LliureX ES", message("comunitat_lliurex"))
        self.assertIn("• General ES", message("edutictac"))
        self.assertIn("Diumenge, 15 de novembre de 2026", message("aules", "va"))
        self.assertIn("• Copias de Aules VA", message("aules", "va"))

    def test_personalized_dry_run_never_reads_credentials_or_sends(self):
        self.notices()
        config = {"site_url": "https://example.test", "announce_groups": ["aules", "comunitat_lliurex"]}
        with patch("semanario.announce.read_token") as token, patch("semanario.announce.TelegramAPI") as api:
            with redirect_stdout(io.StringIO()) as out:
                announce(config, week="2026-11-02", dry_run=True, numeros_dir=self.numeros)
            token.assert_not_called()
            api.assert_not_called()
        self.assertIn("[dry-run] @aules", out.getvalue())
        self.assertIn("• Acceso a LliureX ES", out.getvalue())

    def test_delivery_keeps_group_text_and_prevents_repeat_announcements(self):
        self.notices()
        config = {"site_url": "https://example.test", "announce_groups": ["aules", "comunitat_lliurex"],
                  "database": str(self.numeros / "test.sqlite3"), "token_pass_entry": "unused-test-entry",
                  "announce_threads": {"aules": 123}}
        with patch("semanario.announce.read_token", return_value="unused-test-value"), patch("semanario.announce.TelegramAPI") as api:
            api.return_value.call.side_effect = [{"message_id": 110}, {"message_id": 220}]
            announce(config, week="2026-11-02", wait=0, numeros_dir=self.numeros)
            from semanario.storage import connect, get_state
            db = connect(config["database"])
            self.assertEqual(get_state(db, "announced_message:2026-11-02:aules"), "110")
            self.assertEqual(get_state(db, "announced_message:2026-11-02:comunitat_lliurex"), "220")
            db.close()
            calls = api.return_value.call.call_args_list
            self.assertEqual(len(calls), 2)
            self.assertEqual(calls[0].args[1]["chat_id"], "@aules")
            self.assertIn("Copias de Aules", calls[0].args[1]["text"])
            self.assertEqual(calls[0].args[1]["message_thread_id"], 123)
            self.assertNotIn("message_thread_id", calls[1].args[1])
            self.assertEqual(calls[1].args[1]["chat_id"], "@comunitat_lliurex")
            self.assertIn("Acceso a LliureX", calls[1].args[1]["text"])
            announce(config, week="2026-11-02", wait=0, numeros_dir=self.numeros)
            self.assertEqual(api.return_value.call.call_count, 2)

    def test_invalid_notice_stops_all_delivery_before_credentials(self):
        folder, data = self.notices()
        data["grupos"]["comunitat_lliurex"]["es"]["puntos"] = []
        (folder / "avisos.json").write_text(json.dumps(data))
        config = {"site_url": "https://example.test", "announce_groups": ["aules", "comunitat_lliurex"]}
        with patch("semanario.announce.read_token") as token:
            with self.assertRaises(ValueError):
                announce(config, week="2026-11-02", numeros_dir=self.numeros)
            token.assert_not_called()

    def test_oversized_notice_is_rejected(self):
        folder, data = self.notices()
        data["general"]["es"]["intro"] = "x" * 4096
        (folder / "avisos.json").write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            compose_message(1, "https://example.test/", group="edutictac",
                            week="2026-11-02", numeros_dir=self.numeros)


if __name__ == "__main__":
    unittest.main()
