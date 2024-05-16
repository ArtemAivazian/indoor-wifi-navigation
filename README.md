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
2. Install necessary libraries for the RPi Pico W, such as `network`, `time`, `ubinascii`, `machine`, and `ujson`.

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
            # Check if SSID is not empty or filled with null characters
            if ssid and not ssid.startswith('\x00'):
                bssid = ':'.join(f'{b:02x}' for b in net[1])  # BSSID (MAC address)
                rssi = net[3]  # RSSI (signal strength)
                rssi_data[ssid] = (rssi, bssid)
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
    
    for ssid, info in rssi_data.items():
        single_data = {ssid: info}
        mqtt_publish(client, topic, single_data, qos=1)
        time.sleep(1)
    
    time.sleep(10)
