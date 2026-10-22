import pandas as pd

from scripts.Processed import MODEL_FEATURES, Processed, align_model_features


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


def test_scale_keeps_raw_rows_aligned_with_scaled_rows():
    """Explanations need the original stat values, not just z-scores."""
    processor = Processed(None, standings=None, advanced=None, per_game=None)
    processor.processed = pd.DataFrame(
        {
            "Year": [2025, 2025, 2025],
            "Player": ["Starter", "Bench", "Second Starter"],
            "Team": ["AAA", "BBB", "CCC"],
            "W/L%": [0.700, 0.400, 0.600],
            "MP": [35.0, 20.0, 30.0],
            "PTS": [30.0, 10.0, 20.0],
        }
    )

    scaled = processor.scale()

    assert list(scaled["Player"]) == ["Starter", "Second Starter"]
    assert list(processor.raw_processed["Player"]) == ["Starter", "Second Starter"]
    assert processor.raw_processed["PTS"].tolist() == [30.0, 20.0]
    assert processor.raw_processed["W/L%"].tolist() == [0.700, 0.600]
