from flask import Flask, Response, send_file
import os
from camera_utils import generate_frames, capture_snapshot


app = Flask(__name__)
snapshot_dir = os.path.join(os.path.dirname(__file__), 'tmpsnap', 'snap')

if not os.path.exists(snapshot_dir):
    os.makedirs(snapshot_dir)

@app.route('/mjpeg')
def index():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/snapshot')
def snapshot():
    snapshot_filename = capture_snapshot(snapshot_dir)
    if snapshot_filename:
        return send_file(snapshot_filename, mimetype='image/jpeg')
    else:
        return "Failed to capture image", 500



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
