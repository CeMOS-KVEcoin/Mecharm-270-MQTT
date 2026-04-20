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

def moveTo(angles, speed=40):
    robot.move_angles(angles, speed)
    time.sleep(2)

def home(speed=30):
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
    #tbd
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
    #home(speed)
    #time.sleep(2)
    robot.release()

def show_angles():
    return "Angles: {robot.get_angles()}"