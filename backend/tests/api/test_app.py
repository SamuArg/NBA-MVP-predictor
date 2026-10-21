from unittest.mock import patch

import pytest

from api.app import app

PREDICTIONS = [
    {"player": "Shai Gilgeous-Alexander", "probability": 32.63, "team": "OKC"},
    {"player": "Nikola Jokić", "probability": 27.91, "team": "DEN"},
    {"player": "Giannis Antetokounmpo", "probability": 11.84, "team": "MIL"},
]

SEASON_PREDICTIONS = [
    {
        "date": "2025-03-12",
        "season": 2025,
        "predictions": PREDICTIONS,
    },
    {
        "date": "2025-03-13",
        "season": 2025,
        "predictions": PREDICTIONS,
    },
]

RANKING = [
    {"player": "Shai Gilgeous-Alexander", "probability": "0.913", "team": "OKC"},
    {"player": "Nikola Jokić", "probability": "0.787", "team": "DEN"},
]

SEASONS = [
    {
        "season": 2025,
        "predictions": 50,
        "firstDate": "2025-03-12",
        "lastDate": "2025-04-30",
        "hasRanking": True,
    }
]


@pytest.fixture
def client():
    """Creates a test client for Flask"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@patch("scripts.database.get_prediction_by_date")
def test_get_mvps_by_date(mock_get_prediction_by_date, client):
    """Test /mvps?date=YYYY-MM-DD"""
    mock_get_prediction_by_date.return_value = PREDICTIONS

    response = client.get("/mvps?date=2025-03-12")

    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["player"] == "Shai Gilgeous-Alexander"
    assert len(data) == 3
    mock_get_prediction_by_date.assert_called_once_with("2025-03-12")


@patch("scripts.database.get_prediction_by_date")
def test_get_mvps_by_date_not_found(mock_get_prediction_by_date, client):
    """Test /mvps?date=YYYY-MM-DD when the date has no data"""
    mock_get_prediction_by_date.return_value = None

    response = client.get("/mvps?date=1999-01-01")

    assert response.status_code == 404
    assert "not available" in response.get_json()["error"]


@patch("scripts.database.get_prediction_by_season")
def test_get_mvps_by_season(mock_get_prediction_by_season, client):
    """Test /mvps?season=2025"""
    mock_get_prediction_by_season.return_value = SEASON_PREDICTIONS

    response = client.get("/mvps?season=2025")

    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["date"] == "2025-03-12"
    assert data[0]["predictions"][0]["player"] == "Shai Gilgeous-Alexander"
    mock_get_prediction_by_season.assert_called_once_with(2025)


@patch("scripts.database.get_prediction_by_season")
def test_get_mvps_by_season_not_found(mock_get_prediction_by_season, client):
    """Test a season without predictions returns a JSON 404"""
    mock_get_prediction_by_season.return_value = None

    response = client.get("/mvps?season=2027")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["season"] == 2027
    assert "No predictions available" in payload["error"]


def test_get_mvps_by_invalid_season(client):
    """Test a non-numeric season is rejected"""
    response = client.get("/mvps?season=abc")

    assert response.status_code == 400
    assert "Season must be a number" in response.get_json()["error"]


@patch("scripts.database.get_latest_prediction")
def test_get_latest_mvps(mock_get_latest_prediction, client):
    """Test /mvps with no query params"""
    mock_get_latest_prediction.return_value = PREDICTIONS

    response = client.get("/mvps")

    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["player"] == "Shai Gilgeous-Alexander"
    assert len(data) == 3


@patch("scripts.database.get_latest_prediction")
def test_get_latest_mvps_not_found(mock_get_latest_prediction, client):
    """Test /mvps when the database is empty"""
    mock_get_latest_prediction.return_value = None

    response = client.get("/mvps")

    assert response.status_code == 404


@patch("scripts.database.get_all")
def test_get_all_predictions(mock_get_all, client):
    """Test the root endpoint"""
    mock_get_all.return_value = SEASON_PREDICTIONS

    response = client.get("/")

    assert response.status_code == 200
    assert len(response.get_json()) == 2


@patch("scripts.database.get_ranking_by_season")
def test_get_ranking(mock_get_ranking_by_season, client):
    """Test /ranking?season=2025"""
    mock_get_ranking_by_season.return_value = RANKING

    response = client.get("/ranking?season=2025")

    assert response.status_code == 200
    assert response.get_json()[0]["team"] == "OKC"
    mock_get_ranking_by_season.assert_called_once_with(2025)


@patch("scripts.database.get_ranking_by_season")
def test_get_ranking_not_found(mock_get_ranking_by_season, client):
    """Test /ranking when voting results are missing"""
    mock_get_ranking_by_season.return_value = None

    response = client.get("/ranking?season=2027")

    assert response.status_code == 404
    assert response.get_json()["season"] == 2027


def test_get_ranking_requires_season(client):
    """Test /ranking without a season"""
    response = client.get("/ranking")

    assert response.status_code == 400


@patch("api.app.get_current_season")
def test_get_season(mock_get_current_season, client):
    """Test /season"""
    mock_get_current_season.return_value = 2027

    response = client.get("/season")

    assert response.status_code == 200
    assert response.get_json() == 2027


@patch("scripts.database.get_seasons")
@patch("api.app.get_current_season")
def test_get_seasons(mock_get_current_season, mock_get_seasons, client):
    """Test /seasons returns the catalogue and latest season"""
    mock_get_current_season.return_value = 2027
    mock_get_seasons.return_value = SEASONS

    response = client.get("/seasons")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["current"] == 2027
    assert payload["latest"] == 2025
    assert payload["seasons"][0]["hasRanking"] is True


@patch("scripts.database.get_seasons")
@patch("api.app.get_current_season")
def test_get_seasons_empty(mock_get_current_season, mock_get_seasons, client):
    """Test /seasons when no predictions exist"""
    mock_get_current_season.return_value = 2027
    mock_get_seasons.return_value = []

    response = client.get("/seasons")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["latest"] is None
    assert payload["seasons"] == []


def test_health(client):
    """Test /health"""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_cors_allows_netlify_origin(client):
    """Test the production frontend origin is still allowed"""
    response = client.get(
        "/health", headers={"Origin": "https://nba-mvp-predictions.netlify.app"}
    )

    assert (
        response.headers["Access-Control-Allow-Origin"]
        == "https://nba-mvp-predictions.netlify.app"
    )
