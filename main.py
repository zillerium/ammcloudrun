# main.py

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return "👋 Hello World from Python Cloud Run"

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
    app.run(debug=True, host="0.0.0.0", port=8080)

