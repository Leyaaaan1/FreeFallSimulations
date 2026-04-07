"""
ui.py
─────
All pygame drawing helpers, color constants, Button class, and object renderers.
Keeps main.py clean of low-level draw calls.
"""

import pygame
import math

# ── Color palette ──────────────────────────────────────────────────────────────
BG        = (12,  12,  30)
SURFACE   = (22,  22,  45)
PRIMARY   = (64,  156, 255)
SECONDARY = (255, 107, 107)
ACCENT    = (255, 193,  7)
SUCCESS   = (76,  175,  80)
WHITE     = (255, 255, 255)
LGRAY     = (200, 200, 200)
DGRAY     = (100, 100, 100)
GOLD      = (255, 215,  0)
TXTSEC    = (160, 160, 180)

PLANET_COLORS: dict[str, tuple] = {
    "Mercury": (169, 169, 169),
    "Venus":   (255, 198,  73),
    "Earth":   (100, 149, 237),
    "Mars":    (205,  92,  92),
    "Jupiter": (255, 140,   0),
    "Saturn":  (255, 215,   0),
    "Uranus":  ( 64, 224, 208),
    "Neptune": ( 30, 144, 255),
    "Pluto":   (139,  69,  19),
}


def _fonts():
    """Lazily initialise fonts (pygame must already be init'd)."""
    return {
        "title":  pygame.font.SysFont("Arial", 34, bold=True),
        "large":  pygame.font.SysFont("Arial", 26, bold=True),
        "medium": pygame.font.SysFont("Arial", 19),
        "small":  pygame.font.SysFont("Arial", 15),
        "tiny":   pygame.font.SysFont("Arial", 13),
    }


# ── Button ─────────────────────────────────────────────────────────────────────
class Button:
    def __init__(
            self, x, y, w, h, text,
            color=PRIMARY, hover_color=None, text_color=WHITE,
            active=False, active_color=SUCCESS,
    ):
        self.rect         = pygame.Rect(x, y, w, h)
        self.text         = text
        self.color        = color
        self.hover_color  = hover_color or tuple(min(c + 30, 255) for c in color)
        self.text_color   = text_color
        self.active_color = active_color
        self.active       = active      # toggle / selected state
        self.hovered      = False

    def handle_event(self, event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen, fonts):
        base  = self.active_color if self.active else self.color
        color = self.hover_color  if self.hovered and not self.active else base

        # shadow
        s = self.rect.move(3, 3)
        pygame.draw.rect(screen, (0, 0, 0), s, border_radius=8)
        # body
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        # border
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)
        # label
        surf = fonts["medium"].render(self.text, True, self.text_color)
        screen.blit(surf, surf.get_rect(center=self.rect.center))


# ── Input box ──────────────────────────────────────────────────────────────────
class InputBox:
    def __init__(self, x, y, w, h, default="1.0", label=""):
        self.rect    = pygame.Rect(x, y, w, h)
        self.text    = default
        self.label   = label
        self.active  = False
        self.cursor  = True
        self._timer  = 0

    def handle_event(self, event) -> bool:
        """Returns True when Enter is pressed (value committed)."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode in "0123456789.":
                self.text += event.unicode
        return False

    @property
    def value(self) -> float:
        try:
            v = float(self.text)
            return v if v > 0 else 1.0
        except ValueError:
            return 1.0

    def draw(self, screen, fonts, dt_ms=16):
        # label
        if self.label:
            lbl = fonts["small"].render(self.label, True, LGRAY)
            screen.blit(lbl, (self.rect.x, self.rect.y - 20))

        border = PRIMARY if self.active else DGRAY
        pygame.draw.rect(screen, SURFACE, self.rect, border_radius=6)
        pygame.draw.rect(screen, border,  self.rect, 2, border_radius=6)

        # blinking cursor
        self._timer = (self._timer + dt_ms) % 1000
        display = self.text + ("|" if self.active and self._timer < 500 else "")
        surf = fonts["medium"].render(display, True, WHITE)
        screen.blit(surf, (self.rect.x + 8, self.rect.y + (self.rect.h - surf.get_height()) // 2))


# ── Object drawing ─────────────────────────────────────────────────────────────
OBJECT_SIZE = 20   # base radius / half-side in pixels

def draw_object(screen, obj: dict, fonts):
    """
    Draw a falling object (circle / square / rocket) with trail.
    `obj` is one entry from the simulation state list.
    """
    x, y   = int(obj["x"]), int(obj["y"])
    color  = PLANET_COLORS[obj["planet"]]
    shape  = obj["shape"]
    sz     = OBJECT_SIZE

    # ── trail ──────────────────────────────────────────────────────────────────
    trail = obj.get("trail", [])
    for i, (tx, ty) in enumerate(trail):
        alpha = int(200 * (i / max(len(trail), 1)) * 0.4)
        ts = pygame.Surface((sz * 2, sz * 2), pygame.SRCALPHA)
        tr, tg, tb = color
        if shape == "circle":
            pygame.draw.circle(ts, (tr, tg, tb, alpha), (sz, sz), sz // 2)
        elif shape == "square":
            pygame.draw.rect(ts, (tr, tg, tb, alpha),
                             pygame.Rect(sz // 2, sz // 2, sz, sz))
        else:  # rocket — simple triangle trail
            pts = [(sz, sz // 2), (sz // 2, sz * 3 // 2), (sz * 3 // 2, sz * 3 // 2)]
            pygame.draw.polygon(ts, (tr, tg, tb, alpha), pts)
        screen.blit(ts, (tx - sz, ty - sz))

    # ── shadow ─────────────────────────────────────────────────────────────────
    shadow = pygame.Surface((sz * 2 + 6, sz * 2 + 6), pygame.SRCALPHA)
    if shape == "circle":
        pygame.draw.circle(shadow, (0, 0, 0, 60), (sz + 3, sz + 3), sz)
    elif shape == "square":
        pygame.draw.rect(shadow, (0, 0, 0, 60), pygame.Rect(3, 3, sz * 2, sz * 2))
    else:
        pts = [(sz + 3, 3), (3, sz * 2 + 3), (sz * 2 + 3, sz * 2 + 3)]
        pygame.draw.polygon(shadow, (0, 0, 0, 60), pts)
    screen.blit(shadow, (x - sz, y - sz))

    # ── body ───────────────────────────────────────────────────────────────────
    if shape == "circle":
        pygame.draw.circle(screen, color, (x, y), sz)
        pygame.draw.circle(screen, GOLD,  (x, y), sz, 3)
        # highlight
        pygame.draw.circle(screen, WHITE, (x - sz // 3, y - sz // 3), sz // 5)

    elif shape == "square":
        rect = pygame.Rect(x - sz, y - sz, sz * 2, sz * 2)
        pygame.draw.rect(screen, color, rect, border_radius=4)
        pygame.draw.rect(screen, GOLD,  rect, 3, border_radius=4)
        # highlight
        pygame.draw.rect(screen, WHITE,
                         pygame.Rect(x - sz + 4, y - sz + 4, sz // 2, sz // 4))

    else:  # rocket  (pointing downward — direction of fall)
        body_pts = [
            (x,       y - sz),          # nose
            (x - sz // 2, y + sz // 2), # left shoulder
            (x - sz // 3, y + sz),      # left fin base
            (x,       y + sz // 2),     # center bottom
            (x + sz // 3, y + sz),      # right fin base
            (x + sz // 2, y + sz // 2), # right shoulder
        ]
        pygame.draw.polygon(screen, color, body_pts)
        pygame.draw.polygon(screen, GOLD,  body_pts, 2)
        # exhaust flame
        flame_pts = [
            (x - sz // 4, y + sz // 2),
            (x,           y + sz + sz // 2),
            (x + sz // 4, y + sz // 2),
        ]
        pygame.draw.polygon(screen, ACCENT, flame_pts)


# ── Info label above each object ───────────────────────────────────────────────
def draw_object_label(screen, obj: dict, fonts, show_velocity=True):
    x, y  = int(obj["x"]), int(obj["y"])
    color = PLANET_COLORS[obj["planet"]]
    lines = [obj["planet"]]
    lines.append(f"T:{obj['fall_time']:.1f}s")
    if show_velocity:
        lines.append(f"V:{obj['v']:.1f}")

    label_h = 16
    label_w = 76
    label_x = x - label_w // 2
    label_y = y - OBJECT_SIZE - len(lines) * label_h - 10

    surf = pygame.Surface((label_w, len(lines) * label_h + 6), pygame.SRCALPHA)
    surf.fill((*SURFACE, 180))
    pygame.draw.rect(surf, PRIMARY, surf.get_rect(), 1, border_radius=4)
    screen.blit(surf, (label_x, label_y))

    for i, line in enumerate(lines):
        c   = color if i == 0 else WHITE
        txt = fonts["tiny"].render(line, True, c)
        screen.blit(txt, (label_x + 4, label_y + 3 + i * label_h))


# ── Info panel (slide-in analytics) ───────────────────────────────────────────
def draw_info_panel(screen, objects: list, y0: float, fonts, width: int, height: int):
    PW, PH = 620, height - 160
    panel_surf = pygame.Surface((PW, PH), pygame.SRCALPHA)
    panel_surf.fill((*SURFACE, 225))
    pygame.draw.rect(panel_surf, PRIMARY, panel_surf.get_rect(), 3, border_radius=14)

    # header
    hdr_rect = pygame.Rect(0, 0, PW, 55)
    pygame.draw.rect(panel_surf, (*PRIMARY, 110), hdr_rect, border_radius=14)
    panel_surf.blit(fonts["title"].render("📊 Simulation Analytics", True, WHITE), (20, 12))

    # drop height badge
    badge = pygame.Rect(20, 64, 220, 36)
    pygame.draw.rect(panel_surf, (*ACCENT, 160), badge, border_radius=8)
    panel_surf.blit(fonts["medium"].render(f"Drop Height: {y0:.0f} m", True, WHITE), (30, 73))

    # ── mini bar chart ─────────────────────────────────────────────────────────
    sorted_objs = sorted(objects, key=lambda o: o["true_fall_time"])
    chart_x, chart_y = 20, 112
    chart_w, chart_h = PW - 40, 160
    pygame.draw.rect(panel_surf, (*BG, 160),
                     pygame.Rect(chart_x, chart_y, chart_w, chart_h), border_radius=6)
    pygame.draw.rect(panel_surf, PRIMARY,
                     pygame.Rect(chart_x, chart_y, chart_w, chart_h), 2, border_radius=6)
    panel_surf.blit(fonts["small"].render("Fall Time Comparison (s)", True, LGRAY),
                    (chart_x + 8, chart_y + 6))

    max_t  = max(o["true_fall_time"] for o in sorted_objs) or 1
    bw     = (chart_w - 20) // len(sorted_objs) - 4
    for i, o in enumerate(sorted_objs):
        bh  = int((o["true_fall_time"] / max_t) * (chart_h - 50))
        bx  = chart_x + 10 + i * (bw + 4)
        by  = chart_y + chart_h - bh - 26
        col = PLANET_COLORS[o["planet"]]
        pygame.draw.rect(panel_surf, col, pygame.Rect(bx, by, bw, bh), border_radius=3)
        pygame.draw.rect(panel_surf, WHITE, pygame.Rect(bx, by, bw, bh), 1, border_radius=3)
        # planet abbrev
        lbl = fonts["tiny"].render(o["planet"][:3], True, WHITE)
        panel_surf.blit(lbl, (bx + bw // 2 - lbl.get_width() // 2,
                              chart_y + chart_h - 22))
        # value
        val = fonts["tiny"].render(f"{o['true_fall_time']:.1f}", True, WHITE)
        panel_surf.blit(val, (bx + bw // 2 - val.get_width() // 2, by - 14))

    # ── table ──────────────────────────────────────────────────────────────────
    ty = chart_y + chart_h + 12
    panel_surf.blit(fonts["medium"].render("Detailed Results", True, ACCENT), (30, ty))
    ty += 28

    headers   = ["Planet", "g (m/s²)", "Time (s)", "v (m/s)", "KE (J)", "Status"]
    col_x     = [20, 110, 210, 300, 390, 490]
    for i, h in enumerate(headers):
        panel_surf.blit(fonts["tiny"].render(h, True, LGRAY), (col_x[i], ty))
    ty += 18
    pygame.draw.line(panel_surf, PRIMARY, (20, ty), (PW - 20, ty), 1)
    ty += 6

    for idx, o in enumerate(sorted_objs):
        if ty > PH - 50:
            break
        if idx % 2 == 0:
            pygame.draw.rect(panel_surf, (*BG, 80),
                             pygame.Rect(15, ty - 2, PW - 30, 22), border_radius=4)
        col = PLANET_COLORS[o["planet"]]
        pygame.draw.circle(panel_surf, col, (col_x[0] + 8, ty + 9), 5)
        cells = [
            ("  " + o["planet"], WHITE),
            (f"{o['g']:.2f}", TXTSEC),
            (f"{o['fall_time']:.2f}", WHITE),
            (f"{o['v']:.1f}", TXTSEC),
            (f"{o['ke']:.0f}", TXTSEC),
            ("Done" if not o["falling"] else "↓", SUCCESS if not o["falling"] else ACCENT),
        ]
        for xi, (txt, c) in zip(col_x, cells):
            panel_surf.blit(fonts["tiny"].render(txt, True, c), (xi, ty))
        ty += 24

    # formula footer
    fy = PH - 44
    pygame.draw.rect(panel_surf, (*BG, 180), pygame.Rect(20, fy - 6, PW - 40, 42), border_radius=6)
    panel_surf.blit(fonts["tiny"].render(
        "No drag:  t = √(2h/g)   v = √(2gh)   |   With drag: numerical integration",
        True, LGRAY), (28, fy))
    panel_surf.blit(fonts["tiny"].render(
        "F_net = m·g − ½·ρ·Cd·A·v²",
        True, LGRAY), (28, fy + 18))

    screen.blit(panel_surf, (20, 80))


# ── Background ─────────────────────────────────────────────────────────────────
def draw_background(screen, title_text, width, height, fonts):
    screen.fill(BG)
    # subtle grid
    for gx in range(0, width, 60):
        pygame.draw.line(screen, (*SURFACE, 80), (gx, 0), (gx, height))
    for gy in range(0, height, 60):
        pygame.draw.line(screen, (*SURFACE, 80), (0, gy), (width, gy))
    # title
    t    = fonts["title"].render(title_text, True, WHITE)
    trec = t.get_rect(center=(width // 2, 34))
    bg   = trec.inflate(30, 16)
    pygame.draw.rect(screen, (*SURFACE, 160), bg, border_radius=10)
    screen.blit(t, trec)