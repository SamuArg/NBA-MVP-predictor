from scripts.backfill_explanations import _predictions_match


def _predictions(*rows):
    return [
        {"player": player, "probability": probability}
        for player, probability in rows
    ]


def test_predictions_match_with_tiny_probability_drift():
    stored = _predictions(("Player A", 30.0), ("Player B", 20.0))
    computed = _predictions(("Player B", 20.04), ("Player A", 29.98))

    assert _predictions_match(stored, computed) is True


def test_predictions_match_rejects_large_probability_drift():
    stored = _predictions(("Player A", 30.0), ("Player B", 20.0))
    computed = _predictions(("Player A", 30.2), ("Player B", 20.0))

    assert _predictions_match(stored, computed) is False


def test_predictions_match_rejects_different_players():
    stored = _predictions(("Player A", 30.0), ("Player B", 20.0))
    computed = _predictions(("Player A", 30.0), ("Player C", 20.0))

    assert _predictions_match(stored, computed) is False


def test_predictions_match_rejects_different_lengths():
    stored = _predictions(("Player A", 30.0), ("Player B", 20.0))
    computed = _predictions(("Player A", 30.0))

    assert _predictions_match(stored, computed) is False
