"""
Autonomous Financial Agent Server
Flask application factory — registers route blueprints and serves the
single-page frontend.
"""

from flask import Flask, send_from_directory

from config import BASE_DIR
from routes import plan_bp, event_bp, approve_bp

app = Flask(__name__, static_folder=str(BASE_DIR / "static"))

# Register API blueprints
app.register_blueprint(plan_bp)
app.register_blueprint(event_bp)
app.register_blueprint(approve_bp)


@app.route("/")
def index():
    return send_from_directory(str(BASE_DIR / "static"), "index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
