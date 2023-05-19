import serial
import time

# Configurez ceci avec le port série correct et le débit en bauds de votre Arduino.
arduino = serial.Serial('/dev/tty.usbmodem00001', 9600)

# Ouvrez le fichier pour écrire les données.
with open('Projets/Creation_carte_profondeur/data.txt', 'a') as file:
    # Lisez les données du capteur pendant une certaine durée.
    # Vous pouvez ajuster cette durée en fonction de vos besoins.
    end_time = time.time() + 60*5  # lire pendant 5 minutes
    while time.time() < end_time:
        # Lisez une ligne de données depuis l'Arduino.
        data = arduino.readline().decode().strip()
        print(data)
        # Écrivez la ligne de données dans le fichier.
        file.write(data + '\n')

# Fermez la connexion série avec l'Arduino.
arduino.close()
