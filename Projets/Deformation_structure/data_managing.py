import json
import paho.mqtt.client as mqtt
from datetime import datetime
from pymongo import MongoClient

# Configuration du serveur MQTT
file_path_config = "config.json"
try:
    with open(file_path_config) as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print("Le fichier de configuration n'a pas été trouvé")
    exit()

mqtt_server = config['mqtt_server_ip']
mongo_server_url = config['mongo_server_url']

print(f"MQTT server: {mqtt_server}")
print(f"MongoDB server: {mongo_server_url}")

# Créer une connexion à la base de données
client = MongoClient(mongo_server_url)
db = client.deformation_structure_db
collection = db.sensor_data

# run mongodb server : brew services start mongodb-community
# run mosquitto server : /opt/homebrew/Cellar/mosquitto/2.0.15/sbin/mosquitto -c /opt/homebrew/Cellar/mosquitto/2.0.15/etc/mosquitto/mosquitto.conf
# stop mongodb server : brew services stop mongodb-community
# show running services (mosquitto and mongodb) : brew services list

# Buffer pour stocker temporairement les données des capteurs
data_buffer = {}


def store_data_in_db(data_buffer):
    # Formattez vos données comme vous le souhaitez. Ici, nous créons un document avec
    # un champ pour le timestamp, l'accélération et le gyroscope pour chaque capteur.
    data_to_store = {
        'timestamp': datetime.now(),
    }
    for sensor, (acceleration, gyroscope) in data_buffer.items():
        data_to_store[f'{sensor}_acceleration'] = acceleration
        data_to_store[f'{sensor}_gyroscope'] = gyroscope

    # Stockez les données dans la collection 'sensor_data'. Remplacez 'sensor_data' par le nom de votre collection.
    collection.insert_one(data_to_store)


# Fonctions pour MQTT
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {str(rc)}, subscribing to topics...")
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
        store_data_in_db(data_buffer)


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
    # Fermer la connexion à la base de données
    client.disconnect()
