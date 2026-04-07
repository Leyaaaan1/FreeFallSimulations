"""
app.py  –  Planetary Free-Fall Web Simulator
Run:  gunicorn app:app (production) or python app.py (dev)
"""

import os
import sys
import math
import re
from flask import Flask, jsonify, render_template, request
from physics import (
    PLANETARY_GRAVITY, SHAPE_PARAMS, AIR_DENSITY,
    run_all_planets, terminal_velocity, impact_description,
)

app = Flask(__name__)



# ── Security Headers ───────────────────────────────────────────────────────────
@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    # Cache control based on content type
    if response.content_type and response.content_type.startswith(("image/", "text/css", "application/javascript")):
        response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
    else:
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

    return response

# ── FontAwesome free-solid icon catalogue (subset, searchable) ─────────────────
FA_ICONS = [
    # physics / objects
    {"name": "circle",        "unicode": "f111", "tags": ["circle", "ball", "round", "sphere"]},
    {"name": "square",        "unicode": "f0c8", "tags": ["square", "box", "cube", "block"]},
    {"name": "rocket",        "unicode": "f135", "tags": ["rocket", "space", "launch", "missile"]},
    {"name": "bomb",          "unicode": "f1e2", "tags": ["bomb", "explosion", "heavy", "round"]},
    {"name": "baseball-ball", "unicode": "f433", "tags": ["baseball", "ball", "sport", "round"]},
    {"name": "basketball-ball","unicode":"f434", "tags": ["basketball", "ball", "sport", "bounce"]},
    {"name": "football-ball", "unicode": "f44e", "tags": ["football", "ball", "sport"]},
    {"name": "bowling-ball",  "unicode": "f436", "tags": ["bowling", "ball", "heavy", "round"]},
    {"name": "cube",          "unicode": "f1b2", "tags": ["cube", "box", "3d", "block"]},
    {"name": "dice",          "unicode": "f522", "tags": ["dice", "cube", "game", "square"]},
    {"name": "gem",           "unicode": "f3a5", "tags": ["gem", "diamond", "crystal", "jewel"]},
    {"name": "anchor",        "unicode": "f13d", "tags": ["anchor", "heavy", "metal", "ship"]},
    {"name": "dumbbell",      "unicode": "f44b", "tags": ["dumbbell", "weight", "gym", "heavy"]},
    {"name": "hammer",        "unicode": "f6e3", "tags": ["hammer", "tool", "heavy", "metal"]},
    {"name": "wrench",        "unicode": "f0ad", "tags": ["wrench", "tool", "metal", "fix"]},
    {"name": "feather",       "unicode": "f52d", "tags": ["feather", "light", "soft", "bird"]},
    {"name": "leaf",          "unicode": "f06c", "tags": ["leaf", "light", "nature", "plant"]},
    {"name": "paper-plane",   "unicode": "f1d8", "tags": ["plane", "paper", "light", "fly"]},
    {"name": "snowflake",     "unicode": "f2dc", "tags": ["snowflake", "ice", "light", "winter"]},
    # vehicles
    {"name": "car",           "unicode": "f1b9", "tags": ["car", "vehicle", "auto", "drive"]},
    {"name": "truck",         "unicode": "f0d1", "tags": ["truck", "vehicle", "heavy", "cargo"]},
    {"name": "plane",         "unicode": "f072", "tags": ["plane", "aircraft", "fly", "travel"]},
    {"name": "helicopter",    "unicode": "f533", "tags": ["helicopter", "fly", "aircraft", "rotor"]},
    {"name": "bicycle",       "unicode": "f206", "tags": ["bicycle", "bike", "vehicle", "sport"]},
    {"name": "motorcycle",    "unicode": "f21c", "tags": ["motorcycle", "bike", "vehicle", "fast"]},
    {"name": "ship",          "unicode": "f21a", "tags": ["ship", "boat", "vessel", "heavy"]},
    {"name": "shuttle-space", "unicode": "f197", "tags": ["shuttle", "space", "rocket", "nasa"]},
    {"name": "satellite",     "unicode": "f7bf", "tags": ["satellite", "space", "orbit", "signal"]},
    # space / planets
    {"name": "moon",          "unicode": "f186", "tags": ["moon", "space", "night", "planet"]},
    {"name": "sun",           "unicode": "f185", "tags": ["sun", "star", "space", "light"]},
    {"name": "star",          "unicode": "f005", "tags": ["star", "space", "shine", "sky"]},
    {"name": "meteor",        "unicode": "f753", "tags": ["meteor", "asteroid", "space", "fall", "rock"]},
    {"name": "globe",         "unicode": "f0ac", "tags": ["globe", "earth", "planet", "world"]},
    # animals / fun
    {"name": "dove",          "unicode": "f4ba", "tags": ["dove", "bird", "light", "fly", "peace"]},
    {"name": "dragon",        "unicode": "f6d5", "tags": ["dragon", "fantasy", "fly", "beast"]},
    {"name": "fish",          "unicode": "f578", "tags": ["fish", "animal", "water", "swim"]},
    {"name": "horse",         "unicode": "f6f0", "tags": ["horse", "animal", "run", "fast"]},
    {"name": "spider",        "unicode": "f717", "tags": ["spider", "bug", "insect", "small"]},
    # misc
    {"name": "heart",         "unicode": "f004", "tags": ["heart", "love", "soft", "light"]},
    {"name": "crown",         "unicode": "f521", "tags": ["crown", "gold", "heavy", "royal"]},
    {"name": "shield-alt",    "unicode": "f3ed", "tags": ["shield", "armor", "heavy", "protect"]},
    {"name": "apple-alt",     "unicode": "f5d1", "tags": ["apple", "fruit", "newton", "fall"]},
    {"name": "pizza-slice",   "unicode": "f818", "tags": ["pizza", "food", "slice", "triangle"]},
    {"name": "poop",          "unicode": "f619", "tags": ["poop", "funny", "soft", "brown"]},
    {"name": "ghost",         "unicode": "f6e2", "tags": ["ghost", "spooky", "light", "fun"]},
    {"name": "hat-wizard",    "unicode": "f6e8", "tags": ["wizard", "hat", "magic", "fantasy"]},
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

        # Limit query length
        if len(q) > 50:
            q = q[:50]

        # Sanitize: only allow alphanumeric, dash, underscore, space
        if not re.match(r"^[a-z0-9\-_\s]*$", q):
            return jsonify([])

        if not q:
            return jsonify(FA_ICONS[:24])  # default: show first 24

        results = [
            icon for icon in FA_ICONS
            if q in icon["name"] or any(q in tag for tag in icon["tags"])
        ]

        return jsonify(results[:50])  # Limit results to 50

    except Exception as e:
        return jsonify([]), 500


@app.route("/api/simulate", methods=["POST"])
def simulate():
    """Run physics simulation with full input validation."""
    try:
        # Check Content-Type
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 415

        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # ── Validate mass ──────────────────────────────────────
        try:
            mass_kg = float(data.get("mass", 1.0))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid mass: must be a number"}), 400

        if mass_kg < 0.001 or mass_kg > 10000:
            return jsonify({"error": "Mass must be between 0.001 and 10000 kg"}), 400

        # ── Validate shape ─────────────────────────────────────
        shape = data.get("shape", "circle")
        if shape not in SHAPE_PARAMS:
            return jsonify({
                "error": f"Invalid shape. Allowed: {list(SHAPE_PARAMS.keys())}"
            }), 400

        # ── Validate height ────────────────────────────────────
        try:
            height = float(data.get("height", 100.0))
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid height: must be a number"}), 400

        if height <= 0 or height > 100000:
            return jsonify({"error": "Height must be between 0.1 and 100000 meters"}), 400

        # ── Validate icon ──────────────────────────────────────
        icon_name = data.get("icon", shape)
        if icon_name not in VALID_ICONS:
            icon_name = shape

        # ── Run simulation ─────────────────────────────────────

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
                # animation keyframes: sampled every ~10 steps for bandwidth
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


if __name__ == "__main__":
    # Load environment variables
    port = int(os.environ.get("PORT", 5000))
    flask_env = os.environ.get("FLASK_ENV", "production")
    debug = flask_env == "development"

    app.run(debug=debug, host="0.0.0.0", port=port)