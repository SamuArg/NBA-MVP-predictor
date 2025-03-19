import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
df = pd.read_csv('data/processed/mvps.csv')
clean_df = df.drop(columns=["Year", "Player", "Team"])
matrix = clean_df.corr()
sns.heatmap(matrix)
plt.show()