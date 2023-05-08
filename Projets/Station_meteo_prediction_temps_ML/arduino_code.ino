#include <Wire.h>
#include <SFE_BMP180.h>

const int TEMP_OUT_H = 0x41;
const int TEMP_OUT_L = 0x42;

SFE_BMP180 bmp180;

void setup() {
  Wire.begin();
  Serial.begin(9600);

  // Initialize BMP180
  if (!bmp180.begin()) {
    Serial.println("BMP180 init failed!");
    while (1);
  }
}

void loop() {

  // Read temperature and pressure from BMP180
  double bmpTempC, bmpPressure;
  char status = bmp180.startTemperature();
  if (status != 0) {
    delay(status);
    status = bmp180.getTemperature(bmpTempC);
    if (status != 0) {
      status = bmp180.startPressure(3);
      if (status != 0) {
        delay(status);
        status = bmp180.getPressure(bmpPressure, bmpTempC);
      }
    }
  }

  if (status != 0) {
    Serial.print("Temperature BMP180: ");
    Serial.print(bmpTempC, 2);
    Serial.println(" °C");

    Serial.print("Pressure: ");
    Serial.print(bmpPressure, 2);
    Serial.println(" Pa");
  } else {
    Serial.println("Error reading BMP180 data");
  }

  delay(1000);
}