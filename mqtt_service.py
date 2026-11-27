# import json
# import time
# import logging
# import threading
# import paho.mqtt.client as mqtt
#
# from skills import *
# from mqtt_config import *
#
# skill_lock = threading.Lock()
#
# # ================= MQTT =================
#
# def on_connect(client, userdata, flags, rc):
#     if rc == 0 and client.is_connected():
#         print(f"[MQTT] Connected (Code {rc})")
#         client.subscribe(TOPIC_CMD)
#         publish_connection_state({
#             "state": "online",
#             "online": True,
#         })
#         logging.info("[MQTT] Mecharm-270-Pi connected with result code: " + str(rc))
#         time.sleep(1)
#         vacuum.off()
#         home(40)
#         print("→ starting position set")
#         publish_state("home", "done", show_angles())
#     else:
#         logging.warning("Failed to connect with code %s", rc)
#         print(f'Failed to connect, return code {rc}')
#
#
# def on_disconnect(client, userdata, rc):
#     print(f"Disconnected with result code {rc}")
#     logging.error(
#         "[MQTT] disconnect callback rc=%s is_connected=%s",
#         rc, client.is_connected(),
#     )
#     stop_all_motors(userdata)
#     if rc == 0:
#         print("[MQTT] disconnected cleanly")
#         logging.info("[MQTT] disconnected cleanly")
#     else:
#         print(f"[MQTT] unexpected disconnect, rc={rc}")
#         logging.error(f"[MQTT] unexpected disconnect, rc={rc}")
#
# def publish_connection_state(payload):
#     client.publish(TOPIC_CONNECTION, json.dumps(payload),retain=True)
#
# def publish_state(payload, state, data=None):
#     logging.info("Publishing to %s with payload %s and state %s", TOPIC_STATUS, payload, state)
#
#     client.publish(TOPIC_STATUS, json.dumps({
#         "state": state,
#         "msg": payload,
#         "angles": data,
#     }))
#     return
#
# def run_skill(payload, speed):
#     try:
#         skill = skillset.get(payload["skill"])
#         if skill:
#             publish_state(payload, "starting", show_angles())
#             reset_control()
#             args = payload.get("args", {})
#             skill(**args)
#
#         else:
#             print("unknown command")
#             publish_state(payload, "error - unknown command")
#             return
#
#         publish_state(payload, "done", show_angles())
#
#     except SkillAborted:
#         print(f"[Skill] '{payload}' wurde per stop abgebrochen")
#         publish_state(payload, "stopped")
#
#     except Exception as e:
#         publish_state(str(e), "error")
#     finally:
#         skill_lock.release()
#
# def handle_control(cmd):
#     """
#     Reihenfolge wichtig: erst Events setzen, damit ein Skill-Thread,
#     der gerade in pause_event.wait() haengt, sofort aufwacht und
#     stop_event sieht. Danach den Arm auch physisch sofort anhalten.
#     :param cmd: string
#     :return:
#     """
#     if cmd == "stop":
#         control_state["stop"] = True
#         stop_event.set()
#         pause_event.set()
#         robot.stop()
#         publish_state(cmd, "done")
#
#     elif cmd == "pause":
#         control_state["pause"] = True
#         pause_event.clear()
#         robot.pause()
#         publish_state(cmd, "done")
#
#     elif cmd == "resume":
#         control_state["pause"] = False
#         robot.resume()
#         pause_event.set()
#         publish_state(cmd, "done")
#
#
# def on_message(client, userdata, message):
#     try:
#         payload = json.loads(message.payload)
#         speed = 40
#         logging.info("Received message: %s", payload)
#
#         # Control Commands IMMER durchlassen
#         if payload["skill"] in ["stop", "pause", "resume"]:
#             handle_control(payload["skill"])
#             return
#
#         if skill_lock.locked():
#             print("System busy")
#             return
#
#         skill_lock.acquire()
#
#         thread = threading.Thread(
#             target=run_skill,
#             args=(payload, speed)
#         )
#
#         thread.start()
#
#     except json.JSONDecodeError:
#         logging.error("Invalid JSON received: %s", message.payload)
#         publish_state("invalid JSON", "error")
#
#     except Exception as e:
#         publish_state(str(e), "error")
#
#
# skillset = {
#     "home": home,
#     "grip": grip,
#     "release": release,
#     "release_servos": release_servos,
#     "get_angles": show_angles,
#     "moveTo": moveTo,
#     "pickupFromConveyor1": pickupFromConveyor1,
#     "placeToConveyor1": placeToConveyor1,
#     "pickupFromConveyor2": pickupFromConveyor2,
#     "placeToConveyor2": placeToConveyor2,
#     "pickupFromLaser": pickupFromLaser,
#     "placeToLaser": placeToLaser,
#     "pickupFromChipFlipper": pickupFromChipFlipper,
#     "placeToChipFlipper": placeToChipFlipper,
#     "turn_chip": turn_chip,
#     "move_angle": move_angle,
# }
#
# # ================= START =================
#
# client = mqtt.Client(client_id=CLIENT_ID)
# client.username_pw_set(MQTT_USER, MQTT_PASS)
#
# client.will_set(
#     TOPIC_CONNECTION,
#     payload=json.dumps({
#         "state": "offline",
#         "online": False,
#     }),
#     qos=1,
#     retain=True
# )
#
# client.on_connect = on_connect
# client.on_disconnect = on_disconnect
# client.on_message = on_message
#
# client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
# client.loop_start()
#
# print("[Service] SRP MechArm MQTT Service gestartet")
#
# try:
#     while True:
#         time.sleep(5)
#
# except KeyboardInterrupt:
#     print("[SYSTEM] KeyboardInterrupt")
#     pass
#
# finally:
#     vacuum.cleanup()
#     publish_connection_state({
#         "state": "offline",
#         "online": False,
#     })
#     client.loop_stop()
#     client.disconnect()
