import pandas as pd
from scripts.Processed import Processed, align_model_features
from scripts.Scrap import Scrap
from sklearn.preprocessing import MinMaxScaler


class Predict:
    """
    Makes MVP predictions using a trained model.
    
    Attributes:
        year (int): NBA season year
        data (pd.DataFrame): Processed player statistics
        model: Trained model for predictions
    """

    def __init__(self, year: int, model):
        """
        Args:
            year: NBA season year to predict
            model: Trained model instance
        """
        self.year = year
        self.model = model
        self.feature_matrix = None
        self.raw_data = None
        self.data = self.get_data(year)

    def predict(self, normalize=False) -> pd.DataFrame:
        """
        Make MVP predictions for the current season.

        Args:
            normalize (bool): Whether to normalize predictions to percentages

        Returns:
            pd.DataFrame: Top 10 MVP candidates with predictions
        """
        X = align_model_features(self.data).reset_index(drop=True)
        self.feature_matrix = X
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

    def explain(self, predictions):
        """Return SHAP explanations for the supplied prediction rows.

        ``predict()`` must be called first so the standardized feature matrix is
        available.  The explainer lives in ``scripts.explain`` and is imported
        lazily so the production API image never loads SHAP.
        """
        from scripts.explain import explain_predictions

        if self.feature_matrix is None:
            raise RuntimeError("predict() must be called before explain()")
        if not predictions:
            return []

        positions_by_player = {}
        for position, player in enumerate(self.data["Player"]):
            positions_by_player.setdefault(player, position)

        positions = []
        for prediction in predictions:
            position = positions_by_player.get(prediction["player"])
            if position is not None:
                positions.append(position)

        if not positions:
            return []

        features = self.feature_matrix.iloc[positions].reset_index(drop=True)
        raw_features = self.raw_data.iloc[positions].reset_index(drop=True)
        rows = explain_predictions(
            self.model,
            features,
            raw_features,
            background=self.feature_matrix,
        )

        rows_by_player = {row["player"]: row for row in rows}
        explanations = []
        for prediction in predictions:
            row = rows_by_player.get(prediction["player"])
            if row is None:
                continue
            explanations.append(
                {
                    **row,
                    "team": prediction.get("team", row.get("team", "")),
                    "probability": prediction.get("probability"),
                }
            )
        return explanations

    def predict_proba(self) -> pd.DataFrame:
        return self.predict(normalize=True)

    def get_data(self, year=2025) -> pd.DataFrame:
        scrap = Scrap(year, year)
        advanced = scrap.scrap_advanced()
        standings = scrap.scrap_standings()
        per_game = scrap.scrap_per_game()
        processed = Processed(None, advanced=advanced, standings=standings, per_game=per_game)
        data = processed.process_without_mvps()
        self.raw_data = processed.raw_processed
        return data
