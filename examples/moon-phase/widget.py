"""Moon Phase: a desktop widget showing the Moon's phase tonight (docs/extensions.md in
bromigOS). Nothing is fetched: the phase comes from the date, measured from a known new
moon (6 January 2000, 18:14 UTC) in synodic months of 29.53 days. It's within a few
hours of the published times, which is plenty for a picture of tonight's Moon.

Render it without a window:
    bromigos-widgets render moon_phase OUT.png
"""
import math
import time

import draw as D
from panels import Panel

LAYOUT = {"width": 380, "height": 172}
SYNODIC = 29.530588853                      # days from one new moon to the next
EPOCH = 947182440.0                         # a new moon: 2000-01-06 18:14 UTC (Unix time)
NAMES = ["NEW MOON", "WAXING CRESCENT", "FIRST QUARTER", "WAXING GIBBOUS",
         "FULL MOON", "WANING GIBBOUS", "LAST QUARTER", "WANING CRESCENT"]


def phase(t=None):
    """(age in days, fraction of the cycle 0..1, lit fraction 0..1, name)."""
    age = ((t or time.time()) - EPOCH) / 86400 % SYNODIC
    f = age / SYNODIC
    lit = (1 - math.cos(2 * math.pi * f)) / 2
    return age, f, lit, NAMES[int(f * 8 + 0.5) % 8]


class MoonPhasePanel(Panel):
    name, title = "moon_phase", "MOON"
    width, height = 380, 172
    interval = 60.0
    # what the widget gallery shows (bromigOS's docs/plugins.md, "What the gallery shows")
    description = "The Moon's phase tonight, and the days to the next full and new moon"
    category, reads = "fun", "the date (nothing is fetched)"
    min_size, max_size = (320, 150), (720, 400)

    def __init__(self, cfg=None):
        super().__init__(cfg)
        self.now = phase()

    def tick(self):
        self.now = phase()

    def draw(self, cr, w, h):
        age, f, lit, name = self.now
        top = D.frame(cr, w, h, self.title, f"DAY {age:4.1f} OF {SYNODIC:.1f}")
        self.region(0, 0, w, 34, "Moon Phase: worked out from the date, nothing fetched (a starter-style widget "
                                 "from the bromigOS catalog)")
        r = min((h - top - 16) / 2, 60)
        cx, cy = 16 + r, top + (h - top - 16) / 2
        self._moon(cr, cx, cy, r, f)
        self.region(cx - r, cy - r, 2 * r, 2 * r, f"The Moon tonight: {lit * 100:.0f}% lit, {name.lower()}")
        x = cx + r + 24
        D.label(cr, x, top + 4, name, "phosphor", 13)
        D.seg7(cr, x, top + 26, 34, f"{lit * 100:3.0f}", D.level(0, 1, 2))
        D.text(cr, x + 84, top + 44, "% LIT", 12, "dim", "semibold")
        to_full = (0.5 - f) % 1 * SYNODIC
        to_new = (1 - f) % 1 * SYNODIC
        D.label(cr, x, top + 76, f"FULL IN {to_full:4.1f} D", "static")
        D.label(cr, x, top + 94, f"NEW IN  {to_new:4.1f} D", "static")
        self.region(x, top + 70, w - x - 16, 40, f"The next full moon in {to_full:.1f} days, "
                                                 f"the next new moon in {to_new:.1f} days")

    @staticmethod
    def _moon(cr, cx, cy, r, f):
        """The disc: dark, then the lit part, between the lit limb and the terminator (a
        half ellipse whose width follows the phase)."""
        D.src(cr, "guard", 1.0)
        cr.arc(cx, cy, r, 0, 2 * math.pi)
        cr.fill()
        side = 1 if f < 0.5 else -1                      # waxing: lit on the right
        k = math.cos(2 * math.pi * f)                    # 1 at new, 0 at a quarter, -1 at full
        steps = 48
        for i in range(steps + 1):                       # the limb, top to bottom
            t = -math.pi / 2 + math.pi * i / steps
            (cr.move_to if i == 0 else cr.line_to)(cx + side * r * math.cos(t), cy + r * math.sin(t))
        for i in range(steps + 1):                       # the terminator, bottom to top
            t = math.pi / 2 - math.pi * i / steps
            cr.line_to(cx + side * k * r * math.cos(t), cy + r * math.sin(t))
        cr.close_path()
        D.src(cr, "soft", 0.95)
        cr.fill()
        D.src(cr, "dim", 0.8)
        cr.set_line_width(1)
        cr.arc(cx, cy, r, 0, 2 * math.pi)
        cr.stroke()

PANEL = MoonPhasePanel
