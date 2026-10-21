from .Predict import Predict
from .Scrap import Scrap
import datetime
from urllib.error import HTTPError

import pandas as pd

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
    predict = Predict(season, model)
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


def season_has_started(season):
    """
    Return True once the given season has at least one completed regular-season game.

    Basketball Reference may not have a standings table for an upcoming season.
    A 404 or an empty/incomplete table therefore means the season has not started.
    """
    try:
        standings = Scrap(season, season).scrap_standings()
    except HTTPError as error:
        if error.code == 404:
            return False
        raise
    except (AttributeError, IndexError, KeyError):
        return False

    if standings.empty or not {"Year", "W", "L"}.issubset(standings.columns):
        return False

    years = pd.to_numeric(standings["Year"], errors="coerce")
    if years.isna().any() or not years.eq(season).all():
        return False

    wins = pd.to_numeric(standings["W"], errors="coerce").fillna(0)
    losses = pd.to_numeric(standings["L"], errors="coerce").fillna(0)
    return bool((wins + losses).gt(0).any())


def get_game_date():
    """Return the previous UTC date, which is the last completed game date."""
    today_utc = datetime.datetime.now(datetime.timezone.utc).date()
    return (today_utc - datetime.timedelta(days=1)).isoformat()


def main():
    season = get_current_season()

    if not season_has_started(season):
        print(f"No games have been played for the {season} season yet. Skipping.")
        return

    predictions = make_prediction(season, get_model())
    if not predictions:
        print(f"No predictions were produced for the {season} season. Skipping.")
        return

    save_prediction(predictions, season, get_game_date())


if __name__ == "__main__":
    main()
