import os
import RPi.GPIO as GPIO
from mqtt_config import VACUUM_ON_PIN, VACUUM_OFF_PIN

class VacuumController:
    def __init__(self):
        self.on_pin = VACUUM_ON_PIN
        self.off_pin = VACUUM_OFF_PIN

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
