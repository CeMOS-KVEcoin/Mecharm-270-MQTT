import skills
import time

def pickupFromConveyor1(robot, vacuum, speed=40):
    skills.moveTo(robot, [-151, 0, 0, 0, 0, -90], speed)
    skills.moveTo(robot, [-151, 0, 41, 0, -40, -90], speed)

    skills.pickup(robot, vacuum, speed)


def placeToConveyor2(robot, vacuum, speed=40):
    skills.moveTo(robot, [132, 0, 0, 0, 0, -90], speed)
    skills.moveTo(robot, [132, 0, 39, 0, -40, -90], speed)

    skills.release(vacuum)
    skills.moveTo([132, 0, 35, 0, -40, -90], speed)
    time.sleep(2)

    skills.home(speed)

def placeToLaser(robot, vacuum, speed=40):
    #tbd
    skills.release(vacuum)
    skills.home(speed)

def turnChip(robot, vacuum, speed=40):
    #move to podest A
    #release
    #move to podest B
    #grip or pickup
    #tbd
    skills.home(speed)

def placeToPedestal(robot, vacuum, speed=40):
    skills.moveTo([0, 0, 0, 0, 0, -179], speed)
    time.sleep(2)

    skills.moveTo([-6, 25, 21.5, -10, -41, -179], 20)
    time.sleep(2)

    #vacuum.off()
    skills.release(vacuum)
    time.sleep(4)

    skills.moveTo([5, 0, 20, 0, -10, -179], speed)
    time.sleep(2)

    skills.home(speed) 
