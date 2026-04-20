import json
import time
import logging
import threading
import paho.mqtt.client as mqtt

#from robot_controller import RobotController
#from vacuum_controller import VacuumController
from skills import *
from mqtt_config import *

#robot = RobotController()
#vacuum = VacuumController()
skill_lock = threading.Lock()

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

# ================= STATUS =================

# def publish_status(client, state="idle", extra=None):
#     payload = {
#         "state": state,
#         "coords": robot.get_coords(),
#         "extra": extra or {},
#         "ts": time.time()
#     }
#     client.publish(TOPIC_STATUS, json.dumps(payload))


# ================= MQTT =================

def on_connect(client, userdata, flags, rc):
    if rc == 0 and client.is_connected():
        print(f"[MQTT] Connected (Code {rc})")
        client.subscribe(TOPIC_CMD)

        time.sleep(1)
        vacuum.off()
        home(40)
        print(robot.get_angles())
        print("→ starting position set")
    else:
        print(f'Failed to connect, return code {rc}')

def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

def publish_state(payload, state):
    print(f"Publishing to {TOPIC_STATUS}: {payload}, {state}")
    logging.info("Publishing to %s with payload %s and state %s", TOPIC_STATUS, payload, state)

    client.publish(TOPIC_STATUS, json.dumps({
        "state": state,
        "msg": payload,
    }))
    return

def run_skill(topic, payload):
    try:
        #print(f"Publishing to {topic}: {payload}")
        #client.publish(TOPIC_STATUS, payload)

        if payload == "home":
            publish_state(payload, "starting")
            home()
            publish_state(payload, "done")

        elif payload == "grip":
            publish_state(payload, "starting")
            grip()
            publish_state(payload, "done")

        elif payload == "release":
            publish_state(payload, "starting")
            release()
            publish_state(payload, "done")

        elif payload == "get_angles":
            show_angles()

        elif payload == "pickupFromConveyor1":
            publish_state(payload, "starting")
            pickupFromConveyor1(40)
            publish_state(payload, "done")

        elif payload == "placeToConveyor2":
            publish_state(payload, "starting")
            placeToConveyor2(40)
            publish_state(payload, "done")

        elif payload == "release_servos":
            release_servos(40)

        else:
            print("unknown command")
            client.publish(TOPIC_STATUS, json.dumps({
                "state": "error",
                "msg": f"unknown command {payload}",
            }))
            return

    except Exception as e:
        client.publish(TOPIC_STATUS, json.dumps({
            "state": "error",
            "msg": str(e),
            "cmd": payload,
        }))
    finally:
        skill_lock.release()


def on_message(client, userdata, message):
    try:
        topic = message.topic
        payload = message.payload.decode()
        #print(f"topic: {topic}, payload: {payload}, QoS={message.qos}")

        if skill_lock.locked():
            print("System busy")
            return

        skill_lock.acquire()

        threading.Thread(
            target=run_skill,
            args=(topic, payload)
        ).start()

    except Exception as e:
        client.publish(TOPIC_STATUS, json.dumps({
            "state": "error",
            "msg": str(e),
        }))


# ================= START =================

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_start()

print("[Service] SRP MechArm MQTT Service gestartet")

try:
    while True:
        time.sleep(5)
       # publish_status(client, "idle")

except KeyboardInterrupt:
    pass

finally:
    vacuum.cleanup()
    client.loop_stop()
