# 🪐 Planetary Free-Fall Simulator

A web-based physics simulator that models free-fall motion across all planets in our solar system, accounting for gravity, atmospheric drag, and object shape.

## How It Works

**Input Parameters:**
- **Object Mass** (kg): 0.001 to 10,000 kg
- **Drop Height** (m): 0.1 to 100,000 m
- **Shape/Drag Profile**: Circle (Cd 0.47), Square (Cd 1.05), Rocket (Cd 0.075)

**Real-Time Animation:**
Objects fall simultaneously across all 9 planets, with live velocity readouts and impact detection.

**Real-Time Results Table:**
- Fall time
- Impact velocity
- Kinetic energy at impact
- Terminal velocity
- Momentum at impact
- Impact description (Gentle tap → Catastrophic)

## Physics Calculations

The simulator uses **numerical integration** with the equation of motion:

Where:
- **m** = object mass (kg)
- **g** = planetary surface gravity (m/s²)
- **ρ** = atmospheric density (kg/m³)
- **Cd** = drag coefficient
- **A** = reference area = A_k × mass^(2/3)
- **v** = velocity (m/s)

**Terminal Velocity** (when acceleration = 0):


Integration step: **0.005 seconds** (200 iterations/second)

## Real Planetary Data

| Planet | Gravity (m/s²) | Atmosphere (kg/m³) | Notes |
|--------|----------------|--------------------|-------|
| **Mercury** | 3.70 | 0.000 | No atmosphere → infinite terminal velocity |
| **Venus** | 8.87 | 65.00 | Super-dense CO₂ atmosphere |
| **Earth** | 9.81 | 1.225 | Reference standard |
| **Mars** | 3.71 | 0.020 | Thin atmosphere |
| **Jupiter** | 24.79 | 1.330 | Extreme gravity |
| **Saturn** | 10.44 | 0.190 | Low density atmosphere |
| **Uranus** | 8.69 | 0.420 | Ice giant |
| **Neptune** | 11.15 | 0.450 | Wind giant |
| **Pluto** | 0.62 | 0.000 | Dwarf planet, no atmosphere |

## Features

✅ Real physics integration (drag, gravity, atmosphere)  
✅ 9 planets with accurate gravitational & atmospheric data  
✅ 3 shape profiles (circle, square, rocket)  
✅ 50+ searchable FontAwesome icons  
✅ Sortable results (fall time, velocity, KE, gravity)  
✅ Pause & restart animations  
✅ Dark theme UI with color-coded planets

## Tech Stack

- **Backend**: Flask (Python) + physics engine
- **Frontend**: Vanilla JavaScript + CSS Grid
- **Physics**: Pure Python numerical integration
- **Hosting**: Vercel (serverless)

## Try It

**Live:** [Deploy URL]  
**Local:**
```bash
cd freefall_web
pip install -r requirements.txt
python App.py