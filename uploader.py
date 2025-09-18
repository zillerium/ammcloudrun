import os
import boto3
from botocore.exceptions import ClientError

BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME", "ammresearch2")
REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-north-1")

s3 = boto3.client("s3", region_name=REGION)

def upload_file(local_file, remote_name="example.png"):
    """Upload a file to AWS S3"""
    try:
        print(f"🔍 Uploading {local_file} → s3://{BUCKET_NAME}/{remote_name}")
        s3.upload_file(local_file, BUCKET_NAME, remote_name)
        url = f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/{remote_name}"
        return {"url": url, "bucket": BUCKET_NAME, "key": remote_name}

    except ClientError as e:
        # Extract structured AWS error
        err = e.response["Error"]
        print("❌ AWS ClientError:", err)
        return {
            "error": err.get("Code", "Unknown"),
            "message": err.get("Message", str(e)),
            "request_id": e.response.get("ResponseMetadata", {}).get("RequestId"),
            "http_status": e.response.get("ResponseMetadata", {}).get("HTTPStatusCode"),
        }

    except Exception as e:
        # Catch anything else
        print("❌ Unexpected error:", str(e))
        return {"error": "Unexpected", "message": str(e)}

