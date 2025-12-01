import os
import RPi.GPIO as GPIO
from dotenv import load_dotenv

load_dotenv()

class VacuumController:
    def __init__(self):
        self.on_pin = int(os.getenv("VACUUM_ON_PIN", "20"))
        self.off_pin = int(os.getenv("VACUUM_OFF_PIN", "21"))

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.on_pin, GPIO.OUT)
        GPIO.setup(self.off_pin, GPIO.OUT)

        self.off()

    def on(self):
        GPIO.output(self.on_pin, GPIO.HIGH)
        GPIO.output(self.off_pin, GPIO.LOW)

    def off(self):
        GPIO.output(self.on_pin, GPIO.LOW)
        GPIO.output(self.off_pin, GPIO.HIGH)

    def cleanup(self):
        self.off()
        GPIO.cleanup()
