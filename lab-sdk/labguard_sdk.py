import requests
import time
import json
import base64
import cv2
import numpy as np
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# -----------------------
# Load configs
# -----------------------
with open(os.path.join(BASE_DIR, "sdk.json")) as f:
    SDK_CONFIG = json.load(f)

with open(os.path.join(BASE_DIR, "labs.json")) as f:
    LABS = json.load(f)

CLOUD_URL = SDK_CONFIG["cloud_url"]
API_KEY = SDK_CONFIG["api_key"]

HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def log(msg):
    ts = datetime.utcnow().isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    with open(os.path.join(LOG_DIR, "sdk.log"), "a") as f:
        f.write(line + "\n")

# -----------------------
# RTSP capture
# -----------------------
def capture_frame(rtsp_urls):
    for rtsp in rtsp_urls:
        cap = cv2.VideoCapture(rtsp)
        if not cap.isOpened():
            log(f"RTSP open failed: {rtsp}")
            continue

        ret, frame = cap.read()
        cap.release()

        if ret:
            return frame

    return None

# -----------------------
# Poll cloud for command
# -----------------------
def poll_command(lab_id):
    try:
        resp = requests.get(
            f"{CLOUD_URL}/sdk/commands",
            headers=HEADERS,
            params={"lab_id": lab_id},
            timeout=10
        )
        return resp.json()
    except Exception as e:
        log(f"Poll error: {e}")
        return None

# -----------------------
# Send frame to cloud
# -----------------------
def ingest_frame(lab_id, entry_id, frame):
    _, buf = cv2.imencode(".jpg", frame)
    b64_img = base64.b64encode(buf).decode()

    payload = {
        "lab_id": lab_id,
        "entry_id": entry_id,
        "frames": [b64_img]
    }

    try:
        resp = requests.post(
            f"{CLOUD_URL}/sdk/ingest",
            headers=HEADERS,
            json=payload,
            timeout=30
        )
        log(f"Ingest response: {resp.status_code}")
    except Exception as e:
        log(f"Ingest error: {e}")

# -----------------------
# Main loop
# -----------------------
def run():
    log("LabGuard SDK started")

    while True:
        for lab_id, rtsp_urls in LABS.items():
            cmd = poll_command(lab_id)

            if not cmd or cmd.get("command") == "NONE":
                continue

            if cmd.get("command") == "CAPTURE_ENTRY":
                entry_id = cmd["payload"]["entry_id"]
                log(f"Command received for {lab_id}, entry {entry_id}")

                frame = capture_frame(rtsp_urls)
                if frame is None:
                    log(f"No frame captured for {lab_id}")
                    continue

                ingest_frame(lab_id, entry_id, frame)

        time.sleep(0.5)

if __name__ == "__main__":
    run()
