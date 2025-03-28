import pytest
from api.app import app
from unittest.mock import patch

@pytest.fixture
def client():
    """Creates a test client for Flask"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("scripts.database.get_prediction_by_date")
def test_get_mvps_by_date(mock_get_prediction_by_date, client):
    """Test /mvps?date=YYYY-MM-DD"""
    mock_get_prediction_by_date.return_value = [
    {
        "player": "Shai Gilgeous-Alexander",
        "probability": 32.632552843214,
        "team": "OKC"
    },
    {
        "player": "Nikola Jokić",
        "probability": 27.9161625507081,
        "team": "DEN"
    },
    {
        "player": "Giannis Antetokounmpo",
        "probability": 11.8496904134937,
        "team": "MIL"
    },
    {
        "player": "LeBron James",
        "probability": 8.39655540530923,
        "team": "LAL"
    },
    {
        "player": "Jayson Tatum",
        "probability": 5.80812753540673,
        "team": "BOS"
    },
    {
        "player": "Karl-Anthony Towns",
        "probability": 3.60935164756957,
        "team": "NYK"
    },
    {
        "player": "Anthony Edwards",
        "probability": 3.09657675610277,
        "team": "MIN"
    },
    {
        "player": "Stephen Curry",
        "probability": 2.87630773610419,
        "team": "GSW"
    },
    {
        "player": "Domantas Sabonis",
        "probability": 2.01302398405807,
        "team": "SAC"
    },
    {
        "player": "Alperen Şengün",
        "probability": 1.80165112803359,
        "team": "HOU"
    }
    ]

    response = client.get("/mvps")
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["player"] == "Shai Gilgeous-Alexander"
    assert len(data) == 10

@patch("scripts.database.get_prediction_by_season")
def test_get_mvps_by_season(mock_get_prediction_by_season, client):
    """Test /mvps?season=2025"""
    mock_get_prediction_by_season.return_value = [
  {
    "date": "2025-03-12",
    "predictions": [
      {
        "player": "Shai Gilgeous-Alexander",
        "probability": 28.6149196624756,
        "team": "OKC"
      },
      {
        "player": "Nikola Jokić",
        "probability": 25.1295528411865,
        "team": "DEN"
      },
      {
        "player": "Jayson Tatum",
        "probability": 10.854887008667,
        "team": "BOS"
      },
      {
        "player": "Giannis Antetokounmpo",
        "probability": 10.1209955215454,
        "team": "MIL"
      },
      {
        "player": "LeBron James",
        "probability": 8.9505786895752,
        "team": "LAL"
      },
      {
        "player": "Stephen Curry",
        "probability": 4.69571590423584,
        "team": "GSW"
      },
      {
        "player": "Domantas Sabonis",
        "probability": 4.24863052368164,
        "team": "SAC"
      },
      {
        "player": "Jalen Brunson",
        "probability": 2.76530933380127,
        "team": "NYK"
      },
      {
        "player": "Tyrese Haliburton",
        "probability": 2.46218490600586,
        "team": "IND"
      },
      {
        "player": "Donovan Mitchell",
        "probability": 2.15722393989563,
        "team": "CLE"
      }
    ]
  },
  {
    "date": "2025-03-13",
    "predictions": [
      {
        "player": "Shai Gilgeous-Alexander",
        "probability": 28.6149196624756,
        "team": "OKC"
      },
      {
        "player": "Nikola Jokić",
        "probability": 25.1295528411865,
        "team": "DEN"
      },
      {
        "player": "Jayson Tatum",
        "probability": 10.854887008667,
        "team": "BOS"
      },
      {
        "player": "Giannis Antetokounmpo",
        "probability": 10.1209955215454,
        "team": "MIL"
      },
      {
        "player": "LeBron James",
        "probability": 8.9505786895752,
        "team": "LAL"
      },
      {
        "player": "Stephen Curry",
        "probability": 4.69571590423584,
        "team": "GSW"
      },
      {
        "player": "Domantas Sabonis",
        "probability": 4.24863052368164,
        "team": "SAC"
      },
      {
        "player": "Jalen Brunson",
        "probability": 2.76530933380127,
        "team": "NYK"
      },
      {
        "player": "Tyrese Haliburton",
        "probability": 2.46218490600586,
        "team": "IND"
      },
      {
        "player": "Donovan Mitchell",
        "probability": 2.15722393989563,
        "team": "CLE"
      }
    ]
  }
  ]

    response = client.get("/mvps?season=2025")
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["date"] == "2025-03-12"
    assert data[0]["predictions"][0]["player"] == "Shai Gilgeous-Alexander"

@patch("scripts.database.get_latest_prediction")
def test_get_latest_mvps(mock_get_latest_prediction, client):
    """Test /mvps with no query params"""
    mock_get_latest_prediction.return_value = [
    {
        "player": "Shai Gilgeous-Alexander",
        "probability": 32.632552843214,
        "team": "OKC"
    },
    {
        "player": "Nikola Jokić",
        "probability": 27.9161625507081,
        "team": "DEN"
    },
    {
        "player": "Giannis Antetokounmpo",
        "probability": 11.8496904134937,
        "team": "MIL"
    },
    {
        "player": "LeBron James",
        "probability": 8.39655540530923,
        "team": "LAL"
    },
    {
        "player": "Jayson Tatum",
        "probability": 5.80812753540673,
        "team": "BOS"
    },
    {
        "player": "Karl-Anthony Towns",
        "probability": 3.60935164756957,
        "team": "NYK"
    },
    {
        "player": "Anthony Edwards",
        "probability": 3.09657675610277,
        "team": "MIN"
    },
    {
        "player": "Stephen Curry",
        "probability": 2.87630773610419,
        "team": "GSW"
    },
    {
        "player": "Domantas Sabonis",
        "probability": 2.01302398405807,
        "team": "SAC"
    },
    {
        "player": "Alperen Şengün",
        "probability": 1.80165112803359,
        "team": "HOU"
    }
    ]

    response = client.get("/mvps")
    assert response.status_code == 200
    data = response.get_json()
    assert data[0]["player"] == "Shai Gilgeous-Alexander"
    assert len(data) == 10

