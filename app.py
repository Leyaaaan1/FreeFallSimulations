"""
app.py – Flask WSGI application for Vercel
Simple, clean entrypoint that prioritizes reliability
"""

import os
import sys

# Ensure the project root is in the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Try to import the Flask app with error handling
try:
    from api.index import app
    print("✓ Successfully imported Flask app from api.index")
except ImportError as e:
    print(f"✗ Failed to import Flask app: {e}")
    # Fallback: create a minimal app if import fails
    from flask import Flask, jsonify
    app = Flask(__name__)

    @app.route("/")
    def error():
        return jsonify({"error": "Failed to load main application. Check logs."}), 500

# Export for Vercel
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)