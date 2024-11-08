"""Classes for systems used by the watering process.

Ensure a method called on and off are included for each class present.
These methods will be called during the watering process so make sure
everything is as mentioned. In the case where multiple systems or devices
are used for one plant combine them into a single class.
"""
import RPi.GPIO as GPIO
import time


class ValvePump:
    """Container class for valve and pump."""

    def __init__(self):
        self.valve = self.Valve()
        self.pump = self.Pump()
        self.wait = 2

    def on(self):
        self.valve.on()
        time.sleep(self.wait)
        self.pump.on()

    def off(self):
        self.valve.off()
        time.sleep(self.wait)
        self.pump.off()

    class Valve:
        """Controls outdoor valve.

        The input readings for the switch are not stable
        and often look like 000010101101111. Thus, the
        following methods deal with this and avoid leaving
        the valve half open.
        """

        def __init__(self):
            self.relay = 18
            self.switch = 12
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

    class Pump:
        """Controls outdoor pump."""

        def __init__(self):
            self.relay = 16
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self.relay, GPIO.OUT)

        def on(self):
            GPIO.output(self.relay, True)
            return

        def off(self):
            GPIO.output(self.relay, False)
            return
