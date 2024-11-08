#include <ESP32Servo.h>

Servo myServoX;
Servo myServoY;

void setup() {
  Serial.begin(115200);  // Must match the baud rate in your Python script
  myServoX.attach(27);   // Attach the servo to pin 9
  myServoY.attach(26);   // Attach the servo to pin 10
}

void loop() {
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');  // Read until a newline
    int commaIndex = data.indexOf(',');

    if (commaIndex != -1) {
      // Split the incoming data
      int servoX = data.substring(0, commaIndex).toInt();
      int servoY = data.substring(commaIndex + 1).toInt();

      // Map the values if necessary (e.g., 0-180 range)
      myServoX.write(servoX);
      myServoY.write(servoY);
    }
  }
}
