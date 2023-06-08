#include <Wire.h>
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Remplacer par vos informations de connexion
const char* ssid = "votre_SSID";
const char* password = "votre_mot_de_passe";
const char* mqttServer = "adresse_du_serveur_MQTT";
const int mqttPort = 1883;  // Port MQTT standard

WiFiClient espClient;
PubSubClient client(espClient);

// MPU-6050 configuration
const int MPU_addr = 0x68;  // Adresse I2C du MPU-6050
int16_t AcX, AcY, AcZ, Tmp, GyX, GyY, GyZ; // Variables pour stocker les données du capteur

void setup() {
  Wire.begin();
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  client.setServer(mqttServer, mqttPort);

  while (!client.connected()) {
    Serial.println("Connecting to MQTT...");

    if (client.connect("ESP8266Client")) {
      Serial.println("Connected to MQTT");
    } else {
      Serial.print("Connection failed with state ");
      Serial.print(client.state());
      delay(2000);
    }
  }
}

void loop() {
  Wire.beginTransmission(MPU_addr);
  Wire.write(0x3B);  // Démarre avec le registre 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom(MPU_addr,14,true);  // Demande 14 registres
  AcX=Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)
  AcY=Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  AcZ=Wire.read()<<8|Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  GyX=Wire.read()<<8|Wire.read();  // 0x43 (GYRO_XOUT_H) & 0x44 (GYRO_XOUT_L)
  GyY=Wire.read()<<8|Wire.read();  // 0x45 (GYRO_YOUT_H) & 0x46 (GYRO_YOUT_L)
  GyZ=Wire.read()<<8|Wire.read();  // 0x47 (GYRO_ZOUT_H) & 0x48 (GYRO_ZOUT_L)

  // Création du message JSON
  DynamicJsonDocument doc(1024);

  JsonObject root = doc.to<JsonObject>();
  JsonObject acceleration = root.createNestedObject("acceleration");
  acceleration["x"] = AcX;
  acceleration["y"] = AcY;
  acceleration["z"] = AcZ;

  JsonObject gyroscope = root.createNestedObject("gyroscope");
  gyroscope["x"] = GyX;
  gyroscope["y"] = GyY;
  gyroscope["z"] = GyZ;

  char jsonBuffer[1024];
  serializeJson(root, jsonBuffer);

  // Envoi du message au broker MQTT
  client.publish("topicCapteur1", jsonBuffer);

  delay(2000);
}
