import sys
from unittest.mock import patch

import pytest

from scripts import backfill_explanations
from scripts.backfill_explanations import _predictions_match


def _predictions(*rows):
    return [
        {"player": player, "probability": probability}
        for player, probability in rows
    ]


def test_predictions_match_with_tiny_probability_drift():
    stored = _predictions(("Player A", 30.0), ("Player B", 20.0))
    computed = _predictions(("Player B", 20.04), ("Player A", 29.98))

    assert _predictions_match(stored, computed) is True


def test_predictions_match_rejects_large_probability_drift():
    stored = _predictions(("Player A", 30.0), ("Player B", 20.0))
    computed = _predictions(("Player A", 30.2), ("Player B", 20.0))

    assert _predictions_match(stored, computed) is False


def test_predictions_match_rejects_different_players():
    stored = _predictions(("Player A", 30.0), ("Player B", 20.0))
    computed = _predictions(("Player A", 30.0), ("Player C", 20.0))

    assert _predictions_match(stored, computed) is False


def test_predictions_match_rejects_different_lengths():
    stored = _predictions(("Player A", 30.0), ("Player B", 20.0))
    computed = _predictions(("Player A", 30.0))

    assert _predictions_match(stored, computed) is False


def test_default_backfill_skips_training_era_seasons():
    seasons = [{"season": year} for year in (2023, 2024, 2025, 2026, 2027)]

    with patch.object(
        backfill_explanations, "get_current_season", return_value=2027
    ), patch.object(
        backfill_explanations, "get_seasons", return_value=seasons
    ), patch.object(
        backfill_explanations, "get_model", return_value=object()
    ), patch.object(
        backfill_explanations,
        "get_last_prediction_for_season",
        return_value=None,
    ) as get_last, patch.object(
        sys, "argv", ["backfill_explanations"]
    ):
        backfill_explanations.main()

    assert [call.args[0] for call in get_last.call_args_list] == [2025, 2026]


def test_default_backfill_skips_model_loading_when_no_eligible_seasons():
    seasons = [{"season": 2024}]

    with patch.object(
        backfill_explanations, "get_current_season", return_value=2027
    ), patch.object(
        backfill_explanations, "get_seasons", return_value=seasons
    ), patch.object(
        backfill_explanations, "get_model"
    ) as get_model, patch.object(
        sys, "argv", ["backfill_explanations"]
    ):
        backfill_explanations.main()

    get_model.assert_not_called()


@pytest.mark.parametrize("season", [1981, 2023, 2024])
def test_training_era_season_is_rejected(season):
    with patch.object(
        sys, "argv", ["backfill_explanations", "--season", str(season)]
    ), patch.object(
        backfill_explanations, "get_current_season"
    ) as get_current, patch.object(
        backfill_explanations, "get_seasons"
    ) as get_seasons:
        with pytest.raises(SystemExit) as error:
            backfill_explanations.main()

    assert error.value.code == 2
    get_current.assert_not_called()
    get_seasons.assert_not_called()


@pytest.mark.parametrize("season", [2025, 2026, 2027])
def test_explicit_post_training_season_is_allowed(season):
    with patch.object(
        sys, "argv", ["backfill_explanations", "--season", str(season)]
    ), patch.object(
        backfill_explanations, "get_current_season", return_value=2027
    ), patch.object(
        backfill_explanations,
        "get_seasons",
        return_value=[{"season": season}],
    ), patch.object(
        backfill_explanations, "get_model", return_value=object()
    ), patch.object(
        backfill_explanations,
        "get_last_prediction_for_season",
        return_value=None,
    ) as get_last:
        backfill_explanations.main()

    get_last.assert_called_once_with(season)
