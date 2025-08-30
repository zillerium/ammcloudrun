import os, requests
from flask import jsonify, request
from plotting.cpmm import generate_cpmm_plot

VERCEL_BLOB_URL = "https://api.vercel.com/v2/blob"
BLOB_TOKEN = os.environ.get("BLOB_READ_WRITE_TOKEN")

def register_upload_routes(app):
    @app.route("/store_image", methods=["POST"])
    def store_image():
        # 1. Generate CPMM plot and save under /tmp
        filename = "/tmp/example.png"
        generate_cpmm_plot(filename)

        # 2. Upload to Vercel Blob
        with open(filename, "rb") as f:
            resp = requests.put(
                f"{VERCEL_BLOB_URL}/example.png",
                headers={
                    "Authorization": f"Bearer {BLOB_TOKEN}",
                    "Content-Type": "image/png",
                },
                data=f
            )

        if resp.status_code != 200:
            return jsonify({"error": "Upload failed", "details": resp.text}), resp.status_code

        return jsonify(resp.json())

