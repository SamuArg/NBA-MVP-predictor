from pymongo import MongoClient
import datetime
import os
from scripts.Predict import Predict
from scripts.Scrap import Scrap
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGOURI")

client = MongoClient(MONGO_URI)
db = client.get_database("predictions")
pred_collection = db.predictions
ranking_collection = db.ranking
CURRENT_SEASON = 2025


def make_prediction(season):
    predict = Predict(season)
    data = predict.predict_proba()
    predictions = [{"player": data['Player'][key], "probability": float(data['Proba'][key]), "team": data['Team'][key]}
                   for key in data['Player'].keys()]
    print(predictions)
    return predictions


def save_prediction(predictions, season, date):
    """Store predictions with the current date"""
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


def get_prediction_by_date(date):
    """Retrieve prediction by date"""
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


def save_mvps(mvps, season):
    ranking_collection.update_one(
        {"season": season},
        {"$set": {"predictions": mvps}},
        upsert=True
    )


def update_mvps(season):
    scrap = Scrap(season, season)
    mvps = scrap.scrap_mvps()
    mvps = mvps[["Player", "Tm", "Share"]].rename(columns={"Player": "player", "Tm": "team", "Share": "probability"})
    mvps = mvps.to_dict("records")
    save_mvps(mvps, season)


def main():
    predictions = make_prediction(CURRENT_SEASON)
    save_prediction(predictions, CURRENT_SEASON, datetime.date.today().isoformat())


if __name__ == "__main__":
    main()
