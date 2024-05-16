import paho.mqtt.client as mqtt
import json

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
                data.append(rssi_data)
                print(f"Received complete message: {rssi_data}")
                message_buffer = message_buffer[index:].strip()
            except json.JSONDecodeError:
                break
    except Exception as e:
        print(f"Unexpected error: {e}")
        message_buffer = ""  # Reset buffer on unexpected errors


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

client.loop_forever()