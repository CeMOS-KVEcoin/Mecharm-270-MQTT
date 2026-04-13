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
    print("home skill starting")
    moveTo([0, 0, 0, 0, 0, 0], speed)
    print("home skill done")

def grip():
    vacuum.on()

def release():
    vacuum.off()

## Service Skills

def pickupFromConveyor1(self, speed=40):
    print("pickupFromConveyor1 skill starting")
    self.moveTo([-151, 0, 0, 0, 0, -90], speed)
    self.moveTo([-151, 0, 41, 0, -40, -90], speed)

    self.pickup(speed)
    print("pickupFromConveyor1 done")


def placeToConveyor2(self, speed=40):
    self.moveTo([132, 0, 0, 0, 0, -90], speed)
    self.moveTo([132, 0, 39, 0, -40, -90], speed)

    self.release()
    self.moveTo([132, 0, 35, 0, -40, -90], speed)
    time.sleep(2)

    self.home(speed)

def placeToLaser(self, speed=40):
    #tbd
    self.release(vacuum)
    self.home(speed)

def turnChip(self, speed=40):
    #move to podest A
    #release
    #move to podest B
    #grip or pickup
    #tbd
    self.home(speed)

def placeToPedestal(self, speed=40):
    self.moveTo([0, 0, 0, 0, 0, -179], speed)
    time.sleep(2)

    self.moveTo([-6, 25, 21.5, -10, -41, -179], 20)
    time.sleep(2)

    #vacuum.off()
    self.release(vacuum)
    time.sleep(4)

    self.moveTo([5, 0, 20, 0, -10, -179], speed)
    time.sleep(2)

    self.home(speed)