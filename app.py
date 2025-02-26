import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai

# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Ensure API key is set
if not API_KEY:
    raise ValueError("❌ ERROR: GOOGLE_API_KEY is missing. Set it in the .env file.")

# Configure the API key for Google Gemini
genai.configure(api_key=API_KEY)

# Initialize Gemini client with the selected model
model = genai.GenerativeModel("models/gemini-1.5-flash")

# Unit conversion categories and conversion factors
conversions = {
    "length": {"meter": 1, "kilometer": 0.001, "mile": 0.000621371, "yard": 1.09361},
    "weight": {"gram": 1, "kilogram": 0.001, "pound": 0.00220462, "ounce": 0.035274},
    "temperature": lambda value, from_unit, to_unit: 
        (value * 1.8 + 32 if from_unit == "celsius" and to_unit == "fahrenheit" else
         (value - 32) / 1.8 if from_unit == "fahrenheit" and to_unit == "celsius" else value),
    "area": {"square_meter": 1, "square_kilometer": 0.000001, "square_mile": 3.861e-7, "acre": 0.000247105},
    "volume": {"liter": 1, "milliliter": 1000, "cubic_meter": 0.001, "gallon": 0.264172}
}

# Streamlit UI
st.title("Unit Converter with Optional Gemini Chatbot")

# Unit selection
st.subheader("Select Units")
category = st.selectbox("Select Category", list(conversions.keys()))
from_unit = st.selectbox("From Unit", list(conversions[category]) if category != "temperature" else ["celsius", "fahrenheit"])
to_unit = st.selectbox("To Unit", list(conversions[category]) if category != "temperature" else ["celsius", "fahrenheit"])
value = st.number_input("Enter Value", min_value=0.0, step=0.1)

# Handle conversion through Gemini
def handle_conversion(query):
    try:
        response = model.generate_content(query)
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"

# Local conversion logic
def convert_locally(value, from_unit, to_unit):
    if category == "temperature":
        return conversions[category](value, from_unit, to_unit)
    else:
        return value * (conversions[category][to_unit] / conversions[category][from_unit])

# Conversion buttons
if st.button("Convert with LLM"):
    query = f"Convert {value} {from_unit} to {to_unit}."
    result = handle_conversion(query)
    st.success(result)

if st.button("Convert Without LLM"):
    try:
        result = convert_locally(value, from_unit, to_unit)
        st.success(f"Converted Value: {result} {to_unit}")
    except Exception as e:
        st.error(f"Conversion error: {e}")

# Simple Chatbot
st.subheader("Chatbot")
if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.text_input("Ask something... (like 'Convert 5 miles to km')")

if st.button("Send"):
    if user_input:
        st.session_state.messages.append(f"You: {user_input}")
        response = handle_conversion(user_input)
        st.session_state.messages.append(f"Bot: {response}")

for msg in st.session_state.messages:
    st.text(msg)
