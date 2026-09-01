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

## basic skills

def pickup(speed=40):
    grip()
    time.sleep(2)
    home(speed)  

def placeTo(speed=40):
    release()
    time.sleep(2)
    home(speed)

# coords [x y z rx ry rz] -> not used
# angles [J1 J2 J3 J4 J5 J6]
def moveTo(angles, speed=40):
    check_abort()
    robot.move_angles(angles, speed)
    # kurzer Checkpoint direkt danach, damit ein stop/pause, der waehrend
    # des Aufrufs reinkam, moeglichst schnell greift, bevor der naechste
    # Befehl rausgeht.
    check_abort()


def home(speed=30):
    current_angles = robot.get_angles()
    x = current_angles[0]
    moveTo([x, 0, 0, 0, 0, 0], speed)
    moveTo([0, 0, 0, 0, 0, 0], speed)

def grip():
    vacuum.on()

def release():
    vacuum.off()

## Service Skills
def pickupFromConveyor1(speed=40):
    moveTo([-150.5, 0, 0, 0, 0, -90], speed)
    time.sleep(1)
    moveTo([-150.5, 0, 30, 0, -40, -90], speed)
    time.sleep(1)
    moveTo([-150.5, 0, 41, 0, -40, -90], speed)
    grip()
    time.sleep(2)
    home(speed)

def placeToConveyor1(speed=40):
    moveTo([-150.5, 0, 0, 0, 0, -90], speed)
    time.sleep(1)
    moveTo([-150.5, 0, 30, 0, -40, -90], speed)
    time.sleep(1)
    moveTo([-150.5, 0, 41, 0, -40, -90], speed)
    release()
    moveTo([-150.5, 0, 35, 0, -40, -90], speed)
    time.sleep(2)
    home(speed)

def placeToConveyor2(speed=40):
    moveTo([132, 0, -30, 0, 0, -90], speed)
    time.sleep(1)
    moveTo([132, 0, 39, 0, -40, -90], speed)
    release()
    moveTo([132, 0, 35, 0, -40, -90], speed)
    time.sleep(2)
    moveTo([132, 0, -30, 0, 0, -90], speed)
    home(speed)

def pickupFromConveyor2(speed=40):
    moveTo([132, 0, -30, 0, 0, -90], speed)
    time.sleep(1)
    moveTo([132, 0, 39, 0, -40, -90], speed)
    grip()
    time.sleep(2)
    moveTo([132, 0, -30, 0, 0, -90], speed)
    home(speed)

# TODO genau wenn Modell fertig und Laser in Vorrichtung steht
#  Überdreht manchmal über 160° - verbessern!!
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
    moveTo([0, 0, 0, 0, 0, -90], speed)
    robot.send_angle(Angle.J1.value, -25, speed)
    time.sleep(1)
    moveTo([-21, 25, 0, 0, -30, -90], speed)
    time.sleep(1)
    grip()
    time.sleep(2)
    moveTo([-21, 20, -5, 0, -40, -90], speed)
    home(speed)

# deprecated
def placeToPedestal(speed=40):
    moveTo([0, 0, 0, 0, 0, -179], speed)
    time.sleep(2)

    moveTo([-6, 25, 21.5, -10, -41, -179], 20)
    time.sleep(2)

    release()
    time.sleep(4)

    moveTo([5, 0, 20, 0, -10, -179], speed)
    time.sleep(2)

    home(speed)

# deprecated
def pickupFromPedestel(speed=40):
    # tbd [-49.65,70.04,-43.85,-74,-49.57,56.16]
    moveTo([-50, 0, 0, 0, 0, 0], speed)
    time.sleep(0.5)
    moveTo([-49, 65, -45, -74, -55, 56], speed)
    grip()
    time.sleep(2)
    moveTo([-50, 0, -45, -74, -55, 56], speed)
    time.sleep(1)
    moveTo([-50, 0, 0, 0, 0, 0], speed)
    time.sleep(1)

    home(speed)

def turnChip(speed=40):
    placeToPedestal()
    home(speed)
    pickupFromPedestel(speed) # tbd
    home(speed)

def release_servos(speed=40):
    print("releasing robot-servos now!")
    time.sleep(2)
    robot.release()

def show_angles():
     print(f"Angles: {robot.get_angles()}")