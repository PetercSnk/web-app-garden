import paho.mqtt.client as mqtt

# for use until sensors are setup
def onConnect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
    else:
        print("Bad connection, returned: ", rc)

def onDisconnect(client, userdata, flags, rc = 0):
    print("Disconnected, returned: ", str(rc))

def onMesasge(client, userdata, message):
    print("Received message: ", str(message.payload.decode("utf-8")))

mqttBroker = "192.168.1.200"
client = mqtt.Client("P")

client.on_connect = onConnect
client.on_disconnect = onDisconnect
client.connect(mqttBroker)
client.loop_start()
client.publish("Water", True)
client.loop_stop()
client.disconnect(mqttBroker)