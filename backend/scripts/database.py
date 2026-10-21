import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGOURI")

client = MongoClient(MONGO_URI)
db = client.get_database("predictions")
pred_collection = db.predictions
ranking_collection = db.ranking


def save_prediction(predictions, season, date):
    """
    Store MVP predictions in MongoDB.

    Args:
        predictions (list): List of prediction dictionaries
        season (int): NBA season year
        date (str): ISO format date string

    Raises:
        ValueError: If predictions format is invalid
    """
    if not all(isinstance(p, dict) and 'player' in p and 'probability' in p for p in predictions):
        raise ValueError("Each prediction must be a dictionary with 'player' and 'probability' keys")

    existing_prediction = pred_collection.find_one({"date": date})
    if existing_prediction:
        print(f"Prediction for {date} already exists. Skipping.")
        return

    pred_collection.update_one(
        {"date": date, "season": season},
        {"$set": {"predictions": predictions, "date": date, "season": season}},
        upsert=True
    )
    print(f"Prediction for {date} saved.")


def save_mvps(mvps, season):
    ranking_collection.update_one(
        {"season": season},
        {"$set": {"predictions": mvps}},
        upsert=True
    )


def get_prediction_by_date(date):
    """
    Get predictions for specific date.

    Args:
        date (str): ISO format date string

    Returns:
        list | None: Predictions for the date, or None when unavailable
    """
    result = pred_collection.find_one({"date": date})
    if result:
        return result["predictions"]
    return None


def get_latest_prediction():
    """
    Retrieve the latest prediction.

    Returns:
        list | None: Predictions of the most recent day, or None when unavailable
    """
    result = pred_collection.find_one(sort=[("date", -1)])
    if result:
        return result["predictions"]
    return None


def get_prediction_by_season(season):
    """
    Retrieve all predictions for a given season, sorted by date (oldest to newest).

    Returns:
        list | None: One entry per date, or None when the season has no predictions
    """
    results = pred_collection.find({"season": season}).sort("date", 1)
    predictions = [
        {
            "date": result["date"],
            "predictions": result["predictions"],
            "season": result["season"],
        }
        for result in results
    ]

    return predictions or None


def get_ranking_by_season(season):
    """
    Retrieve the official MVP voting results for a season.

    Returns:
        list | None: Ranking entries, or None when unavailable
    """
    results = ranking_collection.find_one({"season": season})
    if results:
        return results["predictions"]
    return None


def get_seasons():
    """
    Build a lightweight catalogue of every season that has predictions.

    Returns:
        list: Season metadata sorted from newest to oldest
    """
    pipeline = [
        {
            "$group": {
                "_id": "$season",
                "predictions": {"$sum": 1},
                "firstDate": {"$min": "$date"},
                "lastDate": {"$max": "$date"},
            }
        },
        {"$sort": {"_id": -1}},
    ]

    rows = list(pred_collection.aggregate(pipeline))
    ranking_seasons = set(ranking_collection.distinct("season"))

    return [
        {
            "season": row["_id"],
            "predictions": row["predictions"],
            "firstDate": row["firstDate"],
            "lastDate": row["lastDate"],
            "hasRanking": row["_id"] in ranking_seasons,
        }
        for row in rows
        if row["_id"] is not None
    ]


def get_all():
    results = pred_collection.find({}, {"_id": 0})
    return list(results)
