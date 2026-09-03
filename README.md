# Planetary Free-Fall Simulator

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-backend-black)

A web-based physics simulator that models free-fall motion across all nine planetary bodies in our solar system, accounting for gravity, atmospheric drag, and object shape.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Physics Model](#physics-model)
- [Planetary Data](#planetary-data)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [License](#license)

## Overview

The simulator drops a user-defined object simultaneously across nine planetary environments, integrating the equations of motion in real time to capture the interplay between gravity, atmospheric density, and drag. Results are visualized through a live animation and a sortable data table.

## Features

- Real physics integration accounting for drag, gravity, and atmosphere
- Nine planets with accurate gravitational and atmospheric data
- Three configurable shape/drag profiles: circle, square, rocket
- 50+ searchable FontAwesome icons for object customization
- Sortable results table (fall time, velocity, kinetic energy, gravity)
- Pause and restart controls for animations
- Dark theme UI with color-coded planets

## How It Works

### Input Parameters

| Parameter | Range | Notes |
|---|---|---|
| Object Mass | 0.001 – 10,000 kg | User-defined |
| Drop Height | 0.1 – 100,000 m | User-defined |
| Shape / Drag Profile | Circle (Cd 0.47), Square (Cd 1.05), Rocket (Cd 0.075) | Determines drag coefficient |

### Real-Time Animation

Objects fall simultaneously across all nine planets, with live velocity readouts and impact detection.

### Real-Time Results Table

- Fall time
- Impact velocity
- Kinetic energy at impact
- Terminal velocity
- Momentum at impact
- Impact severity classification (Gentle tap → Catastrophic)

## Physics Model

The simulator numerically integrates the equation of motion for a body falling under gravity with quadratic atmospheric drag:

```
m * (dv/dt) = m*g - 0.5 * ρ * Cd * A * v²
```

Where:

| Symbol | Description | Unit |
|---|---|---|
| `m` | Object mass | kg |
| `g` | Planetary surface gravity | m/s² |
| `ρ` | Atmospheric density | kg/m³ |
| `Cd` | Drag coefficient | dimensionless |
| `A` | Reference area, `A = A_k * m^(2/3)` | m² |
| `v` | Velocity | m/s |

**Terminal velocity** (solved at `dv/dt = 0`):

```
v_terminal = sqrt( (2 * m * g) / (ρ * Cd * A) )
```

**Integration step:** 0.005 s (200 iterations/second)

## Planetary Data

| Planet | Gravity (m/s²) | Atmosphere (kg/m³) | Notes |
|---|---|---|---|
| Mercury | 3.70 | 0.000 | No atmosphere → infinite terminal velocity |
| Venus | 8.87 | 65.00 | Super-dense CO₂ atmosphere |
| Earth | 9.81 | 1.225 | Reference standard |
| Mars | 3.71 | 0.020 | Thin atmosphere |
| Jupiter | 24.79 | 1.330 | Extreme gravity |
| Saturn | 10.44 | 0.190 | Low-density atmosphere |
| Uranus | 8.69 | 0.420 | Ice giant |
| Neptune | 11.15 | 0.450 | Wind giant |
| Pluto | 0.62 | 0.000 | Dwarf planet, no atmosphere |

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Flask (Python) + custom physics engine |
| Frontend | Vanilla JavaScript + CSS Grid |
| Physics | Pure Python numerical integration |
| Hosting | Vercel (serverless) |

## Getting Started

### Prerequisites

- Python 3.8 or later
- pip

### Installation

```bash
git clone <repository-url>
cd freefall_web
pip install -r requirements.txt
```

## Usage

```bash
python App.py
```

Then open your browser to the address printed in the terminal (typically `http://localhost:5000`).

**Live demo:** [Deploy URL]

## License

License to be determined. Add a `LICENSE` file to specify usage terms before public release.
