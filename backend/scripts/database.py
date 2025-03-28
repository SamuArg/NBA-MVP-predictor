from pymongo import MongoClient
from .config import MONGO_URI

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
        list: Predictions for date or error message
    """
    result = pred_collection.find_one({"date": date})
    if result:
        return result["predictions"]
    return "Predictions for this date is not available."


def get_latest_prediction():
    """Retrieve the latest prediction"""
    result = pred_collection.find_one(sort=[("date", -1)])
    if result:
        return result["predictions"]
    return "No predictions available."


def get_prediction_by_season(season):
    """Retrieve all predictions for a given season, sorted by date (oldest to newest)."""
    results = pred_collection.find({"season": season}).sort("date", 1)
    predictions = [{"date": result["date"], "predictions": result["predictions"], "season": result["season"]} for result
                   in results]

    if predictions:
        return predictions
    return f"No predictions available for Season {season}."


def get_ranking_by_season(season):
    results = ranking_collection.find_one({"season": season})
    if results:
        return results["predictions"]


def get_all():
    results = pred_collection.find({}, {"_id": 0})
    return list(results)
