import openmeteo_requests

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 51.529,
    "longitude": -3.191,
    "daily": "precipitation_sum",
    "timezone": "Europe/London",
    "start_date": "2024-07-24",
    "end_date": "2024-07-26"
}
om = openmeteo_requests.Client()
responses = om.weather_api(url, params=params)
response = responses[0]
daily = response.Daily()
daily_rain_sum = sum(daily.Variables(0).ValuesAsNumpy())
print(daily_rain_sum)
