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
    c.execute("SELECT timestamp, air_quality, temperature, humidity, altitude "
              "FROM weather_data "
              "WHERE timestamp >= ?", (one_day_ago_str,))
    # Fetch all the rows as a list of tuples
    data = c.fetchall()
    # if the data is empty, return empty lists
    if len(data) == 0:
        return None, None, None, None, None, None, None, None, None
    # Transpose rows to columns
    columns = list(zip(*data))
    # Each column is now a separate list, e.g.
    timestamp_list_one_day = list(columns[0])
    air_quality_list_one_day = list(columns[1])
    temperature_list_one_day = list(columns[2])
    humidity_list_one_day = list(columns[3])
    altitude_list_one_day = list(columns[4])
    # Execute SQL to get temperature, humidity, pressure records from the last 3 days
    c.execute("SELECT timestamp, temperature, humidity, pressure FROM weather_data WHERE timestamp >= ?",
              (three_days_ago_str,))
    # Fetch all the rows as a list of tuples
    data = c.fetchall()
    # Transpose rows to columns
    columns = list(zip(*data))
    # Each column is now a separate list, e.g.
    timestamp_list_three_days = list(columns[0])
    temperature_list_three_days = list(columns[1])
    humidity_list_three_days = list(columns[2])
    pressure_list_three_days = list(columns[3])
    # Remember to close the connection when done
    conn.close()
    return timestamp_list_one_day, air_quality_list_one_day, temperature_list_one_day, humidity_list_one_day, \
        altitude_list_one_day, timestamp_list_three_days, temperature_list_three_days, \
        humidity_list_three_days, pressure_list_three_days


# ====== Streamlit ====== #
st.set_page_config(layout="wide", page_title="Station météo", page_icon=":partly_sunny:")
# == Main layout
st.title("Station météo")
warning_message = st.empty()
temperature_container = st.container()
pressure_container, humidity_container = st.columns(2)
air_quality_container = st.container()
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
def card(date, heure, temperature, pressure, humidity, air_quality, altitude):
    card = f"""
        <div class="info-card" style="text-align: center;">
            <h2>{date} - {heure}</h2>
        </div>
        <br>
        <div class="info-card" style="text-align: center;">
            <p>Température<p>
            <h2>{round(temperature, 1)}°C</h2>
            <p>Altitude<p>
            <h2>{round(altitude, 1)}m</h2>
            <p>Pression<p>
            <h2>{pa_to_hpa(pressure)}hPa</h2>
            <p>Humidité<p>
            <h2>{round(humidity,2)}%</h2>
            <p>Qualité de l'air<p>
            <h2>{interpret_air_quality(air_quality)} ({air_quality})</h2>
        </div>
    """
    return card


def pa_to_hpa(pressure_pa):
    pressure_hpa = pressure_pa / 100.0
    return round(pressure_hpa, 1)


# ====== Serial ====== #
while True:
    date_actuelle = time.strftime("%d %B %Y")
    heure_actuelle = time.strftime("%H:%M")

    timestamp_list_one_day, air_quality_list_one_day, temperature_list_one_day, humidity_list_one_day, \
        altitude_list_one_day, timestamp_list_three_days, temperature_list_three_days, \
        humidity_list_three_days, pressure_list_three_days = connect_db_and_fetch_data()
    if timestamp_list_one_day is None:
        warning_message.warning("La base de données est vide, veuillez patienter le temps de recevoir des données.")
        time.sleep(5)
    else:
        # == Sidebar
        card_sidebar.markdown(card(date_actuelle, heure_actuelle, temperature_list_one_day[-1],
                                   pressure_list_three_days[-1], humidity_list_three_days[-1],
                                   air_quality_list_one_day[-1], altitude_list_one_day[-1]),
                              unsafe_allow_html=True)

        # == Air quality
        # Utiliser une liste en compréhension pour filtrer les valeurs None
        max_air_quality = [x for x in air_quality_list_one_day if x is not None]
        # Calculer le max seulement si la liste filtrée n'est pas vide
        if max_air_quality:
            max_air_quality = max(max(max_air_quality) + 1, 100)
        else:
            max_air_quality = 100
        figure_air_quality.plotly_chart(
            go.Figure(
                data=go.Scatter(
                    x=timestamp_list_one_day,
                    y=air_quality_list_one_day,
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
        filtered_list = [x for x in temperature_list_one_day if x is not None]
        if filtered_list:
            max_temperature_one_day = max(max(filtered_list) + 1, 25)
            min_temperature_one_day = min(min(filtered_list) - 1, 20)
            average_temperature_one_day = sum(filtered_list) / len(filtered_list)
        else:
            max_temperature_one_day = 25
            min_temperature_one_day = 20
            average_temperature_one_day = None

        figure_temperature_aujd.plotly_chart(
            go.Figure(
                data=[
                    go.Scatter(
                        x=timestamp_list_one_day,
                        y=temperature_list_one_day,
                        mode='lines',
                        name='Temperature',
                        line=dict(color='rgb(0, 0, 0)', width=1)
                    )
                ],
                layout=go.Layout(
                    xaxis=dict(title='Date'),
                    yaxis=dict(title='Temperature', range=[min_temperature_one_day, max_temperature_one_day]),
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
        filtered_list = [x for x in temperature_list_three_days if x is not None]
        if filtered_list:
            max_temperature_three_days = max(max(filtered_list) + 1, 25)
            min_temperature_three_days = min(min(filtered_list) - 1, 20)
            average_temperature_three_days = sum(filtered_list) / len(filtered_list)
        else:
            max_temperature_three_days = 25
            min_temperature_three_days = 15
            average_temperature_three_days = None

        figure_temperature_semaine.plotly_chart(
            go.Figure(
                data=[
                    go.Scatter(
                        x=timestamp_list_three_days,
                        y=temperature_list_three_days,
                        mode='lines',
                        name='Temperature',
                        line=dict(color='rgb(0, 0, 0)', width=1)
                    )
                ],
                layout=go.Layout(
                    xaxis=dict(title='Date'),
                    yaxis=dict(title='Temperature', range=[min_temperature_three_days, max_temperature_three_days]),
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
            value=pa_to_hpa(pressure_list_three_days[-1]),
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
                    'value': pressure_list_three_days[-1]
                }
            }
        )), use_container_width=True)

        # == Pressure last 3 days
        # Calcul de la moyenne
        filtered_list = [x for x in pressure_list_three_days if x is not None]
        if filtered_list:
            avg_pressure = sum(filtered_list) / len(filtered_list)
        else:
            avg_pressure = None

        figure_pressure_last_3_days.plotly_chart(
            go.Figure(
                data=[
                    go.Scatter(
                        x=timestamp_list_three_days,
                        y=pressure_list_three_days,
                        mode='lines',
                        name='Pression',
                        line=dict(color='rgb(0, 0, 0)', width=1)
                    )
                ],
                layout=go.Layout(
                    xaxis=dict(title='Date'),
                    yaxis=dict(title='Pression', range=[min(pressure_list_three_days), max(pressure_list_three_days)]),
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
            value=humidity_list_three_days[-1],
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
                    'value': humidity_list_three_days[-1]
                }
            }
        )), use_container_width=True)

        # == Humidity last 3 days
        # Calcul de la moyenne
        filtered_list = [x for x in humidity_list_three_days if x is not None]
        if filtered_list:
            min_humidity_three_days = min(filtered_list) + 1
            max_humidity_three_days = max(filtered_list) - 1
            avg_humidity = sum(filtered_list) / len(filtered_list)
        else:
            min_humidity_three_days = 0
            max_humidity_three_days = 100
            avg_humidity = None

        figure_humidity_last_3_days.plotly_chart(
            go.Figure(
                data=[
                    go.Scatter(
                        x=timestamp_list_three_days,
                        y=humidity_list_three_days,
                        mode='lines',
                        name='Humidité',
                        line=dict(color='rgb(0, 0, 0)', width=1)
                    )
                ],
                layout=go.Layout(
                    xaxis=dict(title='Date'),
                    yaxis=dict(title='Humidité', range=[min_humidity_three_days, max_humidity_three_days]),
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

        # wait 30 seconds
        time.sleep(30)
