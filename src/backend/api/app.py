from flask import Flask, jsonify, request
import datetime
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)
from scripts.dailyPredictions import get_prediction_by_date
from scripts.dailyPredictions import main as daily_predictions
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

@app.route("/mvps", methods=["GET"])
def get_mvps():
    return jsonify(get_prediction_by_date(datetime.date.today().isoformat()))

@app.route("/mvps/<date>", methods=["GET"])
def get_mvps_date(date):
    return jsonify(get_prediction_by_date(date))

@app.route("/daily_predictions", methods=["POST"])
def make_daily_predictions():
    api_key = request.headers.get('Authorization')
    if api_key != f"Bearer {API_KEY}":
        raise PermissionError("Invalid API key")
    daily_predictions()
    

if __name__ == "__main__":
    app.run()