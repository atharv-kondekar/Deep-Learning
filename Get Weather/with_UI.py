import streamlit as st
import os 
import dotenv 
import requests
import json
from  langchain.chat_models import init_chat_model 
dotenv.load_dotenv()
api=os.getenv("open_weather")

# session states 
if "last_city" not in st.session_state:
    st.session_state.last_city = None

if "weather_data" not in st.session_state:
    st.session_state.weather_data=None

if "output" not in st.session_state:
    st.session_state.output= None

# LLm 
llm = init_chat_model(
    model="openai/gpt-oss-120b",
    model_provider="openai",
    api_key=os.getenv("groq_api"),
    base_url="https://api.groq.com/openai/v1"
)

#Weather api 
weather_api = os.getenv("open_weather")

SYSTEM_MESSAGE = """
You interpret live weather data and explain it in simple, clear English.
Rules:
- Do not invent data.
- No exaggeration or dramatic language.
- 3 to 5 sentences max.
- Make the explanation practical (umbrella, clothing, outdoor suitability).
- If data is missing or invalid, say so directly.
"""

st.title("Weather AI Assistant ")
st.text_input("Enter City Name", key="city_input")
city = st.session_state.city_input.strip()

if st.button("Check Weather "):

    if not city:
        st.error("Enter the valid city name")

    else:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api}&units=metric"

        response = requests.get(url)

        if response.status_code != 200:
            st.error("City not found")
        else:
            data = response.json()

            temp = data['main']['temp']
            desc = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind = data['wind']['speed']

            st.session_state.last_city = city
            st.session_state.weather_data = {
                "temp": temp,
                "desc": desc,
                "humidity": humidity,
                "wind": wind,
            }

            # Create prompt
            prompt = f"""
            City: {city}
            Temperature: {temp}°C
            Condition: {desc}
            Humidity: {humidity}%
            Wind speed: {wind} m/s
            """

            result = llm.invoke(
            [
                {
                    "role": "system", 
                    "content": SYSTEM_MESSAGE
                },

                {
                    "role": "user", 
                    "content": prompt
                }
            ])

            
            st.session_state.output = result.content


#Display
if st.session_state.weather_data:
    data = st.session_state.weather_data
    st.subheader(f" Current Weather in **{st.session_state.last_city}**")
    st.write(f"**Temperature:** {data['temp']}°C")
    st.write(f"**Condition:** {data['desc']}")
    st.write(f"**Humidity:** {data['humidity']}%")
    st.write(f"**Wind:** {data['wind']} m/s")

if st.session_state.output:
    st.markdown("### AI Weather Summary")
    st.success(st.session_state.output)



if st.session_state.last_city:
    st.info(f"🔁 Last searched city: **{st.session_state.last_city}**")