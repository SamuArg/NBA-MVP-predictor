from flask import Flask, jsonify
import datetime
import os
import sys
project_root = os.path.abspath(os.path.join(os.getcwd(), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)
from scripts.dailyPredictions import get_prediction_by_date
from scripts.dailyPredictions import main as daily_predictions
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

@app.route("/mvps", methods=["GET"])
def get_mvps():
    return jsonify(get_prediction_by_date(datetime.date.today().isoformat()))

@app.route("/mvps/<date>", methods=["GET"])
def get_mvps_date(date):
    return jsonify(get_prediction_by_date(date))

def main():
    scheduler = BackgroundScheduler()
    scheduler.add_job(daily_predictions, 'interval', days=1, start_date='2025-03-12 12:00:00', name='daily_prediction_job')
    scheduler.start()
    app.run()
    

if __name__ == "__main__":
    main()