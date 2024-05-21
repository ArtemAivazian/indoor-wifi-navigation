# Indoor Navigation Using Wi-Fi

This project utilizes a module with a microcontroller and Wi-Fi interface (RPi Pico W) to measure the strength of Wi-Fi signals from various access points (AP) inside a building. Based on the measured data, it is possible to estimate the approximate location of the device.

## Project Description
The project involves the use of an RPi Pico W to scan for available Wi-Fi networks, measure their signal strength, and send this information to a local computer. This data can then be used to train a model to approximate the device's location within the building.

## Requirements
- Raspberry Pi Pico W
- Wi-Fi network
- MQTT broker

## Installation
1. Clone this repository to your local machine.
2. Install necessary libraries for the RPi Pico W, such as `network`, `time`, `ubinascii`, `machine`, `ujson` and  `umqtt.simple`.

## Usage
This script connects to a Wi-Fi network, scans for available networks, measures their RSSI (Received Signal Strength Indicator), and sends this information to a local computer via MQTT.

```python
import network
import time
import ubinascii
import machine
import ujson as json
from umqtt.simple import MQTTClient

def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    print('Connected to WiFi:', wlan.ifconfig())

def scan_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    networks = wlan.scan()
    return networks

def get_rssi(networks):
    rssi_data = {}
    for net in networks:
        try:
            ssid = net[0].decode('utf-8').strip()  # SSID (network name)
            if ssid and not ssid.startswith('\x00'):
                rssi = net[3]  # RSSI (signal strength)
                rssi_data[ssid] = rssi
        except Exception as e:
            print(f"Error processing network: {e}")
    return rssi_data

def mqtt_publish(client, topic, data, qos=1):
    try:
        json_data = json.dumps(data)
        client.publish(topic, json_data.encode('utf-8'), qos=qos)
        print('Data sent:', json_data)
    except Exception as e:
        print('Failed to send data:', e)
        reconnect_mqtt(client)

def reconnect_mqtt(client):
    try:
        client.connect()
        print('Reconnected to MQTT broker')
    except Exception as e:
        print('Failed to reconnect:', e)
        time.sleep(5)
        reconnect_mqtt(client)

# Connect to a known WiFi network
ssid = 'iPhone (Артём)'
password = '12345678'
connect_wifi(ssid, password)

mqtt_server = '91.121.93.94'
client_id = ubinascii.hexlify(machine.unique_id())
topic = b'rssi_data'

client = MQTTClient(client_id, mqtt_server, keepalive=60)
try:
    client.connect()
except OSError as e:
    print('Failed to connect to MQTT broker:', e)
    reconnect_mqtt(client)

while True:
    networks = scan_wifi()
    rssi_data = get_rssi(networks)
    for ssid, rssi in rssi_data.items():
        single_data = {ssid: rssi}
        mqtt_publish(client, topic, single_data)
    time.sleep(1)
``` 

# WiFi Signal Strength Data

## Overview
This dataset contains Wi-Fi signal strength (RSSI) values collected from various access points (APs) like my room, the left and the right side kitchen on the third floor and the left side kitchen on the second floor of the dormitory. Each CSV file represents data from a specific location and includes signal strength readings for multiple SSIDs (WiFi networks).

## Files and Content

### data_room.csv
- **Description:** Contains RSSI values for different SSIDs recorded in my room.
- **Columns:**
  - `location`: The specific area within the room where the reading was taken.
  - Multiple SSID columns (e.g., `BUK`, `BUK Registrace`, `BUK guest`, etc.): Each column represents the RSSI value for a particular WiFi network.

### data_second_left_kitchen.csv
- **Description:** Contains RSSI values for different SSIDs recorded on the left side kitchen on the second floor.
- **Columns:**
  - `location`: The specific area within the kitchen where the reading was taken.
  - Multiple SSID columns (e.g., `BUK`, `BUK Registrace`, `BUK guest`, etc.): Each column represents the RSSI value for a particular WiFi network.

### data_third_left_kitchen.csv
- **Description:** Contains RSSI values for different SSIDs recorded on the left side kitchen on the third floor.
- **Columns:**
  - `location`: The specific area within the kitchen where the reading was taken.
  - Multiple SSID columns (e.g., `BUK`, `BUK Registrace`, `BUK guest`, etc.): Each column represents the RSSI value for a particular WiFi network.

### data_third_right_kitchen.csv
- **Description:** Contains RSSI values for different SSIDs recorded on the right side kitchen on the third floor.
- **Columns:**
  - `location`: The specific area within the kitchen where the reading was taken.
  - Multiple SSID columns (e.g., `BUK`, `BUK Registrace`, `BUK guest`, etc.): Each column represents the RSSI value for a particular WiFi network.

## General Information
- **RSSI (Received Signal Strength Indicator):** Indicates the power level being received by the device from the WiFi network. Higher RSSI values typically indicate a stronger signal.
- **SSID (Service Set Identifier):** The name of the WiFi network.

## Usage
This dataset can be used for analyzing the WiFi signal strength distribution in different parts of a building, which can help in optimizing network coverage and identifying potential dead zones.

## Video Demonstration
Below is a video demonstrating the data collection process for this dataset:

![Collecting_template_data.gif](img/Collecting_template_data.gif)


## Training the Model
### `train_model.py`
This script performs the following steps:

1. **Load Data**:
    - Loads RSSI data from multiple CSV files using a file pattern.
    ```python
    def load_data_from_csv_files(file_pattern):
        files = glob.glob(file_pattern)
        dataframes = [pd.read_csv(file, on_bad_lines='skip') for file in files]
        combined_df = pd.concat(dataframes, ignore_index=True)
        return combined_df
    ```

2. **Preprocess Data**:
    - Converts all columns to numeric, handles missing values by imputing with a constant value (-100), and encodes the target labels.
    ```python
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
    ```

3. **Train Model**:
    - Splits data into training and test sets, trains a RandomForestClassifier, and evaluates the model.
    ```python
    def train_model(X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Accuracy: {accuracy}")
        return model
    ```

4. **Save Model**:
    - Saves the trained model, label encoder, and imputer to disk.
    ```python
    def save_model(model, label_encoder, imputer):
        try:
            pd.to_pickle(model, '../models/trained_model.pkl')
            pd.to_pickle(label_encoder, '../models/label_encoder.pkl')
            pd.to_pickle(imputer, '../models/imputer.pkl')
            print("Model, label encoder, and imputer saved successfully.")
        except Exception as e:
            print(f"Failed to save model, label encoder, or imputer: {e}")
    ```

### Execution
To train and save the model, run:
```bash
python train_model.py
```
This script is designed to make real-time predictions of a device's location using WiFi signal strength data received via MQTT. The script uses a pre-trained RandomForestClassifier model, a LabelEncoder to decode the predicted labels, and a SimpleImputer to handle any missing values in the input data.


## Real Time Position Prediction
### `real_time_position_predication.py`

### Key Components

1. **Import Libraries**: The script imports necessary libraries for data manipulation, MQTT communication, and machine learning.

    ```python
    import json
    import pandas as pd
    import numpy as np
    import paho.mqtt.client as mqtt
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import LabelEncoder
    from sklearn.impute import SimpleImputer
    ```

2. **Initialize Variables**: It initializes the model, label encoder, a flag to check if the model is trained, and an imputer to handle missing values.

    ```python
    model = RandomForestClassifier()
    label_encoder = LabelEncoder()
    model_trained = False
    imputer = SimpleImputer(strategy='mean')  # Imputer to handle missing values
    ```

3. **Load Model**: This function loads the pre-trained model, label encoder, and imputer from disk.

    ```python
    def load_model():
        global model, label_encoder, model_trained, imputer
        try:
            model = pd.read_pickle('../models/trained_model.pkl')
            label_encoder = pd.read_pickle('../models/label_encoder.pkl')
            imputer = pd.read_pickle('../models/imputer.pkl')
            model_trained = True
            print("Model, label encoder, and imputer loaded successfully.")
        except Exception as e:
            print(f"Failed to load model, label_encoder, or imputer: {e}")
    ```

4. **MQTT Callbacks**: Define the callback functions for MQTT connection and message handling.

    ```python
    def on_connect(client, userdata, flags, rc):
        print(f"Connected with result code {rc}")
        client.subscribe("rssi_data", qos=1)

    def on_message(client, userdata, msg):
        try:
            rssi_data = json.loads(msg.payload.decode('utf-8'))
            predict_location(rssi_data)
        except Exception as e:
            print(f"Unexpected error: {e}")
    ```

5. **Predict Location**: This function preprocesses the incoming data, ensures it matches the format expected by the model, and then makes a prediction.

    ```python
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
    ```

6. **MQTT Client Setup**: Set up the MQTT client, connect to the broker, and start the MQTT loop.

    ```python
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
    ```

### Summary
This script sets up a real-time system for predicting the location of a device based on WiFi signal strength data. It connects to an MQTT broker to receive data, processes the data to match the model's input requirements, and makes predictions using a pre-trained RandomForestClassifier.

### Video Demonstration
![Predicting_position.gif](img/Predicting_position.gif)
