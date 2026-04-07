"""
main.py
───────
Entry point for the Planetary Free-Fall Physics Simulator.

Run:
    python main.py

Controls
────────
  Mass input box  – type a mass (kg) and press Enter to restart
  Shape buttons   – Circle / Square / Rocket
  Height buttons  – 50 m / 80 m / 100 m / 150 m
  Restart         – re-run with current settings
  Info panel      – toggle detailed analytics overlay
  ESC / ✕         – quit
"""

import sys
import math
import pygame

from freefall_web.physics import (
    PLANETARY_GRAVITY,
    SHAPE_PARAMS,
    SHAPES,
    simulate_fall,
    impact_description,
)
from ui import (
    PLANET_COLORS,
    SURFACE, PRIMARY, ACCENT, LGRAY, DGRAY, TXTSEC,
    Button, InputBox,
    draw_object, draw_object_label,
    draw_info_panel, draw_background,
    _fonts, )

# ── Window ─────────────────────────────────────────────────────────────────────
WIDTH,  HEIGHT        = 1400, 820
VERTICAL_MARGIN       = 110          # px from top/bottom edges to the drop zone
TRAIL_LEN             = 14
FPS                   = 60
DT                    = 1 / FPS

N_PLANETS             = len(PLANETARY_GRAVITY)
PLANET_SPACING        = (WIDTH - 160) // N_PLANETS   # horizontal gap per column


# ── Simulation state helpers ───────────────────────────────────────────────────

def _make_object(index: int, planet: str, gravity: float,
                 mass_kg: float, shape: str, drop_height: float) -> dict:
    result        = simulate_fall(planet, mass_kg, shape, drop_height)
    scale         = (HEIGHT - 2 * VERTICAL_MARGIN) / drop_height
    return {
        # identity
        "planet":          planet,
        "shape":           shape,
        "mass":            mass_kg,
        # position / motion
        "x":               90 + index * PLANET_SPACING,
        "y":               float(VERTICAL_MARGIN),
        "v":               0.0,
        "g":               gravity,
        # timing
        "falling":         True,
        "fall_time":       0.0,
        "true_fall_time":  result["fall_time"],
        "final_velocity":  result["final_velocity"],
        # display
        "scale":           scale,
        "trail":           [],
        # analytics shown in panel
        "ke":              0.0,
        "momentum":        0.0,
        "ke_impact":       result["ke_impact"],
        "momentum_impact": result["momentum"],
        "v_terminal":      result["v_terminal"],
        "impact_desc":     impact_description(result["ke_impact"]),
    }


def reset_simulation(mass_kg: float, shape: str, drop_height: float) -> list[dict]:
    return [
        _make_object(i, planet, gravity, mass_kg, shape, drop_height)
        for i, (planet, gravity) in enumerate(PLANETARY_GRAVITY.items())
    ]


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🪐 Planetary Free-Fall Physics Simulator")
    clock  = pygame.time.Clock()
    fonts  = _fonts()

    # ── Simulation defaults ────────────────────────────────────────────────────
    mass_kg     = 1.0
    shape       = "circle"
    drop_height = 100.0

    objects     = reset_simulation(mass_kg, shape, drop_height)
    show_info   = False
    paused      = False

    # ── UI controls ───────────────────────────────────────────────────────────
    CTRL_Y   = HEIGHT - 78      # bottom control strip top edge
    CTRL_Y2  = HEIGHT - 38      # second row

    # Mass input
    mass_box = InputBox(14, CTRL_Y - 52, 140, 34, default="1.0", label="Mass (kg)")

    # Shape buttons
    shape_buttons = {
        s: Button(
            14 + i * 108, CTRL_Y, 100, 34,
            SHAPE_PARAMS[s]["label"],
            color=SURFACE,
            active=(s == shape),
            )
        for i, s in enumerate(SHAPES)
    }

    # Height buttons
    heights     = [50, 80, 100, 150]
    height_btns = {
        h: Button(
            14 + i * 90, CTRL_Y2, 82, 30,
            f"{h} m",
            color=DGRAY,
            active=(h == int(drop_height)),
            )
        for i, h in enumerate(heights)
    }

    # Top-right controls
    restart_btn = Button(WIDTH - 170, 14, 150, 44, "↺  Restart", PRIMARY)
    info_btn    = Button(WIDTH - 340, 14, 160, 44, "📊 Info",    SURFACE)
    pause_btn   = Button(WIDTH - 510, 14, 160, 44, "⏸  Pause",  SURFACE)

    running = True
    while running:
        dt_ms = clock.tick(FPS)

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            # Mass input
            if mass_box.handle_event(event):
                mass_kg = mass_box.value
                objects = reset_simulation(mass_kg, shape, drop_height)

            # Shape selection
            for s, btn in shape_buttons.items():
                if btn.handle_event(event):
                    shape = s
                    for b in shape_buttons.values():
                        b.active = False
                    btn.active = True
                    objects = reset_simulation(mass_kg, shape, drop_height)

            # Height selection
            for h, btn in height_btns.items():
                if btn.handle_event(event):
                    drop_height = float(h)
                    for b in height_btns.values():
                        b.active = False
                    btn.active = True
                    objects = reset_simulation(mass_kg, shape, drop_height)

            # Top controls
            if restart_btn.handle_event(event):
                objects = reset_simulation(mass_kg, shape, drop_height)
                paused  = False
            if info_btn.handle_event(event):
                show_info = not show_info
                info_btn.active = show_info
            if pause_btn.handle_event(event):
                paused = not paused
                pause_btn.active = paused
                pause_btn.text   = "▶  Resume" if paused else "⏸  Pause"

        # ── Physics update ────────────────────────────────────────────────────
        if not paused:
            for obj in objects:
                if not obj["falling"]:
                    continue

                obj["fall_time"] += DT
                # simple Euler with capped velocity (matches simulate_fall logic)
                obj["v"] = min(obj["v"] + obj["g"] * DT, obj["final_velocity"])
                obj["y"] += obj["v"] * DT * obj["scale"]

                # trail
                obj["trail"].append((obj["x"], obj["y"]))
                if len(obj["trail"]) > TRAIL_LEN:
                    obj["trail"].pop(0)

                # running KE / momentum
                obj["ke"]       = 0.5 * obj["mass"] * obj["v"] ** 2
                obj["momentum"] = obj["mass"] * obj["v"]

                # landed?
                ground_y = HEIGHT - VERTICAL_MARGIN
                if obj["y"] >= ground_y or obj["fall_time"] >= obj["true_fall_time"]:
                    obj["falling"]   = False
                    obj["y"]         = float(ground_y)
                    obj["fall_time"] = obj["true_fall_time"]
                    obj["v"]         = obj["final_velocity"]
                    obj["ke"]        = obj["ke_impact"]
                    obj["momentum"]  = obj["momentum_impact"]

        # ── Draw ──────────────────────────────────────────────────────────────
        draw_background(
            screen,
            f"🪐 Planetary Free-Fall  |  {mass_kg} kg  {SHAPE_PARAMS[shape]['label']}  "
            f"|  drop height {drop_height:.0f} m",
            WIDTH, HEIGHT, fonts,
        )

        # Ground line
        ground_y = HEIGHT - VERTICAL_MARGIN
        pygame.draw.line(screen, LGRAY, (0, ground_y), (WIDTH, ground_y), 2)
        gl = fonts["small"].render("Ground  (0 m)", True, LGRAY)
        screen.blit(gl, (WIDTH - gl.get_width() - 10, ground_y + 4))

        # Drop-height marker
        dh_y = VERTICAL_MARGIN
        pygame.draw.line(screen, (*ACCENT, 120), (0, dh_y), (WIDTH, dh_y), 1)
        dhl = fonts["tiny"].render(f"← {drop_height:.0f} m", True, ACCENT)
        screen.blit(dhl, (4, dh_y + 2))

        # Objects
        for obj in objects:
            draw_object(screen, obj, fonts)
            draw_object_label(screen, obj, fonts)

        # Planet name + impact info at column bottom
        for obj in objects:
            cx   = int(obj["x"])
            cy   = ground_y + 8
            pn   = fonts["tiny"].render(obj["planet"], True, PLANET_COLORS[obj["planet"]])
            screen.blit(pn, (cx - pn.get_width() // 2, cy))
            if not obj["falling"]:
                vt  = obj["v_terminal"]
                vts = f"vt={vt:.0f}" if vt != float("inf") else "vt=∞"
                imp = fonts["tiny"].render(obj["impact_desc"], True, ACCENT)
                vtl = fonts["tiny"].render(vts, True, TXTSEC)
                screen.blit(imp, (cx - imp.get_width() // 2, cy + 14))
                screen.blit(vtl, (cx - vtl.get_width() // 2, cy + 28))

        # Pause banner
        if paused:
            banner = fonts["large"].render("⏸  PAUSED", True, ACCENT)
            br     = banner.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
            bg     = br.inflate(40, 20)
            pygame.draw.rect(screen, (*SURFACE, 200), bg, border_radius=12)
            screen.blit(banner, br)

        # Controls strip
        ctrl_bg = pygame.Rect(0, CTRL_Y - 62, WIDTH, 78 + 44)
        cs      = pygame.Surface(ctrl_bg.size, pygame.SRCALPHA)
        cs.fill((*SURFACE, 200))
        screen.blit(cs, ctrl_bg)
        pygame.draw.line(screen, PRIMARY, (0, CTRL_Y - 62), (WIDTH, CTRL_Y - 62), 1)

        mass_box.draw(screen, fonts, dt_ms)

        shape_label = fonts["small"].render("Shape:", True, LGRAY)
        screen.blit(shape_label, (14, CTRL_Y - 18))
        for btn in shape_buttons.values():
            btn.draw(screen, fonts)

        height_label = fonts["small"].render("Height:", True, LGRAY)
        screen.blit(height_label, (14, CTRL_Y2 - 18))
        for btn in height_btns.values():
            btn.draw(screen, fonts)

        restart_btn.draw(screen, fonts)
        info_btn.draw(screen, fonts)
        pause_btn.draw(screen, fonts)

        # Info panel overlay
        if show_info:
            draw_info_panel(screen, objects, drop_height, fonts, WIDTH, HEIGHT)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()