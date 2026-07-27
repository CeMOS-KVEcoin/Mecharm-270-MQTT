import os
import time
import threading
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
        self._serial_lock = threading.RLock()

### Joint and Coordinate Control

    def move_angles(self, angles, speed=40):
        with self._serial_lock:
            self.mc.send_angles(angles, speed)

    def move_coords(self, coords, speed=40):
        with self._serial_lock:
            self.mc.send_coords(coords, speed)

    def get_coords(self):
        with self._serial_lock:
            return self.mc.get_coords()

    def get_angles(self):
        with self._serial_lock:
            return self.mc.get_angles()

    def send_angle(self, angle_value, degree, speed):
        with self._serial_lock:
            self.mc.send_angle(angle_value, degree, speed)

### Movement Control

    def jog_angle(self, joint_index, direction, speed=40): #(1,1,50) for example to move joint 1 in positive direction at speed 50
        self.mc.jog_angle(joint_index, direction, speed)

    def jog_coord(self, axis_index, direction, speed=40): #(2,0,50) for example to move along Y-axis in negative direction at speed 50
        self.mc.jog_coord(axis_index, direction, speed)

    def stop(self):
        acquired = self._serial_lock.acquire(timeout=2)
        try:
            result = self.mc.stop()
            time.sleep(0.05)  # Controller Zeit geben, den Stop zu verarbeiten
            return result
        finally:
            if acquired:
                self._serial_lock.release()

    def is_moving(self):
        with self._serial_lock:
            return self.mc.is_moving()  # Check if the robot is currently moving (1=moving, 0=stopped)

    def pause(self):
        acquired = self._serial_lock.acquire(timeout=2)
        try:
            result = self.mc.pause()
            time.sleep(0.05)
            return result
        finally:
            if acquired:
                self._serial_lock.release()

    def resume(self):
        with self._serial_lock:
            result = self.mc.resume()
            time.sleep(0.05)
            return result

### System and Power

    def power_on(self):
        with self._serial_lock:
            self.mc.power_on()

    def power_off(self):
        with self._serial_lock:
            self.mc.power_off()

    def status(self):
        with self._serial_lock:
            return self.mc.is_power_on()  # Check power status (1=on, 0=off)

    def release(self):
        with self._serial_lock:
            self.mc.release_all_servos()  # Disable all servos (stop holding position, allowing manual movement)
