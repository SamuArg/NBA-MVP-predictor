from pymongo import MongoClient
import datetime
from dotenv import load_dotenv
import os
from scripts.Predict import Predict

load_dotenv()

MONGO_URI = os.getenv("MONGOURI")

client = MongoClient(MONGO_URI)
db = client.get_database("predictions")
collection = db.predictions

def make_prediction():
    predict = Predict(2025)
    data = predict.predict_proba()
    predictions = [{"player": data['Player'][key], "probability": float(data['Proba'][key])} for key in data['Player'].keys()]
    return predictions


def save_prediction(predictions):
    """Store predictions with the current date"""
    if not all(isinstance(p, dict) and 'player' in p and 'probability' in p for p in predictions):
        raise ValueError("Each prediction must be a dictionary with 'player' and 'proba' keys")
    
    today = datetime.date.today().isoformat()
    
    collection.update_one(
        {"date": today},
        {"$set": {"predictions": predictions, "date": today}},
        upsert=True
    )
    print(f"Prediction for {today} saved.")


def get_prediction_by_date(date):
    """Retrieve prediction by date"""
    result = collection.find_one({"date": date})
    if result:
        return result["predictions"]
    return None

def main():
    predictions = make_prediction()
    save_prediction(predictions)


if __name__ == "__main__":
    main()