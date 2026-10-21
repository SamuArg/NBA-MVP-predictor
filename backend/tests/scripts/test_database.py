from unittest.mock import MagicMock, patch

from scripts import database


def test_get_seasons_builds_catalogue():
    """Season metadata is grouped, sorted and annotated with ranking info."""
    pred_collection = MagicMock()
    pred_collection.aggregate.return_value = [
        {
            "_id": 2026,
            "predictions": 185,
            "firstDate": "2025-10-24",
            "lastDate": "2026-04-30",
        },
        {
            "_id": 2025,
            "predictions": 50,
            "firstDate": "2025-03-12",
            "lastDate": "2025-04-30",
        },
    ]
    ranking_collection = MagicMock()
    ranking_collection.distinct.return_value = [2025]

    with patch.object(database, "pred_collection", pred_collection), patch.object(
        database, "ranking_collection", ranking_collection
    ):
        seasons = database.get_seasons()

    assert [entry["season"] for entry in seasons] == [2026, 2025]
    assert seasons[0]["predictions"] == 185
    assert seasons[0]["firstDate"] == "2025-10-24"
    assert seasons[0]["hasRanking"] is False
    assert seasons[1]["hasRanking"] is True


def test_get_seasons_skips_missing_season_values():
    """Documents without a season are ignored."""
    pred_collection = MagicMock()
    pred_collection.aggregate.return_value = [
        {"_id": None, "predictions": 1, "firstDate": "x", "lastDate": "x"},
        {
            "_id": 2025,
            "predictions": 50,
            "firstDate": "2025-03-12",
            "lastDate": "2025-04-30",
        },
    ]
    ranking_collection = MagicMock()
    ranking_collection.distinct.return_value = []

    with patch.object(database, "pred_collection", pred_collection), patch.object(
        database, "ranking_collection", ranking_collection
    ):
        seasons = database.get_seasons()

    assert len(seasons) == 1
    assert seasons[0]["season"] == 2025


def test_lookups_return_none_when_missing():
    """Lookups use None rather than English error strings."""
    pred_collection = MagicMock()
    pred_collection.find_one.return_value = None
    ranking_collection = MagicMock()
    ranking_collection.find_one.return_value = None

    with patch.object(database, "pred_collection", pred_collection), patch.object(
        database, "ranking_collection", ranking_collection
    ):
        assert database.get_prediction_by_date("2027-01-01") is None
        assert database.get_latest_prediction() is None
        assert database.get_ranking_by_season(2027) is None
