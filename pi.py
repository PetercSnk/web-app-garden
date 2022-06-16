import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import grovepi
import math
import pumpmodule

relay = 3
switch = 12
GPIO.setmode(GPIO.BOARD)
grovepi.pinMode(relay, "OUTPUT")
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def onConnect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
        pumpmodule.water_off(relay, switch)
    else:
        print("Bad connection, returned: ", rc)

def onDisconnect(client, userdata, flags, rc = 0):
    # pumpmodule.water_off(relay, switch)
    print("Disconnected, returned: ", str(rc))
    client.loop_stop()

def onMessage(client, userdata, message):
    message = int(message.payload.decode("utf-8"))
    print("Recieved message: ", message)
    pumpmodule.water_on(relay, switch)
    time.sleep(message)
    pumpmodule.water_off(relay, switch)
        
# make itself broker to fix broken pipe issue?        
mqtt_broker = "192.168.1.200"
client = mqtt.Client("GardenPi")
client.on_connect = onConnect
client.on_disconnect = onDisconnect
client.on_message = onMessage
client.connect(mqtt_broker)


client.subscribe("Water")
time.sleep(1)

client.loop_forever()

