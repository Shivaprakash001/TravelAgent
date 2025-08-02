from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import TypedDict, Optional
from langchain.agents import tool, AgentExecutor, create_openai_tools_agent
import os
from dotenv import load_dotenv
import json

load_dotenv()

# Your own modules
from tools.routes import get_route, get_coords
from tools.weather import get_weather
from Agents.place_selector import get_detailed_places_for_trip_planning
from Agents.trip_planner import plan_trip_with_place_selector
from tools.place import get_20_places

# Define State
class AgentState(TypedDict):
    user_input: dict
    places: list[dict]
    weather: dict
    trip_plan: dict

# Groq LLM setup
llm = ChatGroq(model="llama3-8b-8192", api_key=os.getenv("GROQ_API_KEY"))
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     """
You are a smart travel planner assistant. 
Your job is to help the user plan a travel trip based on 4 key things:
- Find the best places to visit in the destination using detailed place research
- Get weather information for the destination and the places to visit
- Create optimized routes between places considering timing and weather
- Generate a comprehensive trip plan with budget and duration constraints

You have access to tools like:
1. get_detailed_places_tool: to get detailed tourist places with visit duration, timing, and requirements
2. get_weather_tool: to get weather information for the destination and the places to visit
3. create_comprehensive_trip_plan: to create a complete itinerary with routes, timing, and weather considerations

Always gather user input first, then call tools as needed, and finally summarize the entire plan.

You must ensure that:
- The travel plan fits within the budget and time constraints
- The route and distance are shown clearly with timing considerations
- Places to visit are well-researched with visit duration and requirements
- Weather conditions are considered for optimal timing
"""),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
    ("human", "{input}")
])

# Tools definition
@tool
def get_detailed_places_tool(destination: str) -> str:
    """Fetches detailed must-visit places for a destination with visit duration, timing, and requirements."""
    coords = get_coords(destination)
    if not coords:
        return f"Could not find coordinates for {destination}"
    
    try:
        # Use the direct place selector function
        detailed_places = get_detailed_places_for_trip_planning(destination, coords)
        if detailed_places:
            places_info = []
            for place in detailed_places:
                info = f"{place['name']} - {place['visit_duration']} - {place['best_time']}"
                places_info.append(info)
            return f"Found {len(detailed_places)} places for {destination}: {'; '.join(places_info)}"
        else:
            return f"No places found for {destination}"
    except Exception as e:
        return f"Error getting places for {destination}: {str(e)}"

@tool
def get_weather_tool(destination: str) -> dict:
    """Gets weather information for a destination."""
    return get_weather(destination)

@tool
def create_comprehensive_trip_plan(destination: str, budget: str, duration: str) -> dict:
    """Creates a comprehensive trip plan with detailed places, routes, and weather considerations."""
    coords = get_coords(destination)
    if not coords:
        return {"error": f"Could not find coordinates for {destination}"}
    
    weather = get_weather(destination)
    
    try:
        # Use the integrated trip planning function
        trip_plan = plan_trip_with_place_selector(destination, coords, weather, budget, duration)
        return trip_plan
    except Exception as e:
        return {"error": f"Error creating trip plan: {str(e)}"}

tools = [get_detailed_places_tool, get_weather_tool, create_comprehensive_trip_plan]
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def print_welcome():
    """Display welcome message and instructions"""
    print("=" * 60)
    print("🌍 TRAVEL AGENT - Your Smart Trip Planner")
    print("=" * 60)
    print("I'll help you plan the perfect trip!")
    print("Please provide your destination, budget, and duration.")
    print("Format: destination/budget/duration")
    print("Example: Paris/Medium/5")
    print("Budget options: Low, Medium, High")
    print("Duration: number of days (e.g., 3, 7, 14)")
    print("=" * 60)

def print_trip_summary(state: AgentState):
    """Display a formatted summary of the trip plan"""
    print("\n" + "=" * 60)
    print("🎉 YOUR TRIP PLAN IS READY!")
    print("=" * 60)
    
    destination = state["user_input"]["destination"]["name"]
    budget = state["user_input"]["budget"]
    duration = state["user_input"]["duration"]
    
    print(f"📍 Destination: {destination}")
    print(f"💰 Budget: {budget}")
    print(f"⏱️  Duration: {duration} days")
    
    if "weather" in state and state["weather"]:
        print(f"🌤️  Weather: {state['weather']}")
    
    if "trip_plan" in state and state["trip_plan"]:
        trip_plan = state["trip_plan"]
        if isinstance(trip_plan, dict):
            print(f"📋 Total Duration: {trip_plan.get('total_duration', 'N/A')}")
            print(f"🏛️  Places to Visit: {trip_plan.get('places_visited', 'N/A')}")
            
            # Display detailed itinerary
            if "itinerary" in trip_plan and trip_plan["itinerary"]:
                print("\n🗺️  DETAILED ITINERARY:")
                print("-" * 40)
                for i, place in enumerate(trip_plan["itinerary"], 1):
                    print(f"{i}. {place['name']}")
                    print(f"   ⏰ Duration: {place.get('visit_duration', 'N/A')}")
                    print(f"   🌅 Best Time: {place.get('best_time', 'N/A')}")
                    print(f"   💰 Cost: {place.get('estimated_cost', 'N/A')}")
                    if place.get('description'):
                        print(f"   📝 {place['description'][:100]}...")
                    print()
            
            # Display daily breakdown if available
            if "daily_breakdown" in trip_plan and trip_plan["daily_breakdown"]:
                print("\n📅 DAILY BREAKDOWN:")
                print("-" * 40)
                for day_plan in trip_plan["daily_breakdown"]:
                    for day, places in day_plan.items():
                        print(f"\n{day}:")
                        for place in places:
                            print(f"  • {place['place']} ({place['duration']}) - {place['best_time']}")
    
    print("=" * 60)
    print("Happy Traveling! ✈️")

# Node 1 - Get input from user
def user_input_node(state: AgentState) -> AgentState:
    print_welcome()
    
    while True:
        try:
            user_input = input("\nEnter your trip details: ").strip()
            if not user_input:
                print("Please enter valid trip details.")
                continue
                
            parts = user_input.split("/")
            if len(parts) != 3:
                print("❌ Invalid format! Please use: destination/budget/duration")
                print("Example: Paris/Medium/5")
                continue
            
            destination, budget, duration = parts
            
            # Validate budget
            if budget.lower() not in ['low', 'medium', 'high']:
                print("❌ Invalid budget! Please choose: Low, Medium, or High")
                continue
            
            # Validate duration
            try:
                duration_int = int(duration)
                if duration_int <= 0:
                    print("❌ Duration must be a positive number!")
                    continue
            except ValueError:
                print("❌ Duration must be a number!")
                continue
            
            # Get coordinates
            coords = get_coords(destination)
            if not coords:
                print(f"❌ Could not find coordinates for {destination}. Please check the destination name.")
                continue
            
            print(f"✅ Valid input received!")
            return {
                "user_input": {
                    "destination": {"name": destination, "coords": coords},
                    "budget": budget,
                    "duration": duration
                }
            }
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for using Travel Agent!")
            exit(0)
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            continue

# Node 2 - Get detailed places from place selector
def agent_places_node(state: AgentState) -> AgentState:
    print("\n🔍 Finding the best places to visit...")
    destination = state["user_input"]["destination"]["name"]
    coords = state["user_input"]["destination"]["coords"]
    
    try:
        # Get places directly instead of using agent tool
        from Agents.place_selector import get_detailed_places_for_trip_planning
        places = get_detailed_places_for_trip_planning(destination, coords)
        
        if places:
            places_info = []
            for place in places:
                info = f"{place['name']} - {place['visit_duration']} - {place['best_time']}"
                places_info.append(info)
            result_text = f"Found {len(places)} places for {destination}: {'; '.join(places_info)}"
        else:
            result_text = f"No places found for {destination}"
        
        print("✅ Places found successfully!")
        return {**state, "places": places, "places_text": result_text}
    except Exception as e:
        print(f"❌ Error finding places: {str(e)}")
        return {**state, "places": [], "places_text": f"Error getting places for {destination}: {str(e)}"}

# Node 3 - Get weather information
def agent_weather_node(state: AgentState) -> AgentState:
    print("🌤️  Getting weather information...")
    destination = state["user_input"]["destination"]["name"]
    
    try:
        # Get weather directly instead of using agent tool
        from tools.weather import get_weather
        weather = get_weather(destination)
        print("✅ Weather information retrieved!")
        return {**state, "weather": weather}
    except Exception as e:
        print(f"❌ Error getting weather: {str(e)}")
        return {**state, "weather": {}}

# Node 4 - Create comprehensive trip plan
def agent_trip_plan_node(state: AgentState) -> AgentState:
    print("🗺️  Creating your comprehensive trip plan...")
    destination = state["user_input"]["destination"]["name"]
    budget = state["user_input"]["budget"]
    duration = state["user_input"]["duration"]
    places = state.get("places", [])
    weather = state.get("weather", {})
    coords = state["user_input"]["destination"]["coords"]
    
    try:
        # Use the integrated trip planning function with existing data
        from Agents.trip_planner import plan_trip_with_place_selector
        trip_plan = plan_trip_with_place_selector(destination, coords, weather, budget, duration, existing_places=places)
        print("✅ Trip plan created successfully!")
        return {**state, "trip_plan": trip_plan}
    except Exception as e:
        print(f"❌ Error creating trip plan: {str(e)}")
        return {**state, "trip_plan": {}}

# Node 5 - Display results
def display_results_node(state: AgentState) -> AgentState:
    print_trip_summary(state)
    return state

# Build Graph
graph = StateGraph(AgentState)
graph.add_node("user_input", user_input_node)
graph.add_node("get_places", agent_places_node)
graph.add_node("get_weather", agent_weather_node)
graph.add_node("create_trip_plan", agent_trip_plan_node)
graph.add_node("display_results", display_results_node)

graph.add_edge(START, "user_input")
graph.add_edge("user_input", "get_places")
graph.add_edge("get_places", "get_weather")
graph.add_edge("get_weather", "create_trip_plan")
graph.add_edge("create_trip_plan", "display_results")
graph.add_edge("display_results", END)

# Compile and Run
if __name__ == "__main__":
    try:
        app = graph.compile()
        app.invoke({})
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using Travel Agent!")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please try again or check your input.")
