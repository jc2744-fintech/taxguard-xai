from __future__ import annotations

import unittest

from form990_xai.entities import hashed_entity_id, normalize_entity_name


class EntityTests(unittest.TestCase):
    def test_name_normalization_is_stable(self) -> None:
        self.assertEqual(normalize_entity_name("  ACME, Inc. "), "acme inc")

    def test_study_salt_changes_pseudonym(self) -> None:
        first = hashed_entity_id("Public Person", "person", "study-salt-one")
        second = hashed_entity_id("Public Person", "person", "study-salt-two")
        self.assertNotEqual(first, second)
        self.assertNotIn("public", first)

    def test_short_salt_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            hashed_entity_id("Public Person", "person", "short")


if __name__ == "__main__":
    unittest.main()
