import requests
import threading
from config import HA_URL, HA_ACCESS_TOKEN, HA_CAMERA_ENTITY_ID

def send_ha_snapshot():
    headers = {
        'Authorization': f'Bearer {HA_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        "entity_id": HA_CAMERA_ENTITY_ID,
        "filename": "/config/www/tmp/snapshot/facesnap.jpg"
    }
    
    try:
        response = requests.post(HA_URL, headers=headers, json=data)
        if response.status_code == 200:
            print("Snapshot taken and sent to Home Assistant.")
            print(f"Response from HA: {response.status_code} - {response.text}")
        else:
            print(f"Failed to send snapshot to Home Assistant: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error sending snapshot to Home Assistant: {e}")

def async_send_snapshot():
    """Run the send_ha_snapshot function in a separate thread."""
    threading.Thread(target=send_ha_snapshot).start()
