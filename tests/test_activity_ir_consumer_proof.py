from __future__ import annotations

import unittest

from src.integrations.render import activity_ir_consumer_proof as consumer


class ActivityIRConsumerProofTests(unittest.TestCase):
    def test_legacy_adapter_preserves_exact_ranges_and_boundaries(self) -> None:
        plan = {
            "sources": [
                {
                    "source_id": "s1",
                    "source_identity": "youtube:one",
                    "provider_channel": "Provider",
                }
            ],
            "activity_units": [
                {
                    "unit_id": "activity_001",
                    "activity_topic": "observable activity",
                    "source_id": "s1",
                    "source_range": [10.0, 20.0],
                    "quote_source_range": [12.0, 15.0],
                    "quote": "direct quote",
                    "date": "2026-08-01",
                }
            ],
            "temporal_bridge": {"visible_text": "one week later"},
        }
        adapted = consumer._adapt_legacy_plan(plan)
        unit = adapted["units"][0]
        self.assertEqual(unit["source"]["source_in"], 10.0)
        self.assertEqual(unit["source"]["source_out"], 20.0)
        self.assertEqual(unit["context"]["source_in"], 10.0)
        self.assertEqual(unit["context"]["source_out"], 20.0)
        self.assertEqual(unit["quote"]["source_in"], 12.0)
        self.assertEqual(unit["quote"]["source_out"], 15.0)
        self.assertIs(unit["subtitle_dependency"], False)

    def test_rolling_overlap_closes_previous_without_delaying_next(self) -> None:
        rows = [
            {
                "provider_event_id": "a",
                "unit_id": "u1",
                "source_start_seconds": 10.0,
                "source_end_seconds": 13.0,
                "output_start_seconds": 0.0,
                "output_end_seconds": 3.0,
                "text": "first",
            },
            {
                "provider_event_id": "b",
                "unit_id": "u1",
                "source_start_seconds": 12.0,
                "source_end_seconds": 15.0,
                "output_start_seconds": 2.0,
                "output_end_seconds": 5.0,
                "text": "second",
            },
        ]
        resolved, stats = consumer._resolve_rolling_overlaps(rows)
        self.assertEqual(resolved[0]["output_end_seconds"], 2.0)
        self.assertEqual(resolved[1]["output_start_seconds"], 2.0)
        self.assertEqual(stats["provider_cues_delayed_to_previous_end"], 0)
        self.assertEqual(stats["previous_cues_closed_at_next_start"], 1)
        self.assertEqual(stats["remaining_overlap_count"], 0)


if __name__ == "__main__":
    unittest.main()
