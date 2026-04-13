import json
import time
import logging
import threading
import paho.mqtt.client as mqtt

from robot_controller import RobotController
from vacuum_controller import VacuumController
from skills import *
from mqtt_config import *

robot = RobotController()
vacuum = VacuumController()
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
        print(f"[MQTT] Verbunden (Code {rc})")
        client.subscribe(TOPIC_CMD)

        time.sleep(1)
        vacuum.off()
        home(40)
        print("→ startposition set")
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

def run_skill(func, client, cmd_name, *args):
    cmd_name = func.__name__
    def wrapper():
        try:
            client.publish(TOPIC_STATUS, json.dumps({
                "state": f"{cmd_name} in progress",
            }))
            func(*args)
            client.publish(TOPIC_STATUS, json.dumps({
                "state": f"{cmd_name} done",
            }))
        except Exception as e:
            client.publish(TOPIC_STATUS, json.dumps({
                "state": "error",
                "msg": str(e),
                "cmd": cmd_name,
            }))
        finally:
            skill_lock.release()

    skill_lock.acquire()
    threading.Thread(target=wrapper).start()



def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        cmd = payload.get("type")
        speed = int(payload.get("speed", 40))

        print(f"[MQTT] Befehl: {payload}")

       # Status VOR dem Start
        client.publish(TOPIC_STATUS, json.dumps({
            "state": f"starting {cmd}",
        }))

        if cmd == "pickup":
            run_skill(pickup, client, "pickup", robot, vacuum, speed)

        elif cmd == "placeToConveyor2":
            run_skill(placeToConveyor2, client, "placeToConveyor2", robot, vacuum, speed)

        elif cmd == "placeToPedestal":
            run_skill(placeToPedestal, client, "placeToPedestal", robot, vacuum, speed)

        elif cmd == "release":
            run_skill(release, client, "release", vacuum)

        elif cmd == "home":
            run_skill(home, client, "home", robot, speed)

        else:
            client.publish(TOPIC_STATUS, json.dumps({
                "state": "error",
                "msg": f"unknown command {cmd}",
            }))

    except Exception as e:
        client.publish(TOPIC_STATUS, json.dumps({
            "state": "error",
            "msg": str(e),
        }))


# ================= START =================

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)

client.on_connect = on_connect
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
