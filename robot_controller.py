from pymycobot import MechArm270

class RobotController:
    def __init__(self, port="/dev/ttyAMA0", baud=1000000):
        self.mc = MechArm270(port, baud)

    def home(self, speed=40):
        self.mc.send_angles([0, 0, 0, 0, 0, 0], speed)

    def move_angles(self, angles, speed=40):
        self.mc.send_angles(angles, speed)

    def get_coords(self):
        return self.mc.get_coords()
