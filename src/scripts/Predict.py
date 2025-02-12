from joblib import load
import pandas as pd
from scripts.Processed import Processed
from scripts.Scrap import Scrap
from sklearn.preprocessing import MinMaxScaler

class Predict:
    def __init__(self, year: int):
        self.year = year
        self.data = self.get_data(year)

    def predict(self) -> pd.DataFrame:
        model = load('../models/model.joblib')
        X = self.data.drop(columns=["Year", "Player", "Team"])
        predictions = model.predict(X)
        preds = self.data.copy()
        preds["Prediction"] = predictions
        preds = preds[["Player", "Prediction"]].sort_values(by="Prediction", ascending=False)[0:10]
        return preds

    def predict_proba(self) -> pd.DataFrame:
        model = load('../models/model.joblib')
        X = self.data.drop(columns=["Year", "Player", "Team"])
        predictions = model.predict(X)
        scaler = MinMaxScaler()
        predictions = scaler.fit_transform(predictions.reshape(-1, 1)).flatten()
        top_10_indices = predictions.argsort()[-10:][::-1]
        top_10_predictions = predictions[top_10_indices]
        top_10_predictions = top_10_predictions / top_10_predictions.sum() * 100
        proba = self.data.copy()
        proba["Proba"] = 0.0
        proba.loc[top_10_indices, "Proba"] = top_10_predictions
        proba = proba[["Player", "Proba"]].sort_values(by="Proba", ascending=False)[0:10]
        return proba

    def get_data(self, year=2025) -> pd.DataFrame:
        scrap = Scrap(year, year)
        advanced = scrap.scrap_advanced()
        standings = scrap.scrap_standings()
        per_game = scrap.scrap_per_game()
        processed = Processed(None, advanced=advanced, standings=standings, per_game=per_game)
        data = processed.process_without_mvps()
        return data