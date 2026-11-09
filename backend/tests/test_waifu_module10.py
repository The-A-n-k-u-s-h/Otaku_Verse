import json
import sqlite3
import unittest

from app.services.waifu_history_schema import HISTORY_SCHEMA
from app.services.waifu_history_service import (
    insert_history_record,
)


class WaifuModule10HistoryTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.db.executescript(HISTORY_SCHEMA)

    def tearDown(self):
        self.db.close()

    def sample_match(self):
        return {
            "character": {
                "id": 7,
                "name": "Test Character",
                "anime_title": "Test Anime",
                "image_url": "https://example.com/character.jpg",
                "description": "A fictional test profile."
            },
            "compatibility": {
                "overall_score": 87.5,
                "personality_score": 82,
                "romantic_score": 91.17
            }
        }

    def test_insert_history_record(self):
        row = insert_history_record(
            self.db, "match-001", "guest:test-owner",
            self.sample_match(), {"title": "A good match"}
        )
        self.assertEqual(row["character_name"], "Test Character")
        self.assertAlmostEqual(row["overall_score"], 87.5)

    def test_same_match_updates_instead_of_duplicating(self):
        insert_history_record(
            self.db, "match-001", "guest:test-owner",
            self.sample_match(), {"title": "First"}
        )
        updated = self.sample_match()
        updated["compatibility"]["overall_score"] = 90
        insert_history_record(
            self.db, "match-001", "guest:test-owner",
            updated, {"title": "Updated"}
        )
        count = self.db.execute(
            "SELECT COUNT(*) FROM waifu_match_history"
        ).fetchone()[0]
        self.assertEqual(count, 1)
        score = self.db.execute(
            "SELECT overall_score FROM waifu_match_history"
        ).fetchone()[0]
        self.assertEqual(score, 90)

    def test_owner_is_stored_separately(self):
        insert_history_record(
            self.db, "match-001", "guest:owner-a",
            self.sample_match(), {}
        )
        row = self.db.execute(
            "SELECT owner_key FROM waifu_match_history"
        ).fetchone()
        self.assertEqual(row["owner_key"], "guest:owner-a")

    def test_rejects_invalid_score(self):
        match = self.sample_match()
        match["compatibility"]["overall_score"] = 120
        with self.assertRaises(ValueError):
            insert_history_record(
                self.db, "match-001", "guest:test-owner", match, {}
            )

    def test_snapshot_is_valid_json(self):
        insert_history_record(
            self.db, "match-001", "guest:test-owner",
            self.sample_match(), {"title": "Test"}
        )
        row = self.db.execute(
            "SELECT snapshot_json FROM waifu_match_history"
        ).fetchone()
        snapshot = json.loads(row["snapshot_json"])
        self.assertEqual(snapshot["character"]["name"], "Test Character")


if __name__ == "__main__":
    unittest.main()
