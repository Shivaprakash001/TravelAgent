import streamlit as st
import json
import os
from dotenv import load_dotenv
from tools.routes import get_coords
from tools.weather import get_weather
from tools.export import get_place_icon, export_trip_plan
from tools.trip_mapper import generate_route_map_data, find_nearby_places
from Agents.place_selector import get_detailed_places_for_trip_planning
from Agents.trip_planner import plan_trip_with_place_selector

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="🌍 Travel Agent - Smart Trip Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS styling for dark mode
st.markdown("""
<style>
    /* Dark mode theme */
    .main {
        background-color: #0e1117;
        color: white;
    }
    .stApp {
        background-color: #0e1117;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: white;
        border-color: #4a5568;
    }
    .stSelectbox > div > div > div {
        background-color: #262730;
        color: white;
    }
    .stNumberInput > div > div > input {
        background-color: #262730;
        color: white;
    }
    .stCheckbox > div > label {
        color: white;
    }
    .stButton > button {
        background-color: #667eea;
        color: white;
        border-radius: 25px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #5a67d8;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-bottom: 1rem;
        border-left: 4px solid #ff7f0e;
        padding-left: 1rem;
    }
    .trip-card {
        background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease;
    }
    .trip-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
    }
    .place-card {
        background: #2d3748;
        color: white;
        padding: 1.2rem;
        border-radius: 12px;
        margin: 0.8rem 0;
        border: 1px solid #4a5568;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        transition: all 0.3s ease;
    }
    .place-card:hover {
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        border-color: #667eea;
        background: #1a202c;
    }
    .weather-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    .success-box {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        color: #68d391;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #4a5568;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    .info-box {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        color: #63b3ed;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #4a5568;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    .warning-box {
        background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        color: #f6ad55;
        padding: 1.2rem;
        border-radius: 10px;
        border: 1px solid #4a5568;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    .metric-card {
        background: #2d3748;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        border: 1px solid #4a5568;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    .feature-item {
        background: #2d3748;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        border: 1px solid #4a5568;
        transition: transform 0.2s ease;
    }
    .feature-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        background: #1a202c;
        border-color: #718096;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1a202c 0%, #2d3748 100%);
    }
    
    /* Map link styling */
    .map-link {
        color: #63b3ed;
        text-decoration: none;
        font-weight: bold;
        padding: 0.5rem 1rem;
        background: #4a5568;
        border-radius: 5px;
        display: inline-block;
        margin-top: 0.5rem;
        transition: all 0.3s ease;
    }
    .map-link:hover {
        background: #667eea;
        color: white;
        text-decoration: none;
    }
    
    /* Text color overrides for dark mode */
    p, h1, h2, h3, h4, h5, h6, span, div {
        color: white !important;
    }
    
    /* Streamlit specific dark mode overrides */
    .stMarkdown {
        color: white;
    }
    .stText {
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'trip_plan' not in st.session_state:
        st.session_state.trip_plan = None
    if 'destination' not in st.session_state:
        st.session_state.destination = ""
    if 'budget' not in st.session_state:
        st.session_state.budget = "Medium"
    if 'duration' not in st.session_state:
        st.session_state.duration = 5
    if 'show_advanced' not in st.session_state:
        st.session_state.show_advanced = False

def show_welcome_section():
    """Display welcome section with features"""
    st.markdown('<h1 class="main-header">🌍 Travel Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 2rem;">Your Smart AI-Powered Trip Planner</p>', unsafe_allow_html=True)
    
    # Feature showcase
    st.markdown("### 🚀 Why Choose Travel Agent?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-item">
            <h4>🤖 AI-Powered</h4>
            <p>Smart recommendations based on your preferences</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-item">
            <h4>🌤️ Weather Aware</h4>
            <p>Plan around real-time weather conditions</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-item">
            <h4>🗺️ Route Optimized</h4>
            <p>Efficient travel between destinations</p>
        </div>
        """, unsafe_allow_html=True)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        st.markdown("""
        <div class="feature-item">
            <h4>💰 Budget Smart</h4>
            <p>Tailored to your budget level</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown("""
        <div class="feature-item">
            <h4>⏰ Time Efficient</h4>
            <p>Optimized visit durations and timing</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col6:
        st.markdown("""
        <div class="feature-item">
            <h4>📱 Export Ready</h4>
            <p>Download plans in multiple formats</p>
        </div>
        """, unsafe_allow_html=True)

def create_sidebar():
    """Create enhanced sidebar with better UX"""
    with st.sidebar:
        st.markdown('<h2 class="sub-header">✈️ Plan Your Trip</h2>', unsafe_allow_html=True)
        
        # Main inputs with better styling and help
        destination = st.text_input(
            "📍 Destination", 
            value=st.session_state.destination,
            placeholder="e.g., Paris, Tokyo, New York",
            help="Enter any city, country, or tourist destination",
            key="destination_input"
        )
        st.session_state.destination = destination
        
        budget = st.selectbox(
            "💰 Budget Level", 
            ["Low", "Medium", "High"], 
            index=1 if st.session_state.budget == "Medium" else 0 if st.session_state.budget == "Low" else 2,
            help="Low: Budget-friendly options, Medium: Balanced choices, High: Premium experiences",
            key="budget_selectbox"
        )
        st.session_state.budget = budget
        
        duration = st.number_input(
            "⏱️ Duration (days)", 
            min_value=1, 
            max_value=30, 
            value=st.session_state.duration,
            help="How many days will you be traveling? (1-30 days)",
            key="duration_input"
        )
        st.session_state.duration = duration
        
        st.markdown("### 🎯 Trip Preferences")
        
        # Basic preferences
        include_weather = st.checkbox(
            "🌤️ Include weather information", 
            value=True,
            help="Get current weather data to optimize your itinerary",
            key="weather_checkbox"
        )
        
        include_routes = st.checkbox(
            "🗺️ Include route optimization", 
            value=True,
            help="Optimize travel routes between destinations",
            key="routes_checkbox"
        )
        
        show_agent_thoughts = st.checkbox(
            "🤖 Show AI reasoning", 
            value=True,
            help="See how the AI plans your trip (recommended for transparency)",
            key="agent_thoughts_checkbox"
        )
        
        # Advanced options toggle
        st.markdown("### ⚙️ Advanced Options")
        show_advanced = st.checkbox("Show advanced options", value=st.session_state.show_advanced, key="advanced_checkbox")
        st.session_state.show_advanced = show_advanced
        
        if show_advanced:
            st.markdown("#### ✨ Display Options")
            show_popular_places = st.checkbox(
                "⭐ Highlight popular places", 
                value=True,
                help="Add star ratings to highly-rated attractions",
                key="popular_places_checkbox"
            )
            show_map_links = st.checkbox(
                 "🗺️ Add map links", 
                 value=True,
                 help="Include Google Maps links for each place",
                 key="map_links_checkbox"
             )
            show_daily_breakdown = st.checkbox(
                "📅 Show daily breakdown", 
                value=True,
                help="Split itinerary across days for better planning",
                key="daily_breakdown_checkbox"
            )
            show_place_icons = st.checkbox(
                "🎯 Show place icons", 
                value=True,
                help="Display emoji icons for different place types",
                key="place_icons_checkbox"
            )
            show_route_optimization = st.checkbox(
                "🚗 Show route details", 
                value=True,
                help="Display optimized route with distances and travel times",
                key="route_optimization_checkbox"
            )
        else:
            # Default values for non-advanced mode
            show_popular_places = True
            show_map_links = True
            show_daily_breakdown = True
            show_place_icons = True
            show_route_optimization = True
        
        # Plan button with enhanced styling
        plan_button = st.button(
            "🗺️ Plan My Trip", 
            type="primary", 
            use_container_width=True,
            help="Click to generate your personalized trip plan",
            key="plan_trip_button"
        )
        
        st.markdown("---")
        
        return plan_button
        
        # Help section
        with st.expander("ℹ️ How it works", expanded=False):
            st.markdown("""
            **Step 1:** Enter your destination (any city or place)
            
            **Step 2:** Choose your budget level:
            - **Low:** Budget-friendly options
            - **Medium:** Balanced choices  
            - **High:** Premium experiences
            
            **Step 3:** Set your trip duration (1-30 days)
            
            **Step 4:** Click "Plan My Trip" to get your personalized itinerary
            
            The AI will:
            - Find the best places to visit
            - Check weather conditions
            - Optimize your route
            - Consider your budget
            - Plan optimal timing
            """)
        
        # Tips section
        with st.expander("💡 Pro Tips", expanded=False):
            st.markdown("""
            **For better results:**
            - Use specific city names (e.g., "Paris" instead of "France")
            - Consider weather when planning outdoor activities
            - Check the daily breakdown for realistic timing
            - Use the export options to save your plan
            - Try different budget levels to see various options
            """)

def show_planning_progress():
    """Show enhanced progress indicators"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Create a more detailed progress display
    progress_steps = [
        ("🔍 Finding the best places to visit...", 25),
        ("🌤️ Getting weather information...", 50),
        ("🗺️ Creating your comprehensive trip plan...", 75),
        ("✅ Trip plan created successfully!", 100)
    ]
    
    return progress_bar, status_text, progress_steps

def display_enhanced_trip_plan(trip_plan, destination, budget, duration, weather, include_weather=True, thoughts_container=None, show_popular_places=True, show_map_links=True, show_daily_breakdown=True, show_place_icons=True, show_route_optimization=True):
    """Display the trip plan with enhanced UI"""
    
    st.markdown('<h2 class="sub-header">🎉 Your Trip Plan is Ready!</h2>', unsafe_allow_html=True)
    
    # Trip summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📍 Destination</h3>
            <p style="font-size: 1.2rem; font-weight: bold; color: #1f77b4;">{destination}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💰 Budget</h3>
            <p style="font-size: 1.2rem; font-weight: bold; color: #ff7f0e;">{budget}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⏱️ Duration</h3>
            <p style="font-size: 1.2rem; font-weight: bold; color: #2ca02c;">{duration} days</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if weather and 'temp' in weather:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🌤️ Temperature</h3>
                <p style="font-size: 1.2rem; font-weight: bold; color: #d62728;">{weather['temp']:.1f}°C</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🌤️ Weather</h3>
                <p style="font-size: 1.2rem; font-weight: bold; color: #d62728;">N/A</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Weather information
    if weather and include_weather:
        with st.container():
            st.markdown('<div class="weather-box">', unsafe_allow_html=True)
            st.markdown(f"### 🌤️ Weather in {destination}")
            if 'temp' in weather and 'weather' in weather:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Temperature", f"{weather['temp']:.1f}°C")
                with col2:
                    st.metric("Conditions", weather['weather'])
            st.markdown('</div>', unsafe_allow_html=True)
    
    if isinstance(trip_plan, dict):
        # Trip statistics with exploration info
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>📋 Total Duration</h3>
                <p style="font-size: 1.2rem; font-weight: bold; color: #1f77b4;">{trip_plan.get('total_duration', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>🏛️ Places to Visit</h3>
                <p style="font-size: 1.2rem; font-weight: bold; color: #ff7f0e;">{trip_plan.get('places_visited', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            route_type = "Optimized" if "Optimized" in str(trip_plan.get('route_details', '')) else "Standard"
            st.markdown(f"""
            <div class="metric-card">
                <h3>🗺️ Route Type</h3>
                <p style="font-size: 1.2rem; font-weight: bold; color: #2ca02c;">{route_type}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            exploration_info = trip_plan.get('exploration_info', {})
            radius_km = exploration_info.get('radius_km', 'N/A')
            st.markdown(f"""
            <div class="metric-card">
                <h3>🔍 Exploration Radius</h3>
                <p style="font-size: 1.2rem; font-weight: bold; color: #d62728;">{radius_km} km</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Route optimization details
        if show_route_optimization and 'trip_summary' in trip_plan:
            trip_summary = trip_plan['trip_summary']
            route_analysis = trip_plan.get('route_analysis', {})
            
            st.markdown("### 🗺️ Route Optimization")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("🚗 Total Distance", f"{trip_summary.get('total_distance_km', 0)} km")
            
            with col2:
                st.metric("⏱️ Travel Time", trip_summary.get('total_travel_time_formatted', 'N/A'))
            
            with col3:
                st.metric("📍 Start Location", trip_summary.get('start_location', 'N/A'))
            
            with col4:
                st.metric("🏁 End Location", trip_summary.get('end_location', 'N/A'))
            
            if route_analysis:
                st.info(f"**Route Analysis:** {route_analysis.get('efficiency', 'N/A')}")
                st.info(f"**Average Distance:** {route_analysis.get('average_distance', 'N/A')}")
                
                if route_analysis.get('suggestions'):
                    st.markdown("**💡 Route Suggestions:**")
                    for suggestion in route_analysis['suggestions']:
                        st.markdown(f"• {suggestion}")
        
        # Detailed itinerary
        if 'itinerary' in trip_plan and trip_plan['itinerary']:
            st.markdown("### 🗺️ Detailed Itinerary")
            
            for i, place in enumerate(trip_plan['itinerary'], 1):
                with st.container():
                    st.markdown(f'<div class="place-card">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        place_name = place['name']
                        if show_popular_places and place.get('is_popular', False):
                            place_name += " ⭐"
                        
                        if show_place_icons:
                            kinds = place.get('kinds', '')
                            icon = get_place_icon(place_name, kinds)
                            st.markdown(f"**{i}. {icon} {place_name}**")
                        else:
                            st.markdown(f"**{i}. {place_name}**")
                        
                        if place.get('description'):
                            st.markdown(f"*{place['description'][:100]}...*")
                        
                        if show_map_links:
                            coords = place.get('point', {})
                            if coords and 'lat' in coords and 'lon' in coords:
                                map_url = f"https://www.google.com/maps?q={coords['lat']},{coords['lon']}"
                                st.markdown(f'<a href="{map_url}" target="_blank" class="map-link">🗺️ View on Map</a>', unsafe_allow_html=True)
                            else:
                                # Fallback: create map link using place name
                                place_name_encoded = place['name'].replace(' ', '+')
                                map_url = f"https://www.google.com/maps/search/{place_name_encoded}+{destination}"
                                st.markdown(f'<a href="{map_url}" target="_blank" class="map-link">🗺️ View on Map</a>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"⏰ **{place.get('visit_duration', 'N/A')}**")
                        st.markdown(f"🌅 **{place.get('best_time', 'N/A')}**")
                        st.markdown(f"💰 **{place.get('estimated_cost', 'N/A')}**")
                        
                        # Show distance from center if available
                        if place.get('distance_from_center'):
                            distance_km = place['distance_from_center']
                            st.markdown(f"📍 **{distance_km} km** from center")
                        
                        if place.get('route_to_next'):
                            route_info = place['route_to_next']
                            st.markdown(f"🚗 **{route_info['distance_km']} km** to {route_info['next_place']}")
                            st.markdown(f"⏱️ **{route_info['travel_time_formatted']}** travel time")
                        elif place.get('distance_to_next'):
                            distance_info = place['distance_to_next']
                            st.markdown(f"🚗 **{distance_info['distance_km']} km** to next")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # Daily breakdown
        if show_daily_breakdown and 'daily_breakdown' in trip_plan and trip_plan['daily_breakdown']:
            st.markdown("### 📅 Daily Breakdown")
            
            for day_plan in trip_plan['daily_breakdown']:
                for day, places in day_plan.items():
                    total_hours = 0
                    for place in places:
                        duration = place['duration']
                        if '1-2' in duration:
                            total_hours += 1.5
                        elif '2-3' in duration:
                            total_hours += 2.5
                        elif '3-4' in duration:
                            total_hours += 3.5
                        else:
                            total_hours += 2.0
                    
                    if total_hours <= 4:
                        intensity = "🟢 Light Day"
                    elif total_hours <= 6:
                        intensity = "🟡 Balanced Day"
                    else:
                        intensity = "🔴 Tight Day"
                    
                    st.markdown(f"**{day}:** {intensity} ({total_hours:.1f} hours)")
                    for place in places:
                        place_name = place['place']
                        if show_popular_places and "⭐" in place_name:
                            place_name += " ⭐"
                        
                        if show_place_icons:
                            kinds = place.get('kinds', '')
                            icon = get_place_icon(place_name, kinds)
                            st.markdown(f"  • **{icon} {place_name}** ({place['duration']}) - {place['best_time']}")
                        else:
                            st.markdown(f"  • **{place_name}** ({place['duration']}) - {place['best_time']}")
                        
                        # Add map link for daily breakdown
                        if show_map_links:
                            place_name_encoded = place_name.replace(' ', '+')
                            map_url = f"https://www.google.com/maps/search/{place_name_encoded}+{destination}"
                            st.markdown(f'<a href="{map_url}" target="_blank" class="map-link" style="font-size: 0.8rem;">🗺️ Map</a>', unsafe_allow_html=True)
                    st.markdown("")
        
        if 'route_details' in trip_plan:
            st.info(f"🗺️ **Route Details:** {trip_plan['route_details']}")
        
        # AI Agent Analysis
        if thoughts_container:
            with thoughts_container:
                st.markdown("### 🤖 AI Agent Analysis")
                
                if 'duration_analysis' in trip_plan:
                    st.markdown("**📅 Duration Analysis:**")
                    st.success(trip_plan['duration_analysis'])
                
                if 'optimal_places_for_duration' in trip_plan:
                    st.markdown("**🎯 Place Selection Strategy:**")
                    optimal_places = trip_plan['optimal_places_for_duration']
                    st.info(f"AI calculated {optimal_places} optimal places for {duration} days based on:")
                    st.markdown(f"• Trip duration: {duration} days = {int(duration) * 8} hours")
                    st.markdown(f"• Budget level: {budget}")
                    if weather and 'weather' in weather:
                        st.markdown(f"• Weather conditions: {weather['weather']}")
                
                if 'exploration_info' in trip_plan:
                    st.markdown("**🔍 Exploration Area Analysis:**")
                    exploration_info = trip_plan['exploration_info']
                    radius_km = exploration_info.get('radius_km', 'N/A')
                    places_explored = exploration_info.get('places_explored', 'N/A')
                    places_selected = exploration_info.get('places_selected', 'N/A')
                    
                    st.success(f"**Exploration Radius:** {radius_km}km around {destination}")
                    st.info(f"**Places Explored:** {places_explored} places found in the area")
                    st.info(f"**Places Selected:** {places_selected} best places chosen for your trip")
                    
                    # Explain the dynamic radius logic
                    if duration_days := int(duration) if duration.isdigit() else 1:
                        if duration_days == 1:
                            st.markdown("• **Short Trip:** Focused on nearby attractions (20km radius)")
                        elif duration_days <= 3:
                            st.markdown("• **Medium Trip:** Extended exploration area for more options")
                        else:
                            st.markdown("• **Long Trip:** Maximum exploration radius for comprehensive coverage")
                
                if 'llm_analysis' in trip_plan:
                    st.markdown("**🤔 AI's Reasoning:**")
                    st.markdown(trip_plan['llm_analysis'])
                
                if 'route_details' in trip_plan:
                    st.markdown("**🗺️ Route Planning:**")
                    st.info(trip_plan['route_details'])
                
                if weather and include_weather:
                    st.markdown("**🌤️ Weather Considerations:**")
                    st.info(f"Temperature: {weather.get('temp', 'N/A')}°C, Conditions: {weather.get('weather', 'N/A')}")
                
                st.markdown("**💰 Budget Analysis:**")
                st.info(f"Budget level: {budget} - Places optimized for {budget.lower()} budget travelers")
                
                if 'itinerary' in trip_plan and trip_plan['itinerary']:
                    st.markdown("**⏰ Timing Optimization:**")
                    timing_analysis = []
                    for place in trip_plan['itinerary']:
                        timing_analysis.append(f"• {place['name']}: {place.get('best_time', 'N/A')} ({place.get('visit_duration', 'N/A')})")
                    st.markdown("\n".join(timing_analysis))
    
    # Export options
    if isinstance(trip_plan, dict):
        st.markdown("### 📱 Export Your Trip Plan")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mobile_export = export_trip_plan(trip_plan, "mobile")
            st.download_button(
                label="📱 Mobile Text",
                data=mobile_export["content"],
                file_name=mobile_export["filename"],
                mime=mobile_export["mime_type"],
                help="Download as mobile-friendly text file",
                use_container_width=True,
                key="mobile_download"
            )
        
        with col2:
            html_export = export_trip_plan(trip_plan, "html")
            st.download_button(
                label="🌐 HTML Page",
                data=html_export["content"],
                file_name=html_export["filename"],
                mime=html_export["mime_type"],
                help="Download as HTML page for offline viewing",
                use_container_width=True,
                key="html_download"
            )
        
        with col3:
            trip_json = json.dumps(trip_plan, indent=2)
            st.download_button(
                label="📊 JSON Data",
                data=trip_json,
                file_name=f"trip_plan_{destination}_{duration}days.json",
                mime="application/json",
                help="Download as JSON data for further processing",
                use_container_width=True,
                key="json_download"
            )

def main():
    """Main application function with enhanced UX"""
    initialize_session_state()
    
    # Show welcome section if no trip plan exists
    if not st.session_state.trip_plan:
        show_welcome_section()
    
    # Create sidebar and get the plan button
    plan_button = create_sidebar()
    
    # Get sidebar values
    destination = st.session_state.destination
    budget = st.session_state.budget
    duration = st.session_state.duration
    show_advanced = st.session_state.show_advanced
    
    # Set default values for advanced options
    include_weather = True
    include_routes = True
    show_agent_thoughts = True
    show_popular_places = True
    show_map_links = True
    show_daily_breakdown = True
    show_place_icons = True
    show_route_optimization = True
    
    # Check if plan button was clicked
    if plan_button and destination:
        with st.spinner("🔍 Planning your perfect trip..."):
            try:
                # Get coordinates
                coords = get_coords(destination)
                if not coords:
                    st.error(f"❌ Could not find coordinates for {destination}. Please check the destination name.")
                    return
                
                # Show progress
                progress_bar, status_text, progress_steps = show_planning_progress()
                
                # Step 1: Find places
                status_text.text(progress_steps[0][0])
                progress_bar.progress(progress_steps[0][1])
                
                places = get_detailed_places_for_trip_planning(destination, coords, str(duration), budget)
                if not places:
                    st.error(f"❌ No places found for {destination}")
                    return
                
                # Step 2: Get weather
                status_text.text(progress_steps[1][0])
                progress_bar.progress(progress_steps[1][1])
                
                weather = {}
                if include_weather:
                    weather = get_weather(destination)
                
                # Step 3: Create trip plan
                status_text.text(progress_steps[2][0])
                progress_bar.progress(progress_steps[2][1])
                
                thoughts_container = None
                if show_agent_thoughts:
                    thoughts_container = st.container()
                    with thoughts_container:
                        st.markdown("### 🤖 AI Agent Analysis")
                        thoughts_placeholder = st.empty()
                        thoughts_placeholder.info("🤔 AI is analyzing places and planning your trip...")
                
                trip_plan = plan_trip_with_place_selector(
                    destination, coords, weather, budget, str(duration), existing_places=places
                )
                
                # Step 4: Complete
                status_text.text(progress_steps[3][0])
                progress_bar.progress(progress_steps[3][1])
                
                # Store trip plan in session state
                st.session_state.trip_plan = trip_plan
                
                # Display the trip plan
                display_enhanced_trip_plan(
                    trip_plan, destination, budget, duration, weather, 
                    include_weather, thoughts_container, show_popular_places, 
                    show_map_links, show_daily_breakdown, show_place_icons, 
                    show_route_optimization
                )
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.info("Please try again with a different destination or check your input.")
    
    elif plan_button and not destination:
        st.warning("⚠️ Please enter a destination to plan your trip.")
    
    # Display existing trip plan if available
    elif st.session_state.trip_plan:
        display_enhanced_trip_plan(
            st.session_state.trip_plan, destination, budget, duration, {}, 
            include_weather, None, show_popular_places, show_map_links, 
            show_daily_breakdown, show_place_icons, show_route_optimization
        )
    
    # Show help section if no trip plan
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            ### 🎯 Ready to Start Planning?
            
            **Enter your trip details in the sidebar to get started:**
            
            ✨ **Smart Place Selection** - Discover the best attractions
            🌤️ **Weather Integration** - Plan around weather conditions  
            🗺️ **Route Optimization** - Efficient travel between places
            💰 **Budget Considerations** - Tailored to your budget
            ⏰ **Time Management** - Optimized visit durations
            
            **Quick Start:**
            1. Enter a destination (e.g., "Paris", "Tokyo")
            2. Choose your budget level
            3. Set your trip duration
            4. Click "Plan My Trip"
            """)

if __name__ == "__main__":
    main() 