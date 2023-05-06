import numpy as np
import serial
import time
import sys
import os
import streamlit as st

import plotly.graph_objects as go

current_directory = os.getcwd()
if current_directory not in sys.path:
    sys.path.append(current_directory)

from Projets.Anomalies_vibratoires_accelerometre_AE_debruitage.DenoisingAutoencoder_file import AnomalyDetector

# ==== Parameters ==== #
window_size = 200
time_step = 0.01  # adjust according to the sensor sampling rate
last_warning_time = 0
warning_interval = 5  # seconds
erreur_ser = False
if "acquiring_data" not in st.session_state:
    st.session_state["acquiring_data"] = False

# ====== Model ======= #
model = AnomalyDetector(window_size)
model.load_model()  # Load the model trained on the training data

# ====== Streamlit ====== #
st.set_page_config(layout="wide")
st.title("Shock Detector")
st.write("Press the button to start the detection")
st.divider()
on_off_button = st.button("On/Off")
col1, col2 = st.columns((1, 3))
with col1:
    shock_message = st.empty()

# ====== Serial ====== #
try:
    ser = serial.Serial('/dev/tty.usbmodem00001', 9600)  # Change the port name according to your computer
except:
    erreur_ser = True

if not erreur_ser:

    amplitude = st.empty()
    detected_shock = st.empty()
    figure = st.empty()

    buffer = np.zeros(window_size)


    def read_data():
        global buffer
        try:
            # Read data from serial port
            data = ser.readline().decode('utf-8').strip()
            data = float(data)
            return data
        except serial.serialutil.SerialException as e:
            print(f"Serial error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None


    def update_buffer(data):
        global buffer
        buffer[:-1] = buffer[1:]
        buffer[-1] = data


    def main_loop():
        global buffer, last_warning_time
        if "acquiring_data" in st.session_state:
            if st.session_state["acquiring_data"]:
                data = read_data()
                if data is not None:
                    update_buffer(data)
                    # Predict
                    output = model.predict(buffer)
                    shock = model.detect_shock(buffer, output, threshold=140)

                    # Display
                    # amplitude.write(f"Data: {data:.2f}")

                    # Display warning message if shock is detected and enough time has passed
                    current_time = time.time()
                    if shock and current_time - last_warning_time >= warning_interval:
                        shock_message.error("Shock detected!")
                        last_warning_time = current_time

                    if last_warning_time != 0 and current_time - last_warning_time >= warning_interval:
                        shock_message.empty()

                    # Create a plotly figure that will be displayed in the streamlit app in real time
                    fig = go.Figure()
                    # display max window_size data points
                    fig.add_trace(go.Scatter(x=np.arange(window_size), y=buffer, name="Data"))
                    figure.plotly_chart(fig, use_container_width=True)

            else:
                amplitude.write("Data acquisition paused.")
                detected_shock.write("")


    def toggle_acquiring_data():
        st.session_state["acquiring_data"] = not st.session_state["acquiring_data"]


    if on_off_button:
        toggle_acquiring_data()

    while True:
        main_loop()
        time.sleep(time_step)

else:
    st.error("Le port série n'est pas disponible. Veuillez vérifier que le port série est bien connecté.")
