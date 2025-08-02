import requests
import os
import math
from typing import List, Dict, Tuple, Any
from dotenv import load_dotenv
from .routes import get_route, calculate_distance_between_places

load_dotenv()

ORS_KEY = os.getenv('OPEN_ROUTE_API')

def calculate_total_distance(places: List[Dict]) -> float:
    """Calculate total distance of the trip route"""
    total_distance = 0
    for i in range(len(places) - 1):
        current_coords = places[i].get('point', {})
        next_coords = places[i + 1].get('point', {})
        
        if (current_coords and next_coords and 
            'lat' in current_coords and 'lon' in current_coords and
            'lat' in next_coords and 'lon' in next_coords):
            try:
                distance_info = calculate_distance_between_places(
                    (current_coords['lat'], current_coords['lon']),
                    (next_coords['lat'], next_coords['lon'])
                )
                total_distance += distance_info['distance_km']
            except Exception:
                continue
    
    return round(total_distance, 1)

def optimize_route(places: List[Dict], start_location: Tuple[float, float] = None) -> List[Dict]:
    """Optimize route using nearest neighbor algorithm"""
    if not places:
        return places
    
    if not start_location:
        first_place = places[0]
        start_location = (first_place['point']['lat'], first_place['point']['lon'])
    
    unvisited = places.copy()
    optimized_route = []
    current_location = start_location
    
    while unvisited:
        nearest_idx = 0
        min_distance = float('inf')
        
        for i, place in enumerate(unvisited):
            if 'point' not in place or 'lat' not in place['point'] or 'lon' not in place['point']:
                continue
                
            place_coords = (place['point']['lat'], place['point']['lon'])
            try:
                distance_info = calculate_distance_between_places(current_location, place_coords)
                if distance_info['distance_km'] < min_distance:
                    min_distance = distance_info['distance_km']
                    nearest_idx = i
            except Exception:
                continue
        
        nearest_place = unvisited.pop(nearest_idx)
        nearest_place['route_info'] = {
            'distance_from_previous': min_distance,
            'travel_time_minutes': min_distance * 5,
            'travel_time_formatted': f"{int(min_distance * 5)} min"
        }
        optimized_route.append(nearest_place)
        current_location = (nearest_place['point']['lat'], nearest_place['point']['lon'])
    
    return optimized_route

def get_detailed_route_info(places: List[Dict]) -> List[Dict]:
    """Get detailed route information between all places"""
    if len(places) < 2:
        return places
    
    enhanced_places = []
    
    for i, place in enumerate(places):
        enhanced_place = place.copy()
        
        if i < len(places) - 1:
            if ('point' not in place or 'lat' not in place['point'] or 'lon' not in place['point'] or
                'point' not in places[i + 1] or 'lat' not in places[i + 1]['point'] or 'lon' not in places[i + 1]['point']):
                continue
                
            current_coords = (place['point']['lat'], place['point']['lon'])
            next_place = places[i + 1]
            next_coords = (next_place['point']['lat'], next_place['point']['lon'])
            
            try:
                route_info = get_route(current_coords, next_coords)
                
                if route_info and 'distance' in route_info and 'duration' in route_info:
                    enhanced_place['route_to_next'] = {
                        'distance_km': route_info['distance'],
                        'travel_time_minutes': route_info['duration'],
                        'travel_time_formatted': f"{int(route_info['duration'])} min",
                        'route_steps': route_info.get('steps', []),
                        'next_place': next_place['name']
                    }
                else:
                    distance_info = calculate_distance_between_places(current_coords, next_coords)
                    enhanced_place['route_to_next'] = {
                        'distance_km': distance_info['distance_km'],
                        'travel_time_minutes': distance_info['travel_time_minutes'],
                        'travel_time_formatted': distance_info['travel_time_formatted'],
                        'route_steps': [],
                        'next_place': next_place['name']
                    }
            except Exception:
                distance_info = calculate_distance_between_places(current_coords, next_coords)
                enhanced_place['route_to_next'] = {
                    'distance_km': distance_info['distance_km'],
                    'travel_time_minutes': distance_info['travel_time_minutes'],
                    'travel_time_formatted': distance_info['travel_time_formatted'],
                    'route_steps': [],
                    'next_place': next_place['name']
                }
        
        enhanced_places.append(enhanced_place)
    
    return enhanced_places

def find_nearby_places(center_coords: Tuple[float, float], radius_km: float = 5) -> List[Dict]:
    """Find nearby places within a radius"""
    try:
        OTM_KEY = os.getenv('OPEN_TRIPMAP_API')
        if not OTM_KEY:
            return []
        
        lat, lon = center_coords
        places_url = f"https://api.opentripmap.com/0.1/en/places/radius?radius={radius_km*1000}&lon={lon}&lat={lat}&rate=1&format=json&apikey={OTM_KEY}"
        
        response = requests.get(places_url)
        if response.status_code == 200:
            places_data = response.json()
            
            nearby_places = []
            for place in places_data[:10]:
                place_coords = (place['point']['lat'], place['point']['lon'])
                distance_info = calculate_distance_between_places(center_coords, place_coords)
                
                nearby_places.append({
                    'name': place.get('name', 'Unknown'),
                    'kinds': place.get('kinds', ''),
                    'distance_km': distance_info['distance_km'],
                    'point': place['point']
                })
            
            nearby_places.sort(key=lambda x: x['distance_km'])
            return nearby_places
        
        return []
    except Exception as e:
        print(f"Error finding nearby places: {e}")
        return []

def create_trip_summary(places: List[Dict]) -> Dict[str, Any]:
    """Create a comprehensive trip summary"""
    if not places:
        return {}
    
    total_distance = calculate_total_distance(places)
    total_places = len(places)
    
    total_travel_time = 0
    for place in places:
        try:
            if 'route_to_next' in place and 'travel_time_minutes' in place['route_to_next']:
                total_travel_time += place['route_to_next']['travel_time_minutes']
            elif 'distance_to_next' in place and 'travel_time_minutes' in place['distance_to_next']:
                total_travel_time += place['distance_to_next']['travel_time_minutes']
        except (KeyError, TypeError):
            continue
    
    start_location = places[0]['name'] if places else "Unknown"
    end_location = places[-1]['name'] if places else "Unknown"
    avg_distance = total_distance / max(1, total_places - 1)
    
    return {
        'total_distance_km': total_distance,
        'total_travel_time_minutes': total_travel_time,
        'total_travel_time_formatted': f"{int(total_travel_time)} min",
        'total_places': total_places,
        'start_location': start_location,
        'end_location': end_location,
        'average_distance_between_places': round(avg_distance, 1),
        'route_efficiency': "Optimized" if total_places > 1 else "Single Destination"
    }

def generate_route_map_data(places: List[Dict]) -> Dict[str, Any]:
    """Generate data for creating a route map"""
    if not places:
        return {}
    
    route_points = []
    place_markers = []
    
    for i, place in enumerate(places):
        coords = place.get('point', {})
        if coords and 'lat' in coords and 'lon' in coords:
            place_markers.append({
                'name': place['name'],
                'lat': coords['lat'],
                'lon': coords['lon'],
                'order': i + 1,
                'visit_duration': place.get('visit_duration', 'N/A'),
                'best_time': place.get('best_time', 'N/A')
            })
            route_points.append([coords['lat'], coords['lon']])
    
    return {
        'route_points': route_points,
        'place_markers': place_markers,
        'total_distance': calculate_total_distance(places),
        'start_location': places[0]['name'] if places else "Unknown",
        'end_location': places[-1]['name'] if places else "Unknown"
    }

def analyze_route_efficiency(places: List[Dict]) -> Dict[str, Any]:
    """Analyze the efficiency of the route"""
    if len(places) < 2:
        return {'efficiency': 'Single destination', 'suggestions': []}
    
    total_distance = calculate_total_distance(places)
    total_places = len(places)
    avg_distance = total_distance / (total_places - 1)
    
    suggestions = []
    
    if avg_distance > 20:
        suggestions.append("Consider grouping nearby attractions together")
    
    if total_distance > 100:
        suggestions.append("This is a long-distance trip - consider transportation options")
    
    if total_places > 8:
        suggestions.append("Many destinations - consider splitting into multiple days")
    
    nearby_groups = []
    for i, place in enumerate(places):
        if 'point' not in place or 'lat' not in place['point'] or 'lon' not in place['point']:
            continue
            
        place_coords = (place['point']['lat'], place['point']['lon'])
        nearby_count = 0
        
        for j, other_place in enumerate(places):
            if i != j:
                if 'point' not in other_place or 'lat' not in other_place['point'] or 'lon' not in other_place['point']:
                    continue
                    
                other_coords = (other_place['point']['lat'], other_place['point']['lon'])
                try:
                    distance = calculate_distance_between_places(place_coords, other_coords)['distance_km']
                    if distance < 2:
                        nearby_count += 1
                except Exception:
                    continue
        
        if nearby_count >= 2:
            nearby_groups.append(place['name'])
    
    if nearby_groups:
        suggestions.append(f"Consider visiting these places together: {', '.join(nearby_groups[:3])}")
    
    return {
        'efficiency': f"Route covers {total_distance}km across {total_places} places",
        'average_distance': f"{avg_distance:.1f}km between places",
        'suggestions': suggestions,
        'nearby_groups': nearby_groups
    } 