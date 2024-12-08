import requests
from flask import Flask, jsonify
app = Flask(__name__)
API_KEY = '	rlyGyOeGgcpNK4NkG3YAJhU853JJd2DM'
BASE_URL = 'http://dataservice.accuweather.com'

def get_weather(lat, lon):
    # Получаем ключ местоположения
    location_url = f"{BASE_URL}/locations/v1/cities/geoposition/search?apikey={API_KEY}&q={lat},{lon}"
    location_response = requests.get(location_url)
    location_data = location_response.json()

    if location_response.status_code != 200:
        return {"error": "Не удалось получить данные о местоположении."}

    location_key = location_data['Key']

    # Получаем данные о погоде
    weather_url = f"{BASE_URL}/currentconditions/v1/{location_key}?apikey={API_KEY}&language=ru&details=true"
    weather_response = requests.get(weather_url)
    weather_data = weather_response.json()

    if weather_response.status_code != 200:
        return {"error": "Не удалось получить данные о погоде."}

    # Извлекаем требуемые параметры
    current_weather = weather_data[0]
    temperature = current_weather['Temperature']['Metric']['Value']
    humidity = current_weather['RelativeHumidity']
    wind_speed = current_weather['Wind']['Speed']['Metric']['Value']
    precipitation_probability = current_weather.get('PrecipitationSummary', {}).get('PrecipitationProbability', 0)

    return {
        "temperature": temperature,
        "humidity": humidity,
        "wind_speed": wind_speed,
        "precipitation_probability": precipitation_probability
    }
@app.route('/weather/<float:lat>/<float:lon>')
def weather(lat, lon):
    weather_data = get_weather(lat, lon)
    return jsonify(weather_data)

if __name__ == '__main__':
    app.run(debug=True)

# Можно зайти на http://127.0.0.1:5000/weather/55.7558/37.6173 и посмотреть погоду для Москвы