import RPi.GPIO as GPIO


class Pump(object):
    def __init__(self, relay):
        self.relay = relay
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.relay, GPIO.OUT)

    def pump_on(self):
        GPIO.output(self.relay, True)
        return

    def pump_off(self):
        GPIO.output(self.relay, False)
        return
