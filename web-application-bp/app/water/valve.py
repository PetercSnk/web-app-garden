"""Required for using outdoor valve."""
import time
import RPi.GPIO as GPIO


class Valve(object):
    """Controls outdoor valve.

    The input readings for the switch are not stable
    and often look like 000010101101111. Thus, the
    following methods deal with this and avoid leaving
    the valve half open.
    """

    def __init__(self, relay, switch):
        self.relay = relay
        self.switch = switch
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.relay, GPIO.OUT)
        GPIO.setup(self.switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def on(self):
        high = False
        low = False
        GPIO.output(self.relay, True)
        while True:
            i = GPIO.input(self.switch)
            if (i == 0):
                low = True
                time.sleep(0.1)
            elif (i == 1):
                high = True
                time.sleep(0.1)
            if high and not low:
                high = False
            elif high and low:
                GPIO.output(self.relay, False)
                return

    def off(self):
        high = False
        low = False
        GPIO.output(self.relay, True)
        while True:
            i = GPIO.input(self.switch)
            if (i == 0):
                low = True
                time.sleep(0.1)
            elif (i == 1):
                high = True
                time.sleep(0.1)
            if low and not high:
                low = False
            elif high and low:
                GPIO.output(self.relay, False)
                return
