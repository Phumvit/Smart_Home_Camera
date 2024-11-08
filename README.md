# Smart Home Camera Project

## Overview
This project uses Python with OpenCV, ESPHome YAML configuration, and an Arduino `.ino` file to operate a smart home camera system integrated with Home Assistant. The system detects faces, adjusts the camera orientation, and interacts with Zigbee smart bulb in real time. The camera orientation can be controlled through two modes: **MQTT mode** (using ESPHome) and **Serial mode** (using Arduino).

## Components

### Python (OpenCV)
The Python script uses OpenCV to detect faces in real-time via a connected webcam. Once a face is detected, it can send commands to adjust the servo motors and track the detected face. The control command can be sent in two modes:
   - **MQTT Mode**: Sends commands via MQTT to the ESP32.
   - **Serial Mode**: Sends commands over a serial connection to an Arduino.

### ESPHome Configuration (MQTT Mode)
In MQTT mode, the ESPHome YAML configuration is used to receive MQTT messages that control the servo motors' position. The ESP32 microcontroller subscribes to specific MQTT topics and adjusts the camera’s orientation based on received commands.

### Arduino Code (Serial Mode)
In Serial mode, the Arduino `.ino` file processes data received directly over a serial connection to control the servo motors. The Arduino reads the serial commands and moves the camera to track faces, offering an alternative to MQTT-based control.

## System Setup

1. **Install Home Assistant**: Set up Home Assistant with an MQTT broker to enable communication between components (required for MQTT mode).
2. **Configure ESPHome** (MQTT Mode): Add the YAML configuration to ESPHome and flash it to the ESP32 microcontroller. Ensure it subscribes to the correct MQTT topics.
3. **Run Python Script**: Install OpenCV on the Raspberry Pi and run the Python script to enable face detection. Configure the script to operate in either MQTT or Serial mode as needed.
4. **Upload Arduino Code** (Serial Mode): Use the Arduino IDE to upload the `.ino` file to the Arduino, ensuring proper wiring to the servo motors for smooth camera movement.

## How It Works
1. **Face Detection**: The Python script detects a face and sends servo control commands.
2. **MQTT or Serial Communication**:
   - **MQTT Mode**: Commands are sent via MQTT to the ESP32, which adjusts the camera using the servos.
   - **Serial Mode**: Commands are sent over a serial connection to the Arduino, which directly controls the servos.
3. **Servo Control**: Based on the selected mode, either ESPHome or Arduino adjusts the servo motors to track the detected face.

This setup enables a flexible smart camera system that can detect, track, and interact with other devices through Home Assistant, using either MQTT or Serial communication.

---
