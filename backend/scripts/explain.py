"""SHAP explanations for MVP model predictions.

The model is a small neural network, so a permutation explainer is used.  It is
model-agnostic, deterministic for a fixed seed, and its contributions are
additive: ``base_value + sum(contributions) == model_output``.

The public :func:`explain_predictions` helper deliberately imports ``shap``
lazily.  The Flask API never generates explanations (they are precomputed by
the daily job), which keeps ``shap`` out of the production API image.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
import pandas as pd


# Human-readable names and formatting for the 46 model features.  Basketball
# Reference's per-game table is merged into the feature matrix, so the counting
# stats (PTS, TRB, ...) are per-game averages rather than season totals.
FEATURE_DISPLAY: dict[str, tuple[str, str]] = {
    "Age": ("Age", "int"),
    "G": ("Games", "int"),
    "PER": ("PER", "float1"),
    "TS%": ("True shooting %", "percent1"),
    "3PAr": ("3-point attempt rate", "percent1"),
    "FTr": ("Free throw rate", "float3"),
    # Basketball Reference stores these advanced rates as 0-100 values
    # (for example, USG% 34.8), unlike TS%/3PAr/FTr and the per-game shooting
    # percentages, which are 0-1 decimals.
    "ORB%": ("Off. rebound %", "percent100"),
    "DRB%": ("Def. rebound %", "percent100"),
    "TRB%": ("Rebound %", "percent100"),
    "AST%": ("Assist %", "percent100"),
    "STL%": ("Steal %", "percent100"),
    "BLK%": ("Block %", "percent100"),
    "TOV%": ("Turnover %", "percent100"),
    "USG%": ("Usage %", "percent100"),
    "OWS": ("Off. win shares", "float1"),
    "DWS": ("Def. win shares", "float1"),
    "WS/48": ("Win shares / 48", "float3"),
    "OBPM": ("Off. box plus/minus", "float1"),
    "DBPM": ("Def. box plus/minus", "float1"),
    "BPM": ("Box plus/minus", "float1"),
    "VORP": ("VORP", "float1"),
    "W/L%": ("Team win %", "percent1"),
    "seed": ("Playoff seed", "int"),
    "MP": ("Minutes / game", "float1"),
    "FG": ("FG / game", "float1"),
    "FGA": ("FGA / game", "float1"),
    "FG%": ("FG %", "percent1"),
    "3P": ("3P / game", "float1"),
    "3PA": ("3PA / game", "float1"),
    "3P%": ("3P %", "percent1"),
    "2P": ("2P / game", "float1"),
    "2PA": ("2PA / game", "float1"),
    "2P%": ("2P %", "percent1"),
    "eFG%": ("Effective FG %", "percent1"),
    "FT": ("FT / game", "float1"),
    "FTA": ("FTA / game", "float1"),
    "FT%": ("FT %", "percent1"),
    "ORB": ("Off. rebounds / game", "float1"),
    "DRB": ("Def. rebounds / game", "float1"),
    "TRB": ("Rebounds / game", "float1"),
    "AST": ("Assists / game", "float1"),
    "STL": ("Steals / game", "float1"),
    "BLK": ("Blocks / game", "float1"),
    "TOV": ("Turnovers / game", "float1"),
    "PF": ("Fouls / game", "float1"),
    "PTS": ("Points / game", "float1"),
}


def _python_value(value: Any) -> Any:
    """Convert numpy scalars to JSON-friendly Python values."""
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def _display_value(name: str, value: Any) -> str:
    """Format a raw stat for the explanation table."""
    value = _python_value(value)
    if value is None:
        return "—"

    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)

    if not math.isfinite(number):
        return "—"

    kind = FEATURE_DISPLAY.get(name, (name, "float2"))[1]
    if kind == "int":
        return f"{number:,.0f}"
    if kind == "percent100":
        return f"{number:.1f}%"
    if kind == "percent1":
        return f"{number * 100:.1f}%"
    if kind == "float1":
        return f"{number:,.1f}"
    if kind == "float3":
        return f"{number:,.3f}"
    return f"{number:,.2f}"


def explain_predictions(
    model: Any,
    features: pd.DataFrame,
    raw_features: pd.DataFrame,
    background: pd.DataFrame | None = None,
    *,
    max_background: int = 100,
    seed: int = 42,
) -> list[dict[str, Any]]:
    """Compute SHAP values for the given model rows.

    Args:
        model: Object with a ``predict(DataFrame) -> array`` method.
        features: Standardized feature rows to explain.
        raw_features: Unscaled rows aligned with ``features`` (used for display).
        background: Reference population used to define the base value.  When
            omitted, the rows being explained are used as the background.
        max_background: Maximum number of background rows (for runtime).
        seed: Random seed for the background sample.

    Returns:
        One dictionary per row with the base value, model output, and the SHAP
        contribution (in raw model-output units) of every feature.
    """
    # Imported lazily so the API image does not need shap installed.
    import shap

    if len(features) != len(raw_features):
        raise ValueError("features and raw_features must have the same number of rows")
    if len(features) == 0:
        return []

    feature_names = list(features.columns)
    reference = features if background is None else background
    reference = reference.reindex(columns=feature_names)
    if reference.dropna(how="all").empty:
        raise ValueError("The SHAP background has no usable feature columns")

    if len(reference) > max_background:
        reference = reference.sample(n=max_background, random_state=seed)
    reference = reference.reset_index(drop=True)

    def predict_fn(values: Any) -> np.ndarray:
        array = values
        if not isinstance(array, pd.DataFrame):
            array = np.asarray(array)
            if array.ndim == 1:
                array = array.reshape(1, -1)
            array = pd.DataFrame(array, columns=feature_names)
        return np.asarray(model.predict(array), dtype=float).reshape(-1)

    explainer = shap.Explainer(
        predict_fn,
        reference,
        algorithm="permutation",
        seed=seed,
    )
    explanation = explainer(features.reset_index(drop=True))

    values = np.asarray(explanation.values, dtype=float)
    if values.ndim == 1:
        values = values.reshape(1, -1)

    base_values = np.asarray(explanation.base_values, dtype=float)
    if base_values.ndim == 0:
        base_values = np.full(len(features), float(base_values))
    else:
        base_values = base_values.reshape(-1)

    outputs = predict_fn(features.to_numpy(dtype=float))

    rows: list[dict[str, Any]] = []
    for row_index in range(len(features)):
        raw_row = raw_features.iloc[row_index]
        contributions = [
            {
                "name": name,
                "label": FEATURE_DISPLAY.get(name, (name, "float2"))[0],
                "value": _python_value(raw_row.get(name)),
                "displayValue": _display_value(name, raw_row.get(name)),
                "contribution": round(float(values[row_index][column]), 6),
            }
            for column, name in enumerate(feature_names)
        ]
        contributions.sort(key=lambda item: abs(item["contribution"]), reverse=True)

        base_value = float(base_values[row_index])
        output_value = float(outputs[row_index])
        expected = base_value + float(values[row_index].sum())
        if abs(expected - output_value) > 1e-4:
            print(
                "Warning: SHAP values are not additive for "
                f"{raw_row.get('Player', row_index)}: "
                f"base + contributions = {expected:.6f}, model = {output_value:.6f}"
            )

        rows.append(
            {
                "player": str(raw_row.get("Player", "")),
                "team": str(raw_row.get("Team", "")),
                "baseValue": round(base_value, 6),
                "outputValue": round(output_value, 6),
                "features": contributions,
            }
        )

    return rows
