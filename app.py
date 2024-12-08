import requests
from flask import Flask, jsonify, render_template, request
app = Flask(__name__)
API_KEY = 'Mm6hOup2ONDEPbyIKOgD649PnJAArOh6'
BASE_URL = 'http://dataservice.accuweather.com'

def get_location_key(city_name):
    # Получаем ключ местоположения по названию города
    location_url = f"{BASE_URL}/locations/v1/cities/search?apikey={API_KEY}&q={city_name}"
    location_response = requests.get(location_url)
    location_data = location_response.json()
    if location_response.status_code != 200 or not location_data:
        return None
    return location_data[0]['Key']

def get_weather(location_key):
    # Получаем данные о погоде
    weather_url = f"{BASE_URL}/currentconditions/v1/{location_key}?apikey={API_KEY}&language=ru&details=true"
    weather_response = requests.get(weather_url)
    weather_data = weather_response.json()
    if weather_response.status_code != 200 or not weather_data:
        return None
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

def check_bad_weather(temperature, humidity, wind_speed, precipitation_probability):
    if temperature < -15 or temperature > 35:
        return "ой-ой, погода плохая"
    if wind_speed > 50:
        return "ой-ой, погода плохая"
    if precipitation_probability > 70:
        return "ой-ой, погода плохая"
    if humidity > 90:
        return "ой-ой, погода плохая"
    return "погода — супер"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_weather', methods=['POST'])
def check_weather():
    start_city = request.form['start_city']
    end_city = request.form['end_city']
    try:
        start_location_key = get_location_key(start_city)
        end_location_key = get_location_key(end_city)
        if not start_location_key or not end_location_key:
            return render_template('index.html', result="Ошибка: Не удалось найти один из городов.")
        start_weather = get_weather(start_location_key)
        end_weather = get_weather(end_location_key)
        if not start_weather or not end_weather:
            return render_template('index.html', result="Ошибка: Не удалось получить данные о погоде.")
        # Оценка погодных условий
        start_condition = check_bad_weather(start_weather['temperature'], start_weather['humidity'],
                                            start_weather['wind_speed'], start_weather['precipitation_probability'])
        end_condition = check_bad_weather(end_weather['temperature'], end_weather['humidity'],
                                          end_weather['wind_speed'], end_weather['precipitation_probability'])
        result = f"Начальная точка: {start_city}: {start_condition}. Конечная точка: {end_city}: {end_condition}."
        return render_template('index.html', result=result)
    except Exception as e:
        return render_template('index.html', result=f"Ошибка: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)