from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

def fetch_current_weather(city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    data = requests.get(url)
    
    if data.status_code==200:
        print("page fetched successfully done")
    elif data.status_code==404:
        print("city is not Found")
    elif data.status_code==429:
        print("API rate limit exceeded - too many requests")
    else:
        print("failed to fetch page")
    
    return data.json()

def fetch_5day_forecast(city_name, api_key):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={api_key}&units=metric"
    data = requests.get(url)
    
    if data.status_code==200:
        print("page fetched successfully done")
    elif data.status_code==404:
        print("city is not Found")
    elif data.status_code==429:
        print("API rate limit exceeded - too many requests")
    else:
        print("failed to fetch page")
    
    return data.json()

api_key = "080ca7d6b2cd7b267cda1d2b1467c121"
cities = ["London", "Paris", "Tokyo", "New York", "Mumbai", "Pune", "Delhi", "Banglore"]

def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', cities=cities)

@app.route('/get_weather', methods=['POST'])
def get_weather():
    city = request.form['city']
    unit = request.form['unit']
    
    current = fetch_current_weather(city, api_key)
    forecast = fetch_5day_forecast(city, api_key)
    
    weather_data = {
        'city': city,
        'unit': unit,
        'current': current,
        'forecast': forecast
    }
    
    return render_template('weather_result.html', data=weather_data, celsius_to_fahrenheit=celsius_to_fahrenheit)

@app.route('/compare_cities')
def compare_cities():
    city_data = []
    for city in cities:
        current = fetch_current_weather(city, api_key)
        if 'main' in current:
            city_data.append({
                'name': city,
                'temperature': current['main']['temp'],
                'humidity': current['main']['humidity'],
                'description': current['weather'][0]['description'] if current.get('weather') else 'N/A'
            })
    
    graph_url = create_comparison_graph(city_data)
    
    return render_template('compare.html', cities=city_data, graph_url=graph_url)

def create_comparison_graph(city_data):
    plt.figure(figsize=(12, 8))
    
    city_names = [city['name'] for city in city_data]
    temperatures = [city['temperature'] for city in city_data]
    humidity = [city['humidity'] for city in city_data]
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    bars1 = ax1.bar(city_names, temperatures, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFA726', '#66BB6A', '#42A5F5', '#AB47BC'])
    ax1.set_title('🌡️ Temperature Comparison Across Cities', fontsize=16, fontweight='bold', pad=20)
    ax1.set_ylabel('Temperature (°C)', fontsize=12)
    ax1.tick_params(axis='x', rotation=45)
    
    for bar, temp in zip(bars1, temperatures):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{temp}°C', ha='center', va='bottom', fontweight='bold')
    
    bars2 = ax2.bar(city_names, humidity, color=['#FFA726', '#66BB6A', '#42A5F5', '#AB47BC', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4'])
    ax2.set_title('💧 Humidity Comparison Across Cities', fontsize=16, fontweight='bold', pad=20)
    ax2.set_ylabel('Humidity (%)', fontsize=12)
    ax2.tick_params(axis='x', rotation=45)
    
    for bar, hum in zip(bars2, humidity):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{hum}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout(pad=3.0)
    
    img = io.BytesIO()
    plt.savefig(img, format='png', dpi=100, bbox_inches='tight')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    
    return f"data:image/png;base64,{graph_url}"

if __name__ == '__main__':
    app.run(debug=True)