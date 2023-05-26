#!/bin/bash

# Chemin vers le répertoire courant
DIR="$PWD"

# Ouvre une nouvelle fenêtre de terminal et exécute le serveur Mosquitto
osascript -e 'tell application "Terminal" to do script "/opt/homebrew/Cellar/mosquitto/2.0.15/sbin/mosquitto -c /opt/homebrew/Cellar/mosquitto/2.0.15/etc/mosquitto/mosquitto.conf"'

# Ouvre une nouvelle fenêtre de terminal et exécute le script Python pour la gestion des données
osascript -e 'tell application "Terminal" to do script "python3 '"$DIR"'/data_managing.py"'

# Ouvre une nouvelle fenêtre de terminal et exécute l'application Streamlit
osascript -e 'tell application "Terminal" to do script "streamlit run '"$DIR"'/streamlit_app.py"'
