"""Unit tests for custom-property detection (no BigQuery / network access).

Run from ``jobs/opportunity-insights``:
    python -m pytest tests/test_custom_properties.py
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from report_runner.taxonomy_adherence import custom_properties as cp  # noqa: E402
from report_runner.taxonomy_adherence import openactive_vocab  # noqa: E402

KNOWN = {"@type", "@id", "type", "id", "name", "location", "address", "activity"}
RUN_DATE = datetime(2026, 9, 29, tzinfo=timezone.utc)


def test_classify_property() -> None:
    assert cp.classify_property("name", KNOWN) is None
    assert cp.classify_property("@language", KNOWN) is None
    assert cp.classify_property("beta:formattedDescription", KNOWN) == cp.BETA
    assert cp.classify_property("ext:foo", KNOWN) == cp.PREFIXED
    assert cp.classify_property("https://example.com/prop", KNOWN) == cp.PREFIXED
    assert cp.classify_property("myField", KNOWN) == cp.UNPREFIXED


def test_aggregator_attributes_to_nested_entity_and_counts() -> None:
    agg = cp.CustomPropertyAggregator(KNOWN)
    payload_a = {
        "@type": "SessionSeries",
        "name": "Yoga",
        "beta:formattedDescription": "<p>x</p>",
        "location": {"@type": "Place", "name": "Hall", "roomCode": "B2"},
    }
    payload_b = {
        "@type": "SessionSeries",
        "name": "Pilates",
        "location": {"@type": "Place", "name": "Hall"},
    }
    agg.add_payload("https://ds1", "feed-1", "SessionSeries", payload_a)
    agg.add_payload("https://ds1", "feed-1", "SessionSeries", payload_b)
    agg.add_payload("https://ds2", "feed-2", "SessionSeries", {"@type": "SessionSeries", "name": "Run"})

    df_feeds = pd.DataFrame([
        {"feed_id": "feed-1", "dataset_name": "DS 1", "publisher_name": "Pub 1",
         "feed_url": "https://ds1/feed", "feed_type": "SessionSeries", "is_regular": True},
    ])
    rows = {r["feed_id"]: r for r in agg.build_rows(RUN_DATE, df_feeds, "test")}

    feed1 = rows["feed-1"]
    assert feed1["sampled_items"] == 2
    assert feed1["publisher_name"] == "Pub 1"
    assert feed1["num_custom_properties"] == 2
    assert feed1["num_custom_property_usages"] == 2
    by_prop = {s["property"]: s for s in feed1["custom_properties"]}
    assert by_prop["roomCode"]["entity_type"] == "Place"
    assert by_prop["roomCode"]["property_kind"] == cp.UNPREFIXED
    assert by_prop["roomCode"]["namespace"] is None
    assert by_prop["roomCode"]["occurrences"] == 1
    assert by_prop["roomCode"]["entity_instances"] == 2
    assert by_prop["roomCode"]["presence_pct"] == 50.0
    assert by_prop["beta:formattedDescription"]["entity_type"] == "SessionSeries"
    assert by_prop["beta:formattedDescription"]["namespace"] == "beta"

    feed2 = rows["feed-2"]
    assert feed2["num_custom_properties"] == 0
    assert feed2["custom_properties"] == []
    assert feed2["dataset_name"] is None


def test_fetch_vocabulary_terms(monkeypatch) -> None:
    doc = {
        "@context": [{"facilityType": {"@id": "oa:facilityType"}}, "https://schema.org/"],
        "@graph": [{"@id": "beta:distance"}, {"label": "no id"}],
    }
    monkeypatch.setattr(openactive_vocab, "fetch_jsonld", lambda url, timeout=30: doc)
    assert openactive_vocab.fetch_vocabulary_terms("ignored") == {"facilityType", "beta:distance"}


def test_load_known_properties_falls_back_to_model_spec(monkeypatch) -> None:
    monkeypatch.setattr(cp, "fetch_vocabulary_terms", lambda url: set())
    known, source = cp.load_known_properties()
    assert source == "model_spec (fallback)"
    assert {"name", "startDate", "facilityType", "@type", "minValue", "givenName"} <= known
