from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from scripts import database
from scripts.seasons import get_current_season

load_dotenv()

DEFAULT_ALLOWED_ORIGINS = [
    "https://nba-mvp-predictions.netlify.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
    r"https://.*--nba-mvp-predictions\.netlify\.app",
]


def get_allowed_origins():
    """Read extra CORS origins from the environment, keeping the defaults."""
    extra_origins = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    # dict.fromkeys keeps the order while removing duplicates
    return list(dict.fromkeys(DEFAULT_ALLOWED_ORIGINS + extra_origins))


app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": get_allowed_origins()}})


def error_response(message, status=404, **extra):
    """Return a consistent JSON error payload."""
    payload = {"error": message, **extra}
    return jsonify(payload), status


def parse_season(raw_season):
    """Convert a season query parameter to an int, or return None."""
    try:
        return int(raw_season)
    except (TypeError, ValueError):
        return None


@app.after_request
def add_cache_headers(response):
    """Cache the slowly-changing reference endpoints for a short while."""
    if request.method == "GET":
        if request.path in ("/seasons", "/season", "/ranking"):
            response.headers["Cache-Control"] = "public, max-age=60"
        elif request.path == "/health":
            response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/mvps", methods=["GET"])
def get_mvps():
    date = request.args.get("date")  # Query param: ?date=YYYY-MM-DD
    season = request.args.get("season")  # Query param: ?season=YYYY
    if date:
        predictions = database.get_prediction_by_date(date)
        if predictions is None:
            return error_response(
                f"Predictions for {date} are not available.", date=date
            )
        return jsonify(predictions)

    if season:
        season_number = parse_season(season)
        if season_number is None:
            return error_response("Season must be a number.", 400)
        predictions = database.get_prediction_by_season(season_number)
        if predictions is None:
            return error_response(
                f"No predictions available for season {season_number}.",
                season=season_number,
            )
        return jsonify(predictions)

    latest = database.get_latest_prediction()
    if latest is None:
        return error_response("No predictions available.")
    return jsonify(latest)


@app.route("/", methods=["GET"])
def get_all_predictions():
    return jsonify(database.get_all())


@app.route("/ranking", methods=["GET"])
def get_ranking():
    season = request.args.get("season")
    season_number = parse_season(season)
    if season_number is None:
        return error_response("A valid season query parameter is required.", 400)

    ranking = database.get_ranking_by_season(season_number)
    if ranking is None:
        return error_response(
            f"No MVP voting results available for season {season_number}.",
            season=season_number,
        )
    return jsonify(ranking)


@app.route("/season", methods=["GET"])
def get_season():
    return jsonify(get_current_season())


@app.route("/seasons", methods=["GET"])
def get_seasons():
    seasons = database.get_seasons()
    latest = max((entry["season"] for entry in seasons), default=None)
    return jsonify(
        {
            "current": get_current_season(),
            "latest": latest,
            "seasons": seasons,
        }
    )


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run()
