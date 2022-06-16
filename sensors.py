#moisture_sensor_01 = 0
#moisture_sensor_02 = 1
#temperature_sensor = 2

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