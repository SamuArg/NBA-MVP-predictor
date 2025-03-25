from scripts.dailyPredictions import make_prediction, save_prediction

for i in range(1981, 2025):
    predictions = make_prediction(i)
    save_prediction(predictions, i, f"{i}-12-31")
