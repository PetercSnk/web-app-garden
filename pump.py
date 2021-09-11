import time

def water_on(relay, switch):
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


