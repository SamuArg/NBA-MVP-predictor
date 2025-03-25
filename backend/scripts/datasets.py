import pandas as pd
from sklearn.model_selection import GroupKFold


def create_folds():
    data = pd.read_csv('data/processed/mvps.csv')

    X = data.drop(columns=['Share'])
    y = data['Share']
    groups = data['Year']

    group_kfold = GroupKFold(n_splits=len(data['Year'].unique()), shuffle=True, random_state=42)

    return X, y, groups, group_kfold
