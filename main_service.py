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

def publish_state(payload, state, data=None):
    print(f"Publishing to {TOPIC_STATUS}: {payload}, {state}")
    logging.info("Publishing to %s with payload %s and state %s", TOPIC_STATUS, payload, state)

    client.publish(TOPIC_STATUS, json.dumps({
        "state": state,
        "msg": payload,
        "data": data,
    }))
    return

def run_skill(topic, payload):
    try:
        #print(f"Publishing to {topic}: {payload}")
        publish_state(payload, "starting")
        data = robot.get_angles()

        if payload == "home":
            home()

        elif payload == "grip":
            grip()

        elif payload == "release":
            release()

        elif payload == "get_angles":
            show_angles()

        elif payload == "pickupFromConveyor1":
            pickupFromConveyor1(40)

        elif payload == "pickupFromConveyor2":
            pickupFromConveyor2(40)

        elif payload == "placeToConveyor2":
            placeToConveyor2(40)

        elif payload == "placeToLaser":
            placeToLaser(40)

        elif payload == "pickupFromLaser":
            pickupFromLaser(40)

        elif payload == "release_servos":
            release_servos(40)

        elif payload == "placeToPedestal":
            placeToPedestal(40)

        elif payload == "pickupFromPedestal":
            pickupFromPedestel(40)

        else:
            print("unknown command")
            client.publish(TOPIC_STATUS, json.dumps({
                "state": "error",
                "msg": f"unknown command {payload}",
            }))
            return

        publish_state(payload, "done", data)

    except Exception as e:
        client.publish(TOPIC_STATUS, json.dumps({
            "state": "error",
            "msg": str(e),
            "cmd": payload,
        }))
    finally:
        skill_lock.release()

def handle_control(cmd):
    if cmd == "stop":
        control_state["stop"] = True
        robot.stop()
        publish_state(cmd, "done")

    elif cmd == "pause":
        control_state["pause"] = True
        robot.pause()
        publish_state(cmd, "done")

    elif cmd == "resume":
        control_state["pause"] = False
        robot.resume()
        publish_state(cmd, "done")


def on_message(client, userdata, message):
    try:
        topic = message.topic
        payload = message.payload.decode()
        #print(f"topic: {topic}, payload: {payload}, QoS={message.qos}")

        # Control Commands IMMER durchlassen
        if payload in ["stop", "pause", "resume"]:
            handle_control(payload)
            return

        if skill_lock.locked():
            print("System busy")
            return

        skill_lock.acquire()

        thread = threading.Thread(
            target=run_skill,
            args=(topic, payload)
        )

        thread.start()
        #thread.join()

    except Exception as e:
        client.publish(TOPIC_STATUS, json.dumps({
            "state": "error",
            "msg": str(e),
        }))

    finally:
        control_state["stop"] = False
        control_state["pause"] = False


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

except KeyboardInterrupt:
    pass

finally:
    vacuum.cleanup()
    client.loop_stop()
