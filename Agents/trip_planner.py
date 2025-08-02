from tools.routes import get_route
from tools.trip_mapper import optimize_route, get_detailed_route_info, create_trip_summary, analyze_route_efficiency
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from ddgs import DDGS
import os
from dotenv import load_dotenv

load_dotenv()

@tool
def web_search_place_info(query: str) -> str:
    """Search the web for information about tourist places, best times to visit, and visit duration."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
            return " ".join([result['body'] for result in results])
    except Exception as e:
        return f"Search error: {str(e)}"

@tool
def get_places_route(input_data: str):
    """Get the route for the places with timing and weather considerations."""
    import json
    
    data = json.loads(input_data)
    places = data["places"]
    coords = eval(data["starting_coords"])
    destination = data["destination"]
    weather = data["weather"]
    
    trip_locations = []
    current_coords = coords

    for place in places:
        destination_coords = (place["point"]["lat"], place["point"]["lon"])
        route = get_route(current_coords, destination_coords)
        trip_locations.append({
            "name": place["name"],
            "route": route,
            "info": place["wikipedia_extracts"],
            "visit_duration": place.get("visit_duration", "2-3 hours"),
            "best_time": place.get("best_time", "morning"),
            "special_requirements": place.get("special_requirements", "None"),
            "description": place.get("description", "")
        })
        current_coords = destination_coords
    return trip_locations

@tool
def create_optimized_itinerary(input_data: str):
    """Create a simple itinerary considering weather, timing, and budget constraints."""
    import json
    
    try:
        data = json.loads(input_data)
        places = data["places"]
        coords = eval(data["starting_coords"])
        destination = data["destination"]
        weather = data["weather"]
        budget = data["budget"]
        duration = data["duration"]
        
        trip_locations = []
        current_coords = coords
        total_time = 0
        
        duration_hours = int(duration) * 8
        optimal_places = min(len(places), int(duration) * 2)
        selected_places = places[:optimal_places]
        
        print(f"Selected {len(selected_places)} places from {len(places)} available places")
        
        for i, place in enumerate(selected_places):
            destination_coords = (place["point"]["lat"], place["point"]["lon"])
            
            visit_duration = place.get("visit_duration", "2-3 hours")
            if "2-3" in visit_duration:
                visit_hours = 2.5
            elif "1-2" in visit_duration:
                visit_hours = 1.5
            elif "3-4" in visit_duration:
                visit_hours = 3.5
            else:
                visit_hours = 2.0
            
            time_slots = ["morning", "afternoon", "evening"]
            best_time = time_slots[i % 3]
            
            place_name = place["name"].lower()
            if any(word in place_name for word in ["museum", "gallery", "palace", "castle"]):
                special_requirements = "May require tickets"
                estimated_cost = "$10-20"
            else:
                special_requirements = "None"
                estimated_cost = "Free"
            
            if total_time + visit_hours <= duration_hours:
                trip_locations.append({
                    "name": place["name"],
                    "visit_duration": visit_duration,
                    "best_time": best_time,
                    "special_requirements": special_requirements,
                    "description": place.get("description", ""),
                    "estimated_cost": estimated_cost
                })
                total_time += visit_hours
                current_coords = destination_coords
            else:
                break
        
        return {
            "itinerary": trip_locations,
            "total_duration": f"{total_time} hours",
            "places_visited": len(trip_locations),
            "optimal_places_for_duration": optimal_places,
            "weather_considerations": weather,
            "budget_friendly": budget,
            "optimization_notes": f"Simple route for {destination}",
            "duration_analysis": f"Selected {len(trip_locations)} places for {duration} days"
        }
        
    except Exception as e:
        return {
            "error": f"Error creating itinerary: {str(e)}",
            "itinerary": [],
            "total_duration": "0 hours",
            "places_visited": 0
        }

def create_trip_planner_agent():
    """Create and return the trip planner agent using LangGraph ReAct agent."""
    tools = [web_search_place_info, get_places_route, create_optimized_itinerary]
    llm = ChatGroq(model="llama3-8b-8192", api_key=os.getenv("GROQ_API_KEY"))
    agent = create_react_agent(model=llm, tools=tools, verbose=True)
    return agent

def plan_trip_with_place_selector(destination: str, starting_coords: tuple, weather: dict, budget: str = "Medium", duration: str = "1", existing_places: list[dict] = None):
    """Simple trip planning workflow with dynamic radius"""
    from Agents.place_selector import get_detailed_places_for_trip_planning
    from tools.place import calculate_dynamic_radius
    
    if existing_places:
        detailed_places = existing_places
        print(f"Using {len(detailed_places)} existing places for {destination}")
    else:
        detailed_places = get_detailed_places_for_trip_planning(destination, starting_coords, duration, budget)
        print(f"Fetched {len(detailed_places)} places for {destination}")
    
    if not detailed_places:
        return {"error": "No places found for trip planning"}
    
    # Calculate dynamic radius for this trip
    duration_days = int(duration) if duration.isdigit() else 1
    dynamic_radius_km = calculate_dynamic_radius(duration_days) / 1000
    
    trip_locations = []
    total_time = 0
    duration_hours = int(duration) * 8
    
    # Select optimal number of places based on duration
    optimal_places = min(len(detailed_places), int(duration) * 2)
    selected_places = detailed_places[:optimal_places]
    
    # Sort by popularity and distance for better selection
    selected_places.sort(key=lambda x: (-x.get('rating', 0), x.get('distance_from_center', 0)))
    
    optimized_places = optimize_route(selected_places)
    enhanced_places = get_detailed_route_info(optimized_places)
    
    for i, place in enumerate(enhanced_places):
        visit_duration = place.get("visit_duration", "2-3 hours")
        if "2-3" in visit_duration:
            visit_hours = 2.5
        elif "1-2" in visit_duration:
            visit_hours = 1.5
        elif "3-4" in visit_duration:
            visit_hours = 3.5
        else:
            visit_hours = 2.0
        
        time_slots = ["morning", "afternoon", "evening"]
        best_time = time_slots[i % 3]
        
        place_name = place["name"].lower()
        if any(word in place_name for word in ["museum", "gallery", "palace", "castle"]):
            estimated_cost = "$10-20"
        else:
            estimated_cost = "Free"
        
        if total_time + visit_hours <= duration_hours:
            trip_locations.append({
                "name": place["name"],
                "visit_duration": visit_duration,
                "best_time": best_time,
                "special_requirements": place.get("special_requirements", "None"),
                "description": place.get("description", ""),
                "estimated_cost": estimated_cost,
                "point": place.get("point", {}),
                "route_to_next": place.get("route_to_next", {}),
                "kinds": place.get("kinds", ""),
                "distance_from_center": place.get("distance_from_center", 0),
                "rating": place.get("rating", 0)
            })
            total_time += visit_hours
        else:
            break
    
    daily_breakdown = create_daily_breakdown(trip_locations, int(duration))
    trip_summary = create_trip_summary(trip_locations)
    route_analysis = analyze_route_efficiency(trip_locations)
    
    # Add exploration radius information
    exploration_info = {
        "radius_km": round(dynamic_radius_km, 1),
        "places_explored": len(detailed_places),
        "places_selected": len(trip_locations),
        "exploration_area": f"{dynamic_radius_km:.1f}km radius around {destination}"
    }
    
    return {
        "destination": destination,
        "duration": f"{duration} days",
        "weather": weather,
        "budget": budget,
        "itinerary": trip_locations,
        "total_duration": f"{total_time} hours",
        "places_visited": len(trip_locations),
        "daily_breakdown": daily_breakdown,
        "route_details": f"Optimized route for {len(trip_locations)} places in {destination}",
        "duration_analysis": f"Selected {len(trip_locations)} places for {duration} days",
        "trip_summary": trip_summary,
        "route_analysis": route_analysis,
        "exploration_info": exploration_info,
        "optimal_places_for_duration": len(trip_locations)
    }

def create_daily_breakdown(places, days):
    """Create a simple daily breakdown of the trip"""
    daily_plans = []
    places_per_day = max(1, len(places) // days)
    
    for day in range(1, days + 1):
        start_idx = (day - 1) * places_per_day
        end_idx = min(start_idx + places_per_day, len(places))
        
        if start_idx < len(places):
            day_places = places[start_idx:end_idx]
            daily_plans.append({
                f"Day {day}": [
                    {
                        "place": place["name"],
                        "duration": place["visit_duration"],
                        "best_time": place["best_time"],
                        "description": place["description"][:100] + "..." if len(place["description"]) > 100 else place["description"],
                        "kinds": place.get("kinds", "")
                    }
                    for place in day_places
                ]
            })
    
    return daily_plans

