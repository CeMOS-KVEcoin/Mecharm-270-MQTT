import os
from dotenv import load_dotenv

load_dotenv()

## ========== MQTT Broker Details ==========

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASS = os.getenv("MQTT_PASS")

## ========== MQTT CLient Details ==========

CLIENT_ID = "robot_mecharm"

TOPIC_CMD = "mecharm/command"
TOPIC_STATUS = "mecharm/status"
TOPIC_CONNECTION = "mecharm/connection"

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60