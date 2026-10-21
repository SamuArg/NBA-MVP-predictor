from .Predict import Predict
from .Scrap import Scrap
import datetime
from .config import get_model
from .database import save_mvps, save_prediction
from .seasons import get_current_season


def make_prediction(season, model, normalize=True):
    """
    Generate MVP predictions for a season.

    Args:
        season (int): NBA season year
        model: Trained model
        normalize (bool): Normalize predictions to percentages

    Returns:
        list: Top 10 MVP candidates with predictions
    """
    predict = Predict(season, get_model())
    data = predict.predict(normalize=normalize)
    predictions = [
        {"player": data['Player'][key], "probability": float(data['Prediction'][key]), "team": data['Team'][key]}
        for key in data['Player'].keys()]
    print(predictions)
    return predictions


def update_mvps(season):
    """
    Update MVP voting results for a season.

    Args:
        season (int): NBA season year
    """
    scrap = Scrap(season, season)
    mvps = scrap.scrap_mvps()
    mvps = mvps[["Player", "Tm", "Share"]].rename(columns={"Player": "player", "Tm": "team", "Share": "probability"})
    mvps = mvps.to_dict("records")
    save_mvps(mvps, season)


def save_current_season_mvps():
    current_season = get_current_season()
    update_mvps(current_season)


def main():
    predictions = make_prediction(get_current_season(), get_model())
    save_prediction(predictions, get_current_season(), datetime.date.today().isoformat())


if __name__ == "__main__":
    main()
