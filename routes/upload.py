from flask import jsonify
from plotting.cpmm import generate_cpmm_plot
from plotting.stableswap import generate_stableswap_plot
from storage.uploader import upload_file

def register_upload_routes(app):
    @app.route("/store_image", methods=["POST"])
    def store_image():
        filename = "/tmp/example.png"
        generate_cpmm_plot(filename)
        result = upload_file(filename, "example.png")
        return jsonify(result)

    @app.route("/store_stableswap", methods=["POST"])
    def store_stableswap():
        filename = "/tmp/stableswap.png"
        generate_stableswap_plot(filename)
        result = upload_file(filename, "stableswap.png")
        return jsonify(result)

