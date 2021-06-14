import time
import grovepi
import RPi.GPIO as GPIO

temperature_sensor = 1
moisture_sensor_01 = 0
moisture_sensor_02 = 2
relay = 2
grovepi.pinMode(relay, "OUTPUT")
run = True

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)


try:
	while run:
		#moisture_01 = grovepi.analogRead(moisture_sensor_01)
		#moisture_02 = grovepi.analogRead(moisture_sensor_02)
		#temperature = grovepi.analogRead(temperature_sensor)
		
		#moisture_01 = float(moisture_01 - 500) / 250
		#moisture_02 = float(moisture_02 - 500) / 250
		
		#print("moisture ", moisture_01, moisture_02)
		#print("temperature ", temperature)
		
		#i = input("relay: 1/0")
		#print(i)
		
		#if i == "1":
		grovepi.digitalWrite(relay, 1)
		i = GPIO.input(12)
		print(i)
		#grovepi.digitalWrite(relay, 1)
		#else:
		#	grovepi.digitalWrite(relay, 0)
		
		time.sleep(0.1)	
except KeyboardInterrupt:
	grovepi.digitalWrite(relay, 0)
	run = False
