"""Unit tests for activity / facility vocabulary adherence (no BigQuery / network access).

Run from ``jobs/opportunity-insights``:
    python -m pytest tests/test_vocabulary_adherence.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quality import vocabulary_adherence as va  # noqa: E402
from report_runner.taxonomy_adherence import openactive_vocab  # noqa: E402

TAI_CHI_ID = "https://openactive.io/activity-list#c16df6ed-a4a0-4275-a8c3-1c8cff56856f"
SWIMMING_ID = "https://openactive.io/activity-list#6ca15167-51da-4d10-a8fe-5a4b46a14c25"

ACTIVITY_DOC = {
    "id": "https://openactive.io/activity-list",
    "type": "ConceptScheme",
    "concept": [
        {"id": TAI_CHI_ID, "type": "Concept", "prefLabel": "Tai Chi"},
        {"id": SWIMMING_ID, "type": "Concept", "prefLabel": "Swimming",
         "altLabel": ["Swim"]},
        {"id": "https://openactive.io/activity-list#aaaa", "type": "Concept",
         "prefLabel": "Table Tennis"},
    ],
}
ACTIVITY = openactive_vocab.build_concept_scheme(
    ACTIVITY_DOC, openactive_vocab.ACTIVITY_LIST_URL, openactive_vocab.ACTIVITY_LIST_NAMESPACE,
)


# ---------------------------------------------------------------------------
# Vocabulary loading / id normalisation
# ---------------------------------------------------------------------------

def test_build_concept_scheme_collects_ids_and_labels() -> None:
    assert TAI_CHI_ID in ACTIVITY.ids
    assert {"tai chi", "swimming", "swim", "table tennis"} <= ACTIVITY.labels
    assert ACTIVITY.namespace == "https://openactive.io/activity-list"


def test_build_concept_scheme_accepts_at_id_and_graph() -> None:
    doc = {"@graph": [{"@id": TAI_CHI_ID, "prefLabel": {"en": "Tai Chi"}}]}
    scheme = openactive_vocab.build_concept_scheme(doc, "u", openactive_vocab.ACTIVITY_LIST_NAMESPACE)
    assert scheme.ids == frozenset({TAI_CHI_ID})
    assert scheme.labels == frozenset({"tai chi"})


def test_normalise_concept_id_variants() -> None:
    n = openactive_vocab.normalise_concept_id
    assert n("http://openactive.io/activity-list#C16DF6ED-A4A0-4275-A8C3-1C8CFF56856F") == TAI_CHI_ID
    assert n(" https://openactive.io/activity-list/#c16df6ed-a4a0-4275-a8c3-1c8cff56856f ") == TAI_CHI_ID
    assert n("https://www.openactive.io/activity-list#c16df6ed-a4a0-4275-a8c3-1c8cff56856f") == TAI_CHI_ID


def test_fetch_concept_scheme(monkeypatch) -> None:
    monkeypatch.setattr(openactive_vocab, "fetch_jsonld", lambda url, timeout=30: ACTIVITY_DOC)
    scheme = openactive_vocab.fetch_concept_scheme("u", openactive_vocab.ACTIVITY_LIST_NAMESPACE)
    assert scheme is not None and TAI_CHI_ID in scheme.ids


def test_fetch_concept_scheme_failure_returns_none(monkeypatch) -> None:
    monkeypatch.setattr(openactive_vocab, "fetch_jsonld", lambda url, timeout=30: None)
    assert openactive_vocab.fetch_concept_scheme("u", openactive_vocab.ACTIVITY_LIST_NAMESPACE) is None
    monkeypatch.setattr(openactive_vocab, "fetch_jsonld", lambda url, timeout=30: {"concept": []})
    assert openactive_vocab.fetch_concept_scheme("u", openactive_vocab.ACTIVITY_LIST_NAMESPACE) is None


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def test_examples_from_brief() -> None:
    # Concept without id, label in vocabulary.
    assert va.classify_item([{"type": "Concept", "prefLabel": "Swimming"}], ACTIVITY) == (
        va.LABEL_MATCH_ONLY, ["swimming"],
    )
    # Plain string, label in vocabulary.
    assert va.classify_item("Table Tennis", ACTIVITY) == (va.LABEL_MATCH_ONLY, ["table tennis"])
    # Full Concept reference.
    full = [{"id": TAI_CHI_ID, "type": "Concept", "prefLabel": "Tai Chi",
             "inScheme": "https://openactive.io/activity-list"}]
    assert va.classify_item(full, ACTIVITY) == (va.VALID_ID, [])


def test_at_id_and_uri_string_are_valid() -> None:
    assert va.classify_item({"@id": TAI_CHI_ID, "prefLabel": "Tai Chi"}, ACTIVITY)[0] == va.VALID_ID
    assert va.classify_item(TAI_CHI_ID, ACTIVITY)[0] == va.VALID_ID
    http_variant = "http://openactive.io/activity-list/#c16df6ed-a4a0-4275-a8c3-1c8cff56856f"
    assert va.classify_item({"id": http_variant}, ACTIVITY)[0] == va.VALID_ID


def test_unknown_oa_id_is_invalid() -> None:
    value = {"id": "https://openactive.io/activity-list#does-not-exist", "prefLabel": "Tai Chi"}
    assert va.classify_item(value, ACTIVITY) == (va.INVALID_ID, ["tai chi"])


def test_publisher_namespace_is_other_scheme() -> None:
    value = {"id": "https://example.com/activities#spin", "prefLabel": "Spin"}
    assert va.classify_item(value, ACTIVITY) == (va.OTHER_SCHEME, ["spin"])


def test_unrecognised_label() -> None:
    assert va.classify_item(["Aqua Fit"], ACTIVITY) == (va.UNRECOGNISED, ["aqua fit"])


def test_best_value_wins() -> None:
    mixed = [{"id": "https://example.com/x#1", "prefLabel": "Spin"}, {"id": TAI_CHI_ID}]
    assert va.classify_item(mixed, ACTIVITY) == (va.VALID_ID, [])
    assert va.classify_item(["Aqua Fit", "Swim"], ACTIVITY)[0] == va.LABEL_MATCH_ONLY


def test_empty_payload_is_none() -> None:
    assert va.classify_item([], ACTIVITY) is None
    assert va.classify_item([None, ""], ACTIVITY) is None


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def test_summarise_empty_is_none() -> None:
    assert va.summarise(Counter(), Counter()) is None


def test_build_adherence_by_feed_weights_counts() -> None:
    df = pd.DataFrame([
        {"dataset_url": "d", "feed_id": "f", "field": "activity",
         "raw_value": json.dumps([{"id": TAI_CHI_ID}]), "n": 3},
        {"dataset_url": "d", "feed_id": "f", "field": "activity",
         "raw_value": json.dumps("Spin"), "n": 1},
        {"dataset_url": "d", "feed_id": "f", "field": "facility",
         "raw_value": json.dumps("Gym"), "n": 5},
        {"dataset_url": "d", "feed_id": "g", "field": "activity",
         "raw_value": json.dumps("Swim"), "n": 2},
    ])
    out = va.build_adherence_by_feed(df, {"activity": ACTIVITY, "facility": None})

    act = out[("d", "f")]["activity"]
    assert act["items"] == 4
    assert act["valid_id"] == 3
    assert act["unrecognised"] == 1
    assert act["adherence_pct"] == 75.0
    assert act["top_unmatched"] == ["spin"]
    assert sum(act[c] for c in va.CATEGORIES) == act["items"]
    # Facility scheme unavailable -> not computed.
    assert "facility" not in out[("d", "f")]

    other = out[("d", "g")]["activity"]
    assert other["adherence_pct"] == 0.0
    assert other["label_match_only"] == 2
