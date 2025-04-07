import streamlit as st
import joblib
import sqlite3
import os
import base64
from datetime import datetime

rf_model = joblib.load("flight_delay_model.joblib")

origin_map = {'ATL': 0, 'CLT': 1, 'DEN': 2, 'DFW': 3, 'IAH': 4, 'LAX': 5, 'ORD': 6, 'PHX': 7, 'SFO': 8}
airline_map = {'AA': 0, 'DL': 1, 'OO': 2, 'UA': 3, 'WN': 4}
airport_list = list(origin_map.keys())
airline_list = list(airline_map.keys())

def fetch_route_features(origin, dest):
    conn = sqlite3.connect("flight_data.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT distance, distancegroup, airtime
        FROM flightsdetail
        WHERE Origin = ? AND Dest = ?
    ''', (origin, dest))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result
    else:
        return None, None, None

def set_bg_local(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as img:
            encoded = base64.b64encode(img.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
                padding-top: 0 !important;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("Background image not found!")

IMAGE_FILE = "background1.png"
set_bg_local(IMAGE_FILE)

# Styling
st.markdown("""
    <style>
    .form-box {
        background-color: rgba(255, 255, 255, 0.92);
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0px 0px 12px rgba(0,0,0,0.2);
        max-width: 600px;
        margin: 0 auto;
    }
    .prediction-box {
        background-color: rgba(255, 255, 255, 0.95);
        padding: 15px;
        border-radius: 10px;
        margin-top: 20px;
        font-size: 18px;
        font-weight: bold;
        color: black;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: white;'>Flight Delay Prediction</h1>", unsafe_allow_html=True)


with st.container():
    st.markdown('<div class="form-box">', unsafe_allow_html=True)

    with st.form("flight_form"):
        col1, col2 = st.columns(2)

        with col1:
            origin = st.selectbox("From", airport_list)
            airline = st.selectbox("Reporting Airline", airline_list)

        with col2:
            dest = st.selectbox("To", airport_list)
            journey_date = st.date_input("Date of Journey")

        agree = st.checkbox("I read and understood the terms and conditions")
        submitted = st.form_submit_button("Search")

    st.markdown('</div>', unsafe_allow_html=True)


if submitted and agree:
    month = journey_date.month
    day = journey_date.day
    weekday = journey_date.weekday() + 1

    distance, distancegroup, airtime = fetch_route_features(origin, dest)

    if distance is not None:
        encoded_origin = origin_map[origin]
        encoded_dest = origin_map[dest]
        encoded_airline = airline_map[airline]

        model_input = [
            month, day, weekday,
            encoded_airline, encoded_origin, encoded_dest,
            distance, distancegroup, airtime
        ]

        prediction = rf_model.predict([model_input])[0]

        if prediction == 1:
            st.markdown("<div class='prediction-box'>⚠️ The flight is likely to be <span style='color:red;'>delayed</span>.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='prediction-box'>✅ The flight is expected to be <span style='color:green;'>on time</span>.</div>", unsafe_allow_html=True)
    else:
        st.warning("Route data not found in the database.")
