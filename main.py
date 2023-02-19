import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
import requests
from adjustText import adjust_text

REGIONS = ['eur', 'afr', 'ame', 'asia', 'aus']
REST_COUNTRIES_ENDPOINT = "https://restcountries.com/v3.1/"
OPEN_WEATHER_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"
OPEN_WEATHER_KEY = "b6c463e3b83566fd97b08df8a6b9578a"
DEGREE_SIGN = u'\N{DEGREE SIGN}'


def get_regional_data(regions):
    data = {}
    if isinstance(regions, str):
        if regions.lower() == 'all':
            regions = REGIONS
        else:
            regions = [regions]
    for region in regions:
        region_data = requests.get(f"{REST_COUNTRIES_ENDPOINT}/region/{region}").json()
        for country in region_data:
            try:
                data[country['name']['common']] = {'lat': country['capitalInfo']['latlng'][1],
                                               'long': country['capitalInfo']['latlng'][0], 'flag': country['flag'],
                                               'capital': country['capital'][0]}
            except:
                continue
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


def plot_graph():
    fig, ax = plt.subplots(figsize=(24, 16))
    countries = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
    countries.plot(color="lightgrey", ax=ax)
    country_data = get_regional_data('eur')
    capital_cities = {values.get('capital'): [values.get('lat'), values.get('long')]
                      for country, values in country_data.items()}
    lats = [x[0] for x in capital_cities.values()]
    longs = [x[1] for x in capital_cities.values()]
    weather_data = get_weather_data(capital_cities.keys())
    ax.scatter(lats, longs, s=0.5)
    texts = []
    for capital, temp in weather_data.items():
        texts.append(ax.text(s=f"{capital}: {temp}{DEGREE_SIGN}C", x=capital_cities.get(capital)[0],
                             y=capital_cities.get(capital)[1], fontsize=2))
    adjust_text(texts, arrowprops=dict(arrowstyle="-", color='r', lw=0.5))
    plt.savefig('map.svg')
    plt.show()


plot_graph()



