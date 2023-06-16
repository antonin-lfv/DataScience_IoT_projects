import json
import paho.mqtt.client as mqtt
from datetime import datetime
from pymongo import MongoClient

# Configuration du serveur MQTT
file_path_config = "Projets/Deformation_structure/config.json"
# le fichier config ressemble à ça :
# {
#   "ssid" : "your ssid",
#   "password" : "your password
#   "mqtt_server_ip" : "your mqtt server ip",
#   "mongo_server_url" : "mongodb://localhost:27017/"
# }
try:
    with open(file_path_config) as config_file:
        config = json.load(config_file)
    mqtt_server = config['mqtt_server_ip']
    mongo_server_url = config['mongo_server_url']
    print(f"MQTT server: {mqtt_server}")
    print(f"MongoDB server: {mongo_server_url}")
except FileNotFoundError:
    print("Le fichier de configuration n'a pas été trouvé")
    exit()

# Créer une connexion à la base de données
client = MongoClient(mongo_server_url)
db = client.deformation_structure_db
collection = db.sensor_data

# Ajouter les positions initiales des capteurs dans la base de données depuis le fichier sensor_initial_positions.json
# si la collection history_positions n'existe pas
if 'history_positions' not in db.list_collection_names():
    print("Ajout des positions initiales des capteurs dans la base de données")
    file_path_sensor_positions = "Projets/Deformation_structure/sensor_initial_positions.json"
    try:
        with open(file_path_sensor_positions) as sensor_positions_file:
            sensor_positions = json.load(sensor_positions_file)
        json_to_insert = {
            'timestamp': datetime.now().timestamp() * 1000,
            'positions': sensor_positions
        }
        db.history_positions.insert_one(json_to_insert)
    except FileNotFoundError:
        print("Le fichier de positions initiales des capteurs n'a pas été trouvé")
        exit()
    except Exception as e:
        print(f"Erreur lors de l'insertion des positions initiales des capteurs dans la base de données: {e}")
        exit()

# run mongodb server : brew services start mongodb-community
# run mosquitto server : /opt/homebrew/Cellar/mosquitto/2.0.15/sbin/mosquitto -c /opt/homebrew/Cellar/mosquitto/2.0.15/etc/mosquitto/mosquitto.conf
# stop mongodb server : brew services stop mongodb-community
# stop mosquitto server : brew services stop mosquitto
# show running services (mosquitto and mongodb) : brew services list

# Buffer pour stocker temporairement les données des capteurs
data_buffer = {}


def store_data_in_db(data_buffer):
    # Formattez vos données comme vous le souhaitez. Ici, nous créons un document avec
    # un champ pour le timestamp, l'accélération et le gyroscope pour chaque capteur.
    data_to_store = {
        # timestamp en millisecondes
        'timestamp': datetime.now().timestamp() * 1000,
        'acceleration': data_buffer['acceleration'],
        'gyroscope': data_buffer['gyroscope']
    }

    # Stockez les données dans la collection 'sensor_data'.
    collection.insert_one(data_to_store)


def add_test_data():
    # accelerations
    accel_data = {'capteur0': {'x': 3.1, 'y': 2., 'z': 8.1},
                  'capteur1': {'x': 3., 'y': 2.1, 'z': 8.},
                  'capteur2': {'x': 3.1, 'y': 2.35, 'z': 8.1},
                  'capteur3': {'x': 3.1, 'y': 2.5, 'z': 8.2}}

    # Exemple de données de gyroscope
    gyro_data = {'capteur0': {'x': 3, 'y': 2.2, 'z': 8},
                 'capteur1': {'x': 3.1, 'y': 2.2, 'z': 8.},
                 'capteur2': {'x': 3., 'y': 2.4, 'z': 8.2},
                 'capteur3': {'x': 3.1, 'y': 2., 'z': 8.1}}

    buffer = {"acceleration": accel_data, "gyroscope": gyro_data}
    store_data_in_db(buffer)


add_test_data()


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
