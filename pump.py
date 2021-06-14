import time
import grovepi
import RPi.GPIO as GPIO

run = True

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)
switch = 12
relay = 3
grovepi.pinMode(relay, "OUTPUT")

def water_on():
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
def water_off():
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

try:
	while run:
		inp = int(input("water: 1/0"))
		if (inp == 1):
			water_on()
		elif (inp == 0):
			water_off()
except KeyboardInterrupt:
	grovepi.digitalWrite(relay, 0)
	run = False

