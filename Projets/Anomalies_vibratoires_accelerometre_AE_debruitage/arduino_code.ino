#include <Wire.h>

const int MPU_ADDR = 0x68;
int16_t ax, ay, az;
const int MAX_SAMPLES = 10000;
int sample_count = 0;

void setup() {
  Wire.begin();
  Serial.begin(9600);

  Wire.beginTransmission(MPU_ADDR);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);
}

void loop() {
  if (sample_count < MAX_SAMPLES) {
    Wire.beginTransmission(MPU_ADDR);
    Wire.write(0x3B);
    Wire.endTransmission(false);
    Wire.requestFrom(MPU_ADDR, 6, true);

    ax = Wire.read() << 8 | Wire.read();
    ay = Wire.read() << 8 | Wire.read();
    az = Wire.read() << 8 | Wire.read();

    float ax_mps2 = ax * (2.0 * 9.81) / 32768.0;
    float ay_mps2 = ay * (2.0 * 9.81) / 32768.0;
    float az_mps2 = az * (2.0 * 9.81) / 32768.0;

    float magnitude = sqrt(ax_mps2 * ax_mps2 + ay_mps2 * ay_mps2 + az_mps2 * az_mps2);

    Serial.println(magnitude);
    sample_count++;

    delay(100);
  }
}
