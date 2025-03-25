import pandas as pd
from scripts.Processed import Processed
from scripts.Scrap import Scrap
from sklearn.preprocessing import MinMaxScaler


class Predict:
    def __init__(self, year: int, model):
        self.year = year
        self.data = self.get_data(year)
        self.model = model

    def predict(self, normalize=False) -> pd.DataFrame:
        X = self.data.drop(columns=["Year", "Player", "Team"]).reset_index(drop=True)
        predictions = self.model.predict(X)
        preds = self.data.copy()

        if normalize:
            scaler = MinMaxScaler()
            predictions = scaler.fit_transform(predictions.reshape(-1, 1)).flatten()
            top_10_indices = predictions.argsort()[-10:][::-1]
            predictions[top_10_indices] = predictions[top_10_indices] / predictions[top_10_indices].sum() * 100

        preds.loc[:, "Prediction"] = predictions
        preds = preds[["Player", "Prediction", "Team"]].sort_values(by="Prediction", ascending=False)[0:10]
        return preds

    def predict_proba(self) -> pd.DataFrame:
        return self.predict(normalize=True)

    def get_data(self, year=2025) -> pd.DataFrame:
        scrap = Scrap(year, year)
        advanced = scrap.scrap_advanced()
        standings = scrap.scrap_standings()
        per_game = scrap.scrap_per_game()
        processed = Processed(None, advanced=advanced, standings=standings, per_game=per_game)
        data = processed.process_without_mvps()
        return data
