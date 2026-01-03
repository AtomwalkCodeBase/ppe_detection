import os
import time
import requests

ATOMWALK_BASE_URL = os.getenv("ATOMWALK_BASE_URL", "https://crm.atomwalk.com/lab_api")
ATOMWALK_DB_NAME = os.getenv("ATOMWALK_DB_NAME", "LEM_002")
ATOMWALK_DEVICE_NO = os.getenv("ATOMWALK_DEVICE_NO", "123")
ATOMWALK_SECRET_KEY = os.getenv("ATOMWALK_SECRET_KEY")

_token = None
_token_expiry = 0


def _get_token():
    global _token, _token_expiry

    if _token and time.time() < _token_expiry:
        return _token

    url = f"{ATOMWALK_BASE_URL}/lab_device_auth/{ATOMWALK_DB_NAME}/"

    resp = requests.post(
        url,
        json={
            "device_no": ATOMWALK_DEVICE_NO,
            "secret_key": ATOMWALK_SECRET_KEY
        },
        timeout=10
    )

    if not resp.ok:
        raise Exception(
            f"Atomwalk auth failed | {resp.status_code} | {resp.text}"
        )

    data = resp.json()
    _token = data["token"]
    _token_expiry = time.time() + data["expires_in"] - 30

    return _token


def upload_to_atomwalk(image_path: str, violation: str, lab_id: str):
    token = _get_token()

    url = f"{ATOMWALK_BASE_URL}/lab_device_upload_data/{ATOMWALK_DB_NAME}/"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    data = {
        "iot_data": "PPE",
        "data_value": violation,
        "remarks": f"LabGuard | {lab_id}"
    }

    with open(image_path, "rb") as img:
        files = {
            # Image preview
            "ref_image": ("snapshot.jpg", img, "image/jpeg"),

            # Same file sent as File
            "ref_file": ("snapshot.jpg", img, "image/jpeg"),
        }

        resp = requests.post(
            url,
            headers=headers,
            data=data,
            files=files,
            timeout=20
        )

    if not resp.ok:
        raise Exception(
            f"Atomwalk upload failed | {resp.status_code} | {resp.text}"
        )

    return resp.json()
