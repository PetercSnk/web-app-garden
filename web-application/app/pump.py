import time
import RPi.GPIO as GPIO

pump_relay = 16

class Pump:
    def __init__(self, relay):
        self.relay = relay
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.relay, GPIO.OUT)

    def pump_on():
        GPIO.output(self.relay, True)

    def pump_off():
        GPIO.output(self.relay, False)