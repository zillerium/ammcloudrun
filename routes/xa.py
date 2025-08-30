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

