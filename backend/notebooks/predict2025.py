from scripts.Predict import Predict
from joblib import load

model = load("models/model.joblib")

predict = Predict(2025, model)
proba = predict.predict_proba()
print(proba)
predict = predict.predict()
print(predict)
