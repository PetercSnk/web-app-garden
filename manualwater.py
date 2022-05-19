import paho.mqtt.client as mqtt
import time

# for use until sensors are setup
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
client = mqtt.Client("P")

client.on_connect = onConnect
client.on_disconnect = onDisconnect
client.on_message = onMessage
client.connect(mqttBroker)
client.loop_start()

time.sleep(0.5)
max_timer = 300
while True:
    try:
        timer = int(input("Watering time in seconds, (0) to cancel: "))
        if timer < max_timer and timer != 0:
            client.publish("Water", timer)
            break
        elif timer == 0:
            break
        else:
            print("Timer exceeds max ", max_timer, " seconds")
    except:
        print("Invalid type")

client.loop_stop()
client.disconnect(mqttBroker)