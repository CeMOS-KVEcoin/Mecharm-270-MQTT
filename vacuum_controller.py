import RPi.GPIO as GPIO

class VacuumController:
    def __init__(self, on_pin=20, off_pin=21):
        self.on_pin = on_pin
        self.off_pin = off_pin

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
