import time
import grovepi
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
relay = 3
grovepi.pinMode(relay, "OUTPUT")
grovepi.digitalWrite(relay, 1)
time.sleep(1)
grovepi.digitalWrite(relay, 0)
time.sleep(1)
grovepi.digitalWrite(relay, 1)
time.sleep(1)
grovepi.digitalWrite(relay, 0)