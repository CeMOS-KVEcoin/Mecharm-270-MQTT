import time

from robot_controller import RobotController
from vacuum_controller import VacuumController

robot = RobotController()
vacuum = VacuumController()

control_state = {
    "stop": False,
    "pause": False,
    "resume": False,
}

## basic skills

def pickup(speed=40):
    grip()
    time.sleep(2)
    home(speed)  

#angles [x y z rx ry rz]
def moveTo(angles, speed=40):
    if control_state["stop"]:
        robot.stop()
        print("Movement aborted")
        return

    robot.move_angles(angles, speed)

    if control_state["stop"]:
        robot.stop()
        print("Movement stopped mid-execution")
        return


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
    moveTo([-151, 0, 0, 0, 0, -90], speed)
    moveTo([-151, 0, 41, 0, -40, -90], speed)

    pickup(speed)


def placeToConveyor2(speed=40):
    moveTo([132, 0, 0, 0, 0, -90], speed)
    moveTo([132, 0, 39, 0, -40, -90], speed)

    release()
    moveTo([132, 0, 35, 0, -40, -90], speed)
    time.sleep(2)

    home(speed)

def pickupFromConveyor2(speed=40):
    moveTo([132, 0, 0, 0, 0, -90], speed)
    moveTo([132, 0, 39, 0, -40, -90], speed)

    grip()
    time.sleep(2)

    home(speed)

def placeToLaser(speed=40):
    home(speed)
    current_angles = robot.get_angles()
    x = current_angles[0]
    y = current_angles[1]
    z = current_angles[2]
    rx = current_angles[3]
    ry = current_angles[4]
    rz = current_angles[5]
    moveTo([159.9, y, z, rx, ry, rz], speed)
    #ang = robot.Angle.J1.value
    #moveTo(ang, 160, 40)
    time.sleep(1)
    moveTo([159.9,80,-47,0,-35.5,-90], speed)
    release()
    home(speed)

def pickupFromLaser(speed=40):
    home(speed)
    current_angles = robot.get_angles()
    x = current_angles[0]
    y = current_angles[1]
    z = current_angles[2]
    rx = current_angles[3]
    ry = current_angles[4]
    rz = current_angles[5]
    moveTo([159.9, y, z, rx, ry, rz], speed)
    time.sleep(1)
    moveTo([159.9, 80, -47, 0, -35.5, -90], speed)
    grip()
    home(speed)

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