import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
import glob


# Load data from multiple CSV files
def load_data_from_csv_files(file_pattern):
    files = glob.glob(file_pattern)
    dataframes = [pd.read_csv(file, on_bad_lines='skip') for file in files]
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df


# Preprocess data
def preprocess_data(df):
    rssi_df = df.apply(pd.to_numeric, errors='coerce')
    rssi_df['location'] = df['location']
    X = rssi_df.drop(columns=['location'])
    y = rssi_df['location']
    imputer = SimpleImputer(strategy='constant', fill_value=-100)
    X = pd.DataFrame(imputer.fit_transform(X), columns=X.columns)
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    return X, y_encoded, label_encoder, imputer


# Train model
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy}")
    return model


# Save model, label encoder, and imputer
def save_model(model, label_encoder, imputer):
    try:
        pd.to_pickle(model, '../models/trained_model.pkl')
        pd.to_pickle(label_encoder, '../models/label_encoder.pkl')
        pd.to_pickle(imputer, '../models/imputer.pkl')
        print("Model, label encoder, and imputer saved successfully.")
    except Exception as e:
        print(f"Failed to save model, label encoder, or imputer: {e}")


# Main function to load data, preprocess, train, and save model
def main():
    file_pattern = 'data/*.csv'  # Ensure correct path to your CSV files
    df = load_data_from_csv_files(file_pattern)
    X, y, label_encoder, imputer = preprocess_data(df)
    model = train_model(X, y)
    save_model(model, label_encoder, imputer)


if __name__ == '__main__':
    main()
