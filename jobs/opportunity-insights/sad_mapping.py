"""Sport & Discipline (SAD) matching.

Ported from jobs/analyse-opportunities/analyse_aggregate_opportunities.py:241-340.
Takes the activity/facility count DataFrame and joins it against the
OpenActive -> Sport England mapping CSV. Produces matched/unmatched rollups
plus the master SAD taxonomy with a per-run ``is_matched_by_any_feed`` flag.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

SE_SPORT_AND_DISCIPLINE_FILENAME = "000-SE-sport-and-discipline.csv"
OA_SE_MAPPING_FILENAME = "000-OA-SE-mapping.csv"

_NO_MATCH = "No Match"


@dataclass
class SadResult:
    matched: pd.DataFrame
    unmatched: pd.DataFrame
    master: pd.DataFrame
    unmatched_activities: pd.DataFrame
    num_sad: int
    num_sad_matched: int
    num_sad_unmatched: int
    percentage_sad_matched: float
    percentage_sad_unmatched: float
    total_num_activities_with_sad: int
    total_num_activities_without_sad: int
    total_num_items_with_sad: int
    total_num_items_without_sad: int


def run_sad_matching(df_activities_facilities: pd.DataFrame, data_dir: Path) -> SadResult:
    """Match activity/facility labels to Sport England sport-and-discipline entries.

    ``df_activities_facilities`` must have columns ``activity`` (str) and
    ``count`` (int); it is the combined activity + facility count DataFrame
    equivalent to ``df_total_activitiesfacilities_counts`` in the legacy job.
    """
    df_se = pd.read_csv(data_dir / SE_SPORT_AND_DISCIPLINE_FILENAME)
    df_mapping = pd.read_csv(data_dir / OA_SE_MAPPING_FILENAME)

    joined = pd.merge(
        df_activities_facilities[["activity", "count"]].assign(
            activity=lambda x: x["activity"].astype("string").str.strip()
        ),
        df_mapping,
        how="left",
        on="activity",
    )

    unmatched_activities = joined.loc[joined["sport_and_discipline"].isna()].copy()
    joined["sport_and_discipline"] = joined["sport_and_discipline"].fillna(_NO_MATCH)

    matched = joined.loc[joined["sport_and_discipline"] != _NO_MATCH]
    unmatched = joined.loc[joined["sport_and_discipline"] == _NO_MATCH]

    # Roll up matched: concat activity labels, count distinct activities, sum item counts.
    matched_rollup = (
        matched.groupby("sport_and_discipline")
        .agg({"activity": lambda x: "; ".join(list(x)), "count": ["count", "sum"]})
        .sort_values(by=("count", "sum"), ascending=False)
        .reset_index()
    )
    matched_rollup.columns = ["sport_and_discipline", "activity", "count_activities", "count_items"]

    unmatched_out = unmatched[["sport_and_discipline", "activity", "count"]].copy()
    unmatched_out.columns = ["sport_and_discipline", "activity", "count_items"]

    total_num_activities_with_sad = int(matched_rollup["count_activities"].sum())
    total_num_activities_without_sad = int(unmatched_out.shape[0])
    total_num_items_with_sad = int(matched_rollup["count_items"].sum())
    total_num_items_without_sad = int(unmatched_out["count_items"].sum())

    matched_rollup["percentage_activities"] = (
        matched_rollup["count_activities"] / total_num_activities_with_sad * 100
        if total_num_activities_with_sad else 0.0
    )
    matched_rollup["percentage_items"] = (
        matched_rollup["count_items"] / total_num_items_with_sad * 100
        if total_num_items_with_sad else 0.0
    )
    unmatched_out["percentage_items"] = (
        unmatched_out["count_items"] / total_num_items_without_sad * 100
        if total_num_items_without_sad else 0.0
    )

    num_sad = int(df_se["sport_and_discipline"].count())
    num_sad_matched = int(matched_rollup["sport_and_discipline"].count())
    num_sad_unmatched = num_sad - num_sad_matched
    percentage_sad_matched = (num_sad_matched / num_sad * 100) if num_sad else 0.0
    percentage_sad_unmatched = 100 - percentage_sad_matched

    master = df_se.copy()
    master["is_matched_by_any_feed"] = master["sport_and_discipline"].isin(
        matched_rollup["sport_and_discipline"]
    )

    return SadResult(
        matched=matched_rollup,
        unmatched=unmatched_out,
        master=master,
        unmatched_activities=unmatched_activities,
        num_sad=num_sad,
        num_sad_matched=num_sad_matched,
        num_sad_unmatched=num_sad_unmatched,
        percentage_sad_matched=percentage_sad_matched,
        percentage_sad_unmatched=percentage_sad_unmatched,
        total_num_activities_with_sad=total_num_activities_with_sad,
        total_num_activities_without_sad=total_num_activities_without_sad,
        total_num_items_with_sad=total_num_items_with_sad,
        total_num_items_without_sad=total_num_items_without_sad,
    )
