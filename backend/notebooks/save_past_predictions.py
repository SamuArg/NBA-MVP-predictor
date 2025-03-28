from scripts.dailyPredictions import make_prediction, save_prediction
from scripts.datasets import create_folds
from models.Mvp_mlp import Mvp_mlp

model = Mvp_mlp(46, [256, 128, 64, 32, 16], 0.3, 1000, 0.001)

X, y, groups, group_kfold = create_folds()

for fold_idx, (train_idx, test_idx) in enumerate(group_kfold.split(X, y, groups)):
    X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

    year = int(X_test['Year'].iloc[0])

    X_train_clean = X_train.drop(columns=["Year", "Player", "Team"]).reset_index(drop=True)
    model.fit(X_train_clean, y_train)

    predictions = make_prediction(year, model, normalize=True)
    save_prediction(predictions, year, f"{year}-12-31")
