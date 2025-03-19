from scripts.Predict import Predict

predict = Predict(2025)
proba = predict.predict_proba()
print(proba)
predict = predict.predict()
print(predict)