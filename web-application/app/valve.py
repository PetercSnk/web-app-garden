import time
import RPi.GPIO as GPIO

valve_relay = 18
valve_switch = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(valve_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(valve_relay, GPIO.OUT)

def valve_on(relay, switch):
    high = False
    low = False
    GPIO.output(relay, True)
    while True:
        i = GPIO.input(switch)
        if (i == 0):
            low = True
            time.sleep(0.1)
        elif (i == 1):
            high = True
            time.sleep(0.1)
        if high and not low:
            high = False
        elif high and low:
            GPIO.output(relay, False)
            break

def valve_off(relay, switch):
    high = False
    low = False
    GPIO.output(relay, True)
    while True:
        i = GPIO.input(switch)
        if (i == 0):
            low = True
            time.sleep(0.1)
        elif (i == 1):
            high = True
            time.sleep(0.1)
        if low and not high:
            low = False
        elif high and low:
            GPIO.output(relay, False)
            break

water_on(valve_relay, valve_switch)
time.sleep(2)
water_off(valve_relay, valve_switch)
