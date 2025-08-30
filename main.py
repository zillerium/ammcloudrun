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

