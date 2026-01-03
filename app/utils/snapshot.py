import boto3
import cv2
import os
from datetime import datetime

S3_BUCKET = os.environ.get("S3_BUCKET_NAME")
if not S3_BUCKET:
    raise RuntimeError("S3_BUCKET_NAME not set")

AWS_REGION = os.environ.get("AWS_REGION", "eu-north-1")

s3 = boto3.client("s3", region_name=AWS_REGION)


def upload_to_s3(image, lab_id: str, entry_id: str):
    date = datetime.utcnow().strftime("%Y-%m-%d")
    key = f"{lab_id}/{date}/{entry_id}.jpg"

    ok, buffer = cv2.imencode(".jpg", image)
    if not ok:
        raise RuntimeError("Failed to encode image")

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=buffer.tobytes(),
        ContentType="image/jpeg",
        ServerSideEncryption="AES256"
    )

    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": S3_BUCKET,
            "Key": key
        },
        ExpiresIn=3600
    )
