import locale
import datetime
import os

import time
import random

import streamlit as st
import sqlite3
import plotly.graph_objects as go
from datetime import datetime, timedelta

from utils import sidebar_bg, interpret_air_quality

script_dir = os.path.dirname(os.path.realpath(__file__))

color_mean = "#85c7ff"


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
    # Calculate the date 1 day ago
    one_day_ago = datetime.now() - timedelta(days=1)
    # Convert it to the string format that matches your timestamp column
    three_days_ago_str = three_days_ago.strftime('%Y-%m-%dT%H:%M:%S')
    one_day_ago_str = one_day_ago.strftime('%Y-%m-%dT%H:%M:%S')
    # Execute SQL to get all records from the last day
    c.execute("SELECT timestamp, air_quality FROM weather_data WHERE timestamp >= ?", (one_day_ago_str,))
    # Fetch all the rows as a list of tuples
    data = c.fetchall()
    # Transpose rows to columns
    columns = list(zip(*data))
    # Each column is now a separate list, e.g.
    timestamp_list = list(columns[0])
    air_quality_list = list(columns[1])
    # continue for other columns...
    # Execute SQL to get temperature records from the last 3 days
    # c.execute("SELECT timestamp, temperature, pressure, humidity FROM weather_data WHERE timestamp >= ?", (three_days_ago_str,))
    # Fetch all the rows as a list of tuples
    # data = c.fetchall()
    # Transpose rows to columns
    # columns = list(zip(*data))
    # Each column is now a separate list, e.g.
    # timestamp_list = list(columns[0])
    # temperature_list = list(columns[1])
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
relative_path_side_bg = 'clouds.png'
side_bg = os.path.join(script_dir, relative_path_side_bg)
sidebar_bg(side_bg)
card_sidebar = st.sidebar.empty()

# ======== App ======= #
with temperature_container.expander("TEMPÉRATURE (°C)", expanded=True):
    temperature_aujd, temperature_semaine = st.tabs(["Aujourd'hui", "Ces 3 derniers jours"])
    with temperature_aujd:
        figure_temperature_aujd = st.empty()
    with temperature_semaine:
        figure_temperature_semaine = st.empty()
with pressure_container.expander("PRESSION (hPa)", expanded=True):
    pressure_now, pressure_last_3_days = st.tabs(["Maintenant", "Ces 3 derniers jours"])
    with pressure_now:
        figure_pressure_now = st.empty()
    with pressure_last_3_days:
        figure_pressure_last_3_days = st.empty()
with humidity_container.expander("HUMIDITÉ (%)", expanded=True):
    humidity_now, humidity_last_3_days = st.tabs(["Maintenant", "Ces 3 derniers jours"])
    with humidity_now:
        figure_humidity_now = st.empty()
    with humidity_last_3_days:
        figure_humidity_last_3_days = st.empty()
with air_quality_container.expander("QUALITÉ DE L'AIR AUJOURD'HUI", expanded=True):
    figure_air_quality = st.empty()

# Préparation du CSS
css = """
    <style>
        .info-card {
            background-color: #FFF;
            border-radius: 5px;
            padding: 10px;
            margin: 10px 0;
            opacity: 0.6;
        }
        .info-card h2 {
            color: #333;
            font-weight: bold;
            font-size: 25px;
        }
        .info-card p {
            color: #666;
            margin: 0;
        }
    </style>
"""
st.sidebar.markdown(css, unsafe_allow_html=True)


# Création de la carte
def card(date, heure, temperature, pressure, humidity, air_quality):
    card = f"""
        <div class="info-card" style="text-align: center;">
            <h2>{date} - {heure}</h2>
        </div>
        <br>
        <div class="info-card" style="text-align: center;">
            <p>Température<p>
            <h2>{temperature}°C</h2>
            <p>Pression<p>
            <h2>{pressure}hPa</h2>
            <p>Humidité<p>
            <h2>{humidity}%</h2>
            <p>Qualité de l'air<p>
            <h2>{interpret_air_quality(air_quality)} ({air_quality})</h2>
        </div>
    """
    return card


# ====== Serial ====== #
while True:
    date_actuelle = time.strftime("%d %B %Y")
    heure_actuelle = time.strftime("%H:%M")

    timestamps, air_quality = connect_db_and_fetch_data()
    fake_temperature_one_day = [random.randint(0, 30) for _ in range(0, len(timestamps))]

    fake_temperature_three_days = [random.randint(0, 30) for _ in range(0, 3 * len(timestamps))]
    fake_timestamps_three_days = [i for i in range(1, 3 * len(timestamps) + 1)]
    fake_pressure = [random.randint(990, 1018) for _ in range(0, 3*len(timestamps))]
    fake_humidity = [random.randint(0, 100) for _ in range(0, 3*len(timestamps))]

    # == Sidebar
    card_sidebar.markdown(card(date_actuelle, heure_actuelle, fake_temperature_one_day[-1],
                               fake_pressure[-1], fake_humidity[-1], air_quality[-1]),
                          unsafe_allow_html=True)

    # == Air quality
    max_air_quality = max(max(air_quality), 100)
    figure_air_quality.plotly_chart(
        go.Figure(
            data=go.Scatter(
                x=timestamps,
                y=air_quality,
                mode='lines',
                name='Air quality',
                line=dict(color='rgb(0, 0, 0)', width=1)
            ),
            layout=go.Layout(
                # title="Aujourd'hui",
                xaxis=dict(title='Date'),
                yaxis=dict(title='Air quality', range=[0, max_air_quality]),
                template='plotly_white',
                shapes=[
                    dict(
                        type="line",
                        xref="paper", yref="y",
                        x0=0, y0=100, x1=1, y1=100,
                        line=dict(color='green',
                                  width=1)
                    ),
                    dict(
                        type="line",
                        xref="paper", yref="y",
                        x0=0, y0=200, x1=1, y1=200,
                        line=dict(color="orange", width=2)
                    )
                ]
            )
        ), use_container_width=True
    )

    # == Temperature one day
    max_temperature_one_day = max(max(fake_temperature_one_day), 30)
    # Calculez la moyenne des températures
    average_temperature_one_day = sum(fake_temperature_one_day) / len(fake_temperature_one_day)

    figure_temperature_aujd.plotly_chart(
        go.Figure(
            data=[
                go.Scatter(
                    x=timestamps,
                    y=fake_temperature_one_day,
                    mode='lines',
                    name='Temperature',
                    line=dict(color='rgb(0, 0, 0)', width=1)
                )
            ],
            layout=go.Layout(
                xaxis=dict(title='Date'),
                yaxis=dict(title='Temperature', range=[0, max_temperature_one_day]),
                template='plotly_white',
                shapes=[
                    # Ajout de la ligne horizontale de la moyenne
                    dict(
                        type='line',
                        yref='y', y0=average_temperature_one_day, y1=average_temperature_one_day,
                        xref='paper', x0=0, x1=1,
                        line=dict(
                            color=color_mean,
                            width=1,
                            dash="dash",
                        )
                    )
                ],
                annotations=[
                    # Ajout de l'annotation de la valeur moyenne
                    dict(
                        xref='paper', x=0.05,
                        yref='y', y=average_temperature_one_day,
                        text=f'Moyenne: {average_temperature_one_day:.2f}°C',
                        showarrow=False,
                        font=dict(
                            size=12,
                            color="Black"
                        ),
                        bgcolor=color_mean,
                        opacity=0.9
                    )
                ]
            )
        ), use_container_width=True
    )

    # == Temperature three days
    max_temperature_three_days = max(max(fake_temperature_three_days), 30)
    # Calculez la moyenne des températures
    average_temperature_three_days = sum(fake_temperature_three_days) / len(fake_temperature_three_days)

    figure_temperature_semaine.plotly_chart(
        go.Figure(
            data=[
                go.Scatter(
                    x=fake_timestamps_three_days,
                    y=fake_temperature_three_days,
                    mode='lines',
                    name='Temperature',
                    line=dict(color='rgb(0, 0, 0)', width=1)
                )
            ],
            layout=go.Layout(
                xaxis=dict(title='Date'),
                yaxis=dict(title='Temperature', range=[0, max_temperature_three_days]),
                template='plotly_white',
                shapes=[
                    # Ajout de la ligne horizontale de la moyenne
                    dict(
                        type='line',
                        yref='y', y0=average_temperature_three_days, y1=average_temperature_three_days,
                        xref='paper', x0=0, x1=1,
                        line=dict(
                            color=color_mean,
                            width=1,
                            dash="dash",
                        )
                    )
                ],
                annotations=[
                    # Ajout de l'annotation de la valeur moyenne
                    dict(
                        xref='paper', x=0.05,
                        yref='y', y=average_temperature_three_days,
                        text=f'Moyenne: {average_temperature_three_days:.2f}°C',
                        showarrow=False,
                        font=dict(
                            size=12,
                            color="Black"
                        ),
                        bgcolor=color_mean,
                        opacity=0.9
                    )
                ]
            )
        ), use_container_width=True
    )

    # == Pressure Now
    figure_pressure_now.plotly_chart(go.Figure(go.Indicator(
        mode="gauge+number",
        value=fake_pressure[-1],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Pression"},
        gauge={
            'axis': {'range': [1013.25 - 30, 1013.25 + 30]},  # Ajuster la plage en fonction de vos données
            'bar': {'color': "black"},  # Couleur de la barre/jauge
            'steps': [
                {'range': [0, 1013.25], 'color': 'lightblue'},  # couleur pour "dépression"
                {'range': [1013.25, 1100], 'color': 'salmon'}  # couleur pour "anticyclone"
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': fake_pressure[-1]
            }
        }
    )), use_container_width=True)

    # == Pressure last 3 days
    # Calcul de la moyenne
    avg_pressure = sum(fake_pressure) / len(fake_pressure)

    figure_pressure_last_3_days.plotly_chart(
        go.Figure(
            data=[
                go.Scatter(
                    x=fake_timestamps_three_days,
                    y=fake_pressure,
                    mode='lines',
                    name='Pression',
                    line=dict(color='rgb(0, 0, 0)', width=1)
                )
            ],
            layout=go.Layout(
                xaxis=dict(title='Date'),
                yaxis=dict(title='Pression', range=[min(fake_pressure), max(fake_pressure)]),
                template='plotly_white',
                shapes=[
                    # Ajout de la ligne horizontale
                    dict(
                        type='line',
                        yref='y', y0=avg_pressure, y1=avg_pressure,
                        xref='paper', x0=0, x1=1,
                        line=dict(
                            color=color_mean,
                            width=1,
                            dash="dash",
                        )
                    )
                ],
                annotations=[
                    # Ajout de l'annotation de la valeur moyenne
                    dict(
                        xref='paper', x=0.05,
                        yref='y', y=avg_pressure,
                        text=f'Moyenne: {avg_pressure:.2f} hPa',
                        showarrow=False,
                        font=dict(
                            size=12,
                            color="Black"
                        ),
                        bgcolor=color_mean,
                        opacity=0.9
                    )
                ]
            )
        ), use_container_width=True
    )

    # == Humidity Now
    figure_humidity_now.plotly_chart(go.Figure(go.Indicator(
        mode="gauge+number",
        value=fake_humidity[-1],
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Humidité"},
        gauge={
            'axis': {'range': [0, 100]},  # Ajuster la plage en fonction de vos données
            'bar': {'color': "black"},  # Couleur de la barre/jauge
            'steps': [
                {'range': [0, 40], 'color': 'lightblue'},
                {'range': [40, 70], 'color': 'lightgreen'},
                {'range': [70, 100], 'color': 'salmon'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': fake_humidity[-1]
            }
        }
    )), use_container_width=True)

    # == Humidity last 3 days
    # Calcul de la moyenne
    avg_humidity = sum(fake_humidity) / len(fake_humidity)

    figure_humidity_last_3_days.plotly_chart(
        go.Figure(
            data=[
                go.Scatter(
                    x=fake_timestamps_three_days,
                    y=fake_humidity,
                    mode='lines',
                    name='Humidité',
                    line=dict(color='rgb(0, 0, 0)', width=1)
                )
            ],
            layout=go.Layout(
                xaxis=dict(title='Date'),
                yaxis=dict(title='Humidité', range=[min(fake_humidity), max(fake_humidity)]),
                template='plotly_white',
                shapes=[
                    # Ajout de la ligne horizontale
                    dict(
                        type='line',
                        yref='y', y0=avg_humidity, y1=avg_humidity,
                        xref='paper', x0=0, x1=1,
                        line=dict(
                            color=color_mean,
                            width=1,
                            dash="dash",
                        )
                    )
                ],
                annotations=[
                    # Ajout de l'annotation de la valeur moyenne
                    dict(
                        xref='paper', x=0.05,
                        yref='y', y=avg_humidity,
                        text=f'Moyenne: {avg_humidity:.2f} %',
                        showarrow=False,
                        font=dict(
                            size=12,
                            color="Black"
                        ),
                        bgcolor=color_mean,
                        opacity=0.9
                    )
                ]
            )
        ), use_container_width=True
    )

    time.sleep(5)
