from flask import Flask, jsonify
import datetime
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)
from scripts.dailyPredictions import get_prediction_by_date
from scripts.dailyPredictions import main as daily_predictions

app = Flask(__name__)

@app.route("/mvps", methods=["GET"])
def get_mvps():
    return jsonify(get_prediction_by_date(datetime.date.today().isoformat()))

@app.route("/mvps/<date>", methods=["GET"])
def get_mvps_date(date):
    return jsonify(get_prediction_by_date(date))

@app.route("/daily_predictions", methods=["POST"])
def make_daily_predictions():
    daily_predictions()
    

if __name__ == "__main__":
    app.run()