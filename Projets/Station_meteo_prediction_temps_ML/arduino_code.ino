#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <Wire.h>
#include <RtcDS1302.h>   // Incluez la bibliothèque RtcDS1302
#include <DHT.h>

// Remplacez par vos identifiants réseau
const char* ssid = "SFR_323F";
const char* password = "4f55kgmqtw3v6ahn5azy";

// Remplacez par l'adresse de votre serveur MQTT
const char* mqtt_server = "192.168.1.37";

#define AIR_QUALITY_SENSOR_PIN 35  // Connectez votre capteur Grove à cette broche

// Pins pour le DS1302
#define CLK_PIN  27
#define DAT_PIN  26
#define RST_PIN  25

// Définir la broche du capteur DHT11
#define DHTPIN 32

// Définir le type de capteur DHT
#define DHTTYPE DHT11

// Initialiser le capteur DHT
DHT dht(DHTPIN, DHTTYPE);

// Créez un objet ThreeWire de manière persistante
ThreeWire myWire = ThreeWire(DAT_PIN, CLK_PIN, RST_PIN);

// Initialisez l'objet RtcDS1302 avec les pins appropriées
RtcDS1302<ThreeWire> Rtc(myWire);

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connexion à ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connecté");
  Serial.println("Adresse IP : ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentative de connexion MQTT...");
    String clientId = "ESP32Client-";
    clientId += String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("connecté");
    } else {
      Serial.print("échec, code erreur = ");
      Serial.print(client.state());
      Serial.println(" nouvel essai dans 5 secondes");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);

  // Initialize DHT
  dht.begin();

  // Initialize RTC
  Rtc.Begin();

  if (!Rtc.GetIsRunning())
  {
    Serial.println("RTC was not actively running, starting now");
    Rtc.SetIsRunning(true);
  }

  RtcDateTime compiled = RtcDateTime(__DATE__, __TIME__);
  if (!Rtc.IsDateTimeValid())
  {
    Serial.println("RTC lost confidence in the DateTime!");
    Rtc.SetDateTime(compiled);
  }

  if (Rtc.GetIsWriteProtected())
  {
    Serial.println("RTC was write protected, enabling writing now");
    Rtc.SetIsWriteProtected(false);
  }

  RtcDateTime now = Rtc.GetDateTime();
  if (now < compiled)
  {
    Serial.println("RTC is older than compile time! Updating");
    Rtc.SetDateTime(compiled);
  }
  else if (now > compiled)
  {
    Serial.println("RTC is newer than compile time. This is expected");
  }
  else if (now == compiled)
  {
    Serial.println("RTC is the same as compile time! (not expected but all is fine)");
  }
}


void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Lecture de la qualité de l'air
  int air_quality = analogRead(AIR_QUALITY_SENSOR_PIN);

  // Lecture des valeurs du capteur DHT11
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Lecture de la date et l'heure du DS1302
  RtcDateTime now = Rtc.GetDateTime();

  // Création du JSON
  StaticJsonDocument<300> doc;
  doc["air_quality"] = air_quality;
  doc["temperature"] = temperature;
  doc["humidity"] = humidity;
  char timestamp[20];
  sprintf(timestamp, "%04d-%02d-%02dT%02d:%02d:%02d", now.Year(), now.Month(), now.Day(), now.Hour(), now.Minute(), now.Second());
  doc["time"] = timestamp;

  char jsonBuffer[512];
  serializeJson(doc, jsonBuffer);

  // Publication sur le topic "weather station"
  client.publish("weather station", jsonBuffer);

  delay(600000);  // Attente de 10 minutes
}