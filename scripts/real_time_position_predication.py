import json
import pandas as pd
import numpy as np
import paho.mqtt.client as mqtt
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer

model = RandomForestClassifier()
label_encoder = LabelEncoder()
model_trained = False
imputer = SimpleImputer(strategy='mean')  # Imputer to handle missing values


# Load the trained model, label encoder, and imputer
def load_model():
    global model, label_encoder, model_trained, imputer
    try:
        model = pd.read_pickle('../models/trained_model.pkl')
        label_encoder = pd.read_pickle('../models/label_encoder.pkl')
        imputer = pd.read_pickle('../models/imputer.pkl')
        model_trained = True
        print("Model, label encoder, and imputer loaded successfully.")
    except Exception as e:
        print(f"Failed to load model, label encoder, or imputer: {e}")


# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("rssi_data", qos=1)


def on_message(client, userdata, msg):
    try:
        rssi_data = json.loads(msg.payload.decode('utf-8'))
        predict_location(rssi_data)
    except Exception as e:
        print(f"Unexpected error: {e}")


def predict_location(new_data):
    if model_trained:
        X_new = pd.DataFrame([new_data])

        # Ensure the columns match those used during training
        missing_cols = set(model.feature_names_in_) - set(X_new.columns)
        for col in missing_cols:
            X_new[col] = np.nan

        # Reorder columns to match the model's expected input
        X_new = X_new[model.feature_names_in_]

        # Use the imputer to handle NaN values
        X_new = pd.DataFrame(imputer.transform(X_new), columns=X_new.columns)

        prediction = model.predict(X_new).round().astype(int)
        predicted_location = label_encoder.inverse_transform(prediction)
        print(f"Predicted location: {predicted_location[0]}")
        return predicted_location[0]
    else:
        print("Model is not trained yet.")
        return None


broker = '91.121.93.94'
client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(broker, 1883, 60)
except Exception as e:
    print('Failed to connect to broker:', e)

load_model()

client.loop_forever()
