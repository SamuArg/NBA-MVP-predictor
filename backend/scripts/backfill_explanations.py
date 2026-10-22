"""Backfill SHAP explanations for the final date of completed seasons.

Older predictions were stored without their feature snapshots, so mid-season
dates cannot be explained exactly.  The final date of a completed season can
be recomputed from Basketball Reference's final season totals; we only attach
the explanation when the recomputed top 10 matches the stored prediction.

An explicit ``--season`` may target the current season's latest stored date
too.  The same top-10 comparison still guards against attaching an explanation
that describes different data than the stored prediction.
"""

from __future__ import annotations

import argparse

from .config import get_model
from .dailyPredictions import make_prediction_with_explanations
from .database import get_last_prediction_for_season, get_seasons, save_explanations
from .seasons import get_current_season


# Percentage points.  A tight tolerance makes sure the explanation describes
# the prediction that is actually stored.
PROBABILITY_TOLERANCE = 0.05


def _predictions_match(stored, computed):
    if len(stored) != len(computed):
        return False

    stored_by_player = {
        prediction["player"]: float(prediction["probability"])
        for prediction in stored
    }
    computed_by_player = {
        prediction["player"]: float(prediction["probability"])
        for prediction in computed
    }

    if set(stored_by_player) != set(computed_by_player):
        return False

    return all(
        abs(stored_by_player[player] - computed_by_player[player])
        <= PROBABILITY_TOLERANCE
        for player in stored_by_player
    )


def main():
    parser = argparse.ArgumentParser(
        description="Backfill SHAP explanations for completed seasons."
    )
    parser.add_argument(
        "--season",
        type=int,
        help="Only backfill this season year (e.g. 2026 or the current season).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Recompute and compare without writing to MongoDB.",
    )
    args = parser.parse_args()

    current_season = get_current_season()
    available = [
        entry["season"]
        for entry in get_seasons()
        if entry["season"] is not None
    ]

    if args.season is not None:
        targets = [season for season in available if season == args.season]
    else:
        targets = [season for season in available if season < current_season]

    if not targets:
        print("No seasons are available to backfill.")
        return

    model = get_model()

    for season in sorted(targets):
        last_prediction = get_last_prediction_for_season(season)
        if last_prediction is None:
            print(f"{season}: no stored predictions; skipping.")
            continue

        date = last_prediction["date"]
        print(f"{season}: recomputing predictions for {date}...")

        try:
            predictions, explanations = make_prediction_with_explanations(
                season,
                model,
                raise_on_explanation_error=True,
            )
        except Exception as error:
            print(f"{season}: recomputation failed: {error}")
            continue

        if not _predictions_match(last_prediction["predictions"], predictions):
            print(
                f"{season}: stored predictions for {date} do not match the "
                "recomputed top 10; skipping."
            )
            continue

        if not explanations:
            print(f"{season}: no explanations were generated; skipping.")
            continue

        if args.dry_run:
            print(
                f"{season}: would save {len(explanations)} explanations "
                f"for {date}."
            )
            continue

        matched = save_explanations(explanations, season, date)
        print(
            f"{season}: saved {len(explanations)} explanations for {date} "
            f"(matched documents: {matched})."
        )


if __name__ == "__main__":
    main()
