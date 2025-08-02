import json
import os
from datetime import datetime
from typing import Dict, List, Any

PLACE_ICONS = {
    'temple': '🛕', 'church': '⛪', 'mosque': '🕌', 'cathedral': '⛪', 'monastery': '🏛️', 'shrine': '🛕',
    'museum': '🏛️', 'gallery': '🖼️', 'palace': '🏰', 'castle': '🏰', 'fort': '🏰', 'monument': '🗽', 'statue': '🗽',
    'park': '🌳', 'garden': '🌺', 'beach': '🏖️', 'mountain': '⛰️', 'lake': '🏞️', 'river': '🏞️', 'forest': '🌲',
    'sanctuary': '🐦', 'zoo': '🦁', 'wildlife': '🦁', 'bird': '🐦', 'nature': '🌿',
    'theater': '🎭', 'cinema': '🎬', 'amusement': '🎡', 'aquarium': '🐠', 'circus': '🎪', 'concert': '🎵',
    'stadium': '🏟️', 'bowling': '🎳', 'restaurant': '🍽️', 'cafe': '☕', 'market': '🛒', 'mall': '🏬',
    'shopping': '🛍️', 'bakery': '🥖', 'pizzeria': '🍕', 'bar': '🍺', 'pub': '🍺', 'airport': '✈️',
    'station': '🚉', 'port': '🚢', 'default': '📍'
}

def get_place_icon(place_name: str, kinds: str = "") -> str:
    """Get appropriate emoji icon for a place based on name and types"""
    name_lower = place_name.lower()
    kinds_lower = kinds.lower()
    
    for keyword, icon in PLACE_ICONS.items():
        if keyword in name_lower or keyword in kinds_lower:
            return icon
    
    return PLACE_ICONS['default']

def generate_mobile_friendly_trip(trip_data: Dict[str, Any]) -> str:
    """Generate a mobile-friendly text version of the trip plan"""
    destination = trip_data.get('destination', 'Unknown')
    duration = trip_data.get('duration', 'Unknown')
    budget = trip_data.get('budget', 'Unknown')
    
    mobile_text = f"""
🌍 TRAVEL PLAN: {destination.upper()}
⏱️ Duration: {duration}
💰 Budget: {budget}
📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

"""
    
    weather = trip_data.get('weather', {})
    if weather and 'temp' in weather:
        mobile_text += f"🌤️ Weather: {weather.get('temp', 'N/A')}°C, {weather.get('weather', 'N/A')}\n\n"
    
    itinerary = trip_data.get('itinerary', [])
    if itinerary:
        mobile_text += "🗺️ ITINERARY:\n"
        mobile_text += "=" * 50 + "\n\n"
        
        for i, place in enumerate(itinerary, 1):
            place_name = place.get('name', 'Unknown')
            kinds = place.get('kinds', '')
            icon = get_place_icon(place_name, kinds)
            
            mobile_text += f"{i}. {icon} {place_name}\n"
            mobile_text += f"   ⏰ Duration: {place.get('visit_duration', 'N/A')}\n"
            mobile_text += f"   🌅 Best Time: {place.get('best_time', 'N/A')}\n"
            mobile_text += f"   💰 Cost: {place.get('estimated_cost', 'N/A')}\n"
            
            description = place.get('description', '')
            if description:
                mobile_text += f"   📝 {description[:100]}...\n"
            
            route_info = place.get('route_to_next', {})
            if route_info and 'distance_km' in route_info:
                mobile_text += f"   🚗 {route_info['distance_km']} km to {route_info.get('next_place', 'next')}\n"
                mobile_text += f"   ⏱️ {route_info.get('travel_time_formatted', 'N/A')} travel time\n"
            elif place.get('distance_to_next', {}):
                distance_info = place['distance_to_next']
                if 'distance_km' in distance_info:
                    mobile_text += f"   🚗 {distance_info['distance_km']} km to next\n"
            
            mobile_text += "\n"
    
    daily_breakdown = trip_data.get('daily_breakdown', [])
    if daily_breakdown:
        mobile_text += "📅 DAILY BREAKDOWN:\n"
        mobile_text += "=" * 50 + "\n\n"
        
        for day_plan in daily_breakdown:
            for day, places in day_plan.items():
                mobile_text += f"{day}:\n"
                for place in places:
                    place_name = place.get('place', 'Unknown')
                    kinds = place.get('kinds', '')
                    icon = get_place_icon(place_name, kinds)
                    mobile_text += f"  {icon} {place_name} ({place.get('duration', 'N/A')}) - {place.get('best_time', 'N/A')}\n"
                mobile_text += "\n"
    
    mobile_text += f"""
📊 SUMMARY:
• Total Duration: {trip_data.get('total_duration', 'N/A')}
• Places to Visit: {trip_data.get('places_visited', 'N/A')}
• Budget Level: {budget}

💡 TIPS:
• Save this plan offline for easy access
• Check opening hours before visiting
• Have backup plans for weather changes
• Keep emergency contacts handy

Enjoy your trip to {destination}! 🌟
"""
    
    return mobile_text

def generate_simple_html(trip_data: Dict[str, Any]) -> str:
    """Generate a simple HTML version for better mobile viewing"""
    destination = trip_data.get('destination', 'Unknown')
    duration = trip_data.get('duration', 'Unknown')
    budget = trip_data.get('budget', 'Unknown')
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trip Plan - {destination}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 20px;
        }}
        .place-card {{
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .place-icon {{
            font-size: 24px;
            margin-right: 10px;
        }}
        .place-name {{
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 5px;
        }}
        .place-details {{
            color: #666;
            font-size: 14px;
            line-height: 1.4;
        }}
        .weather-box {{
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }}
        .summary {{
            background: #e8f5e8;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌍 {destination}</h1>
        <p>⏱️ {duration} | 💰 {budget}</p>
        <p>📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
"""
    
    weather = trip_data.get('weather', {})
    if weather and 'temp' in weather:
        html += f"""
    <div class="weather-box">
        <h3>🌤️ Weather</h3>
        <p>Temperature: {weather.get('temp', 'N/A')}°C</p>
        <p>Conditions: {weather.get('weather', 'N/A')}</p>
    </div>
"""
    
    itinerary = trip_data.get('itinerary', [])
    if itinerary:
        html += "<h2>🗺️ Itinerary</h2>"
        
        for i, place in enumerate(itinerary, 1):
            place_name = place.get('name', 'Unknown')
            kinds = place.get('kinds', '')
            icon = get_place_icon(place_name, kinds)
            
            html += f"""
    <div class="place-card">
        <div class="place-name">
            <span class="place-icon">{icon}</span>
            {i}. {place_name}
        </div>
        <div class="place-details">
            <p>⏰ Duration: {place.get('visit_duration', 'N/A')}</p>
            <p>🌅 Best Time: {place.get('best_time', 'N/A')}</p>
            <p>💰 Cost: {place.get('estimated_cost', 'N/A')}</p>
"""
            
            description = place.get('description', '')
            if description:
                html += f"            <p>📝 {description[:150]}...</p>\n"
            
            route_info = place.get('route_to_next', {})
            if route_info and 'distance_km' in route_info:
                html += f"            <p>🚗 {route_info['distance_km']} km to {route_info.get('next_place', 'next')}</p>\n"
                html += f"            <p>⏱️ {route_info.get('travel_time_formatted', 'N/A')} travel time</p>\n"
            elif place.get('distance_to_next', {}):
                distance_info = place['distance_to_next']
                if 'distance_km' in distance_info:
                    html += f"            <p>🚗 {distance_info['distance_km']} km to next</p>\n"
            
            html += "        </div>\n    </div>\n"
    
    html += f"""
    <div class="summary">
        <h3>📊 Summary</h3>
        <p>Total Duration: {trip_data.get('total_duration', 'N/A')}</p>
        <p>Places to Visit: {trip_data.get('places_visited', 'N/A')}</p>
        <p>Budget Level: {budget}</p>
    </div>
    
    <div class="summary">
        <h3>💡 Tips</h3>
        <p>• Save this plan offline for easy access</p>
        <p>• Check opening hours before visiting</p>
        <p>• Have backup plans for weather changes</p>
        <p>• Keep emergency contacts handy</p>
    </div>
</body>
</html>
"""
    
    return html

def export_trip_plan(trip_data: Dict[str, Any], export_format: str = "mobile") -> Dict[str, Any]:
    """Export trip plan in various formats for offline use"""
    export_options = {
        "mobile": generate_mobile_friendly_trip,
        "html": generate_simple_html,
        "json": lambda data: json.dumps(data, indent=2)
    }
    
    if export_format not in export_options:
        export_format = "mobile"
    
    content = export_options[export_format](trip_data)
    
    destination = trip_data.get('destination', 'trip')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    
    if export_format == "mobile":
        filename = f"trip_plan_{destination}_{timestamp}.txt"
        mime_type = "text/plain"
    elif export_format == "html":
        filename = f"trip_plan_{destination}_{timestamp}.html"
        mime_type = "text/html"
    else:
        filename = f"trip_plan_{destination}_{timestamp}.json"
        mime_type = "application/json"
    
    return {
        "content": content,
        "filename": filename,
        "mime_type": mime_type,
        "format": export_format
    } 