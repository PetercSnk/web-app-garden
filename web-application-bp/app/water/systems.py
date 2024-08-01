"""Classes for systems used by watering process.

Ensure a method called on and off are included for each class present.
These methods will be called during the watering process so make sure
everything is ok. In the case where multiple systems or devices are used
for one plant combine them into a single class.
"""
from flask import current_app
# from app.water.valve import Valve
# from app.water.pump import Pump
# import time
#
#
# class Herbs(Valve, Pump):
#     def __init__(self):
#         Valve.__init__(self, 18, 12)
#         Pump.__init__(self, 16)
#         self.wait = 2
#
#     def on(self):
#         Valve.on()
#         time.sleep(self.wait)
#         Pump.on()
#
#     def off(self):
#         Valve.off()
#         time.sleep(self.wait)
#         Pump.off()


class TEST(object):
    def __init__(self):
        self.atr = "TEST_ATR"

    def on(self):
        current_app.logger.debug("ON")

    def off(self):
        current_app.logger.debug("OFF")
