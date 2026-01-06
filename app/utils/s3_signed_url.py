import boto3
import os

s3 = boto3.client("s3")
BUCKET = os.getenv("S3_BUCKET_NAME")

def generate_signed_url(key, expiry=300):
    return s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": BUCKET,
            "Key": key
        },
        ExpiresIn=expiry
    )
