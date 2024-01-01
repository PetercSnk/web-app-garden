# Automated Garden

A web application built in Flask for watering outdoor plants.

## Installation
1. This is designed to be installed on a Raspberry Pi or another similiar device. 
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
4. Once these values are correct everything should be able to be installed using the setup script ```sudo ./setup.sh```, the only prequisite is that Python3 is installed.

## Configuration


## Front End
The front end of the web application is very simple and may be updated at a later date. It contains the following three sections:
1. Login page for basic authenitcation.
2. Interactive graph that displays temperature, humidity, rain fall recorded, and rain chance.
3. Water page where you can specify in seconds how long the plants should be watered for, can be cancelled mid process.

## Back End
The majority of this web application is controlled via the back end, further information is provided below:
1. All weather data is collected from OpenWeatherMap using their API. This request returns a large JSON which is sorted and stored within a SQL database.
2. Getting the weather data is controlled via the scheduler which can be set to collect at a certain time and day.
3. The scheduler also deletes weather data that is x days old, these functions can be found in jobs.py.
4. 


## Important
Validation has not been added yet so this web application is intended for local host only.

## To Do
- [ ] Validation on authentication attempts.
- [ ] Option for watering to be done automatically based on certain parameters that can be tweaked.
- [ ] Complete the config readme section


