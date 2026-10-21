import pandas as pd

from scripts.Processed import MODEL_FEATURES, align_model_features


def test_model_features_match_the_trained_model():
    """The model was trained on 46 features in this exact order."""
    assert len(MODEL_FEATURES) == 46
    assert len(set(MODEL_FEATURES)) == 46


def test_align_model_features_fills_early_season_columns():
    """Box plus/minus columns are missing early in the season and must be filled."""
    early_season = pd.DataFrame(
        {
            "Year": [2027],
            "Player": ["Test Player"],
            "Team": ["OKC"],
            "Age": [25.0],
            "G": [1.0],
            "MP": [36.0],
        }
    )

    aligned = align_model_features(early_season)

    assert list(aligned.columns) == MODEL_FEATURES
    assert len(aligned.columns) == 46
    assert aligned.loc[0, "Age"] == 25.0
    assert aligned.loc[0, "MP"] == 36.0
    assert aligned.loc[0, "BPM"] == 0.0
    assert aligned.loc[0, "VORP"] == 0.0
