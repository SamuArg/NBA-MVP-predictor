import joblib
import xgboost as xgb
from sklearn.ensemble import RandomForestRegressor, AdaBoostRegressor
from sklearn.neural_network import MLPRegressor
from scripts.datasets import create_folds
from joblib import dump

models = [
    (RandomForestRegressor(n_estimators=100, n_jobs=-1, random_state=42), "Forest"),
    (xgb.XGBRegressor(n_estimators=100, n_jobs=-1, random_state=42), "XGBoost"),
    (AdaBoostRegressor(n_estimators=100, random_state=42), "AdaBoost"),
    (MLPRegressor(hidden_layer_sizes=(64, 32, 16), max_iter=1000, random_state=42), "MLP_64_32_16"),
    (MLPRegressor(hidden_layer_sizes=(32, 16, 8), max_iter=1000, random_state=42), "MLP_32_16_8")
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

        X_train_clean = X_train.drop(columns=["Year", "Player", "Team", "index"])
        model.fit(X_train_clean, y_train)

        X_test_clean = X_test.drop(columns=["Year", "Player", "Team", "index"])
        y_preds = model.predict(X_test_clean)

        X_test2 = X_test.copy()
        X_test2["Predicted"] = y_preds
        X_test2["Actual"] = y_test
        X_predict = X_test2.sort_values("Predicted", ascending=False)
        X_real = X_test2.sort_values("Actual", ascending=False)

        total += 1
        if X_real["Player"].iloc[0] != X_predict["Player"].iloc[0]:
            error += 1

    accuracy = (total - error) / total
    print(f"Accuracy for {name}: {accuracy}")

    if accuracy > best_accuracy:
        best_accuracy = accuracy
        best_model = model

print(f"Best model: {best_model}, accuracy: {best_accuracy}")

print(f"Retraining the best model ({best_model}) on the entire dataset.")

X_clean = X.drop(columns=["Year", "Player", "Team", "index"])

best_model.fit(X_clean, y)

dump(best_model, "models/model.joblib")
