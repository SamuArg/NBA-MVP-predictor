import pytest
import datetime
from unittest.mock import patch, MagicMock
from scripts.dailyPredictions import make_prediction, update_mvps, get_current_season, save_current_season_mvps, main
import pandas as pd


def test_get_current_season():
    with patch.object(datetime, "datetime", wraps=datetime.datetime) as mock_datetime:
        mock_datetime.now.return_value = datetime.datetime(2025, 5, 1)
        assert get_current_season() == 2025

        mock_datetime.now.return_value = datetime.datetime(2025, 10, 1)
        assert get_current_season() == 2026

        mock_datetime.now.return_value = datetime.datetime(2025, 12, 30)
        assert get_current_season() == 2026


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


@patch("scripts.dailyPredictions.make_prediction")
@patch("scripts.dailyPredictions.save_prediction")
def test_main(mock_save_prediction, mock_make_prediction):
    mock_predictions = [{"player": "Player1", "probability": 0.8, "team": "Team1"}]
    mock_make_prediction.return_value = mock_predictions

    with patch("scripts.dailyPredictions.MODEL") as mock_model:
        with patch("datetime.date") as mock_date:
            mock_date.today.return_value = datetime.date(2025, 5, 1)
            mock_date.today().isoformat.return_value = "2025-05-01"

            main()

            mock_make_prediction.assert_called_once_with(2025, mock_model)
            mock_save_prediction.assert_called_once_with(mock_predictions, 2025, "2025-05-01")
