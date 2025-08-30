import os
from flask import request, jsonify

API_KEY = os.environ.get("API_KEY", "changeme")

def require_api_key():
    if request.method == "GET":  # optional: leave GET unprotected
        return None
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        return jsonify({"error": "unauthorized"}), 401

