import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from load_data import load_data


def train_and_evaluate_model(df):
    # Prepare the data
    X = df.drop('location', axis=1).fillna(0)
    y = df['location']

    # Split the data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Train the model
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # Predict and evaluate
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Accuracy:", accuracy)
    return clf, accuracy


if __name__ == "__main__":
    data_file = 'wifi_rssi_data.csv'  # Specify your CSV file name here
    df = load_data(data_file)
    model, accuracy = train_and_evaluate_model(df)
