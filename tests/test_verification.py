import copy
import json
import unittest
from pathlib import Path

from mandoryve import verify


class VerificationTests(unittest.TestCase):
    def setUp(self):
        self.case = json.loads((Path(__file__).resolve().parents[1] / "examples/group.json").read_text())

    def test_inherited_excess(self):
        self.assertEqual(verify(self.case)["differences"], [
            dict(user="lea", folder="interne", permission="read", expected_until=None, observed_until=80)])

    def test_direct_and_existing_permissions(self):
        self.case["before"]["users"]["lea"] = ["support"]
        self.assertEqual(verify(self.case)["status"], "conformant")

    def test_overlong_permission(self):
        self.case["after"]["direct"][0]["until"] += 1
        self.assertEqual(len(verify(self.case)["differences"]), 2)

    def test_incomplete_observation(self):
        del self.case["after"]["groups"]["support"]
        self.assertEqual(verify(self.case)["status"], "unverifiable")

    def test_missing_grants_and_write(self):
        self.case["after"] = copy.deepcopy(self.case["before"])
        self.assertEqual(len(verify(self.case)["differences"]), 2)
        self.case["after"]["direct"] = [dict(user="lea", folder="client", permission="write", until=80)]
        self.assertIn("write", [d["permission"] for d in verify(self.case)["differences"]])

    def test_expired_mandate(self):
        self.case["observed_at"] = 80
        with self.assertRaises(ValueError):
            verify(self.case)
