import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
