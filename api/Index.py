"""
api/index.py  –  Planetary Free-Fall Web Simulator (Vercel)
"""

import os
import sys
import math
import re

# Add root directory to Python path so we can import freefall_web
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, jsonify, render_template, request

# Fix 1: Import from correct path (freefall_web module)
from freefall_web.physics import (
    PLANETARY_GRAVITY, SHAPE_PARAMS, AIR_DENSITY,
    run_all_planets, terminal_velocity, impact_description,
)


# Fix 2: Configure Flask to find templates and static files
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'),
    static_url_path='/static'
)

# ── Security Headers ───────────────────────────────────────────────────────────
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    if response.content_type and response.content_type.startswith(("image/", "text/css", "application/javascript")):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    else:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

    return response

# ── FontAwesome free-solid icon catalogue ─────────────────────────────────────
FA_ICONS = [
    # physics / objects
    {"name": "circle",        "unicode": "f111", "tags": ["circle", "ball", "round", "sphere"]},
    {"name": "square",        "unicode": "f0c8", "tags": ["square", "box", "cube", "block"]},
    {"name": "rocket",        "unicode": "f135", "tags": ["rocket", "space", "launch", "missile"]},
    {"name": "cube",          "unicode": "f1b2", "tags": ["cube", "3d", "box", "block"]},
    {"name": "sphere",        "unicode": "f1a4", "tags": ["sphere", "ball", "round", "globe"]},
    {"name": "coins",         "unicode": "f51e", "tags": ["money", "coins", "cash"]},
    {"name": "feather",       "unicode": "f52d", "tags": ["feather", "light", "air", "float"]},
    {"name": "meteor",        "unicode": "f753", "tags": ["meteor", "asteroid", "space", "impact"]},
    {"name": "arrow-down",    "unicode": "f063", "tags": ["down", "arrow", "drop", "fall"]},
    {"name": "arrow-up",      "unicode": "f062", "tags": ["up", "arrow", "rise"]},
    {"name": "star",          "unicode": "f005", "tags": ["star", "favorite", "rating"]},
    {"name": "heart",         "unicode": "f004", "tags": ["heart", "love", "favorite"]},
    {"name": "flask",         "unicode": "f0c3", "tags": ["chemistry", "science", "experiment", "physics"]},
    {"name": "microscope",    "unicode": "f578", "tags": ["science", "research", "biology"]},
    {"name": "graduation-cap","unicode": "f19d", "tags": ["education", "learning", "study"]},
    {"name": "book",          "unicode": "f02d", "tags": ["book", "read", "knowledge"]},
]

# Valid icon names cache
VALID_ICONS = {icon["name"] for icon in FA_ICONS} | set(SHAPE_PARAMS.keys())


@app.route("/")
def index():
    return render_template("index.html",
                           planets=list(PLANETARY_GRAVITY.keys()),
                           shapes=list(SHAPE_PARAMS.keys()))


@app.route("/api/icons")
def search_icons():
    """Search FontAwesome icons with input sanitization."""
    try:
        q = request.args.get("q", "").lower().strip()

        if len(q) > 50:
            q = q[:50]

        if not re.match(r"^[a-z0-9\-_\s]*$", q):
            return jsonify([])

        if not q:
            return jsonify(FA_ICONS[:24])

        results = [
            icon for icon in FA_ICONS
            if q in icon["name"] or any(q in tag for tag in icon["tags"])
        ]

        return jsonify(results[:50])

    except Exception as e:
        return jsonify([]), 500


@app.route("/api/simulate", methods=["POST"])
def simulate():
    """Run physics simulation with full input validation."""
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415

        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate mass
        try:
            mass_kg = float(data.get("mass", 1.0))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid mass: must be a number"}), 400

        if mass_kg < 0.001 or mass_kg > 10000:
            return jsonify({"error": "Mass must be between 0.001 and 10000 kg"}), 400

        # Validate shape
        shape = data.get("shape", "circle")
        if shape not in SHAPE_PARAMS:
            return jsonify({
                "error": f"Invalid shape. Allowed: {list(SHAPE_PARAMS.keys())}"
            }), 400

        # Validate height
        try:
            height = float(data.get("height", 100.0))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid height: must be a number"}), 400

        if height <= 0 or height > 100000:
            return jsonify({"error": "Height must be between 0.1 and 100000 meters"}), 400

        # Validate icon
        icon_name = data.get("icon", shape)
        if icon_name not in VALID_ICONS:
            icon_name = shape

        # Run simulation
        results = run_all_planets(mass_kg, shape, height)

        # Build response payload
        payload = []
        for planet, r in results.items():
            vt = r["v_terminal"]
            payload.append({
                "planet":          planet,
                "gravity":         PLANETARY_GRAVITY[planet],
                "air_density":     AIR_DENSITY[planet],
                "fall_time":       round(r["fall_time"], 3),
                "final_velocity":  round(r["final_velocity"], 2),
                "ke_impact":       round(r["ke_impact"], 1),
                "momentum":        round(r["momentum"], 2),
                "v_terminal":      round(vt, 1) if vt != math.inf else None,
                "impact_desc":     impact_description(r["ke_impact"]),
                "t_series":        r["t_series"][::10] + [r["t_series"][-1]],
                "y_series":        r["y_series"][::10] + [r["y_series"][-1]],
                "v_series":        r["v_series"][::10] + [r["v_series"][-1]],
            })

        return jsonify({
            "mass":    mass_kg,
            "shape":   shape,
            "height":  height,
            "icon":    icon_name,
            "results": payload,
        })

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        return jsonify({"error": "Simulation failed. Please try again."}), 500


# Fix 3: For Vercel, export the app directly (don't use if __name__ == "__main__")
# Vercel will call this app object directly

if __name__ == "__main__":
    # Load environment variables
    port = int(os.environ.get("PORT", 5000))
    flask_env = os.environ.get("FLASK_ENV", "development")
    debug = flask_env == "development"

    app.run(debug=debug, host="0.0.0.0", port=port)