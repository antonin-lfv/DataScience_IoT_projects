import locale
import datetime

import serial
import time
import streamlit as st
import sqlite3
import plotly.graph_objects as go

from utils import sidebar_bg

# streamlit run streamlit_app.py
# Pour acceder au dashboard depuis un autre appareil sur le meme reseau local: http://192.168.1.37:8501

# ====== Database connection ====== #
conn = sqlite3.connect('sensors_data.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS measurements
                  (timestamp TEXT, temperature REAL, pressure REAL, humidity REAL)''')
conn.commit()


# ====== CRUD ====== #
def insert_data(timestamp, temperature, pressure, humidity):
    cursor.execute("INSERT INTO measurements (timestamp, temperature, pressure, humidity) VALUES (?, ?, ?, ?)",
                   (timestamp, temperature, pressure, humidity))
    conn.commit()


def get_last_n_elements(window_size):
    cursor.execute("SELECT * FROM measurements ORDER BY timestamp DESC LIMIT ?", (window_size,))
    return cursor.fetchall()


# ====== Read data from serial port ====== #
def read_data():
    """
    Try to read data from the serial port and insert it in the database
    """
    if ser is not None:
        temp, press, humidity = None, None, None
        # Read a line from the serial port
        line = ser.readline().decode('utf-8').strip()
        # Get the current time to save in database
        current_timestamp = time.time()
        if "T" in line:
            temp = float(line.split(":")[1])
            temperature_actuelle.title(f"🌡️ {int(temp)} °C")
        elif "P" in line:
            press = float(line.split(":")[1])
        elif "H" in line:
            # humidity = float(line.split(":")[1])
            ...
        humidity = 70
        insert_data(current_timestamp, temp, press, humidity)

    else:
        warning_message.warning("Le port série n'est pas disponible. "
                                "Veuillez vérifier que le port série est bien connecté.")


# ==== Parameters ==== #
window_size = 100
time_step = 0.01  # adjust according to the sensor sampling rate
ser = None
erreur_ser = False
erreur_values = False
temp, press, humidity = None, None, None

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
date_affichage = st.sidebar.title(f"📆 {date_actuelle} &nbsp;&nbsp; 🕒 {heure_actuelle}")
temperature_actuelle = st.sidebar.empty()
side_bg = 'clouds.png'
sidebar_bg(side_bg)

# ======== App ======= #
with temperature_container.expander("TEMPÉRATURE (°C)", expanded=True):
    temperature_aujd, temperature_semaine = st.tabs(["Aujourd'hui", "Cette semaine"])
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
try:
    ser = serial.Serial('/dev/tty.usbmodem00001', 9600)  # Change the port name according to your computer
    while True:
        read_data()  # try to read data from the serial port and insert it in the database

        # == Display the last n elements from the database for each widget
        ARRAY = get_last_n_elements(window_size)
        timestamps = [t[0] for t in ARRAY]
        timestamps = [datetime.datetime.fromtimestamp(float(t)).strftime('%Y-%m-%dT%H:%M:%S') for t in timestamps]
        temp_array = [t[1] for t in ARRAY]
        press_array = [t[2] for t in ARRAY]
        humidity_array = [t[3] for t in ARRAY]

        if temp_array.count(None) != len(temp_array):
            # Create a plotly figure that will be displayed in the streamlit app in real time
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=timestamps, y=temp_array, name="Température (°C)",
                                     line=dict(color='#85c7ff', width=4),
                                     marker=dict(color='#85c7ff', size=10),
                                     mode='markers'))
            fig.update_yaxes(range=[min([val for val in temp_array if val is not None])*0.9,
                                    max([val for val in temp_array if val is not None])*1.1])
            figure_temperature_aujd.plotly_chart(fig, use_container_width=True)

        if press_array.count(None) != len(press_array):
            # Create a plotly figure that will be displayed in the streamlit app in real time
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=timestamps, y=press_array, name="Pression (hPa)",
                                     line=dict(color='#85c7ff', width=4),
                                     marker=dict(color='#85c7ff', size=5),
                                     mode='markers'))
            fig.update_yaxes(range=[min([val for val in press_array if val is not None])*0.98,
                                    max([val for val in press_array if val is not None])*1.02])
            figure_pressure.plotly_chart(fig, use_container_width=True)

        if humidity_array.count(None) != len(humidity_array):
            # plotly gauge with humidity
            # mean value is 50% for humidity
            fig = go.Figure(go.Indicator(
                domain={'x': [0, 1], 'y': [0, 1]},
                value=humidity_array[-1],
                mode="gauge+number+delta",
                title={'text': "Humidité (%)"},
                delta={'reference': humidity_array[-2] if len(humidity_array) > 1 else humidity_array[-1]},
                gauge={'axis': {'range': [None, 100]},
                       'bar': {'color': "#85c7ff"}}))
            figure_humidity.plotly_chart(fig, use_container_width=True)

        time.sleep(time_step)
except KeyboardInterrupt:
    conn.close()
except serial.SerialException:
    # == offline mode
    warning_message.subheader("Mode hors ligne, aucune donnée n'est disponible via les capteurs.")
    # == Display the last n elements from the database for each widget
    ARRAY = get_last_n_elements(window_size)
    timestamps = [t[0] for t in ARRAY]
    timestamps = [datetime.datetime.fromtimestamp(float(t)).strftime('%Y-%m-%dT%H:%M:%S') for t in timestamps]
    temp_array = [t[1] for t in ARRAY]
    press_array = [t[2] for t in ARRAY]
    humidity_array = [t[3] for t in ARRAY]

    if temp_array is not None:
        # Create a plotly figure that will be displayed in the streamlit app in real time
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=timestamps, y=temp_array, name="Température (°C)",
                                 line=dict(color='#85c7ff', width=4),
                                 marker=dict(color='#85c7ff', size=10)))
        fig.update_yaxes(range=[min(10, min([val for val in temp_array if val is not None])),
                                max(35, max([val for val in temp_array if val is not None]))])
        figure_temperature_aujd.plotly_chart(fig, use_container_width=True)

    if press_array is not None:
        # Create a plotly figure that will be displayed in the streamlit app in real time
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=timestamps, y=press_array, name="Pression (hPa)",
                                 line=dict(color='#85c7ff', width=4),
                                 marker=dict(color='#85c7ff', size=10)))
        fig.update_yaxes(range=[min(990, min([val for val in press_array if val is not None])),
                                max(1015, max([val for val in press_array if val is not None]))])
        figure_pressure.plotly_chart(fig, use_container_width=True)

    if humidity_array is not None:
        # plotly gauge with humidity
        # mean value is 50% for humidity
        fig = go.Figure(go.Indicator(
            domain={'x': [0, 1], 'y': [0, 1]},
            value=humidity_array[-1],
            mode="gauge+number+delta",
            title={'text': "Humidité (%)"},
            delta={'reference': humidity_array[-2] if len(humidity_array) > 1 else humidity_array[-1]},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "#85c7ff"}}))
        figure_humidity.plotly_chart(fig, use_container_width=True)

    time.sleep(time_step)
