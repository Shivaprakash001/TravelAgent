import requests
import os
from dotenv import load_dotenv

load_dotenv()

ORS_KEY = os.getenv('OPEN_ROUTE_API')
if not ORS_KEY:
    print("Warning: OPEN_ROUTE_API environment variable not set")

def get_coords(place_name: str) -> tuple:
    """Get coordinates for a place name using OpenRouteService Geocoding API"""
    try:
        geocoding_url = f"https://api.openrouteservice.org/geocode/search?api_key={ORS_KEY}&text={place_name}"
        response = requests.get(geocoding_url)
        data = response.json()
        
        if data.get('features'):
            coords = data['features'][0]['geometry']['coordinates']
            return (coords[1], coords[0])
        return None
    except Exception as e:
        print(f"Error getting coordinates for {place_name}: {e}")
        return None

def get_route(start_coords: tuple, end_coords: tuple) -> dict:
    """Get route between two coordinates using OpenRouteService"""
    try:
        route_url = f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={ORS_KEY}"
        
        payload = {
            "coordinates": [
                [start_coords[1], start_coords[0]],
                [end_coords[1], end_coords[0]]
            ]
        }
        
        response = requests.post(route_url, json=payload)
        data = response.json()
        
        if data.get('features'):
            route = data['features'][0]['properties']['segments'][0]
            return {
                "distance": route['distance'] / 1000,
                "duration": route['duration'] / 60,
                "steps": route['steps']
            }
        return None
    except Exception as e:
        print(f"Error getting route: {e}")
        return None

def calculate_distance_between_places(place1_coords: tuple, place2_coords: tuple) -> dict:
    """Simple distance calculation using basic math"""
    try:
        import math
        
        lat1, lon1 = place1_coords
        lat2, lon2 = place2_coords
        
        lat_diff = lat2 - lat1
        lon_diff = lon2 - lon1
        distance_km = math.sqrt(lat_diff**2 + lon_diff**2) * 111
        
        travel_time_minutes = distance_km * 5
        
        return {
            "distance_km": round(distance_km, 1),
            "travel_time_minutes": round(travel_time_minutes, 0),
            "travel_time_formatted": f"{int(travel_time_minutes)} min"
        }
    except Exception as e:
        print(f"Error calculating distance: {e}")
        return {"distance_km": 0, "travel_time_minutes": 0, "travel_time_formatted": "Unknown"}

def get_places_with_distances(places: list) -> list:
    """Add simple distance information between consecutive places"""
    enhanced_places = []
    
    for i, place in enumerate(places):
        enhanced_place = place.copy()
        
        if i < len(places) - 1:
            current_coords = place.get('point', {})
            next_coords = places[i + 1].get('point', {})
            
            if current_coords and next_coords and 'lat' in current_coords and 'lat' in next_coords:
                distance_info = calculate_distance_between_places(
                    (current_coords['lat'], current_coords['lon']),
                    (next_coords['lat'], next_coords['lon'])
                )
                enhanced_place['distance_to_next'] = distance_info
        
        enhanced_places.append(enhanced_place)
    
    return enhanced_places
