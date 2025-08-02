"""
Configuration file for Travel Agent app
Contains all customizable settings and constants
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "default_key")

# App Configuration
APP_TITLE = "🌍 Travel Agent - Smart Trip Planner"
APP_ICON = "✈️"
PAGE_LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# Default Values
DEFAULT_BUDGET = "Medium"
DEFAULT_DURATION = 5
DEFAULT_DESTINATION = ""

# Budget Levels
BUDGET_LEVELS = ["Low", "Medium", "High"]
BUDGET_DESCRIPTIONS = {
    "Low": "Budget-friendly options",
    "Medium": "Balanced choices", 
    "High": "Premium experiences"
}

# Duration Limits
MIN_DURATION = 1
MAX_DURATION = 30

# Feature Toggles (Default Settings)
DEFAULT_FEATURES = {
    "include_weather": True,
    "include_routes": True,
    "show_agent_thoughts": True,
    "show_popular_places": True,
    "show_map_links": False,
    "show_daily_breakdown": True,
    "show_place_icons": True,
    "show_route_optimization": True
}

# Progress Steps
PROGRESS_STEPS = [
    ("🔍 Finding the best places to visit...", 25),
    ("🌤️ Getting weather information...", 50),
    ("🗺️ Creating your comprehensive trip plan...", 75),
    ("✅ Trip plan created successfully!", 100)
]

# Export Options
EXPORT_FORMATS = {
    "mobile": {
        "label": "📱 Mobile Text",
        "help": "Download as mobile-friendly text file"
    },
    "html": {
        "label": "🌐 HTML Page", 
        "help": "Download as HTML page for offline viewing"
    },
    "json": {
        "label": "📊 JSON Data",
        "help": "Download as JSON data for further processing"
    }
}

# UI Colors and Styling
COLORS = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e", 
    "success": "#2ca02c",
    "warning": "#d62728",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40"
}

# Feature Icons
FEATURE_ICONS = {
    "ai_powered": "🤖",
    "weather_aware": "🌤️",
    "route_optimized": "🗺️",
    "budget_smart": "💰",
    "time_efficient": "⏰",
    "export_ready": "📱"
}

# Place Type Icons
PLACE_ICONS = {
    "museum": "🏛️",
    "temple": "🛕",
    "park": "🌳",
    "restaurant": "🍽️",
    "hotel": "🏨",
    "shopping": "🛍️",
    "entertainment": "🎭",
    "historical": "🏛️",
    "nature": "🌲",
    "beach": "🏖️",
    "mountain": "⛰️",
    "castle": "🏰",
    "church": "⛪",
    "mosque": "🕌",
    "synagogue": "🕍",
    "monument": "🗽",
    "tower": "🗼",
    "bridge": "🌉",
    "square": "🏛️",
    "garden": "🌺"
}

# Help Messages
HELP_MESSAGES = {
    "destination": "Enter any city, country, or tourist destination",
    "budget": "Low: Budget-friendly options, Medium: Balanced choices, High: Premium experiences",
    "duration": "How many days will you be traveling? (1-30 days)",
    "weather": "Get current weather data to optimize your itinerary",
    "routes": "Optimize travel routes between destinations",
    "ai_reasoning": "See how the AI plans your trip (recommended for transparency)",
    "popular_places": "Add star ratings to highly-rated attractions",
    "map_links": "Include Google Maps links for each place",
    "daily_breakdown": "Split itinerary across days for better planning",
    "place_icons": "Display emoji icons for different place types",
    "route_details": "Display optimized route with distances and travel times"
}

# Error Messages
ERROR_MESSAGES = {
    "no_destination": "⚠️ Please enter a destination to plan your trip.",
    "coordinates_not_found": "❌ Could not find coordinates for {destination}. Please check the destination name.",
    "no_places_found": "❌ No places found for {destination}",
    "general_error": "❌ An error occurred: {error}",
    "try_again": "Please try again with a different destination or check your input."
}

# Success Messages
SUCCESS_MESSAGES = {
    "trip_created": "✅ Trip plan created successfully!",
    "valid_input": "✅ Valid input received!"
}

# Tips and Pro Tips
PRO_TIPS = [
    "Use specific city names (e.g., \"Paris\" instead of \"France\") for better results",
    "Consider weather when planning outdoor activities",
    "Check the daily breakdown for realistic timing",
    "Use the export options to save your plan",
    "Try different budget levels to see various options",
    "Enable AI reasoning to understand how the AI makes decisions"
]

# How It Works Steps
HOW_IT_WORKS = [
    "**Step 1:** Enter your destination (any city or place)",
    "**Step 2:** Choose your budget level:",
    "  - **Low:** Budget-friendly options",
    "  - **Medium:** Balanced choices",  
    "  - **High:** Premium experiences",
    "**Step 3:** Set your trip duration (1-30 days)",
    "**Step 4:** Click \"Plan My Trip\" to get your personalized itinerary",
    "",
    "The AI will:",
    "- Find the best places to visit",
    "- Check weather conditions",
    "- Optimize your route",
    "- Consider your budget",
    "- Plan optimal timing"
]

# Welcome Message
WELCOME_MESSAGE = """
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
"""

# Feature Descriptions
FEATURE_DESCRIPTIONS = {
    "ai_powered": "Smart recommendations based on your preferences",
    "weather_aware": "Plan around real-time weather conditions",
    "route_optimized": "Efficient travel between destinations",
    "budget_smart": "Tailored to your budget level",
    "time_efficient": "Optimized visit durations and timing",
    "export_ready": "Download plans in multiple formats"
} 