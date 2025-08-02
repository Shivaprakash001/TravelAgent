import requests
import os
from dotenv import load_dotenv
from tools.place import get_20_places, get_places_with_dynamic_radius

load_dotenv()

OTM_KEY = os.getenv('OPEN_TRIPMAP_API')

def get_top_places(destination: str, coords: tuple, duration_days: int = 1) -> list:
    """Get top places for a destination using dynamic radius"""
    return get_places_with_dynamic_radius(destination, coords, duration_days, 25)

def get_detailed_places_for_trip_planning(destination: str, coords: tuple, duration: str, budget: str) -> list:
    """Get detailed places with additional information for trip planning"""
    try:
        # Convert duration to days for radius calculation
        duration_days = int(duration) if duration.isdigit() else 1
        
        # Get more places for longer trips
        max_places = min(duration_days * 3, 40)  # More places for longer trips
        
        places = get_places_with_dynamic_radius(destination, coords, duration_days, max_places)
        detailed_places = []
        
        print(f"🎯 Selecting best {len(places)} places for {duration_days} day trip in {destination}")
        
        for place in places:
            try:
                if place.get('xid'):
                    detail_url = f"https://api.opentripmap.com/0.1/en/places/xid/{place['xid']}?apikey={OTM_KEY}"
                    detail_response = requests.get(detail_url)
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        description = detail_data.get('wikipedia_extracts', {}).get('text', '')
                        
                        if description:
                            description = description[:200] + "..." if len(description) > 200 else description
                        else:
                            description = f"Visit {place['name']} in {destination}"
                        
                        is_popular = detail_data.get('rate', 0) > 3
                    else:
                        description = f"Visit {place['name']} in {destination}"
                        is_popular = False
                else:
                    description = f"Visit {place['name']} in {destination}"
                    is_popular = False
                
                detailed_place = {
                    "name": place['name'],
                    "point": place.get('point', {}),
                    "kinds": place.get('kinds', ''),
                    "visit_duration": place.get('visit_duration', '2-3 hours'),
                    "best_time": place.get('best_time', 'morning'),
                    "description": description,
                    "rating": place.get('rate', 0),
                    "is_popular": is_popular,
                    "distance_from_center": place.get('distance_from_center', 0),
                    "kinds": place.get('kinds', '')
                }
                detailed_places.append(detailed_place)
                
            except Exception as e:
                print(f"Error getting details for {place.get('name', 'Unknown')}: {e}")
                continue
        
        # Sort by popularity and distance for better selection
        detailed_places.sort(key=lambda x: (-x.get('rating', 0), x.get('distance_from_center', 0)))
        
        print(f"✅ Found {len(detailed_places)} detailed places for {destination}")
        return detailed_places
    except Exception as e:
        print(f"Error getting detailed places for {destination}: {e}")
        return []