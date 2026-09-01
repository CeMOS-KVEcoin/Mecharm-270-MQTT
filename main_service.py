import json
import time
import logging
import threading
import paho.mqtt.client as mqtt

from skills import *
from mqtt_config import *

skill_lock = threading.Lock()

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

# ================= MQTT =================

def on_connect(client, userdata, flags, rc):
    if rc == 0 and client.is_connected():
        print(f"[MQTT] Connected (Code {rc})")
        client.subscribe(TOPIC_CMD)
        publish_connection_state({
            "state": "online",
            "online": True,
        })

        time.sleep(1)
        vacuum.off()
        home(40)
        print(robot.get_angles())
        print("→ starting position set")
    else:
        print(f'Failed to connect, return code {rc}')
        publish_connection_state({
            "state": "offline",
            "online": False,
        })

def on_disconnect(client, userdata, rc):
    logging.info("Disconnected with result code: %s", rc)
    publish_connection_state({
        "state": "offline",
        "online": False,
    })
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        logging.info("Reconnecting in %d seconds...", reconnect_delay)
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            logging.info("Reconnected successfully!")
            publish_connection_state({
                "state": "online",
                "online": True,
            })
            return
        except Exception as err:
            logging.error("%s. Reconnect failed. Retrying...", err)

        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    logging.info("Reconnect failed after %s attempts. Exiting...", reconnect_count)

def publish_connection_state(payload):
    client.publish(TOPIC_CONNECTION, json.dumps(payload),retain=True)

def publish_state(payload, state, data=None):
    logging.info("Publishing to %s with payload %s and state %s", TOPIC_STATUS, payload, state)

    client.publish(TOPIC_STATUS, json.dumps({
        "state": state,
        "msg": payload,
        "data": data,
    }))
    return

def run_skill(payload, speed):
    try:
        publish_state(payload, "starting")
        reset_control()
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
            pickupFromConveyor1(speed)

        elif payload == "placeToConveyor1":
            placeToConveyor1(speed)

        elif payload == "pickupFromConveyor2":
            pickupFromConveyor2(speed)

        elif payload == "placeToConveyor2":
            placeToConveyor2(speed)

        elif payload == "placeToLaser":
            placeToLaser(speed)

        elif payload == "pickupFromLaser":
            pickupFromLaser(speed)

        elif payload == "release_servos":
            release_servos(speed)

        elif payload == "placeToPedestal":
            placeToPedestal(speed)

        elif payload == "pickupFromPedestal":
            pickupFromPedestel(speed)

        elif payload == "placeToChipFlipper":
            placeToChipFlipper(speed)

        elif payload == "pickupFromChipFlipper":
            pickupFromChipFlipper(speed)

        else:
            print("unknown command")
            publish_state(f"unknown command: {payload}", "error")
            return

        publish_state(payload, "done", data)

    except SkillAborted:
        print(f"[Skill] '{payload}' wurde per stop abgebrochen")
        publish_state(payload, "stopped")

    except Exception as e:
        publish_state(str(e), "error")
    finally:
        skill_lock.release()

def handle_control(cmd):
    if cmd == "stop":
        # Reihenfolge wichtig: erst Events setzen, damit ein Skill-Thread,
        # der gerade in pause_event.wait() haengt, sofort aufwacht und
        # stop_event sieht. Danach den Arm auch physisch sofort anhalten.
        control_state["stop"] = True
        stop_event.set()
        pause_event.set()
        robot.stop()
        publish_state(cmd, "done")

    elif cmd == "pause":
        control_state["pause"] = True
        pause_event.clear()
        robot.pause()
        publish_state(cmd, "done")

    elif cmd == "resume":
        control_state["pause"] = False
        robot.resume()
        pause_event.set()
        publish_state(cmd, "done")


def on_message(client, userdata, message):
    try:
        payload = message.payload.decode()
        speed = 40

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
            args=(payload, speed)
        )

        thread.start()

    except Exception as e:
        publish_state(str(e), "error")


# ================= START =================

client = mqtt.Client(client_id=CLIENT_ID)
client.username_pw_set(MQTT_USER, MQTT_PASS)

client.will_set(
    TOPIC_CONNECTION,
    payload=json.dumps({
        "state": "offline",
        "online": False,
    }),
    qos=1,
    retain=True
)

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
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
    client.disconnect()
