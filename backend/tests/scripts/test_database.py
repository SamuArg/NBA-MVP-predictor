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
        assert database.get_explanation("2027-01-01", "Player") is None


PREDICTIONS = [
    {"player": "Shai Gilgeous-Alexander", "probability": 32.63, "team": "OKC"},
    {"player": "Nikola Jokić", "probability": 27.91, "team": "DEN"},
]

EXPLANATIONS = [
    {
        "player": "Shai Gilgeous-Alexander",
        "team": "OKC",
        "probability": 32.63,
        "baseValue": 0.1,
        "outputValue": 0.7,
        "features": [{"name": "PTS", "contribution": 0.2}],
    }
]


def test_save_prediction_stores_explanations():
    """Explanations live beside the predictions in the same date document."""
    pred_collection = MagicMock()
    pred_collection.find_one.return_value = None

    with patch.object(database, "pred_collection", pred_collection):
        database.save_prediction(
            PREDICTIONS,
            2025,
            "2025-03-12",
            explanations=EXPLANATIONS,
        )

    query, update = pred_collection.update_one.call_args.args
    assert query == {"date": "2025-03-12", "season": 2025}
    assert update["$set"]["predictions"] == PREDICTIONS
    assert update["$set"]["explanations"] == EXPLANATIONS
    assert pred_collection.update_one.call_args.kwargs == {"upsert": True}


def test_save_explanations_updates_an_existing_document():
    """The backfill path updates explanations without touching predictions."""
    pred_collection = MagicMock()
    pred_collection.update_one.return_value.matched_count = 1

    with patch.object(database, "pred_collection", pred_collection):
        matched = database.save_explanations(
            EXPLANATIONS, 2025, "2025-03-12"
        )

    assert matched == 1
    query, update = pred_collection.update_one.call_args.args
    assert query == {"date": "2025-03-12", "season": 2025}
    assert update == {"$set": {"explanations": EXPLANATIONS}}


def test_get_explanation_finds_a_player():
    pred_collection = MagicMock()
    pred_collection.find_one.return_value = {"explanations": EXPLANATIONS}

    with patch.object(database, "pred_collection", pred_collection):
        explanation = database.get_explanation(
            "2025-03-12", "Shai Gilgeous-Alexander", 2025
        )

    assert explanation == EXPLANATIONS[0]
    pred_collection.find_one.assert_called_once_with(
        {"date": "2025-03-12", "season": 2025}
    )


def test_get_explanation_returns_none_for_unknown_player():
    pred_collection = MagicMock()
    pred_collection.find_one.return_value = {"explanations": EXPLANATIONS}

    with patch.object(database, "pred_collection", pred_collection):
        assert database.get_explanation("2025-03-12", "Someone Else") is None


def test_get_last_prediction_for_season():
    pred_collection = MagicMock()
    pred_collection.find_one.return_value = {
        "date": "2025-04-30",
        "season": 2025,
        "predictions": PREDICTIONS,
    }

    with patch.object(database, "pred_collection", pred_collection):
        latest = database.get_last_prediction_for_season(2025)

    assert latest == {
        "date": "2025-04-30",
        "season": 2025,
        "predictions": PREDICTIONS,
    }
    pred_collection.find_one.assert_called_once_with(
        {"season": 2025},
        {"_id": 0, "date": 1, "season": 1, "predictions": 1},
        sort=[("date", -1)],
    )


def test_prediction_reads_do_not_fetch_explanations():
    """Date, latest and season reads only project the fields they return."""
    pred_collection = MagicMock()
    pred_collection.find_one.return_value = {"predictions": PREDICTIONS}
    pred_collection.find.return_value.sort.return_value = []

    with patch.object(database, "pred_collection", pred_collection):
        assert database.get_prediction_by_date("2025-04-30") == PREDICTIONS
        pred_collection.find_one.assert_called_once_with(
            {"date": "2025-04-30"},
            {"_id": 0, "predictions": 1},
        )

        pred_collection.reset_mock()
        assert database.get_latest_prediction() == PREDICTIONS
        pred_collection.find_one.assert_called_once_with(
            {},
            {"_id": 0, "predictions": 1},
            sort=[("date", -1)],
        )

        assert database.get_prediction_by_season(2025) is None
        pred_collection.find.assert_called_once_with(
            {"season": 2025},
            {"_id": 0, "date": 1, "season": 1, "predictions": 1},
        )
        pred_collection.find.return_value.sort.assert_called_once_with("date", 1)


def test_get_all_excludes_explanations_from_the_bulk_payload():
    pred_collection = MagicMock()
    documents = [
        {
            "date": "2025-04-30",
            "season": 2025,
            "predictions": PREDICTIONS,
        }
    ]
    pred_collection.find.return_value = documents

    with patch.object(database, "pred_collection", pred_collection):
        result = database.get_all()

    assert result == documents
    pred_collection.find.assert_called_once_with(
        {}, {"_id": 0, "explanations": 0}
    )
