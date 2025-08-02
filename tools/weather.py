import requests
import os
from dotenv import load_dotenv

load_dotenv()

OWM_KEY = os.getenv('OPENWEATHER_API')

def get_weather(city: str) -> dict:
    """Get current weather for a city"""
    try:
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OWM_KEY}&units=metric"
        response = requests.get(weather_url)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'temp': data['main']['temp'],
                'weather': data['weather'][0]['main'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed']
            }
        else:
            return {}
    except Exception as e:
        print(f"Error getting weather for {city}: {e}")
        return {}
