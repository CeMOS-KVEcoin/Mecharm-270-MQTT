import os
from dotenv import load_dotenv
from pymycobot import MechArm270

load_dotenv()

class RobotController:
    def __init__(self):
        port = os.getenv("SERIAL_PORT", "/dev/ttyAMA0")
        baud = int(os.getenv("BAUD", "1000000"))
        self.mc = MechArm270(port, baud)

    def home(self, speed=40):
        self.mc.send_angles([0, 0, 0, 0, 0, 0], speed)

    def move_angles(self, angles, speed=40):
        self.mc.send_angles(angles, speed)

    def get_coords(self):
        return self.mc.get_coords()
