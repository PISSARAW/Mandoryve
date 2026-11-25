import json
import unittest
from pathlib import Path

from mandoryve import evidence, verify


class EvidenceTests(unittest.TestCase):
    def test_inherited_and_unavailable(self):
        data = json.loads((Path(__file__).resolve().parents[1] / "examples/group.json").read_text())
        packet = evidence(data, verify(data), "exercise", 1)
        self.assertEqual(packet["events"][0]["facts"], {"expected": None, "observed": 80})
        del data["after"]["groups"]["support"]
        packet = evidence(data, verify(data), "exercise", 0)
        self.assertEqual(packet["events"][0]["kind"], "unavailable")

    def test_conformant_summary(self):
        packet = evidence({"observed_at": 7}, {"status": "conformant", "differences": []}, "exercise", 2)
        self.assertEqual(packet["events"][0]["kind"], "verified")
        self.assertEqual(packet["events"][0]["time_s"], 7)
