"""Markdown renderers for the field-usage reports.

Pure string builders — no I/O. ``run.py`` writes the returned strings to files.
"""

from __future__ import annotations

from field_usage.aggregator import (
    RARE,
    UNUSED,
    CategoryReport,
    FieldRow,
    UsageResults,
)


def _fmt_pct(pct: float | None) -> str:
    return "—" if pct is None else f"{pct:.1f}%"


def _fmt_int(n: int) -> str:
    return f"{n:,}"


def _model_fields_table(rows: list[FieldRow], show_exact: bool) -> list[str]:
    if show_exact:
        header = "| Field | Model status | Sampled % | Exact % | Instances with | Total | Classification |"
        sep = "|---|---|---:|---:|---:|---:|---|"
    else:
        header = "| Field | Model status | Sampled % | Instances with | Total | Classification |"
        sep = "|---|---|---:|---:|---:|---|"
    lines = [header, sep]
    for r in rows:
        cells = [f"`{r.field}`", r.model_status or "—", _fmt_pct(r.presence_pct)]
        if show_exact:
            cells.append(_fmt_pct(r.exact_pct))
        cells += [_fmt_int(r.instances_with), _fmt_int(r.total_instances), r.classification]
        lines.append("| " + " | ".join(cells) + " |")
    return lines


def _observed_fields_table(rows: list[FieldRow]) -> list[str]:
    lines = [
        "| Field | Presence % | Instances with | Total |",
        "|---|---:|---:|---:|",
    ]
    for r in rows:
        lines.append(
            f"| `{r.field}` | {_fmt_pct(r.presence_pct)} | "
            f"{_fmt_int(r.instances_with)} | {_fmt_int(r.total_instances)} |"
        )
    return lines


def _render_category(cat: CategoryReport, show_exact: bool) -> list[str]:
    out: list[str] = []
    out.append(f"## {cat.category}")
    out.append("")
    observed = ", ".join(f"`{t}`" for t in cat.observed_types) or "_(none observed)_"
    out.append(f"- Observed `@type`s: {observed}")
    out.append(f"- Total instances sampled: **{_fmt_int(cat.total_instances)}**")
    out.append("")

    if cat.total_instances == 0:
        out.append("_No sampled instances for this category._")
        out.append("")
        return out

    out.append("### Model fields")
    out.append("")
    out.extend(_model_fields_table(cat.model_fields, show_exact))
    out.append("")

    candidates = [r for r in cat.model_fields if r.classification in (UNUSED, RARE)]
    out.append("### ⚠️ Deletion candidates (UNUSED / RARE)")
    out.append("")
    if candidates:
        for r in candidates:
            out.append(
                f"- `{r.field}` ({r.model_status}) — {r.classification}, "
                f"{_fmt_pct(r.presence_pct)} ({_fmt_int(r.instances_with)}/{_fmt_int(r.total_instances)})"
            )
    else:
        out.append("_None — every model field is used above the RARE threshold._")
    out.append("")

    out.append("### Provider-extension fields (not in the model)")
    out.append("")
    if cat.extension_fields:
        out.extend(_observed_fields_table(cat.extension_fields))
    else:
        out.append("_None observed._")
    out.append("")
    return out


def render_model_usage_report(results: UsageResults, meta: dict) -> str:
    # Exact full-scan column disabled: its top-level-only, row-weighted % was
    # confusing next to the per-group Sampled % (see run.py). Re-enable by
    # restoring the line below.
    # show_exact = bool(meta.get("exact_scan"))
    show_exact = False
    out: list[str] = []
    out.append("# OpenActive Data-Model Field-Usage Report")
    out.append("")
    out.append(f"- Generated: {meta.get('generated_at', '—')}")
    out.append(f"- Opportunities table: `{meta.get('table', '—')}`")
    out.append(f"- Model spec version: {meta.get('model_version', '—')}")
    out.append(f"- Sampling window: {meta.get('window', 'all-time')}")
    out.append(f"- Samples per (dataset, feed, kind): {meta.get('samples_per_kind', '—')}")
    out.append(
        f"- Thresholds: RARE < {meta.get('rare_threshold')}%, "
        f"LOW < {meta.get('low_threshold')}%"
    )
    # out.append(f"- Exact full-scan: {'yes' if show_exact else 'no'}")
    out.append("")
    out.append(
        "> **Sampled %** is the share of *object instances* of a type whose "
        "`json_data` contains the field key (value may be null), measured over "
        f"the random sample (up to {meta.get('samples_per_kind', '?')} rows per "
        "dataset/feed/kind). Entities referenced by URI string are counted where "
        "they are themselves published (their own rows), not at the reference "
        "site; in-place nested entities are counted wherever they appear. Because "
        "the sample is capped per group, rare fields can wobble run to run."
    )
    # Exact % explainer disabled along with the exact full-scan (see run.py):
    # out.append(">")
    # out.append(
    #     "> - **Exact %** — presence measured over the *entire* table in one scan "
    #     "(ground truth, no sampling). Computed only for top-level model fields of "
    #     "the top-level kinds (Event family, FacilityUse, IndividualFacilityUse, "
    #     "Slot); nested types and extension fields show `—` because the scan can "
    #     "only read top-level keys."
    # )
    # out.append(">")
    # out.append(
    #     "> They differ mainly due to sampling error: where both are present, "
    #     "trust **Exact %**; **Sampled %** is the only signal for nested entities "
    #     "and provider extensions."
    # )
    out.append("")

    out.append("## Contents")
    out.append("")
    out.append("- Model categories: " + ", ".join(c.category for c in results.categories))
    if results.discovered_types:
        out.append(
            "- Discovered-only nested types: "
            + ", ".join(d.type_name for d in results.discovered_types)
        )
    out.append("")

    for cat in results.categories:
        out.extend(_render_category(cat, show_exact))

    out.append("## Discovered-only nested entity types")
    out.append("")
    out.append(
        "_These `@type`s are not part of the OpenActive opportunity model "
        "catalog (e.g. Place, Organization, Offer). Reported as discovered from "
        "in-place nested objects; sampling-only coverage._"
    )
    out.append("")
    if results.discovered_types:
        for d in results.discovered_types:
            out.append(f"### `{d.type_name}` (instances sampled: {_fmt_int(d.total_instances)})")
            out.append("")
            out.extend(_observed_fields_table(d.fields))
            out.append("")
    else:
        out.append("_None observed._")
        out.append("")

    return "\n".join(out)


def render_per_dataset_dump(results: UsageResults, dump_percentages: bool = False) -> str:
    out: list[str] = []
    out.append("# Per-Dataset Field Usage")
    out.append("")
    out.append(
        "For each dataset, the fields actually present in sampled `json_data`, "
        "grouped by entity `@type`. `absent (model)` lists model fields that "
        "never appeared in this dataset for that type."
    )
    out.append("")
    out.append(f"Datasets: **{len(results.datasets)}**")
    out.append("")

    for ds in results.datasets:
        out.append(f"## {ds.dataset_url}")
        if ds.publisher_name:
            out.append(f"_publisher: {ds.publisher_name}_")
        out.append("")
        feeds = ", ".join(
            f"`{fid or '∅'}` ({knd or '∅'}, n={n})" for fid, knd, n in ds.sample_counts
        )
        out.append(f"- feeds sampled: {feeds or '—'}")
        out.append("")

        for block in ds.type_blocks:
            label = block.type_name + (" (nested)" if not block.is_model else "")
            out.append(f"### {label}  (instances sampled: {_fmt_int(block.instances)})")
            out.append("")
            if dump_percentages:
                present = ", ".join(f"{f} ({p:.0f}%)" for f, p in block.present)
            else:
                present = ", ".join(f for f, _ in block.present)
            out.append(f"- present: {present or '—'}")
            if block.is_model:
                absent = ", ".join(block.absent_model)
                out.append(f"- absent (model): {absent or '—'}")
            out.append("")

    return "\n".join(out)


__all__ = ["render_model_usage_report", "render_per_dataset_dump"]
