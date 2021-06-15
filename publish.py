import paho.mqtt.client as mqtt
import time
import grovepi
import math

moisture_sensor_01 = 0
moisture_sensor_02 = 1
temperature_sensor = 2
relay = 2
grovepi.pinMode(relay, "OUTPUT")
water_timer = 5

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
        #grovepi.digitalWrite(relay, 1)
        #time.sleep(water_timer)
        water = True
    else:
        #grovepi.digitalWrite(relay, 0)
        water = False

    return moisture_01, moisture_02, temperature, water

def onConnect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
    else:
        print("Bad connection, returned: ", rc)

def onDisconnect(client, userdata, flags, rc = 0):
    print("Disconnected, returned: ", str(rc))

def onMesasge(client, userdata, message):
    print("Recieved message: ", str(message.payload.decode("utf-8")))

mqttBroker = "192.168.1.200"
client = mqtt.Client("GardenPi")

client.on_connect = onConnect
client.on_disconnect = onDisconnect
client.connect(mqttBroker)
client.loop_start()

while True:
    moisture_01, moisture_02, temperature, water = getSensor()
    client.publish("Moisture_01", moisture_01)
    print(moisture_01)
    client.publish("Moisture_02", moisture_02)
    print(moisture_02)
    client.publish("Temperature", temperature)
    print(temperature)
    client.publish("Water", water)
    time.sleep(1)

client.loop_stop()
client.disconnect(mqttBroker)
