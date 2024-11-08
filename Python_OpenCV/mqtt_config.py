import paho.mqtt.client as mqtt
from config import MQTT_USERNAME, MQTT_PASSWORD
# MQTT configuration
MQTT_BROKER = 'homeassistant.local'
MQTT_PORT = 1883
MQTT_TOPIC = 'servo/position'       # 'Servo position MQTT topic'
MAX_RECONNECT_DELAY = 60


client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message published: {mid}")

client.on_connect = on_connect
client.on_publish = on_publish

def initialize_mqtt():
    try:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        client.connect(MQTT_BROKER, MQTT_PORT, MAX_RECONNECT_DELAY)
        client.loop_start()
    except Exception as e:
        print(f"Error: Could not connect to MQTT broker: {e}")
        exit(1)

def publish_mqtt(message,MQTT_TOPIC='servo/position'):
    client.publish(MQTT_TOPIC, message)
    print(f"Published via MQTT: {message},{MQTT_TOPIC}")
