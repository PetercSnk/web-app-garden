import paho.mqtt.client as mqtt
import time

def onConnect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
    else:
        print("Bad connection, returned: ", rc)

def onDisconnect(client, userdata, flags, rc = 0):
    print("Disconnected, returned: ", str(rc))

def onMessage(client, userdata, message):
    print("Received message: ", str(message.payload.decode("utf-8")))
    
mqttBroker = "192.168.1.200"
client = mqtt.Client("Main")

client.on_connect = onConnect
client.on_disconnect = onDisconnect
client.on_message = onMessage
client.connect(mqttBroker)
client.loop_start()
while True:
    client.subscribe("Water")
    time.sleep(1)
client.loop_stop()
client.disconnect(mqttBroker)
