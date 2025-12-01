import time

def pickup(robot, vacuum, speed=40):
    robot.move_angles([-151, 0, 0, 0, 0, -90], speed)
    time.sleep(2)

    robot.move_angles([-151, 0, 41, 0, -40, -90], speed)
    time.sleep(2)

    vacuum.on()
    time.sleep(1)

    robot.home(speed)


def release(vacuum):
    vacuum.off()


def home(robot, speed=40):
    robot.home(speed)
