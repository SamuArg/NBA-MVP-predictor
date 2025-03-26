from scripts.Predict import Predict
from joblib import load
import torch

model = torch.load("models/best_model.pt", weights_only=False)

predict = Predict(2025, model)
proba = predict.predict_proba()
print(proba)
predict = predict.predict()
print(predict)

total_params = sum(p.numel() for p in model.parameters())
print(f"Number of parameters: {total_params}")
