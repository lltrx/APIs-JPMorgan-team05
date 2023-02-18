import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import geopandas as gpd
import requests

REGIONS = ['eur', 'afr', 'ame', 'asia', 'aus']
REST_COUNTRIES_ENDPOINT = "https://restcountries.com/v3.1/"
OPEN_WEATHER_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"
OPEN_WEATHER_KEY = "b6c463e3b83566fd97b08df8a6b9578a"


def get_country_data():
    data = {}
    regions = requests.get(f"{REST_COUNTRIES_ENDPOINT}/region/eur").json()
    for country in regions:
        data[country['name']['common']] = {'lat': country['capitalInfo']['latlng'][1], 'long': country['capitalInfo']['latlng'][0], 'flag': country['flag'],
                                           'capital': country['capital'][0]}
    return pd.DataFrame.from_dict(data)


def get_weather_data(capital_cities):
    weather_data = {}
    for city_name in capital_cities:
        params = {
            "q": city_name,
            "appid": OPEN_WEATHER_KEY,
            "units": "metric"
        }
        response = requests.get(OPEN_WEATHER_ENDPOINT, params=params)
        if response.status_code == 200:
            data = response.json()
            temperature = data.get("main", {}).get("temp")
            weather_data[city_name] = temperature
    return weather_data

fig, ax = plt.subplots(figsize=(12, 8))
countries = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
countries.plot(color="lightgrey", ax=ax)
country_data = get_country_data()
capital_cities = [values.get('capital') for country, values in country_data.items()]
latlongs = [[values.get('lat'), values.get('long')] for country, values in country_data.items()]
lats = [x[0] for x in latlongs]
longs = [x[1] for x in latlongs]
weather_data = get_weather_data(capital_cities)
uk = country_data['United Kingdom']
print(uk, uk['lat'])
print(lats)
print(longs)
ax.scatter(lats, longs, s=0.5)
for i, txt in enumerate(weather_data.values()):
    ax.annotate(txt, (lats[i], longs[i]), fontsize=8)
plt.show()


