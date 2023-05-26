import locale
import datetime
import os

import time
import streamlit as st
import sqlite3
import plotly.graph_objects as go
from datetime import datetime, timedelta

from utils import sidebar_bg

script_dir = os.path.dirname(os.path.realpath(__file__))


# streamlit run streamlit_app.py
# Pour acceder au dashboard depuis un autre appareil sur le meme reseau local: http://192.168.1.37:8501


# ==== Functions ==== #
# Connect to SQLite database
def connect_db_and_fetch_data():
    relative_path_weather_data_db = "weather_data.db"
    file_path_weather_data_db = os.path.join(script_dir, relative_path_weather_data_db)
    conn = sqlite3.connect(file_path_weather_data_db)
    c = conn.cursor()
    # Calculate the date 3 days ago
    three_days_ago = datetime.now() - timedelta(days=3)
    # Convert it to the string format that matches your timestamp column
    three_days_ago_str = three_days_ago.strftime('%Y-%m-%dT%H:%M:%S')
    # Execute SQL to get all records from the last 3 days
    c.execute("SELECT * FROM weather_data WHERE timestamp >= ?", (three_days_ago_str,))
    # Fetch all the rows as a list of tuples
    # Fetch all the rows as a list of tuples
    data = c.fetchall()
    # Transpose rows to columns
    columns = list(zip(*data))
    # Each column is now a separate list, e.g.
    timestamp_list = list(columns[0])
    air_quality_list = list(columns[1])
    # continue for other columns...
    # Remember to close the connection when done
    conn.close()
    return timestamp_list, air_quality_list


# ====== Streamlit ====== #
st.set_page_config(layout="wide", page_title="Station météo", page_icon=":partly_sunny:")
# == Main layout
st.title("Station météo")
warning_message = st.empty()
temperature_container = st.container()
pressure_container, humidity_container, air_quality_container = st.columns(3)
# == Sidebar layout
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
date_actuelle = time.strftime("%d %B %Y")
heure_actuelle = time.strftime("%H:%M")
date_affichage = st.sidebar.title(f"📆 {date_actuelle}")
heure_affichage = st.sidebar.title(f"🕒 {heure_actuelle}")
temperature_actuelle = st.sidebar.empty()
relative_path_side_bg = 'clouds.png'
side_bg = os.path.join(script_dir, relative_path_side_bg)
sidebar_bg(side_bg)

# ======== App ======= #
with temperature_container.expander("TEMPÉRATURE (°C)", expanded=True):
    temperature_aujd, temperature_semaine = st.tabs(["Aujourd'hui", "Ces 3 derniers jours"])
    with temperature_aujd:
        figure_temperature_aujd = st.empty()
    with temperature_semaine:
        figure_temperature_semaine = st.empty()
with pressure_container.expander("PRESSION (hPa)", expanded=True):
    figure_pressure = st.empty()
with humidity_container.expander("HUMIDITÉ (%)", expanded=True):
    figure_humidity = st.empty()
with air_quality_container.expander("QUALITÉ DE L'AIR", expanded=True):
    figure_air_quality = st.empty()

# ====== Serial ====== #
while True:
    timestamps, air_quality = connect_db_and_fetch_data()

    # == Air quality
    max_air_quality = max(max(air_quality), 100)
    figure_air_quality.plotly_chart(
        go.Figure(
            data=go.Scatter(
                x=timestamps,
                y=air_quality,
                mode='lines',
                name='Air quality',
                line=dict(color='rgb(0, 0, 0)', width=2)
            ),
            layout=go.Layout(
                title="Qualité de l'air",
                xaxis=dict(title='Date'),
                yaxis=dict(title='Air quality', range=[0, max_air_quality]),
                template='plotly_white',
                shapes=[
                    dict(
                        type="line",
                        xref="paper", yref="y",
                        x0=0, y0=100, x1=1, y1=100,
                        line=dict(color="Orange", width=2)
                    ),
                    dict(
                        type="line",
                        xref="paper", yref="y",
                        x0=0, y0=200, x1=1, y1=200,
                        line=dict(color="Red", width=2)
                    )
                ]
            )
        ), use_container_width=True
    )

    time.sleep(5)
