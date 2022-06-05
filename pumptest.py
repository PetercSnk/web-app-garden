import time
import grovepi
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def water_on(relay, switch):
    grovepi.pinMode(relay, "OUTPUT")
    grovepi.digitalWrite(relay, 1)
    high = False
    low = False
    while True:
        i = GPIO.input(switch)
        print(i)
        if (i == 0):
            low = True
            time.sleep(0.1)
        if (i == 1):
            high = True
            time.sleep(0.1)
        if high and not low:
            high = False
        if high and low:
            grovepi.digitalWrite(relay, 0)
            break

def water_off(relay, switch):
    grovepi.pinMode(relay, "OUTPUT")
    grovepi.digitalWrite(relay, 1)
    high = False
    low = False
    while True:
        i = GPIO.input(switch)
        print(i)
        if (i == 1):
            high = True
            time.sleep(0.1)
        if (i == 0):
            low = True
            time.sleep(0.1)
        if low and not high:
            low = False
        if high and low:
            grovepi.digitalWrite(relay, 0)
            break

#water_on(3, 12)
#time.sleep(5)
water_off(3, 12)
