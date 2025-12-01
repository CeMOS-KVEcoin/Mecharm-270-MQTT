import json
import time
import threading
import paho.mqtt.client as mqtt

from robot_controller import RobotController
from vacuum_controller import VacuumController
from skills import pickup, put_pedastel, release, home, release_conveyor2
from mqtt_config import *

robot = RobotController()
vacuum = VacuumController()

# ================= STATUS =================

def publish_status(client, state="idle", extra=None):
    payload = {
        "state": state,
        "coords": robot.get_coords(),
        "extra": extra or {},
        "ts": time.time()
    }
    client.publish(TOPIC_STATUS, json.dumps(payload))


# ================= MQTT =================

def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Verbunden (Code {rc})")
    client.subscribe(TOPIC_CMD)

    # ✅ Startsequenz
    time.sleep(1)
    robot.home(40)
    vacuum.off()
    print("→ Startposition gesetzt")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        cmd = payload.get("type")
        speed = int(payload.get("speed", 40))

        print(f"[MQTT] Befehl: {payload}")

        if cmd == "pickup":
            threading.Thread(
                target=pickup,
                args=(robot, vacuum, speed)
            ).start()

        if cmd == "release_conveyor2":
            threading.Thread(
                target=release_conveyor2,
                args=(robot, vacuum, speed)
            ).start()

        if cmd == "put_pedastel":
            threading.Thread(
                target=put_pedastel,
                args=(robot, vacuum, speed)
            ).start()

        elif cmd == "release":
            release(vacuum)

        elif cmd == "home":
            home(robot, speed)

        elif cmd == "move":
            angles = payload.get("angles")
            if angles and len(angles) == 6:
                robot.move_angles(angles, speed)
                publish_status(client, "done", {"action": "move"})
            else:
                publish_status(client, "error", {"msg": "invalid angles"})

        else:
            publish_status(client, "error", {"msg": f"unknown command {cmd}"})

    except Exception as e:
        publish_status(client, "error", {"msg": str(e)})


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
        publish_status(client, "idle")

except KeyboardInterrupt:
    pass

finally:
    vacuum.cleanup()
    client.loop_stop()
