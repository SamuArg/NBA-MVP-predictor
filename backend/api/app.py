from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from scripts.dailyPredictions import get_prediction_by_date, get_latest_prediction, get_prediction_by_season, get_all, \
    get_ranking_by_season, get_current_season
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

CORS(app, resources={
    r"/*": {"origins": ["https://nba-mvp-predictions.netlify.app"]}})


@app.route("/mvps", methods=["GET"])
def get_mvps():
    date = request.args.get("date")  # Query param: ?date=YYYY-MM-DD
    season = request.args.get("season")  # Query param: ?season=YYYY
    if date:
        return jsonify(get_prediction_by_date(date))
    elif season:
        return jsonify(get_prediction_by_season(int(season)))

    return jsonify(get_latest_prediction())


@app.route("/", methods=["GET"])
def get_all_predictions():
    return jsonify(get_all())


@app.route("/ranking", methods=["GET"])
def get_ranking():
    season = request.args.get("season")
    if season:
        return jsonify(get_ranking_by_season(int(season)))


@app.route("/season", methods=["GET"])
def get_season():
    return jsonify(get_current_season())


if __name__ == "__main__":
    app.run()
