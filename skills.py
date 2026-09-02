import time
import threading

from robot_controller import RobotController
from vacuum_controller import VacuumController
from pymycobot.genre import Coord, Angle

robot = RobotController()
vacuum = VacuumController()

stop_event = threading.Event()
pause_event = threading.Event()
pause_event.set()  # Start-Zustand: nicht pausiert

control_state = {
    "stop": False,
    "pause": False,
    "resume": False,
}

angle_joints = {
    "J1": Angle.J1.value,
    "J2": Angle.J2.value,
    "J3": Angle.J3.value,
    "J4": Angle.J4.value,
    "J5": Angle.J5.value,
    "J6": Angle.J6.value
}

class SkillAborted(Exception):
    """Wird geworfen, um einen laufenden Skill wegen 'stop' sauber
    abzubrechen und den kompletten Aufruf-Stack zu verlassen."""
    pass


def reset_control():
    """Vor jedem neuen Skill-Start aufrufen, damit ein vorheriger
    stop/pause-Zustand nicht in den naechsten Lauf durchsickert."""
    stop_event.clear()
    pause_event.set()
    control_state["stop"] = False
    control_state["pause"] = False

    try:
        robot.resume()
    except Exception as e:
        print(f"[Control] robot.resume() beim Reset fehlgeschlagen: {e}")


def check_abort():
    """Checkpoint, der vor/zwischen jeder Bewegung aufgerufen wird.
    - stop: bricht sofort per Exception ab
    - pause: blockiert den Thread, bis resume kommt (oder stop waehrend
      der Pause reinkommt)
    """
    if stop_event.is_set():
        raise SkillAborted("stop requested")

    if not pause_event.is_set():
        print("[Skill] paused - waiting for resume/stop ...")
        while not pause_event.wait(timeout=0.1):
            if stop_event.is_set():
                raise SkillAborted("stop requested while paused")
        print("[Skill] resumed")


def interruptible_sleep(seconds):
    """Ersatz fuer time.sleep(), der alle 100ms auf stop/pause reagiert,
    statt die volle Dauer stur abzuwarten."""
    end = time.time() + seconds
    while True:
        check_abort()
        remaining = end - time.time()
        if remaining <= 0:
            return
        time.sleep(min(0.1, remaining))

## ========= Basic Skills ==========

def move_angle(joint="J1", angle=0, speed=30):
    """
    Moves one joint of the robot seperately
    :param joint: J1 to J6 as string
    :param angle: degree as integer, example: 20
    :param speed: int
    :return:
    """
    if joint in angle_joints:
        robot.send_angle(angle_joints[joint], angle, speed)

def pickup(speed=40):
    """
    Starts the suction pump and then moves to home-angles [ 0, 0, 0, 0, 0, 0 ]
    :param speed: 0 to 100
    :return:
    """
    grip()
    time.sleep(2)
    home(speed)  

def placeTo(speed=40):
    """
    Stops the suction pump and then moves to home-angles [ 0, 0, 0, 0, 0, 0 ]
    :param speed: 0 to 100
    :return:
    """
    release()
    time.sleep(2)
    home(speed)

def moveTo(angles, speed=40):
    """
    Moves robot arm to specific angles.
    Checkpoint before and after the move_angles-call, if a stop or pause command came in during the call.
    So the command takes effect quickly, before the next call starts.
    :param angles: [J1 J2 J3 J4 J5 J6]
    :param speed: 0 to 100
    :return:
    """
    check_abort()
    robot.move_angles(angles, speed)
    check_abort()

def home(speed=30):
    """
    Returns robot-arm to home-angles [0, 0, 0, 0, 0, 0 ]
    :param speed:
    :return:
    """
    current_angles = robot.get_angles()
    x = current_angles[0]
    moveTo([x, 0, 0, 0, 0, 0], speed)
    moveTo([0, 0, 0, 0, 0, 0], speed)

def grip():
    vacuum.on()

def release():
    vacuum.off()

## ====== Service Skills ======

def pickupFromConveyor1(speed=40):
    """
    moves to Conveyor 1 and picks up the chip with the suction pump.
    :param speed: 0 to 100
    :return:
    """
    moveTo([-150.5, 0, 0, 0, 0, -90], speed)
    time.sleep(1)
    moveTo([-150.5, 0, 35, 0, -40, -90], speed)
    time.sleep(1)
    moveTo([-150.5, 0, 41, 0, -40, -90], speed)
    grip()
    time.sleep(2)
    home(speed)

def placeToConveyor1(speed=40):
    """
    moves to Conveyor 1 and places the chip there with the suction pump.
    :param speed: 0 to 100
    :return:
    """
    moveTo([-150.5, 0, 0, 0, 0, -90], speed)
    time.sleep(1)
    moveTo([-150.5, 0, 35, 0, -40, -90], speed)
    time.sleep(1)
    moveTo([-150.5, 0, 41, 0, -40, -90], speed)
    release()
    moveTo([-150.5, 0, 35, 0, -40, -90], speed)
    time.sleep(2)
    home(speed)

def placeToConveyor2(speed=40):
    """
    moves to Conveyor 2 and places the chip there with the suction pump.
    :param speed: 0 to 100
    :return:
    """
    moveTo([132, 0, -30, 0, 0, -90], speed)
    time.sleep(1)
    moveTo([132, 0, 39, 0, -40, -90], speed)
    release()
    moveTo([132, 0, 35, 0, -40, -90], speed)
    time.sleep(2)
    moveTo([132, 0, -30, 0, 0, -90], speed)
    time.sleep(1)
    moveTo([0, 0, -30, 0, 0, -90], speed)
    home(speed)

def pickupFromConveyor2(speed=40):
    """
    moves to Conveyor 1 and picks up the chip with the suction pump.
    :param speed: 0 to 100
    :return:
    """
    moveTo([132, 0, -30, 0, 0, -90], speed)
    time.sleep(1)
    moveTo([132, 0, 39, 0, -40, -90], speed)
    grip()
    time.sleep(2)
    moveTo([132, 0, -30, 0, 0, -90], speed)
    time.sleep(1)
    moveTo([0, 0, -30, 0, 0, -90], speed)
    home(speed)

# TODO genau wenn Modell fertig und Laser in Vorrichtung steht
def placeToLaser(speed=40):
    moveTo([158, 0, -30, 0, 0, 0], speed)
    time.sleep(1)
    moveTo([158, 30, 20, 0, -60, -90], speed)
    time.sleep(1)
    moveTo([158, 90, -80, 0, -10, -90], speed)
    time.sleep(1)
    release()
    time.sleep(2)
    moveTo([158, 30, 20, 0, -60, -90], speed)
    time.sleep(1)
    moveTo([158, 0, -30, 0, 0, 0], speed)
    time.sleep(1)
    home(speed)

# TODO
def pickupFromLaser(speed=40):
    moveTo([158, 0, -30, 0, 0, 0], speed)
    time.sleep(1)
    moveTo([158, 30, 20, 0, -60, -90], speed)
    time.sleep(1)
    moveTo([158, 90, -80, 0, -10, -90], speed)
    time.sleep(1)
    grip()
    time.sleep(1)
    moveTo([158, 30, 20, 0, -60, -90], speed)
    time.sleep(1)
    moveTo([158, 0, -30, 0, 0, 0], speed)
    time.sleep(1)
    home(speed)

def placeToChipFlipper(speed=40):
    """
    places Chip to Chip-Flipper
    :param speed: 0 to 100
    :return:
    """
    moveTo([0, 0, -30, 0, 0, -90], speed)
    time.sleep(1)
    moveTo([-20, 30, -55, 0, 2, -90], speed)
    time.sleep(1)
    release()
    time.sleep(2)
    robot.send_angle(Angle.J3.value, -52, speed)
    time.sleep(1)
    robot.send_angle(Angle.J3.value, -60, speed)
    home(speed)

def pickupFromChipFlipper(speed=40):
    """
    picks up Chip from Chip-Flipper
    :param speed: 0 to 100
    :return:
    """
    moveTo([0, 0, 0, 0, 0, -90], speed)
    robot.send_angle(Angle.J1.value, -25, speed)
    time.sleep(1)
    moveTo([-21, 25, 0, 0, -30, -90], speed)
    time.sleep(1)
    grip()
    time.sleep(2)
    moveTo([-21, 20, -5, 0, -40, -90], speed)
    home(speed)

def turn_chip(speed=40):
    """
    turns Chip on Chip-Flipper with using placeToChipFlipper and pickupFromChipFlipper
    :param speed: 0 to 100
    :return:
    """
    placeToChipFlipper(speed)
    home(speed)
    pickupFromChipFlipper(speed)
    home(speed)

def release_servos(speed=40):
    time.sleep(2)
    robot.release()

def show_angles():
    """
    shows current angles of the robot arm.
    :return: a float list of all angles
    """
    return robot.get_angles()