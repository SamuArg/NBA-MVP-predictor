from pymongo import MongoClient
import datetime
import os
from scripts.Predict import Predict
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGOURI")

client = MongoClient(MONGO_URI)
db = client.get_database("predictions")
collection = db.predictions
CURRENT_SEASON = 2025

def make_prediction():
    predict = Predict(2025)
    data = predict.predict_proba()
    predictions = [{"player": data['Player'][key], "probability": float(data['Proba'][key]), "team": data['Team'][key]} for key in data['Player'].keys()]
    print(predictions)
    return predictions


def save_prediction(predictions):
    """Store predictions with the current date"""
    if not all(isinstance(p, dict) and 'player' in p and 'probability' in p for p in predictions):
        raise ValueError("Each prediction must be a dictionary with 'player' and 'probability' keys")
    
    today = datetime.date.today().isoformat()

    existing_prediction = collection.find_one({"date": today})
    if existing_prediction:
        print(f"Prediction for {today} already exists. Skipping.")
        return
    
    collection.update_one(
        {"date": today, "season": CURRENT_SEASON},
        {"$set": {"predictions": predictions, "date": today, "season": CURRENT_SEASON}},
        upsert=True
    )
    print(f"Prediction for {today} saved.")


def get_prediction_by_date(date):
    """Retrieve prediction by date"""
    result = collection.find_one({"date": date})
    if result:
        return result["predictions"]
    return "Predictions for this date is not available."

def get_latest_prediction():
    """Retrieve the latest prediction"""
    result = collection.find_one(sort=[("date", -1)])
    if result:
        return result["predictions"]
    return "No predictions available."

def get_prediction_by_season(season):
    """Retrieve all predictions for a given season, sorted by date (oldest to newest)."""
    results = collection.find({"season": season}).sort("date", 1)
    predictions = [{ "date": result["date"], "predictions": result["predictions"] } for result in results]
    
    if predictions:
        return predictions
    return f"No predictions available for Season {season}."
    

def main():
    predictions = make_prediction()
    save_prediction(predictions)


if __name__ == "__main__":
    main()