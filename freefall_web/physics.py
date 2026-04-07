"""
physics.py
──────────
Pure-Python physics engine for the free-fall simulator.
No pygame dependency — safe to import anywhere (tests, notebooks, etc.)
"""

import math

# ── Planetary data ─────────────────────────────────────────────────────────────
PLANETARY_GRAVITY: dict[str, float] = {  # surface gravity  m/s²
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

# Surface atmospheric density kg/m³  (approximate)
AIR_DENSITY: dict[str, float] = {
    "Mercury": 0.000,
    "Venus":   65.00,   # super-dense CO₂ atmosphere
    "Earth":   1.225,
    "Mars":    0.020,
    "Jupiter": 1.330,
    "Saturn":  0.190,
    "Uranus":  0.420,
    "Neptune": 0.450,
    "Pluto":   0.000,
}

# ── Shape aerodynamic properties ───────────────────────────────────────────────
# Cd  = drag coefficient
# A_k = area scaling constant  →  A_ref = A_k * mass^(2/3)
#        (heavier/bigger objects have a proportionally larger cross-section)
SHAPE_PARAMS: dict[str, dict] = {
    "circle": {"Cd": 0.47,  "A_k": 0.010, "label": "⬤  Circle"},
    "square": {"Cd": 1.05,  "A_k": 0.012, "label": "■  Square"},
    "rocket": {"Cd": 0.075, "A_k": 0.005, "label": "🚀 Rocket"},
}

SHAPES = list(SHAPE_PARAMS.keys())


# ── Physics helpers ────────────────────────────────────────────────────────────

def reference_area(mass_kg: float, shape: str) -> float:
    """Cross-sectional reference area in m², scaled by mass."""
    return SHAPE_PARAMS[shape]["A_k"] * (mass_kg ** (2 / 3))


def terminal_velocity(mass_kg: float, shape: str, planet: str) -> float:
    """
    Terminal velocity in m/s.
    Returns math.inf when there is no atmosphere (drag-free).

        v_t = sqrt( 2 m g / (Cd ρ A) )
    """
    rho = AIR_DENSITY[planet]
    if rho == 0.0:
        return math.inf
    g  = PLANETARY_GRAVITY[planet]
    Cd = SHAPE_PARAMS[shape]["Cd"]
    A  = reference_area(mass_kg, shape)
    return math.sqrt(2 * mass_kg * g / (Cd * rho * A))


def simulate_fall(
        planet:   str,
        mass_kg:  float,
        shape:    str,
        height:   float = 100.0,
        dt:       float = 0.005,
) -> dict:
    """
    Numerically integrate the equation of motion with aerodynamic drag.

        F_net = m·g  −  ½·ρ·Cd·A·v²      (drag opposes motion)
        a     = F_net / m

    Parameters
    ----------
    planet   : one of PLANETARY_GRAVITY keys
    mass_kg  : object mass in kilograms
    shape    : one of SHAPE_PARAMS keys
    height   : drop height in metres
    dt       : integration time step in seconds

    Returns
    -------
    dict with keys:
        fall_time       float  – seconds to reach ground
        final_velocity  float  – m/s at impact
        ke_impact       float  – kinetic energy at impact  (J)
        momentum        float  – linear momentum at impact (kg·m/s)
        v_terminal      float  – terminal velocity (m/s or inf)
        t_series        list   – time stamps for animation / plotting
        y_series        list   – height above ground at each stamp
        v_series        list   – velocity at each stamp
    """
    g   = PLANETARY_GRAVITY[planet]
    rho = AIR_DENSITY[planet]
    Cd  = SHAPE_PARAMS[shape]["Cd"]
    A   = reference_area(mass_kg, shape)
    v_t = terminal_velocity(mass_kg, shape, planet)

    y, v, t = float(height), 0.0, 0.0
    t_list: list[float] = [t]
    y_list: list[float] = [y]
    v_list: list[float] = [v]

    while y > 0.0:
        drag_force = 0.5 * rho * Cd * A * v * v if rho > 0 else 0.0
        a = g - drag_force / mass_kg        # net downward acceleration
        a = max(a, 0.0)                     # drag can never reverse motion here

        v += a * dt
        y -= v * dt
        t += dt

        y = max(y, 0.0)
        t_list.append(round(t,  6))
        y_list.append(round(y,  6))
        v_list.append(round(v,  6))

        if y == 0.0:
            break

    v_impact = v_list[-1]
    return {
        "fall_time":      t,
        "final_velocity": v_impact,
        "ke_impact":      0.5 * mass_kg * v_impact ** 2,
        "momentum":       mass_kg * v_impact,
        "v_terminal":     v_t,
        "t_series":       t_list,
        "y_series":       y_list,
        "v_series":       v_list,
    }


def run_all_planets(mass_kg: float, shape: str, height: float = 100.0) -> dict[str, dict]:
    """Run simulate_fall for every planet and return {planet: result}."""
    return {p: simulate_fall(p, mass_kg, shape, height) for p in PLANETARY_GRAVITY}


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