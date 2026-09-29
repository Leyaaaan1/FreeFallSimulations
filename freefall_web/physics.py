"""
physics.py
──────────
Pure-Python physics engine for the free-fall simulator.

Model: ideal free fall under constant surface gravity.
    - No air resistance (no atmosphere modeled)
    - Constant gravity (no change with altitude)
    - Object starts at rest

Because the motion is exact, closed-form equations are used:
    y(t)      = h - 1/2 g t^2
    v(t)      = g t
    fall time = sqrt(2h / g)
    impact v  = sqrt(2 g h)

Mass does not affect fall time or impact velocity in this model
(it only affects kinetic energy and momentum).
"""

import math

# ── Planetary data ─────────────────────────────────────────────────────────────
# Surface gravity in m/s²
PLANETARY_GRAVITY: dict[str, float] = {
    "Mercury": 3.70,
    "Venus":   8.87,
    "Earth":   9.81,
    "Mars":    3.71,
    "Jupiter": 24.79,
    "Saturn":  10.44,
    "Uranus":  8.69,
    "Neptune": 11.15,
    "Pluto":   0.62,
}

# Minimum spacing between returned data points (seconds) and the
# maximum number of points per planet (keeps responses small for tall drops).
MIN_STEP = 0.05
MAX_POINTS = 1000


def simulate_fall(planet: str, mass_kg: float, height: float = 100.0) -> dict:
    """
    Compute an ideal free fall (no air resistance) on the given planet.

    Parameters
    ----------
    planet   : one of PLANETARY_GRAVITY keys
    mass_kg  : object mass in kilograms
    height   : drop height in metres

    Returns
    -------
    dict with keys:
        fall_time       float – seconds to reach the ground
        final_velocity  float – m/s at impact
        ke_impact       float – kinetic energy at impact (J)
        momentum        float – linear momentum at impact (kg·m/s)
        t_series        list  – time stamps for animation / plotting
        y_series        list  – height above ground at each stamp
        v_series        list  – velocity at each stamp
    """
    g = PLANETARY_GRAVITY[planet]

    fall_time = math.sqrt(2.0 * height / g)
    v_impact = g * fall_time

    step = max(MIN_STEP, fall_time / MAX_POINTS)

    t_list: list[float] = []
    y_list: list[float] = []
    v_list: list[float] = []

    t = 0.0
    while t < fall_time:
        t_list.append(round(t, 6))
        y_list.append(round(height - 0.5 * g * t * t, 6))
        v_list.append(round(g * t, 6))
        t += step

    # Final point lands exactly at impact
    t_list.append(round(fall_time, 6))
    y_list.append(0.0)
    v_list.append(round(v_impact, 6))

    return {
        "fall_time":      fall_time,
        "final_velocity": v_impact,
        "ke_impact":      0.5 * mass_kg * v_impact ** 2,
        "momentum":       mass_kg * v_impact,
        "t_series":       t_list,
        "y_series":       y_list,
        "v_series":       v_list,
    }


def run_all_planets(mass_kg: float, height: float = 100.0) -> dict[str, dict]:
    """Run simulate_fall for every planet and return {planet: result}."""
    return {p: simulate_fall(p, mass_kg, height) for p in PLANETARY_GRAVITY}


def impact_description(ke_joules: float) -> str:
    """Return a human-readable impact category based on kinetic energy."""
    if ke_joules < 10:
        return "Gentle tap 🪶"
    if ke_joules < 500:
        return "Solid thud 💥"
    if ke_joules < 5_000:
        return "Heavy impact 🔨"
    if ke_joules < 50_000:
        return "Explosive hit 💣"
    return "Catastrophic 🌋"