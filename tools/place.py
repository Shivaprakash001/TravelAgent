import requests
import os
import re
from difflib import SequenceMatcher
from dotenv import load_dotenv

load_dotenv()

OTM_KEY = os.getenv('OPEN_TRIPMAP_API')

def calculate_dynamic_radius(duration_days: int) -> int:
    """
    Calculate dynamic radius based on trip duration
    Longer trips allow for larger exploration areas
    """
    # Base radius: 20km for 1 day
    base_radius = 20000  # 20km in meters
    
    # Scale factor: increase radius by 10km per additional day
    # Cap at 100km for very long trips
    additional_radius = min((duration_days - 1) * 10000, 80000)  # Max 80km additional
    
    dynamic_radius = base_radius + additional_radius
    
    # Ensure minimum and maximum bounds
    dynamic_radius = max(dynamic_radius, 15000)  # Minimum 15km
    dynamic_radius = min(dynamic_radius, 100000)  # Maximum 100km
    
    return int(dynamic_radius)

def get_visit_duration(place_name: str, place_type: str) -> str:
    """Determine visit duration based on place type"""
    place_name_lower = place_name.lower()
    place_type_lower = place_type.lower()
    
    if any(word in place_name_lower for word in ['museum', 'gallery', 'palace', 'castle']):
        return "3-4 hours"
    elif any(word in place_name_lower for word in ['park', 'garden', 'beach']):
        return "2-3 hours"
    elif any(word in place_name_lower for word in ['temple', 'church', 'mosque']):
        return "1-2 hours"
    elif any(word in place_type_lower for word in ['historic', 'cultural']):
        return "2-3 hours"
    else:
        return "1-2 hours"

def get_best_time(place_name: str, place_type: str) -> str:
    """Determine best time to visit based on place type"""
    place_name_lower = place_name.lower()
    place_type_lower = place_type.lower()
    
    if any(word in place_name_lower for word in ['beach', 'park', 'garden']):
        return "morning"
    elif any(word in place_name_lower for word in ['museum', 'gallery', 'palace']):
        return "afternoon"
    elif any(word in place_name_lower for word in ['temple', 'church', 'mosque']):
        return "morning"
    else:
        return "morning"

def normalize_place_name(name: str) -> str:
    """Normalize place name for better comparison"""
    normalized = name.lower()
    
    prefixes_to_remove = ['the ', 'sri ', 'shri ', 'sree ']
    suffixes_to_remove = [' temple', ' church', ' mosque', ' palace', ' fort', ' museum', ' park']
    
    for prefix in prefixes_to_remove:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
    
    for suffix in suffixes_to_remove:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)]
    
    normalized = re.sub(r'[^\w\s]', '', normalized)
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized

def are_similar_places(name1: str, name2: str, similarity_threshold: float = 0.8) -> bool:
    """Check if two place names refer to the same location"""
    norm1 = normalize_place_name(name1)
    norm2 = normalize_place_name(name2)
    
    if norm1 == norm2:
        return True
    
    if norm1 in norm2 or norm2 in norm1:
        return True
    
    similarity = SequenceMatcher(None, norm1, norm2).ratio()
    return similarity >= similarity_threshold

def is_duplicate_place(new_place_name: str, existing_places: list) -> bool:
    """Check if a place is a duplicate of any existing place"""
    for existing_place in existing_places:
        existing_name = existing_place.get('name', '')
        if are_similar_places(new_place_name, existing_name):
            return True
    return False

def get_places_with_dynamic_radius(destination: str, coords: tuple, duration_days: int, max_places: int = 30) -> list:
    """
    Get places using dynamic radius based on trip duration
    Longer trips get larger exploration areas
    """
    try:
        lat, lon = coords
        dynamic_radius = calculate_dynamic_radius(duration_days)
        
        # Calculate radius in km for logging
        radius_km = dynamic_radius / 1000
        
        print(f"🔍 Exploring {destination} with {radius_km:.1f}km radius for {duration_days} day trip")
        
        places_url = f"https://api.opentripmap.com/0.1/en/places/radius?radius={dynamic_radius}&lon={lon}&lat={lat}&rate=1&format=json&apikey={OTM_KEY}"
        
        places_data = requests.get(places_url).json()
        places = []
        
        # Get more places initially to have better selection
        initial_places = min(len(places_data), max_places * 2)
        
        for place in places_data[:initial_places]:
            place_name = place.get('name', 'Unknown')
            
            if is_duplicate_place(place_name, places):
                continue
            
            place_details = {
                "name": place_name,
                "point": place.get('point', {}),
                "kinds": place.get('kinds', ''),
                "visit_duration": get_visit_duration(place_name, place.get('kinds', '')),
                "best_time": get_best_time(place_name, place.get('kinds', '')),
                "distance_from_center": calculate_distance_from_center(coords, place.get('point', {}))
            }
            places.append(place_details)
        
        # Sort by distance and rating to get the best places within the radius
        places.sort(key=lambda x: (x.get('distance_from_center', 0), -x.get('rate', 0)))
        
        print(f"📍 Found {len(places)} unique places within {radius_km:.1f}km radius")
        return places[:max_places]
        
    except Exception as e:
        print(f"Error getting places for {destination}: {e}")
        return []

def calculate_distance_from_center(center_coords: tuple, place_point: dict) -> float:
    """Calculate distance from center coordinates to a place"""
    try:
        import math
        
        center_lat, center_lon = center_coords
        place_lat = place_point.get('lat', center_lat)
        place_lon = place_point.get('lon', center_lon)
        
        lat_diff = place_lat - center_lat
        lon_diff = place_lon - center_lon
        distance_km = math.sqrt(lat_diff**2 + lon_diff**2) * 111
        
        return round(distance_km, 1)
    except Exception:
        return 0.0

def get_20_places(destination: str, coords: tuple, duration_days: int = 1) -> list:
    """Get top places for a destination using dynamic radius"""
    return get_places_with_dynamic_radius(destination, coords, duration_days, 20)
