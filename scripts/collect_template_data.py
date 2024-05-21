import json
from threading import Timer
import paho.mqtt.client as mqtt
import pandas as pd
import os

data = []
observed_ssids = set()  # Set to keep track of all observed SSIDs
location_label = "second_left_kitchen"  # Set the location label manually or programmatically


# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("rssi_data", qos=1)


def on_message(client, userdata, msg):
    global data, observed_ssids
    try:
        rssi_data = json.loads(msg.payload.decode('utf-8'))
        rssi_data['location'] = location_label  # Add the location label to the data
        data.append(rssi_data)
        observed_ssids.update(rssi_data.keys())  # Track observed SSIDs
        observed_ssids.discard('location')
        print(f"Received message: {rssi_data}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def save_data_to_files():
    global data, observed_ssids
    if not data:
        print("No data to save.")
        return

    # Group data by location
    data_by_location = {}
    for entry in data:
        location = entry['location']
        if location not in data_by_location:
            data_by_location[location] = []
        data_by_location[location].append(entry)

    for location, location_data in data_by_location.items():
        filename = os.path.join('scripts', f"data_{location}.csv")
        file_exists = os.path.isfile(filename)

        # Create DataFrame with all observed SSIDs as columns
        df = pd.DataFrame(location_data)

        # Ensure all observed SSIDs are columns in the DataFrame
        for ssid in observed_ssids:
            if ssid not in df.columns:
                df[ssid] = 'unset'

        # Reorder DataFrame columns
        all_fieldnames = ['location'] + sorted(observed_ssids)
        df = df[all_fieldnames]

        # Cast all columns to object type to avoid dtype issues
        df = df.astype(object)

        # Fill NaN values with 'unset'
        df.fillna('unset', inplace=True)

        # Save to CSV
        df.to_csv(filename, mode='a', header=not file_exists, index=False)

    data.clear()  # Clear data after saving


def schedule_data_saving(interval):
    save_data_to_files()
    Timer(interval, schedule_data_saving, [interval]).start()


broker = '91.121.93.94'
client = mqtt.Client()

client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(broker, 1883, 60)
except Exception as e:
    print('Failed to connect to broker:', e)

schedule_data_saving(180)  # Reduced interval for faster data saving

client.loop_start()

try:
    while True:
        pass
except KeyboardInterrupt:
    print("Script terminated by user.")
    client.loop_stop()
