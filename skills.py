import time

from robot_controller import RobotController
from vacuum_controller import VacuumController

robot = RobotController()
vacuum = VacuumController()

## basic skills

def pickup(speed=40):
    grip()
    time.sleep(2)
    home(speed)  

#angles [x y z rx ry rz]
def moveTo(angles, speed=40):
    robot.move_angles(angles, speed)

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

def placeToLaser(speed=40):
    home(speed)
    current_angles = robot.get_angles()
    x = current_angles[0]
    y = current_angles[1]
    z = current_angles[2]
    rx = current_angles[3]
    ry = current_angles[4]
    rz = current_angles[5]
    moveTo([160, y, z, rx, ry, rz], speed)
    moveTo([160.66,83.58,-47.72,-2.63,-35.5,-93.95], speed)
    release()
    home(speed)

def turnChip(self, speed=40):
    #move to podest A
    #release
    #move to podest B
    #grip or pickup
    #tbd
    self.home(speed)

def placeToPedestal(speed=40):
    moveTo([0, 0, 0, 0, 0, -179], speed)
    time.sleep(2)

    moveTo([-6, 25, 21.5, -10, -41, -179], 20)
    time.sleep(2)

    #vacuum.off()
    release()
    time.sleep(4)

    moveTo([5, 0, 20, 0, -10, -179], speed)
    time.sleep(2)

    home(speed)

def release_servos(speed=40):
    print("releasing robot-servos now!")
    time.sleep(2)
    robot.release()

def show_angles():
     print(f"Angles: {robot.get_angles()}")