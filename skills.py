import time

def pickup(robot, vacuum, speed=40):
    grip(vacuum)
    time.sleep(2)
    home(speed)  

def moveTo(robot, angles, speed=40):
    robot.move_angles(angles, speed)
    time.sleep(2)

def home(robot, speed=40):
    moveTo(robot, [0, 0, 0, 0, 0, 0], speed)

def grip(vacuum):
    vacuum.on()

def release(vacuum):
    vacuum.off()
