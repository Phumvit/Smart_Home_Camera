import cv2
import time
import os
from datetime import datetime
from mqtt_config import publish_mqtt, initialize_mqtt
from ha_api import async_send_snapshot
import serial

# Initialize camera and settings
camera = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
initialize_mqtt()

# Global settings
current_servo_x, current_servo_y = 90, 90
direction = 1

# Constants
MIN_INTERVAL = 0.05     # mqtt publish rate
INTERVAL_SNAP = 2
FACE_TIMEOUT = 3        # Face timeout after 3 second passes
MODE = "serial"         # "mqtt" or "serial"

if MODE == serial:
    arduinoData = serial.Serial('COM0', 115200)     # 'COM_NUM', Arduino_serial_monitor

# Flag for changing Zigbee smart bulb color
face_detected = False
face_detection_state = False

def publish_face_status(detected):
    if detected:
        mqtt_payload = '{"status": "face_detected"}'
    else:
        mqtt_payload = '{"status": "no_face"}'
    

# Time tracking variables
last_sent_time = last_snapshot_time = last_face_time = 0

# Function to calculate servo positions
def calculate_servo(x, y, w, h, frame_width, frame_height):
    global current_servo_x, current_servo_y

    face_center_x = x + w // 2
    face_center_y = y + h // 2

    x_offset = (face_center_x - frame_width / 2) / (frame_width / 2)
    y_offset = (face_center_y - frame_height / 2) / (frame_height / 2)

    if x_offset > 0.2:
        current_servo_x = max(0, current_servo_x - 3)
    elif x_offset < -0.2:
        current_servo_x = min(180, current_servo_x + 3)

    if y_offset > 0.2:
        current_servo_y = min(180, current_servo_y + 3)
    elif y_offset < -0.2:
        current_servo_y = max(0, current_servo_y - 3)

    return current_servo_x, current_servo_y

# Function to send data to Arduino
def send_servo_data(x=0, y=0, w=0, h=0, sweep=False):
    global last_sent_time, direction, current_servo_x ,current_servo_y

    current_time = time.time()
    if sweep:  # Servo sweep logic when no face detected
        if current_time - last_sent_time > MIN_INTERVAL:
            step = 3
            current_servo_y = 110
            if direction == 1:
                if current_servo_x < 180:
                    current_servo_x += step
                else:
                    direction = -1
            else:
                if current_servo_x > 0:
                    current_servo_x -= step
                else:
                    direction = 1
            send_data(current_servo_x, current_servo_y)
            last_sent_time = current_time
    else:
        if current_time - last_sent_time > MIN_INTERVAL:
            frame_width = camera.get(cv2.CAP_PROP_FRAME_WIDTH)
            frame_height = camera.get(cv2.CAP_PROP_FRAME_HEIGHT)
            servo_x, servo_y = calculate_servo(x, y, w, h, frame_width, frame_height)
            send_data(servo_x, servo_y)
            last_sent_time = current_time

# Helper function to either send data via MQTT or Serial
def send_data(servo_x, servo_y):
    if MODE == "mqtt":
        mqtt_payload = f'{{"x": {180-servo_x}, "y": {servo_y}}}'
        publish_mqtt(mqtt_payload)
    elif MODE == "serial":
        arduinoData.write(f'{servo_x},{180-servo_y}\n'.encode())
        print(f"Sent via Serial: X={servo_x}, Y={servo_y}")

# Frame generator for streaming
def generate_frames():
    global last_face_time, last_snapshot_time ,face_detected, face_detection_state
    while True:
        success, frame = camera.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=8, minSize=(120, 120))
        current_time = time.time()

        if len(faces) > 0:
            last_face_time = current_time

            face_detected = True
            if not face_detection_state:
                publish_face_status(True)  
                face_detection_state = True  
                publish_mqtt('{"color":{"hex":"#ff0000"}}','zigbee2mqtt/lord1/set')     # 'mqtt_messege', 'mqtt topic'

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                send_servo_data(x, y, w, h)
            # Send snapshot based on interval
            if current_time - last_snapshot_time > INTERVAL_SNAP:
                async_send_snapshot()
                last_snapshot_time = current_time
            else:
                print("skip snapshot")

        else:
            face_detected = False  
            if current_time - last_face_time > FACE_TIMEOUT:
                send_servo_data(sweep=True)
                if face_detection_state :
                    publish_mqtt('{"color":{"hex":"#ffff00"}}','zigbee2mqtt/lord1/set') # 'mqtt_messege', 'mqtt topic'
                    publish_face_status(False)
                    face_detection_state = False



        # Overlay timestamp and yield frame for streaming
        overlay_timestamp(frame)
        yield encode_frame(frame)

# Helper function to overlay timestamp on frame
def overlay_timestamp(frame):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

# Helper function to encode frame
def encode_frame(frame):
    ret, buffer = cv2.imencode('.jpg', frame)
    return (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

# Capture snapshot and save to disk
def capture_snapshot(snapshot_dir):
    success, frame = camera.read()
    if success:
        overlay_timestamp(frame)
        snapshot_filename = os.path.join(snapshot_dir, "snapshot.jpg")
        cv2.imwrite(snapshot_filename, frame)
        return snapshot_filename
    return None
