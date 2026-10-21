import pytest
import datetime
from unittest.mock import patch, MagicMock
from scripts.dailyPredictions import (
    get_current_season,
    get_game_date,
    main,
    make_prediction,
    save_current_season_mvps,
    season_has_started,
    update_mvps,
)
import pandas as pd


def test_get_current_season():
    with patch.object(datetime, "datetime", wraps=datetime.datetime) as mock_datetime:
        mock_datetime.now.return_value = datetime.datetime(2025, 5, 1)
        assert get_current_season() == 2025

        mock_datetime.now.return_value = datetime.datetime(2025, 10, 1)
        assert get_current_season() == 2026

        mock_datetime.now.return_value = datetime.datetime(2025, 12, 30)
        assert get_current_season() == 2026


@patch("scripts.dailyPredictions.Scrap")
def test_season_has_started_is_false_before_games(mock_scrap):
    """A 0-0 standings table means the season has not started."""
    mock_scrap.return_value.scrap_standings.return_value = pd.DataFrame(
        {"Year": [2027, 2027], "W": [0, 0], "L": [0, 0]}
    )

    assert season_has_started(2027) is False


@patch("scripts.dailyPredictions.Scrap")
def test_season_has_started_is_true_after_games(mock_scrap):
    """A team with a win or loss means at least one game has been played."""
    mock_scrap.return_value.scrap_standings.return_value = pd.DataFrame(
        {"Year": [2027, 2027], "W": [1, 0], "L": [0, 1]}
    )

    assert season_has_started(2027) is True


@patch("scripts.dailyPredictions.Scrap")
def test_season_has_started_ignores_other_seasons(mock_scrap):
    """Stale standings for another season do not count as a started season."""
    mock_scrap.return_value.scrap_standings.return_value = pd.DataFrame(
        {"Year": [2026, 2026], "W": [10, 8], "L": [5, 9]}
    )

    assert season_has_started(2027) is False


def test_get_game_date_uses_the_previous_utc_day():
    now = datetime.datetime(2025, 5, 2, 17, 0, tzinfo=datetime.timezone.utc)
    with patch("scripts.dailyPredictions.datetime.datetime") as mock_datetime:
        mock_datetime.now.return_value = now
        assert get_game_date() == "2025-05-01"


def test_make_prediction():
    mock_model = MagicMock()
    mock_predict_instance = MagicMock()
    mock_predict_instance.predict.return_value = pd.DataFrame({
        "Player": [
            "Shai Gilgeous-Alexander", "Nikola Jokić", "Donovan Mitchell", "Jayson Tatum",
            "Giannis Antetokounmpo", "Jalen Brunson", "Evan Mobley", "Jalen Williams",
            "Alperen Şengün", "Darius Garland"
        ],
        "Prediction": [43.382759, 37.923771, 7.979124, 6.231991, 3.812191, 0.322651, 0.127538, 0.096359, 0.080305, 0.043306],
        "Team": ["OKC", "DEN", "CLE", "BOS", "MIL", "NYK", "CLE", "OKC", "HOU", "CLE"]
    })
    
    with patch("scripts.dailyPredictions.Predict", return_value=mock_predict_instance):
        predictions = make_prediction(2025, mock_model)
        assert isinstance(predictions, list)
        assert len(predictions) == 10
        assert predictions[0]["player"] == "Shai Gilgeous-Alexander"
        assert predictions[1]["probability"] == 37.923771


@patch("scripts.dailyPredictions.Scrap")
@patch("scripts.dailyPredictions.save_mvps")
def test_update_mvps(mock_save_mvps, mock_scrap):
    mock_scrap_instance = MagicMock()
    mock_scrap.return_value = mock_scrap_instance
    
    mock_mvps_df = pd.DataFrame({
        "Player": ["Player1", "Player2"],
        "Tm": ["Team1", "Team2"],
        "Share": [0.8, 0.2]
    })
    mock_scrap_instance.scrap_mvps.return_value = mock_mvps_df
    
    update_mvps(2025)
    
    mock_scrap.assert_called_once_with(2025, 2025)
    mock_scrap_instance.scrap_mvps.assert_called_once()
    mock_save_mvps.assert_called_once()
    
    call_args = mock_save_mvps.call_args[0]
    mvps_data = call_args[0]
    assert isinstance(mvps_data, list)
    assert len(mvps_data) == 2
    assert mvps_data[0]["player"] == "Player1"
    assert mvps_data[0]["team"] == "Team1"
    assert mvps_data[0]["probability"] == 0.8


@patch("scripts.dailyPredictions.update_mvps")
def test_save_current_season_mvps(mock_update_mvps):
    with patch.object(datetime, "datetime", wraps=datetime.datetime) as mock_datetime:
        mock_datetime.now.return_value = datetime.datetime(2025, 5, 1)
        save_current_season_mvps()
        mock_update_mvps.assert_called_once_with(2025)


@patch("scripts.dailyPredictions.get_game_date", return_value="2025-05-01")
@patch("scripts.dailyPredictions.season_has_started", return_value=True)
@patch("scripts.dailyPredictions.make_prediction")
@patch("scripts.dailyPredictions.save_prediction")
def test_main(
    mock_save_prediction,
    mock_make_prediction,
    mock_season_has_started,
    mock_game_date,
):
    mock_predictions = [{"player": "Player1", "probability": 0.8, "team": "Team1"}]
    mock_make_prediction.return_value = mock_predictions

    with patch("scripts.dailyPredictions.get_current_season", return_value=2025):
        with patch("scripts.dailyPredictions.get_model") as mock_model:
            main()

    mock_season_has_started.assert_called_once_with(2025)
    mock_make_prediction.assert_called_once_with(2025, mock_model())
    mock_save_prediction.assert_called_once_with(mock_predictions, 2025, "2025-05-01")


@patch("scripts.dailyPredictions.get_current_season", return_value=2027)
@patch("scripts.dailyPredictions.make_prediction")
@patch("scripts.dailyPredictions.save_prediction")
@patch("scripts.dailyPredictions.season_has_started", return_value=False)
def test_main_skips_before_the_season_starts(
    mock_season_has_started,
    mock_save_prediction,
    mock_make_prediction,
    mock_current_season,
):
    main()

    mock_season_has_started.assert_called_once_with(2027)
    mock_make_prediction.assert_not_called()
    mock_save_prediction.assert_not_called()
