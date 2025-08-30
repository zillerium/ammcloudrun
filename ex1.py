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

