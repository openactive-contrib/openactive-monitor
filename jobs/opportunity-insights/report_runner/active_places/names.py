"""Venue-name similarity, used as the last-resort matching channel.

OpenActive venue names and Active Places site names describe the same places in
different registers: ``Whitwick & Coalville Lc`` against
``WHITWICK AND COALVILLE LEISURE CENTRE``. Bridging them needs four things —
case folding, ``&``/``and`` unification, expansion of the abbreviations the
sector uses, and removal of the address that publishers routinely append to the
name (``Queens Park Tennis Club, Queens Park, East Drive, Brighton, BN2 0BQ``).

Scoring is deliberately token-based rather than edit-distance: word order varies
between the two registers, and an edit distance over a name with an address glued
to it is meaningless.
"""

from __future__ import annotations

import html
import re

# A trailing or embedded postcode is address, not name.
_POSTCODE = re.compile(r"\b[A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2}\b", re.IGNORECASE)

# Abbreviations that appear in OpenActive names but are spelled out in Active Places.
_ABBREVIATIONS = {
    "lc": "leisure centre",
    "sc": "sports centre",
    "rfc": "rugby football club",
    "afc": "football club",
    "fc": "football club",
    "cc": "cricket club",
    "gc": "golf club",
    "tc": "tennis club",
    "uni": "university",
    "rec": "recreation",
    "pf": "playing fields",
}

# Words carried by so many venue names that they say nothing about identity.
# Dropping them is what lets "Tarka" match "TARKA LEISURE CENTRE".
_GENERIC = {
    "the", "and", "of", "at", "in", "on", "a", "uk", "ltd", "limited",
    "centre", "center", "leisure", "sports", "sport", "club", "school", "academy",
    "college", "community", "trust", "council", "campus", "site", "venue", "hall",
    "room", "studio", "court", "courts", "pitch", "pitches", "gym", "fitness",
    "main", "indoor", "outdoor", "new", "old",
}


def candidate_segments(raw: str | None) -> list[str]:
    """Split a raw name field into the name-like fragments worth scoring.

    A venue may carry several names (pipe-separated) and each may have an address
    appended after a comma or newline. Both the leading fragment and the whole
    string are returned, so a name that legitimately contains a comma is not lost.
    """
    if not isinstance(raw, str) or not raw.strip():
        return []
    segments: list[str] = []
    for name in raw.split("|"):
        name = html.unescape(name).replace("\\n", "\n")
        leading = re.split(r"[\n,]", name)[0]
        segments.extend(part for part in (leading, name) if part.strip())
    return segments


def content_tokens(text: str) -> frozenset[str]:
    """Distinctive words of a name, normalised and stripped of generic vocabulary."""
    text = html.unescape(str(text)).lower()
    text = _POSTCODE.sub(" ", text)
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    words: list[str] = []
    for word in text.split():
        words.extend(_ABBREVIATIONS.get(word, word).split())
    return frozenset(w for w in words if w not in _GENERIC and len(w) > 2)


def all_tokens(text: str) -> frozenset[str]:
    """Every normalised word of a name, generic vocabulary included."""
    text = html.unescape(str(text)).lower()
    text = _POSTCODE.sub(" ", text)
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    words: list[str] = []
    for word in text.split():
        words.extend(_ABBREVIATIONS.get(word, word).split())
    return frozenset(words)


# When a match rests only on place-name tokens, this much whole-name agreement is
# required to keep it. It separates "Redwell Leisure Centre" from "Wetherby".
_PLACE_ONLY_FULL_JACCARD = 0.7


def similarity(oa_name: str | None,
               ap_name: str | None,
               place_tokens: frozenset[str] = frozenset()) -> float:
    """Best similarity in 0..1 between an OpenActive name field and a site name.

    Blends Jaccard with containment. Containment alone would score any name whose
    tokens are a subset of a longer one, which is what makes an appended address
    match; Jaccard alone punishes exactly that legitimate case. Averaging keeps the
    appended-address matches while still penalising names that merely share a town.

    ``place_tokens`` guards the dominant false-positive class. Publishers often put
    a bare town in the name field — "Wetherby", "Clacton-on-Sea, UK" — which would
    otherwise score 1.0 against any site in that town, because once generic words
    are dropped both sides reduce to the town. When every shared word is a place
    name, the pair is kept only if the *whole* names agree too, which still admits
    a genuine venue that happens to be named after its town.
    """
    if not isinstance(ap_name, str):
        return 0.0
    ap_content = content_tokens(ap_name)
    if not ap_content:
        return 0.0
    ap_all = all_tokens(ap_name)

    best = 0.0
    for segment in candidate_segments(oa_name):
        oa_content = content_tokens(segment)
        if not oa_content:
            continue
        shared = oa_content & ap_content
        if not shared:
            continue
        if place_tokens and shared <= place_tokens:
            # Everything the two names share is a place word, so on its own this pair
            # says only "same town". Keep it only if the whole names agree AND the
            # site name adds no distinctive word of its own — "Whitwick & Coalville
            # Lc" survives against "WHITWICK AND COALVILLE LEISURE CENTRE", while
            # "Clacton-on-Sea, UK" does not against "PUREGYM (CLACTON-ON-SEA)",
            # whose "puregym" is exactly the venue identity the other name lacks.
            oa_all = all_tokens(segment)
            full_jaccard = len(oa_all & ap_all) / len(oa_all | ap_all)
            ap_distinctive = (ap_content - shared) - place_tokens
            if full_jaccard < _PLACE_ONLY_FULL_JACCARD or ap_distinctive:
                continue
        jaccard = len(shared) / len(oa_content | ap_content)
        containment = len(shared) / min(len(oa_content), len(ap_content))
        best = max(best, 0.5 * jaccard + 0.5 * containment)
    return best
