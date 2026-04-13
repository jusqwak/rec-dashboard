"""
Metaphorical Recreation Center — Backend
Flask + MySQL for persistent storage

This entry point now keeps the backend modular by delegating config,
database utilities, and API routes to separate modules.
"""

from flask import Flask, send_from_directory
from mysql.connector import Error
from db import init_db
from routes import register_routes

# Create the Flask application and register route blueprints from the routes package.
# The static folder serves the frontend assets like index.html, styles.css, and any JS.
app = Flask(__name__, static_folder="static")
register_routes(app)


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


if __name__ == "__main__":
    try:
        init_db()
    except Error as e:
        print(f"\n❌  MySQL connection failed: {e}")
        print("    → Check your .env or database configuration\n")
        raise SystemExit(1)

    print("\n🏊  Rec Center running → http://localhost:5050\n")
    app.run(port=5050, debug=True)
