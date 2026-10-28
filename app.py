import streamlit as st
import requests
from datetime import datetime
import os
from typing import Optional, Dict, Any

# Page Configuration
st.set_page_config(
    page_title="Weather App",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
.main {
    background-color: #0E1117;
}
.title {
    text-align: center;
    color: #00BFFF;
    font-size: 40px;
    font-weight: bold;
    margin-bottom: 30px;
}
.weather-box {
    background: #1E1E1E;
    padding: 20px;
    border-radius: 15px;
    color: white;
    box-shadow: 0px 0px 15px #00BFFF;
    margin: 20px 0;
}
.forecast-box {
    background: #1E1E1E;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border-left: 4px solid #00BFFF;
}
.error-box {
    background: #3d1f1a;
    padding: 15px;
    border-radius: 10px;
    color: #ff6b6b;
}
</style>
""", unsafe_allow_html=True)

# Constants
API_KEY = os.getenv("WEATHERAPI_KEY", "1d0260351ad64da490885128262507")
BASE_URL = "http://api.weatherapi.com/v1/forecast.json"
DEFAULT_DAYS = 3


@st.cache_data(ttl=600)
def fetch_weather_data(city: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Fetch weather data from API with caching (10 minutes)."""
    try:
        params = {
            "key": api_key,
            "q": city.strip(),
            "days": DEFAULT_DAYS,
            "aqi": "yes",
            "alerts": "yes"
        }
        response = requests.get(BASE_URL, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timeout. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🌐 Connection error. Please check your internet.")
        return None
    except requests.exceptions.HTTPError as e:
        if response.status_code == 400:
            st.error(f"❌ City not found: '{city}'. Please enter a valid city name.")
        else:
            st.error(f"API Error: {response.status_code}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return None


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9/5) + 32


def display_current_weather(data: Dict[str, Any], use_fahrenheit: bool = False) -> None:
    """Display current weather information."""
    try:
        location = data["location"]["name"]
        country = data["location"]["country"]
        
        current = data["current"]
        temp = current["temp_c"]
        feels = current["feelslike_c"]
        humidity = current["humidity"]
        wind = current["wind_kph"]
        pressure = current["pressure_mb"]
        uv = current["uv"]
        visibility = current["vis_km"]
        condition = current["condition"]["text"]
        icon = "https:" + current["condition"]["icon"]
        
        # Convert temperatures if needed
        if use_fahrenheit:
            temp = celsius_to_fahrenheit(temp)
            feels = celsius_to_fahrenheit(feels)
            temp_unit = "°F"
        else:
            temp_unit = "°C"
        
        # Air quality
        try:
            aqi = current["air_quality"]["pm2_5"]
        except KeyError:
            aqi = "N/A"
        
        # Display icon
        col1, col2 = st.columns([1, 3])
        with col1:
            st.image(icon, width=100)
        
        with col2:
            st.markdown(f"<div class='weather-box'>", unsafe_allow_html=True)
            st.success(f"📍 **{location}, {country}**")
            
            # Display metrics in columns
            metric_cols = st.columns(2)
            with metric_cols[0]:
                st.metric("Temperature", f"{temp:.1f} {temp_unit}")
                st.metric("Wind Speed", f"{wind} km/h")
                st.metric("Pressure", f"{pressure} mb")
                st.metric(" UV Index", f"{uv}")
            
            with metric_cols[1]:
                st.metric("Feels Like", f"{feels:.1f} {temp_unit}")
                st.metric("Humidity", f"{humidity}%")
                st.metric(" Visibility", f"{visibility} km")
                if aqi != "N/A":
                    st.metric("PM2.5 AQI", f"{aqi:.2f}")
            
            st.write(f"**Condition:** {condition}")
            st.caption(f"Last updated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")
            st.markdown("</div>", unsafe_allow_html=True)
    except KeyError as e:
        st.error(f"Error parsing weather data: {str(e)}")


def display_forecast(data: Dict[str, Any], use_fahrenheit: bool = False) -> None:
    """Display 3-day forecast."""
    try:
        st.subheader("📅 3-Day Weather Forecast")
        
        forecast_days = data["forecast"]["forecastday"]
        cols = st.columns(len(forecast_days))
        
        for idx, day in enumerate(forecast_days):
            with cols[idx]:
                date = day["date"]
                max_temp = day["day"]["maxtemp_c"]
                min_temp = day["day"]["mintemp_c"]
                avg_temp = day["day"]["avgtemp_c"]
                condition = day["day"]["condition"]["text"]
                forecast_icon = "https:" + day["day"]["condition"]["icon"]
                chance_of_rain = day["day"]["daily_chance_of_rain"]
                
                # Convert temperatures if needed
                if use_fahrenheit:
                    max_temp = celsius_to_fahrenheit(max_temp)
                    min_temp = celsius_to_fahrenheit(min_temp)
                    avg_temp = celsius_to_fahrenheit(avg_temp)
                    temp_unit = "°F"
                else:
                    temp_unit = "°C"
                
                st.markdown(f"<div class='forecast-box'>", unsafe_allow_html=True)
                st.image(forecast_icon, width=80, use_column_width=True)
                st.write(f"**📅 {date}**")
                st.write(f"Max: {max_temp:.1f} {temp_unit}")
                st.write(f"Min: {min_temp:.1f} {temp_unit}")
                st.write(f"Avg: {avg_temp:.1f} {temp_unit}")
                st.write(f"{condition}")
                st.write(f"Rain: {chance_of_rain}%")
                st.markdown("</div>", unsafe_allow_html=True)
    except KeyError as e:
        st.error(f"Error parsing forecast data: {str(e)}")


# Main App
st.markdown("<p class='title'>🌦️ Weather App</p>", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("Settings")
    use_fahrenheit = st.toggle("Use Fahrenheit", value=False, help="Toggle between Celsius and Fahrenheit")
    st.divider()
    st.caption("Tip: Weather data is cached for 10 minutes to improve performance.")

# Main Input
city = st.text_input(
    "Enter City Name",
    placeholder="e.g., London, New York, Tokyo",
    help="Type the name of a city to get its weather"
)

# Buttons
col1, col2 = st.columns([3, 1])
with col1:
    search_button = st.button("Get Weather", use_container_width=True)
with col2:
    refresh_button = st.button("Refresh", use_container_width=True)

# Handle button click
if search_button or refresh_button:
    if not city:
        st.warning("Please enter a city name.")
    else:
        with st.spinner(f"Fetching weather data for {city}..."):
            data = fetch_weather_data(city, API_KEY)
            
            if data:
                display_current_weather(data, use_fahrenheit)
                st.divider()
                display_forecast(data, use_fahrenheit)
            else:
                st.stop()
    
    