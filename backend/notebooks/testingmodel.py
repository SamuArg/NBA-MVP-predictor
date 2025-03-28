from scripts.datasets import create_folds
import torch
import pandas as pd
from models.Mvp_mlp import Mvp_mlp

scaled = pd.read_csv("data/processed/scaled.csv")

models = [
    # (RandomForestRegressor(n_estimators=100, n_jobs=-1, random_state=42), "Forest"),
    # (xgb.XGBRegressor(n_estimators=100, n_jobs=-1, random_state=42), "XGBoost"),
    # (AdaBoostRegressor(n_estimators=100, random_state=42), "AdaBoost"),
    # (MLPRegressor(hidden_layer_sizes=(64, 32, 16), max_iter=1000, random_state=42), "MLP_64_32_16"),
    # (MLPRegressor(hidden_layer_sizes=(32, 16, 8), max_iter=1000, random_state=42), "MLP_32_16_8"),
    (Mvp_mlp(46, [256, 128, 64, 32, 16], 0.3, 1000, 0.001), "MVP_MLP"),
]

X, y, groups, group_kfold = create_folds()

best_model = None
best_accuracy = 0

for model, name in models:
    error = 0
    total = 0
    for fold_idx, (train_idx, test_idx) in enumerate(group_kfold.split(X, y, groups)):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        year = int(X_test['Year'].iloc[0])
        X_to_predict = scaled[scaled.Year == year]
        X_to_predict_clean = X_to_predict.drop(columns=["Year", "Player", "Team"]).reset_index(drop=True)
        X_train_clean = X_train.drop(columns=["Year", "Player", "Team"]).reset_index(drop=True)
        model.fit(X_train_clean, y_train)

        # Make predictions directly on test data
        y_preds = model.predict(X_to_predict_clean)

        # Get predicted MVP
        X_test = X_to_predict.copy()
        X_test["Predicted"] = y_preds
        X_predict = X_test.sort_values("Predicted", ascending=False)
        predicted_player = X_predict["Player"].iloc[0]
        predicted_value = X_predict["Predicted"].iloc[0]

        # Get actual MVP
        X_test["Actual"] = y_test
        X_real = X_test.sort_values("Actual", ascending=False)
        actual_player = X_real["Player"].iloc[0]

        total += 1
        print(actual_player, predicted_player)
        if actual_player != predicted_player:
            error += 1

    accuracy = (total - error) / total
    print(f"Accuracy for {name}: {accuracy}")

    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model = model

print(f"Best model: {best_model}, accuracy: {best_accuracy}")

print(f"Retraining the best model ({best_model}) on the entire dataset.")

X_clean = X.drop(columns=["Year", "Player", "Team"]).reset_index(drop=True)
best_model.fit(X_clean, y)

torch.save(best_model, "models/best_model.pt")

# dump(best_model, "models/model.joblib")
