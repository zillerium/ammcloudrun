# main.py

from flask import Flask, request, jsonify
from rl_agent import GridWorld, Agent

app = Flask(__name__)

@app.route("/", methods=["GET"])
def root():
    return "👋 Python Cloud Run is alive. Use POST /"

@app.route("/", methods=["POST"])
def get_walk():
    data = request.get_json()
    rows = data.get("rows")
    cols = data.get("cols")
    danger_zones = data.get("dangerZones", [])

    # Debug log to verify correct danger zones
    print(f"🔴 Danger zones received: {danger_zones}")

    # Use external RL module
    env = GridWorld(rows, cols, danger_zones)
    agent = Agent(env)
    path = agent.act()

    print(f"✅ Path returned: {path}")
    return jsonify(path)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)

