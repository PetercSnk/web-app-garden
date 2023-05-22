from datetime import datetime
import requests

def kelvin_to_celsius(kelvin):
    return (kelvin - 273.15)

def request_weather():
    BASE_URL = "http://api.openweathermap.org/data/2.5/forecast?"
    with open("api.txt", "r") as f:
        API_KEY = f.read()
    LAT = "51.529"
    LON = "-3.191"
    url = BASE_URL + "lat=" + LAT + "&lon=" + LON + "&appid=" + API_KEY
    json_response = requests.get(url).json()
    return json_response

def extract_data(json):
    timezone = json["city"]["timezone"]
    sunrise = datetime.utcfromtimestamp(json["city"]["sunrise"] + timezone).time()
    sunset = datetime.utcfromtimestamp(json["city"]["sunset"] + timezone).time()
    current_date = datetime.now().date()
    for t_dict in json["list"]:
        date = datetime.utcfromtimestamp(t_dict["dt"] + timezone)
        if date.date() == current_date:
            temperature = round(kelvin_to_celsius(t_dict["main"]["temp"]), 2)
            temperature_min = round(kelvin_to_celsius(t_dict["main"]["temp_min"]), 2)
            temperature_max = round(kelvin_to_celsius(t_dict["main"]["temp_max"]), 2)
            humidity = t_dict["main"]["humidity"]
            weather = t_dict["weather"][0]["description"]
            rain_chance = t_dict["pop"]
            if "rain" in t_dict:
                rain_recorded = t_dict["rain"]["3h"]
            else:
                rain_recorded = 0
            print(timezone, sunrise, sunset, date, temperature, temperature_min, temperature_max, humidity, weather, rain_chance, rain_recorded)



j = request_weather()
extract_data(j)
