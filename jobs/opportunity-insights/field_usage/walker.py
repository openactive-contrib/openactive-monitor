"""Recursive walker over an OpenActive ``json_data`` payload.

Attributes each field key to the ``@type`` of the actual object it belongs to.
In-place nested dicts (and lists of dicts) that carry their own ``@type`` are
recursed into and their keys attributed to that nested type; string values
(URI references to objects living in other rows) are leaves and contribute
nothing — the referenced object is counted where it is itself published.

The walker is pure: no I/O, no global state. It yields one observation per
object *instance* so the aggregator can count field presence per instance.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

# Keys carrying the entity type. ``@type`` (JSON-LD) wins over the bare
# schema.org ``type`` alias.
_TYPE_KEYS: tuple[str, ...] = ("@type", "type")

# JSON-LD framing key — never a model field, excluded from observations.
_EXCLUDE_KEYS: frozenset[str] = frozenset({"@context"})

# Guard against pathological / cyclic-looking nesting.
_MAX_DEPTH: int = 6


def _resolve_type(obj: dict[str, Any]) -> str | None:
    """Return the entity type declared on ``obj`` (``@type`` or ``type``), or None."""
    for key in _TYPE_KEYS:
        raw = obj.get(key)
        if isinstance(raw, list):
            raw = raw[0] if raw else None
        if isinstance(raw, str) and raw.strip():
            return raw.strip()
    return None


def _walk_object(
    obj: Any,
    depth: int,
    fallback_type: str | None,
) -> Iterator[tuple[str, frozenset[str]]]:
    """Yield ``(entity_type, field_keys)`` for ``obj`` and every nested entity.

    ``fallback_type`` is only used for the top-level object (the BigQuery
    ``kind``); nested dicts without an explicit ``@type`` are skipped — they
    cannot be reliably named, so attributing their keys would pollute
    per-type percentages.
    """
    if depth > _MAX_DEPTH or not isinstance(obj, dict):
        return

    entity_type = _resolve_type(obj) or fallback_type
    if entity_type:
        field_keys = frozenset(k for k in obj.keys() if k not in _EXCLUDE_KEYS)
        yield entity_type, field_keys

    for value in obj.values():
        if isinstance(value, dict):
            yield from _walk_object(value, depth + 1, fallback_type=None)
        elif isinstance(value, list):
            for element in value:
                if isinstance(element, dict):
                    yield from _walk_object(element, depth + 1, fallback_type=None)
        # scalars / strings (e.g. URI references) are leaves — nothing to yield


def walk(
    payload: dict[str, Any],
    top_level_kind: str | None = None,
) -> Iterator[tuple[str, frozenset[str]]]:
    """Walk a parsed ``json_data`` payload.

    Yields one ``(entity_type, field_keys)`` tuple per object instance found:
    the top-level object plus every in-place nested object that carries an
    ``@type``. The top-level object falls back to ``top_level_kind`` (the
    BigQuery ``kind`` column) when it declares no ``@type``.
    """
    if not isinstance(payload, dict):
        return
    yield from _walk_object(payload, depth=0, fallback_type=top_level_kind)


__all__ = ["walk"]
