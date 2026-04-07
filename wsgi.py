"""
wsgi.py – WSGI entrypoint for Vercel
Explicitly exports the Flask app for serverless deployment
"""

import os
import sys

# Get the absolute path to the project root
project_root = os.path.dirname(os.path.abspath(__file__))

# Ensure root and api directories are in the path
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the Flask app from the API module
try:
    from api.index import app
except ImportError as e:
    print(f"Failed to import app: {e}")
    raise

if __name__ == "__main__":
    app.run()