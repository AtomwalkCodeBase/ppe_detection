import boto3
import os
import cv2
from datetime import datetime

s3 = boto3.client("s3")
BUCKET = os.getenv("S3_BUCKET_NAME")

def upload_to_s3(image, lab_id, entry_id):
    date = datetime.utcnow().strftime("%Y-%m-%d")
    key = f"{lab_id}/{date}/{entry_id}.jpg"

    _, buf = cv2.imencode(".jpg", image)

    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=buf.tobytes(),
        ContentType="image/jpeg"
    )

    return key   # ✅ IMPORTANT (store this in DB)
