# main.py

from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Load API key from environment (Secret Manager injects this)
API_KEY = os.environ.get("API_KEY", "changeme")

@app.before_request
def require_api_key():
    # Skip for the root GET (optional — remove this if you want even GET to be protected)
    if request.method == "GET":
        return None

    key = request.headers.get("x-api-key")
    if key != API_KEY:
        return jsonify({"error": "unauthorized"}), 401

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)

