# 🌍 Travel Agent - Smart AI-Powered Trip Planner

A modern, user-friendly travel planning application that uses AI to create personalized trip itineraries with weather integration, route optimization, and budget considerations.

## ✨ Features

- **🤖 AI-Powered Planning** - Smart recommendations based on your preferences
- **🌤️ Weather Integration** - Plan around real-time weather conditions
- **🗺️ Route Optimization** - Efficient travel between destinations
- **💰 Budget Smart** - Tailored to your budget level (Low/Medium/High)
- **⏰ Time Management** - Optimized visit durations and timing
- **📱 Export Ready** - Download plans in multiple formats (Mobile, HTML, JSON)

## 🚀 Quick Start

### Option 1: Deploy to Streamlit Cloud (Recommended)

**Easiest way to get started!**

1. **Fork this repository** to your GitHub account
2. **Get your API keys:**
   - [Groq API Key](https://console.groq.com) for AI functionality
   - [OpenWeather API Key](https://openweathermap.org/api) for weather data
3. **Deploy to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Set Repository to `your-username/TravelAgent`
   - Set Main file path to `app.py`
   - Add environment variables: `GROQ_API_KEY` and `OPENWEATHER_API_KEY`
   - Click "Deploy!"

**See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.**

### Option 2: Run Locally

**Prerequisites:**
- Python 3.8 or higher
- Internet connection (for weather and place data)

**Installation:**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TravelAgent
   ```

2. **Activate the virtual environment**
   ```bash
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory with your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   OPENWEATHER_API_KEY=your_openweather_api_key_here
   ```

5. **Run the Streamlit app**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:8501` to access the app

## 📖 How to Use

### Step 1: Enter Trip Details
- **Destination**: Enter any city, country, or tourist destination (e.g., "Paris", "Tokyo", "New York")
- **Budget Level**: Choose from Low, Medium, or High
- **Duration**: Set how many days you'll be traveling (1-30 days)

### Step 2: Configure Preferences
- **Weather Information**: Include current weather data to optimize your itinerary
- **Route Optimization**: Optimize travel routes between destinations
- **AI Reasoning**: See how the AI plans your trip (recommended for transparency)

### Step 3: Advanced Options (Optional)
- **Popular Places**: Highlight highly-rated attractions with ⭐
- **Map Links**: Include Google Maps links for each place
- **Daily Breakdown**: Split itinerary across days for better planning
- **Place Icons**: Display emoji icons for different place types
- **Route Details**: Show optimized routes with distances and travel times

### Step 4: Generate Your Plan
Click "🗺️ Plan My Trip" and wait for the AI to create your personalized itinerary!

## 🎯 What You'll Get

### Trip Summary
- Destination, budget, and duration overview
- Current weather conditions
- Total trip duration and places to visit
- Route optimization details

### Detailed Itinerary
- List of places to visit with descriptions
- Visit duration and best times
- Estimated costs for each place
- Travel distances and times between places

### Daily Breakdown
- Places organized by day
- Activity intensity indicators (Light/Balanced/Tight)
- Optimal timing for each activity

### AI Analysis
- Duration analysis and place selection strategy
- AI's reasoning process
- Weather considerations
- Budget analysis
- Timing optimization details

### Export Options
- **📱 Mobile Text**: Download as mobile-friendly text file
- **🌐 HTML Page**: Download as HTML page for offline viewing
- **📊 JSON Data**: Download as JSON data for further processing

## 💡 Pro Tips

- **Use specific city names** (e.g., "Paris" instead of "France") for better results
- **Consider weather** when planning outdoor activities
- **Check the daily breakdown** for realistic timing
- **Use the export options** to save your plan
- **Try different budget levels** to see various options
- **Enable AI reasoning** to understand how the AI makes decisions

## 🛠️ Technical Details

### Architecture
- **Frontend**: Streamlit for user interface
- **AI Engine**: LangChain with Groq LLM
- **Data Sources**: OpenRouteService for routes, OpenWeatherMap for weather
- **Place Data**: OpenTripMap API for tourist attractions

### Key Components
- `app.py`: Main Streamlit application
- `main.py`: Command-line interface with LangGraph
- `Agents/`: AI agents for place selection and trip planning
- `tools/`: Utility functions for weather, routes, and exports

### Dependencies
- `streamlit`: Web application framework
- `langchain`: AI/LLM framework
- `langchain_groq`: Groq LLM integration
- `requests`: HTTP requests for APIs
- `openrouteservice`: Route optimization
- `folium`: Map generation

## 🔧 Troubleshooting

### Common Issues

1. **"Could not find coordinates"**
   - Try using more specific location names
   - Check spelling of the destination

2. **"No places found"**
   - Try a different destination
   - Check your internet connection

3. **API Key Issues**
   - Ensure your `.env` file is in the root directory
   - Verify your API keys are correct
   - Check if you have sufficient API credits

4. **Slow Loading**
   - The app fetches real-time data from multiple APIs
   - First-time requests may take longer
   - Check your internet connection

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Verify your API keys are set correctly
3. Try with a different destination
4. Restart the Streamlit app

## 🤝 Contributing

We welcome contributions! Please feel free to:
- Report bugs
- Suggest new features
- Submit pull requests
- Improve documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenRouteService for route optimization
- OpenWeatherMap for weather data
- OpenTripMap for place information
- Groq for AI/LLM services
- Streamlit for the web framework

---

**Happy Traveling! ✈️**

*Built with ❤️ for travelers who want smart, personalized trip planning.*
