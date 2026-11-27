# main.py
import logging
import threading

from mqtt_service import MqttService

from mqtt_config import (
    CLIENT_ID, MQTT_USER, MQTT_PASS,
    MQTT_BROKER, MQTT_PORT,
    TOPIC_CMD, TOPIC_STATUS, TOPIC_CONNECTION,
)

from skills import (
    SkillAborted,
    # control_state,
    # pause_event,
    reset_control,
    check_abort,
    robot,
    show_angles,
    # stop_event,
    # stop_all_motors,
    vacuum,
    home,
    grip,
    release,
    release_servos,
    moveTo,
    pickupFromConveyor1,
    placeToConveyor1,
    pickupFromConveyor2,
    placeToConveyor2,
    pickupFromLaser,
    placeToLaser,
    pickupFromChipFlipper,
    placeToChipFlipper,
    turn_chip,
    move_angle,
)

skill_lock = threading.Lock()

SKILLS = {
    "home": home,
    "grip": grip,
    "release": release,
    "release_servos": release_servos,
    "get_angles": show_angles,
    "moveTo": moveTo,
    "pickupFromConveyor1": pickupFromConveyor1,
    "placeToConveyor1": placeToConveyor1,
    "pickupFromConveyor2": pickupFromConveyor2,
    "placeToConveyor2": placeToConveyor2,
    "pickupFromLaser": pickupFromLaser,
    "placeToLaser": placeToLaser,
    "pickupFromChipFlipper": pickupFromChipFlipper,
    "placeToChipFlipper": placeToChipFlipper,
    "turn_chip": turn_chip,
    "move_angle": move_angle,
}


def handle_command(payload, mqtt_service):
    command = payload.get("skill")

    if not isinstance(command, str):
        mqtt_service.publish_status("Feld 'skill' fehlt oder ist ungültig", "error")
        return

    # Steuerbefehle müssen auch ankommen, während ein Skill läuft.
    if command == "stop":
        control_state["stop"] = True
        stop_event.set()
        pause_event.set()  # weckt einen pausierten Skill-Thread auf
        robot.stop()
        # stop_all_motors(robot)
        mqtt_service.publish_status(command, "done")
        return

    if command == "pause":
        control_state["pause"] = True
        pause_event.clear()
        robot.pause()
        mqtt_service.publish_status(command, "done")
        return

    if command == "resume":
        control_state["pause"] = False
        robot.resume()
        pause_event.set()
        mqtt_service.publish_status(command, "done")
        return

    skill = SKILLS.get(command)
    if skill is None:
        mqtt_service.publish_status(command, "error - unknown command")
        return

    # Nicht erst .locked() prüfen und danach sperren: Das wäre ein Race.
    if not skill_lock.acquire(blocking=False):
        mqtt_service.publish_status(command, "busy")
        return

    args = payload.get("args", {})
    if not isinstance(args, dict):
        skill_lock.release()
        mqtt_service.publish_status("Feld 'args' muss ein JSON-Objekt sein", "error")
        return

    thread = threading.Thread(
        target=run_skill,
        args=(command, skill, args, mqtt_service),
        daemon=True,
    )
    thread.start()


def run_skill(command, skill, args, mqtt_service):
    try:
        mqtt_service.publish_status(command, "starting", show_angles())
        reset_control()
        skill(**args)
        mqtt_service.publish_status(command, "done", show_angles())

    except SkillAborted:
        logging.info("Skill %s wurde gestoppt", command)
        mqtt_service.publish_status(command, "stopped", show_angles())

    except Exception as exc:
        logging.exception("Fehler beim Skill %s", command)
        mqtt_service.publish_status(str(exc), "error", show_angles())

    finally:
        skill_lock.release()


def main():
    service = MqttService(
        client_id=CLIENT_ID,
        username=MQTT_USER,
        password=MQTT_PASS,
        broker=MQTT_BROKER,
        port=MQTT_PORT,
        topic_cmd=TOPIC_CMD,
        topic_status=TOPIC_STATUS,
        topic_connection=TOPIC_CONNECTION,
        on_command=lambda payload: handle_command(payload, service),
    )
    service.start()
    try:
        # Hier kann dein Startverhalten hin:
        # vacuum.off()
        # home(40)
        threading.Event().wait()
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received: ctrl + c")
    finally:
        service.stop()

if __name__ == "__main__":
    main()