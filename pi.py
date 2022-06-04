import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time
import grovepi
import math
import pumpmodule

#moisture_sensor_01 = 0
#moisture_sensor_02 = 1
#temperature_sensor = 2
relay = 3
switch = 12
GPIO.setmode(GPIO.BOARD)
grovepi.pinMode(relay, "OUTPUT")
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def getSensor():
    moisture_01 = grovepi.analogRead(moisture_sensor_01)
    moisture_02 = grovepi.analogRead(moisture_sensor_02)
    temperature = grovepi.analogRead(temperature_sensor)

    b = 4275
    r0 = 100000
    r = 1023.0 / temperature - 1.0
    r = 100000.0 * r
    temperature = round(1.0 / (math.log(r/100000.0) / b + 1 / 298.15) - 273.15, 3)

    moisture_01 = round(float(1 - (moisture_01 - 500) / 250), 3)
    moisture_02 = round(float(1 - (moisture_02 - 500) / 250), 3)

    if moisture_01 < 0.3 and moisture_02 < 0.3:
        client.publish("Water", True)
    else:
        client.publish("Water", False)
    return moisture_01, moisture_02, temperature

def onConnect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
        pumpmodule.water_off(relay, switch)
    else:
        print("Bad connection, returned: ", rc)

def onDisconnect(client, userdata, flags, rc = 0):
    pumpmodule.water_off(relay, switch)
    print("Disconnected, returned: ", str(rc))

def onMessage(client, userdata, message):
    message = int(message.payload.decode("utf-8"))
    print("Recieved message: ", message)
    pumpmodule.water_on(relay, switch)
    time.sleep(message)
    pumpmodule.water_off(relay, switch)
        
mqtt_broker = "192.168.1.200"
client = mqtt.Client("GardenPi")
client.on_connect = onConnect
client.on_disconnect = onDisconnect
client.on_message = onMessage
client.connect(mqtt_broker)
client.loop_start()

while True:
    """
    # insert when sensors are setup
    moisture_01, moisture_02, temperature = getSensor()
    client.publish("Moisture_01", moisture_01)
    print(moisture_01)
    client.publish("Moisture_02", moisture_02)
    print(moisture_02)
    client.publish("Temperature", temperature)
    print(temperature)
    time.sleep(1)
    """
    client.subscribe("Water")
    time.sleep(1)

client.loop_stop()
client.disconnect(mqttBroker)
