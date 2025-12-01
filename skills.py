import time

def pickup(robot, vacuum, speed=40):
    robot.move_angles([-151, 0, 0, 0, 0, -90], speed)
    time.sleep(2)

    robot.move_angles([-151, 0, 41, 0, -40, -90], speed)
    time.sleep(2)

    vacuum.on()
    time.sleep(2)

    robot.home(speed)

def release_conveyor2(robot, vacuum, speed=40):
    robot.move_angles([132, 0, 0, 0, 0, -90], speed)
    time.sleep(2)

    robot.move_angles([132, 0, 39, 0, -40, -90], speed)
    time.sleep(2)

    vacuum.off()
    robot.move_angles([132, 0, 35, 0, -40, -90], speed)
    time.sleep(4)

    robot.home(speed)

def put_pedastel(robot, vacuum, speed=40):
    robot.move_angles([0, 0, 0, 0, 0, -179], speed)
    time.sleep(2)

    robot.move_angles([0, 15, 20, 0, -10, -179], speed)
    time.sleep(2)

    vacuum.off()
    time.sleep(4)

    robot.home(speed)   

def release(vacuum):
    vacuum.off()


def home(robot, speed=40):
    robot.home(speed)
