import csv
import json
from threading import Timer

import paho.mqtt.client as mqtt

data = []
message_buffer = ""  # Buffer to accumulate message parts


# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("rssi_data", qos=1)


def on_message(client, userdata, msg):
    global data, message_buffer
    try:
        message_buffer += msg.payload.decode('utf-8')

        while message_buffer:
            try:
                rssi_data, index = json.JSONDecoder().raw_decode(message_buffer)
                rssi_data['location'] = 'stairs'  # Label the data with the current location
                data.append(rssi_data)
                print(f"Received complete message: {rssi_data}")
                message_buffer = message_buffer[index:].strip()
            except json.JSONDecodeError:
                break
    except Exception as e:
        print(f"Unexpected error: {e}")
        message_buffer = ""


# Function to save data to CSV
# Function to save data to CSV
def save_data_to_csv(filename):
    global data
    if not data:
        print("No data to save.")
        return

    with open(filename, 'a', newline='') as csvfile:
        # Collect all possible fieldnames
        all_fieldnames = {'location'}
        for entry in data:
            all_fieldnames.update(entry.keys())
            all_fieldnames.discard('location')

        fieldnames = ['location'] + list(all_fieldnames)

        # Check if file is empty to write headers
        write_header = csvfile.tell() == 0

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()

        for entry in data:
            row = {field: entry.get(field) if field != 'location' else entry.get('location') for field in fieldnames}
            writer.writerow(row)

    data = []  # Clear data after saving


broker = '91.121.93.94'
client = mqtt.Client()

client.max_inflight_messages_set(20)
client.max_queued_messages_set(0)

client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(broker, 1883, 60)
except Exception as e:
    print('Failed to connect to broker:', e)


# Function to perform statistical analysis
# def analyze_data():
#     global data
#     if not data:
#         print("No data to analyze.")
#         return
#
#     # Prepare a list to hold expanded data
#     expanded_data = []
#
#     # Process each message
#     for entry in data:
#         for ssid, info in entry.items():
#             rssi, mac = info
#             expanded_data.append({
#                 'SSID': ssid,
#                 'RSSI': rssi,
#                 'MAC': mac
#             })
#
#     # Convert expanded data to a DataFrame
#     df = pd.DataFrame(expanded_data)
#
#     # Get statistics for each SSID
#     stats = df.groupby('SSID').agg(
#         mean_rssi=('RSSI', 'mean'),
#         min_rssi=('RSSI', 'min'),
#         max_rssi=('RSSI', 'max'),
#         std_rssi=('RSSI', 'std'),
#         range_rssi=('RSSI', lambda x: x.max() - x.min())
#     )
#
#     # Display the statistics
#     print(stats)
#
#     # Clear data after analysis
#     #data = []


# Function to schedule periodic analysis
def schedule_data_saving(interval, filename):
    save_data_to_csv(filename)
    Timer(interval, schedule_data_saving, [interval, filename]).start()


# Schedule analysis every 60 seconds
schedule_data_saving(60, 'wifi_rssi_data.csv')

client.loop_forever()
