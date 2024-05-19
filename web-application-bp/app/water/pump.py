import time
import RPi.GPIO as GPIO

class Pump:
    def __init__(self, relay):
        self.relay = relay
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.relay, GPIO.OUT)

    def pump_on(self):
        GPIO.output(self.relay, True)

    def pump_off(self):
        GPIO.output(self.relay, False)