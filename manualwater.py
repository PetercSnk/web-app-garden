import paho.mqtt.client as mqtt
import time
import numpy as np
from datetime import datetime
import os
import pandas as pd

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

client = mqtt.Client("P")
client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set("Sunuku", "5nEAH5egV3YM26D")
client.connect("760086dbd62d4a53bd2bd7421eb7fc94.s2.eu.hivemq.cloud", 8883)
client.on_connect = onConnect
client.on_disconnect = onDisconnect
client.on_message = onMessage
client.loop_start()

time.sleep(0.5)
max_timer = 300
while True:
    try:
        timer = int(input("Watering time in seconds, (0) to cancel: "))
        if timer < max_timer and timer != 0:
            client.publish("Water", timer)
            dbname = "history.csv"
            if not os.path.exists(dbname):
                file = open(dbname, "x")
                file.close()
            df = pd.read_csv(dbname, names = ["datetime", "length"], header = 0)
            dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            df.loc[len(df.index)] = [dt_string, timer]
            df.to_csv(dbname)
            break
        elif timer == 0:
            break
        else:
            print("Timer exceeds max ", max_timer, " seconds")
    except:
        print("Invalid type")

client.loop_stop()
client.disconnect(mqttBroker)