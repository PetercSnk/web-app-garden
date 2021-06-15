import paho.mqtt.client as mqtt
import time

def onMessage(client, userdata, message):
    print("Received message: ", str(message.payload.decode("utf-8")))

def onLog(client, userdata, level, buf):
    print("Log: ", buf)

def onConnect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
    else:
        print("Bad connection, returned: ", rc)

def onDisconnect(client, userdata, flags, rc = 0):
    print("Disconnected, returned: ", str(rc))

mqttBroker = "192.168.1.200"
client = mqtt.Client("Main")

client.on_connect = onConnect
client.on_disconnect = onDisconnect
#client.on_log = onLog
client.on_message = onMessage

client.connect(mqttBroker)
client.loop_start()
client.subscribe("Moisture_01")
#client.publish("Moisture_01", 50)
time.sleep(4)
client.loop_stop()
client.disconnect(mqttBroker)
