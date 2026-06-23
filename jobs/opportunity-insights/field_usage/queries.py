"""SQL builders for the field-usage analysis.

Two query shapes:

* ``sampled_json_data`` — up to ``samples_per_kind`` random ``json_data``
  payloads per ``(dataset_url, feed_id, kind)``, optionally restricted to a
  recency window. Reuses the deterministic-sample pattern from
  ``quality.queries`` (``ROW_NUMBER() OVER (PARTITION BY ... ORDER BY
  FARM_FINGERPRINT(...))``). Streamed and walked in Python.
* ``exact_field_presence`` — exact ``COUNTIF`` of top-level key presence for a
  fixed, code-generated list of known model fields, grouped by ``kind``. Field
  names come from the model catalog (never user input) so they are safe to
  embed; values are never interpolated.
"""

from __future__ import annotations

from datetime import date

DEFAULT_SAMPLES_PER_KIND = 500


def _window_clause(window_days: int | None, reference_date: date) -> str:
    if window_days is None:
        return ""
    return (
        f"AND last_updated >= DATE_SUB(DATE '{reference_date.isoformat()}', "
        f"INTERVAL {int(window_days)} DAY)"
    )


def sampled_json_data(
    opportunities_table: str,
    reference_date: date,
    window_days: int | None = None,
    samples_per_kind: int = DEFAULT_SAMPLES_PER_KIND,
) -> str:
    """Up to ``samples_per_kind`` random ``json_data`` rows per (dataset, feed, kind).

    When ``window_days`` is ``None`` the whole table history is eligible;
    otherwise only rows whose ``last_updated`` falls within ``window_days`` of
    ``reference_date`` are considered.
    """
    window = _window_clause(window_days, reference_date)
    return f"""
        WITH eligible AS (
          SELECT dataset_url, feed_id, kind, id, json_data
          FROM `{opportunities_table}`
          WHERE feed_id IS NOT NULL
            AND kind    IS NOT NULL
            {window}
        ),
        sampled AS (
          SELECT
            dataset_url,
            feed_id,
            kind,
            json_data,
            ROW_NUMBER() OVER (
              PARTITION BY dataset_url, feed_id, kind
              ORDER BY FARM_FINGERPRINT(CONCAT(CAST(RAND() AS STRING), IFNULL(id, '')))
            ) AS rn
          FROM eligible
        )
        SELECT dataset_url, feed_id, kind, json_data
        FROM sampled
        WHERE rn <= {int(samples_per_kind)}
    """


def _json_path(field: str) -> str:
    """Return a quoted JSONPath for ``field`` that is safe for special keys.

    The quoted form (``$."@type"``) is valid for ordinary keys too and handles
    JSON-LD keys such as ``@type`` / ``@id`` uniformly.
    """
    return f'$."{field}"'


def exact_field_presence(
    opportunities_table: str,
    field_paths: list[list[str]],
    window_days: int | None = None,
    reference_date: date | None = None,
) -> str:
    """Exact per-kind top-level presence counts.

    ``field_paths[i]`` is the list of top-level key names that satisfy column
    ``fN`` — the field itself plus any alternative keys (e.g. ``["@type",
    "type"]``). A row is counted for the column when *any* of those keys is
    present (value may be JSON null). Columns are positional: ``fN`` maps to
    ``field_paths[N]``. ``GROUP BY kind`` lets the caller fold counts into spec
    categories.
    """
    window = _window_clause(window_days, reference_date or date.today())

    def _countif(alts: list[str], i: int) -> str:
        ors = " OR ".join(
            f"JSON_QUERY(json_data, '{_json_path(a)}') IS NOT NULL" for a in alts
        )
        return f"COUNTIF({ors}) AS f{i}"

    countifs = ",\n          ".join(
        _countif(alts, i) for i, alts in enumerate(field_paths)
    )
    return f"""
        SELECT
          kind,
          COUNT(*) AS total,
          {countifs}
        FROM `{opportunities_table}`
        WHERE kind IS NOT NULL
          {window}
        GROUP BY kind
    """


__all__ = ["sampled_json_data", "exact_field_presence", "DEFAULT_SAMPLES_PER_KIND"]
