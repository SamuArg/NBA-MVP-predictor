import joblib
import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_csv('data/processed/mvps.csv')

X_train = data.drop(columns=['Share', "Team", "Player", "Year"])

model = joblib.load('models/model.joblib')

feature_importances = model.feature_importances_
feature_names = X_train.columns

print(len(feature_importances))
print(len(feature_names))

importance_df = pd.DataFrame({
    'Feature': feature_names,
    'Importance': feature_importances
})

importance_df = importance_df.sort_values(by='Importance', ascending=False)

plt.figure(figsize=(10, 10))
plt.barh(importance_df['Feature'], importance_df['Importance'], color='skyblue')
plt.xlabel('Importance')
plt.title('Feature Importances from Random Forest')
plt.gca().invert_yaxis()
plt.show()
