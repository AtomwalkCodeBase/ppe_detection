
# LabGuard SDK – PPE Entry Capture Client

## Overview

LabGuard SDK is a lightweight Python client that runs inside a laboratory network.
It listens for commands from the LabGuard cloud, captures camera frames from RTSP streams, and securely sends entry images back to the cloud for **PPE detection and compliance verification**.

This SDK is designed to run **continuously** on a lab machine and requires **no manual interaction** once configured.

---

## What This SDK Does

1. Polls the cloud backend for commands (every 0.5s)
2. Waits for a `CAPTURE_ENTRY` command for a specific lab
3. Connects to the lab’s RTSP camera stream
4. Captures a single frame
5. Sends the image to the cloud for:

   * PPE detection
   * Evidence storage
   * Entry approval or rejection
6. Logs all activity locally for audit/debugging

---

## How the Flow Works

```
User clicks "Enter Lab" (LMS / Mobile / Web)
        ↓
Cloud creates CAPTURE_ENTRY command
        ↓
SDK polls cloud and receives command
        ↓
SDK captures frame from RTSP camera
        ↓
SDK sends image to cloud (/sdk/ingest)
        ↓
Cloud runs PPE detection + stores evidence
```

---

## Project Structure

```
labguard-sdk/
│
├── sdk.py            # Main SDK runner
├── sdk.json          # SDK configuration (cloud + auth)
├── labs.json         # Lab → RTSP camera mapping
├── logs/
│   └── sdk.log       # Runtime logs
```

---

## Configuration Files

### `sdk.json`

Defines cloud connection and authentication.

```json
{
  "sdk_id": "SDK-LAB-01",
  "api_key": "SDK_NET_01_SECRET",
  "cloud_url": "http://44.222.68.21:8000"
}
```

**Fields**

* `sdk_id` – Unique identifier for this SDK installation
* `api_key` – Secret key issued by LabGuard cloud
* `cloud_url` – Cloud backend base URL

---

### `labs.json`

Maps lab IDs to RTSP camera streams.

```json
{
  "LAB-01": [
    "rtsp://admin:password@192.168.0.60:554/stream1"
  ],
  "LAB-02": [
    "rtsp://192.168.1.20/stream1"
  ]
}
```

**Notes**

* One SDK can serve **multiple labs**
* Each lab can have **multiple RTSP cameras**
* SDK tries cameras in order until a frame is captured

---

## How to Run

### 1. Install dependencies

```bash
pip install requests opencv-python numpy
```

### 2. Configure

* Edit `sdk.json`
* Edit `labs.json`

### 3. Start the SDK

```bash
python sdk.py
```

You should see:

```
[2026-01-03T...] LabGuard SDK started
```

---

## Logs

All logs are written to:

```
logs/sdk.log
```

Log entries include:

* RTSP failures
* Cloud connectivity issues
* Command receipt
* Image ingestion status
