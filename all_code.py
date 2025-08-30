
# ===== FILE: ./all_code.py =====


# ===== FILE: ./auth.py =====

import os
from flask import request, jsonify

API_KEY = os.environ.get("API_KEY", "changeme")

def require_api_key():
    if request.method == "GET":  # optional: leave GET unprotected
        return None
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        return jsonify({"error": "unauthorized 11"}), 401


# ===== FILE: ./ex1.py =====

import os
import boto3
import matplotlib.pyplot as plt
import numpy as np

# --- Config ---
BUCKET_NAME = os.environ.get("AWS_BUCKET_NAME", "ammresearch2")
REGION = os.environ.get("AWS_DEFAULT_REGION", "eu-north-1")
LOCAL_FILE = "/tmp/example1.png"
REMOTE_KEY = "example1.png"

# --- Step 1: generate a simple CPMM plot ---
def generate_cpmm_plot(filename=LOCAL_FILE):
    x0, y0 = 1000, 1000
    k = x0 * y0

    x_values = np.linspace(100, 2000, 100)
    y_values = [k / x for x in x_values]

    plt.figure(figsize=(6, 4))
    plt.plot(x_values, y_values, 'b-', linewidth=2, label="CPMM (xy=k)")
    plt.scatter([x0], [y0], color="red", label="Initial point")
    plt.title("Simple CPMM Curve")
    plt.xlabel("Token X Balance")
    plt.ylabel("Token Y Balance")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"✅ Plot saved to {filename}")

# --- Step 2: upload to S3 ---
def upload_to_s3(local_file, bucket, remote_key):
    s3 = boto3.client("s3")
    s3.upload_file(local_file, bucket, remote_key)
    url = f"https://{bucket}.s3.{REGION}.amazonaws.com/{remote_key}"
    return url

if __name__ == "__main__":
    generate_cpmm_plot()
    try:
        url = upload_to_s3(LOCAL_FILE, BUCKET_NAME, REMOTE_KEY)
        print("✅ Uploaded to:", url)
    except Exception as e:
        print("❌ Upload failed:", e)


# ===== FILE: ./main.py =====

from flask import Flask
from auth import require_api_key
from routes.xa import register_xa_routes
from routes.upload import register_upload_routes

app = Flask(__name__)

# Security: add API key check before each request
app.before_request(require_api_key)

# Register routes from modules
register_xa_routes(app)
register_upload_routes(app)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)


# ===== FILE: ./plotting/cpmm.py =====

import numpy as np
import matplotlib.pyplot as plt

def generate_cpmm_plot(filename="example.png"):
    x0, y0 = 1000, 1000
    k = x0 * y0

    x_values = np.linspace(100, 2000, 10)  # 10 sample points
    y_values = [k / x for x in x_values]

    plt.figure(figsize=(6, 4))
    plt.plot(x_values, y_values, 'b-', linewidth=2, label="CPMM (xy=k)")
    plt.scatter([x0], [y0], color="red", label="Initial point")

    plt.title("Simple CPMM Curve")
    plt.xlabel("Token X Balance")
    plt.ylabel("Token Y Balance")
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


# ===== FILE: ./routes/upload.py =====

from flask import jsonify
from plotting.cpmm import generate_cpmm_plot
from storage.uploader import upload_file

def register_upload_routes(app):
    @app.route("/store_image", methods=["POST"])
    def store_image():
        # 1. Generate CPMM plot
        filename = "/tmp/example.png"
        generate_cpmm_plot(filename)

        # 2. Upload to Vercel Blob
        result = upload_file(filename, "example.png")
        return jsonify(result)


# ===== FILE: ./routes/xa.py =====

from flask import request, jsonify

def register_xa_routes(app):
    @app.route("/", methods=["GET"])
    def root():
        return "👋 Hello World from Python Cloud Run (secured)"

    @app.route("/", methods=["POST"])
    def hello_post():
        data = request.get_json(silent=True) or {}
        x = data.get("x")
        A = data.get("A")
        return jsonify({
            "message": "hello world",
            "x": x,
            "A": A
        })


# ===== FILE: ./storage/uploader.py =====

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

