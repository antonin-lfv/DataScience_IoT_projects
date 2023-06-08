import paho.mqtt.client as mqtt
import json
import sqlite3
import os

# Obtenez le chemin vers le répertoire contenant le script
script_dir = os.path.dirname(os.path.realpath(__file__))
# Spécifiez le chemin relatif au fichier depuis le répertoire du script
relative_path_weather_data_db = "weather_data.db"
relative_path_config = "config.json"
# Joignez les deux pour obtenir le chemin complet vers le fichier
file_path_weather_data_db = os.path.join(script_dir, relative_path_weather_data_db)
file_path_config = os.path.join(script_dir, relative_path_config)

# Initialisez la base de données
conn = sqlite3.connect(file_path_weather_data_db)
c = conn.cursor()

# Créez la table si elle n'existe pas déjà
c.execute('''
    CREATE TABLE IF NOT EXISTS weather_data
    (timestamp TEXT, air_quality INTEGER, temperature REAL, humidity REAL, pressure REAL, altitude REAL)
''')


try:
    with open(file_path_config) as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print("Le fichier de configuration n'a pas été trouvé")
    exit(1)

ssid = config['ssid']
password = config['password']
mqtt_server = config['mqtt_server_ip']


def on_connect(client, userdata, flags, rc):
    print("Connecté avec le code résultat " + str(rc))
    client.subscribe("weather station")  # ou le nom du topic que vous utilisez


def on_message(client, userdata, msg):
    # print(f"Topic: {msg.topic}, Data: {msg.payload.decode('utf-8')}")
    data = json.loads(msg.payload.decode('utf-8'))
    print(data)

    # Enregistrez les données dans la base de données
    c.execute("INSERT INTO weather_data VALUES (?, ?, ?, ?, ?, ?)",
              (data['time'], data['air_quality'], data['temperature'],
               data['humidity'], data['pressure'], data['altitude'])
              )
    conn.commit()


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(host=mqtt_server, port=1883, keepalive=60)

client.loop_forever()
