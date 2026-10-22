import pandas as pd
import pytest

# CI uses shap 0.54.1 (Python 3.13).  Environments without shap skip these
# tests; requirements-analysis.txt installs shap 0.46 on older interpreters.
pytest.importorskip("shap")

from scripts.explain import _display_value, explain_predictions


class LinearModel:
    """A deterministic stand-in for the PyTorch model."""

    def predict(self, frame):
        return (2.0 * frame["PTS"] + 3.0 * frame["PER"]).to_numpy()


def test_shap_values_are_additive():
    background = pd.DataFrame(
        {
            "PTS": [10.0, 20.0, 30.0, 40.0],
            "PER": [12.0, 18.0, 24.0, 30.0],
        }
    )
    features = pd.DataFrame({"PTS": [31.2], "PER": [28.4]})
    raw = pd.DataFrame(
        {
            "Player": ["Test Player"],
            "Team": ["OKC"],
            "PTS": [31.2],
            "PER": [28.4],
        }
    )

    rows = explain_predictions(
        LinearModel(),
        features,
        raw,
        background=background,
        seed=7,
    )

    assert len(rows) == 1
    row = rows[0]
    assert row["player"] == "Test Player"
    assert row["team"] == "OKC"
    assert len(row["features"]) == 2

    contribution_total = row["baseValue"] + sum(
        feature["contribution"] for feature in row["features"]
    )
    assert contribution_total == pytest.approx(row["outputValue"], abs=1e-5)

    by_name = {feature["name"]: feature for feature in row["features"]}
    assert by_name["PTS"]["label"] == "Points / game"
    assert by_name["PTS"]["displayValue"] == "31.2"
    assert by_name["PTS"]["value"] == 31.2


def test_explain_returns_nothing_for_no_rows():
    empty = pd.DataFrame(columns=["PTS", "PER"])
    assert explain_predictions(LinearModel(), empty, empty) == []


def test_display_value_formats_stats():
    # Advanced rates are already 0-100, shooting percentages are 0-1.
    assert _display_value("USG%", 34.8) == "34.8%"
    assert _display_value("TRB%", 8.7) == "8.7%"
    assert _display_value("TS%", 0.556) == "55.6%"
    assert _display_value("FG%", 0.481) == "48.1%"
    assert _display_value("PTS", 31.24) == "31.2"
    assert _display_value("Age", 27) == "27"
    assert _display_value("WS/48", 0.2014) == "0.201"
    assert _display_value("PTS", None) == "—"
