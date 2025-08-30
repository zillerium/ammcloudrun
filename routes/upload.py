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

