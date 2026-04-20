import os
from dotenv import load_dotenv
from pymycobot import MechArm270
from pymycobot.genre import Coord, Angle

load_dotenv()

class RobotController:
    def __init__(self):
        self.Angle = None
        port = os.getenv("SERIAL_PORT", "/dev/ttyAMA0")
        baud = int(os.getenv("BAUD", "1000000"))
        print(f"[Motion] Initialise MechArm at Port {port} with Baudrate {baud}")
        self.mc = MechArm270(port, baud)

### Joint and Coordinate Control

    def move_angles(self, angles, speed=40):
        self.mc.send_angles(angles, speed)

    def move_coords(self, coords, speed=40):
        self.mc.send_coords(coords, speed)

    def get_coords(self):
        return self.mc.get_coords()

    def get_angles(self):
        return self.mc.get_angles()

### Movement Control

    def jog_angle(self, joint_index, direction, speed=40): #(1,1,50) for example to move joint 1 in positive direction at speed 50
        self.mc.jog_angle(joint_index, direction, speed)

    def jog_coord(self, axis_index, direction, speed=40): #(2,0,50) for example to move along Y-axis in negative direction at speed 50
        self.mc.jog_coord(axis_index, direction, speed)

    def stop(self):
        self.mc.stop()

    def is_moving(self):
        return self.mc.is_moving() #Check if the robot is currently moving (1=moving, 0=stopped)

    def pause(self):
        self.mc.pause() # Pause current movement

    def resume(self):
        self.mc.resume() # Resume paused movement

### System and Power
    
    def power_on(self):
        self.mc.power_on()

    def power_off(self):
        self.mc.power_off()

    def reset(self):
        self.mc.reset()

    def status(self):
        return self.mc.is_power_on() #Check power status (1=on, 0=off)

    def release(self):
        self.mc.release_all_servos() #Disable all servos (stop holding position, allowing manual movement)
