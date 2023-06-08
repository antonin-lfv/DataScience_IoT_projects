import json
import sqlite3
import paho.mqtt.client as mqtt
from datetime import datetime

# Configuration du serveur MQTT
file_path_config = "config.json"
try:
    with open(file_path_config) as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print("Le fichier de configuration n'a pas été trouvé")
    exit(1)

mqtt_server = config['mqtt_server_ip']

# Base de données SQLite
database = sqlite3.connect('accelerometer_sensor_data.db')

# Création de la table s'il n'existe pas déjà
cursor = database.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS donnees_capteurs(
     id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
     timestamp DATETIME,
     capteur TEXT,
     acceleration_x INTEGER,
     acceleration_y INTEGER,
     acceleration_z INTEGER,
     gyroscope_x INTEGER,
     gyroscope_y INTEGER,
     gyroscope_z INTEGER
)
""")
database.commit()

# Buffer pour stocker temporairement les données des capteurs
data_buffer = {}


# Fonctions pour MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {str(rc)}")
    client.subscribe("topicCapteur1")
    client.subscribe("topicCapteur2")
    client.subscribe("topicCapteur3")


def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic}\nMessage: {str(msg.payload)}")

    data = json.loads(msg.payload)
    acceleration = data["acceleration"]
    gyroscope = data["gyroscope"]

    data_buffer[msg.topic] = (acceleration, gyroscope)

    if len(data_buffer) == 3:  # Nous avons reçu des données de tous les capteurs
        timestamp = datetime.now()
        for capteur, data in data_buffer.items():
            acceleration, gyroscope = data
            cursor.execute("""
                INSERT INTO donnees_capteurs(timestamp, capteur, acceleration_x, acceleration_y, acceleration_z, gyroscope_x, gyroscope_y, gyroscope_z) VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                timestamp, capteur,
                acceleration['x'],
                acceleration['y'],
                acceleration['z'],
                gyroscope['x'],
                gyroscope['y'],
                gyroscope['z']))
        database.commit()
        data_buffer.clear()  # Effacer le buffer pour les prochaines données


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_server, 1883, 60)

# Loop forever
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Interrupted by Keyboard")
finally:
    database.close()
