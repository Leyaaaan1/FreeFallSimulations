"""
wsgi.py – WSGI entrypoint for Vercel
Explicitly exports the Flask app for serverless deployment
"""

import os
import sys

# Add root directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app from the API module
from api.index import app

if __name__ == "__main__":
    app.run()