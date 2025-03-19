from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)
from scripts.dailyPredictions import get_prediction_by_date, get_latest_prediction, get_prediction_by_season
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

CORS(app)  # Allow all origins (for development)

@app.route("/mvps", methods=["GET"])
def get_mvps():
    date = request.args.get("date")  # Query param: ?date=YYYY-MM-DD
    season = request.args.get("season")  # Query param: ?season=YYYY
    if date:
        return jsonify(get_prediction_by_date(date))
    elif season:
        return jsonify(get_prediction_by_season(int(season)))
    
    return jsonify(get_latest_prediction())
    

if __name__ == "__main__":
    app.run()