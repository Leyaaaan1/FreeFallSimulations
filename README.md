# Planetary Free-Fall Simulator

**Python · Flask · Vanilla JavaScript**

A web-based physics simulator that drops the same object on nine planetary bodies at once, using each world's real surface gravity, and shows how differently it falls.

**Live demo:** https://free-fall-ten.vercel.app/

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Physics Model](#physics-model)
- [Assumptions and Limitations](#assumptions-and-limitations)
- [Planetary Data](#planetary-data)
- [Example Results](#example-results)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)

## Overview

The simulator models **ideal free fall**: an object released from rest under constant surface gravity, with no air resistance. Atmospheric density changes with altitude, so a single constant value is not accurate for tall drops. Ignoring air keeps every result exact and easy to verify by hand.

Results are shown through a live animation and a sortable results table.

## Features

- Nine planetary bodies: Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto
- Exact closed-form physics, with no numerical error
- Live animation with real-time velocity readouts and impact detection
- Sortable results (fall time, impact velocity, kinetic energy, gravity)
- Impact severity classification, from "Gentle tap" to "Catastrophic"
- Searchable icon picker (FontAwesome) to customize the falling object
- Pause and restart controls
- Dark theme UI with color-coded planets

## How It Works

### Input Parameters

| Parameter   | Range             | Notes                                                                      |
| ----------- | ----------------- | -------------------------------------------------------------------------- |
| Object mass | 0.001 – 10,000 kg | User-defined                                                               |
| Drop height | 0.1 – 100,000 m   | The UI offers quick presets (50 m – 300 m); the API accepts the full range |
| Object icon | Any listed icon   | Cosmetic only, does not affect physics                                     |

### Outputs (per planet)

- Fall time
- Impact velocity
- Kinetic energy at impact
- Momentum at impact
- Impact severity classification

## Physics Model

The object starts at rest and accelerates under constant gravity `g`:

```
y(t)      = h − ½ g t²
v(t)      = g t
fall time = √(2h / g)
impact v  = √(2 g h)
KE        = ½ m v²  (= m g h)
p         = m v
```

| Symbol | Description               | Unit |
| ------ | ------------------------- | ---- |
| h      | Drop height               | m    |
| g      | Planetary surface gravity | m/s² |
| m      | Object mass               | kg   |
| t      | Time                      | s    |
| v      | Velocity                  | m/s  |

**Mass does not affect fall time or impact velocity.** It only changes kinetic energy and momentum. This is the same effect seen in the Apollo 15 hammer-and-feather demonstration on the Moon.

## Assumptions and Limitations

- **No air resistance.** No atmosphere, drag, or terminal velocity is modeled.
- **Constant gravity.** `g` does not change with altitude. This is a good approximation for drops of a few kilometers, and less accurate for very tall drops.
- **Starts from rest.** Initial velocity is zero.
- **Vertical motion only.** No wind, rotation, or horizontal velocity.
- **Gas and ice giants.** Jupiter, Saturn, Uranus and Neptune have no solid surface, so gravity is taken at the reference level (about 1 bar pressure) and "impact" means reaching that level.
- **Educational tool.** Not intended for orbital mechanics or engineering calculations.

## Planetary Data

| Planet  | Surface gravity (m/s²) |
| ------- | ---------------------- |
| Mercury | 3.70                   |
| Venus   | 8.87                   |
| Earth   | 9.81                   |
| Mars    | 3.71                   |
| Jupiter | 24.79                  |
| Saturn  | 10.44                  |
| Uranus  | 8.69                   |
| Neptune | 11.15                  |
| Pluto   | 0.62                   |

Pluto is classified as a dwarf planet and is included as a ninth body.

## Example Results

Drop height 100 m, any mass:

| Planet  | Fall time | Impact velocity |
| ------- | --------- | --------------- |
| Mercury | 7.35 s    | 27.2 m/s        |
| Venus   | 4.75 s    | 42.1 m/s        |
| Earth   | 4.52 s    | 44.3 m/s        |
| Mars    | 7.34 s    | 27.2 m/s        |
| Jupiter | 2.84 s    | 70.4 m/s        |
| Saturn  | 4.38 s    | 45.7 m/s        |
| Uranus  | 4.80 s    | 41.7 m/s        |
| Neptune | 4.24 s    | 47.2 m/s        |
| Pluto   | 17.96 s   | 11.1 m/s        |

## Tech Stack

| Layer    | Technology                         |
| -------- | ---------------------------------- |
| Backend  | Flask (Python)                     |
| Physics  | Pure Python, closed-form equations |
| Frontend | Vanilla JavaScript + CSS Grid      |
| Icons    | FontAwesome 6 Free                 |
| Hosting  | Vercel (serverless)                |

## Project Structure

```
FreeFallSimulations/
├── index.py                 # Flask app and API routes
├── freefall_web/
│   └── physics.py           # Physics engine
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/sim.js
└── requirements.txt
```

## Getting Started

### Prerequisites

- Python 3.9 or later
- pip

### Installation

```bash
git clone https://github.com/Leyaaaan1/FreeFallSimulations.git
cd FreeFallSimulations
pip install -r requirements.txt
```

### Run

```bash
python index.py
```

Then open http://localhost:5000 in your browser.

## Author

Created by **Lean Paninsoro** · [GitHub](https://github.com/Leyaaaan1)
