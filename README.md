# Automated Garden

A web application built in Flask for watering outdoor plants with a Raspberry Pi or any other similar device.

This was designed with specific components and devices in mind, it can work for you but will need editing. The configuration section below outlines what needs to be done.

## Configuration
The files pump.py and valve.py will likely not work with your system. You will need to replace these with your own file(s) that control your component(s).
These are imported and used within routes.py and \_\_init__.py, change these imports to match yours instead.
```
from .pump import Pump 
from .valve import Valve
```
Within routes.py the water_event function is used to water plants for x amount of time, you need to replace the highlighted lines with your corresponding setup and on/off functions.
```
def water_event(water_time):
    water_status = WaterStatus.query.first()
    pump_relay = 16                           <-- REPLACE WITH YOUR SETUP AND TURN ON FUNCTIONS
    valve_relay = 18                          <--
    valve_switch = 12                         <--
    valve = Valve(valve_relay, valve_switch)  <--
    pump = Pump(pump_relay)                   <--
    valve.valve_on()                          <--
    pump.pump_on()                            <--
    for x in range(water_time):
        time.sleep(1)
        if event.is_set():
            valve.valve_off()                 <-- REPLACE WITH YOUR TURN OFF FUNCTIONS
            pump.pump_off()                   <--
            event.clear()
            return
    valve.valve_off()                         <-- REPLACE WITH YOUR TURN OFF FUNCTIONS
    pump.pump_off()                           <--
    water_status.status = False
    db.session.commit()
    return
```
Within \_\_init__.py lines 52 to 60 turn the components off if the host device restarts, replace this with your setup and off function(s). 
```
    # incase of restart during water
    from .pump import Pump
    from .valve import Valve
    pump_relay = 16
    valve_relay = 18
    valve_switch = 12
    valve = Valve(valve_relay, valve_switch)
    pump = Pump(pump_relay)
    valve.valve_off()
    pump.pump_off()
```
That is everything that needs to be replaced/changed.

## Installation
1. Ensure Python3 is installed before starting.
2. Check the service file provided as it will likely need to be changed depending on where you have this repository saved. Change the ExecStart line to contain your full directory path.
```
[Unit]
Description=Automated Garden Flask Application (THIS CAN ALSO BE CHANGED)

[Service]
Type=simple
ExecStart=/YOUR PATH TO/Automated-Garden/web-application/venv/bin/gunicorn --chdir /YOUR PATH TO/Automated-Garden/web-application main:app
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```
3. Change the api file to contain your OpenWeatherMap API key.
4. Once these values are correct everything should be able to be installed using the setup script ```sudo ./setup.sh```.
5. An account for the site can be created using Flask Click CLI, to use it move to the web-application directory and activate the virtual environment with ```source venv/bin/activate```.
6. Use the command ```Flask create-user YOUR_USERNAME YOUR_PASSWORD``` to create a user account.
7. You should now be able to access the site and use its features as long as the configuration was done correctly. 

## Front End
The front end of the web application is very simple and may be updated at a later date. It contains the following three sections:
1. Login page for basic authenitcation.
2. Interactive graph that displays temperature, humidity, rain fall recorded, and rain chance.
3. Water page where you can specify in seconds how long the plants should be watered for, can be cancelled mid process.

## Back End
The majority of this web application is controlled via the back end, further information is provided below:
1. All weather data is collected from OpenWeatherMap using their API. This request returns a large JSON which is sorted and stored within our SQL database.
2. The functions that retrieve new weather data and delete old weather data are contained within jobs.py, here the scheduler automatically executes these functions at a certain time and day.
4. When selecting to view the weather for a certain date the database is intially queried and formatted appropriately for Chart.js.
5. Watering makes use of flask executor and threading where components are toggled in the background and running processes are cancelled with events.

## Important
Validation has not been added yet so this web application is intended for local host only.

## To Do
- [ ] Validation on authentication attempts.
- [ ] Option for watering to be done automatically based on certain parameters that can be tweaked.
- [ ] Complete the config readme section


