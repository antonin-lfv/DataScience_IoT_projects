#!/bin/bash

# Run this file from the directory where it is located (Projets/Station_meteo_prediction_temps_ML)

# Chemin vers le répertoire courant
DIR="$PWD"

# Ouvre une nouvelle fenêtre de terminal et exécute le serveur Mosquitto
osascript -e 'tell application "Terminal" to do script "/opt/homebrew/Cellar/mosquitto/2.0.15/sbin/mosquitto -c /opt/homebrew/Cellar/mosquitto/2.0.15/etc/mosquitto/mosquitto.conf"'

# Ouvre une nouvelle fenêtre de terminal et exécute le script Python pour la gestion des données
osascript -e 'tell application "Terminal" to do script "python3 '"$DIR"'/data_managing.py"'

# Ouvre une nouvelle fenêtre de terminal et exécute l'application Streamlit
osascript -e 'tell application "Terminal" to do script "streamlit run '"$DIR"'/streamlit_app.py --theme.primaryColor \"#85c7ff\" --theme.base \"light\" --theme.backgroundColor \"#fcffff\" --theme.secondaryBackgroundColor \"#74b8ce\" --theme.textColor \"#545454\""'
