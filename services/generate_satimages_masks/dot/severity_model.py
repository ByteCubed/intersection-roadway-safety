"""
Train a model to predict the proportion of severe accidents at intersections.
Severe accidents have a "severity" measure of 3 or 4 on a scale of 1-4.
Due to the limited intersection metadata currently available the model
performs poorly. This is a proof of concept.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

from pathlib import Path


def calculate_mean_severity(accidents):
    severity = [acc['severity'] for acc in accidents]
    return np.mean(severity)


if __name__ == "__main__":
    # Load intersection with crash data created by integration.py
    project_dir = Path(__file__).resolve().parent.parent.parent
    intrs_file = project_dir / 'data' / 'intersection_accidents.pkl'
    intersections = pd.read_pickle(str(intrs_file))

    # Data processing to prepare for modeling
    intersections = intersections[intersections.accidents.str.len() > 0]
    intersections['mean_accident_severity'] = intersections.apply(
        lambda x: calculate_mean_severity(x['accidents']), axis=1)

    # Train/test split
    X = intersections[['crossing', 'roundabout', 'stop', 'traffic_signal', 'num_legs',
                       'lanes', 'angle', 'oneway']]
    y = intersections['mean_accident_severity']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Train model
    clf = RandomForestRegressor()
    clf.fit(X_train, y_train)
    score = clf.score(X_train, y_train)
    print(f"Model R^2: {score}")

    # Evaluate model on test set
    predictions = clf.predict(X_test)
    error = y_test - predictions
    sq_err = error ** 2
    rmse = sq_err.mean() ** 0.5
    print(f'RMSE: {rmse}')

    features_importance = clf.feature_importances_
    print("Feature ranking:")
    for i, data_class in enumerate(X.columns):
        print("{}. {} ({})".format(i + 1, data_class, features_importance[i]))
