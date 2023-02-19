import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import requests
from adjustText import adjust_text

REGIONS = ['eur', 'afr', 'ame', 'asia', 'oce']
REST_COUNTRIES_ENDPOINT = "https://restcountries.com/v3.1/"
OPEN_WEATHER_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"
OPEN_WEATHER_KEY = ""
DEGREE_SIGN = u'\N{DEGREE SIGN}'


def get_regional_data():
    data = {}
    for region in REGIONS:
        region_data = requests.get(f"{REST_COUNTRIES_ENDPOINT}/region/{region}")
        if region_data.status_code == 200:
            for country in region_data.json():
                try:
                    data[country['name']['common']] = {'lat': country['capitalInfo']['latlng'][1],
                                                   'long': country['capitalInfo']['latlng'][0], 'flag': country['flag'],
                                                   'capital': country['capital'][0]}
                except:
                    continue
        else:
            raise requests.exceptions.RequestException(f"Invalid status code for request {region_data.url}, try again")
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
        if response.status_code == 401:
            raise requests.exceptions.RequestException("Invalid API key. Please add a valid key to the top of this file")
    return weather_data


def annotate_graph(ax, weather_data, capital_cities_coords):
    texts = []
    for capital, temp in weather_data.items():
        texts.append(ax.text(s=f"{capital}: {temp}{DEGREE_SIGN}C", x=capital_cities_coords.get(capital)[0],
                             y=capital_cities_coords.get(capital)[1], fontsize=2))
    adjust_text(texts, arrowprops=dict(arrowstyle="-", color='r', lw=0.2))


def plot_graph():
    fig, ax = plt.subplots(figsize=(24, 16))
    countries = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    countries.plot(color="lightgrey", ax=ax)
    country_data = get_regional_data()
    capital_cities_coords = {values.get('capital'): [values.get('lat'), values.get('long')]
                             for country, values in country_data.items()}
    lats = [x[0] for x in capital_cities_coords.values()]
    longs = [x[1] for x in capital_cities_coords.values()]
    weather_data = get_weather_data(capital_cities_coords.keys())
    ax.scatter(lats, longs, s=0.5)
    annotate_graph(ax, weather_data, capital_cities_coords)
    plt.savefig('map.svg')
    plt.show()


plot_graph()



