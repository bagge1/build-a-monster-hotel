"""The interface's images, first drafts (UI.md "Images"; GDD §10.2, §12).

    python tools/draw_ui.py

Writes into ui/:
  hud/Icon_*.png      256 x 256, WHITE ON TRANSPARENT, glow baked into alpha:
                      the HUD tints them (ImageColor3 / UIGradient), so one file
                      covers every colour and state.
  panel/Panel*.png    512 x 512 9-slices, white, for the panels.
  Gloom.png           512 x 512, in colour: the bat concierge (GDD §17 q6).
  pass/Pass_*.png     512 x 512, in colour; what matters sits inside the circle
                      Roblox crops a pass icon to.
  product/Product_*.png 512 x 512, in colour, same rule.
  _sheet.png          every image on a dark ground, for review (not uploaded).

Everything is drawn procedurally in unit coordinates (-1..1, y up) at SS times
the final size and downsampled, so edges are antialiased. Deterministic: the
same script writes the same pixels. Text is kept to "$" and "2x", in Arial
Black, which every Windows machine has.

Art direction (GDD §12): "cozy creepy": saturated purples, teals, pumpkin
orange and moonlight blue, chunky shapes with a dark ink outline, big eyes,
cute, never scary. The palette is Ui.Colour (src/client/Ui.luau).
"""

import math
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "ui"
SS = 4
FONT_BLACK = "C:/Windows/Fonts/ariblk.ttf"
FONT_LABEL = "C:/Windows/Fonts/segoeuib.ttf"

# Ui.Colour
INK = (24, 16, 38)
PANEL = (46, 32, 70)
PANEL_LIGHT = (70, 50, 104)
LINE = (120, 95, 170)
TEXT = (246, 240, 255)
MUTED = (180, 168, 210)
PUMPKIN = (245, 145, 45)
TEAL = (60, 205, 190)
MOON = (170, 200, 255)
GOOD = (120, 220, 120)
BAD = (240, 90, 100)
GOLD = (255, 205, 80)
# Shades of those for the colour art.
PURPLE_HI = (170, 110, 240)
PURPLE = (130, 80, 205)
PURPLE_LO = (80, 45, 140)
TEAL_HI = (120, 240, 220)
TEAL_LO = (30, 140, 140)
GOLD_HI = (255, 235, 140)
GOLD_LO = (225, 145, 35)
PUMPKIN_HI = (255, 185, 85)
PUMPKIN_LO = (205, 95, 25)
MOON_HI = (235, 245, 255)
MOON_LO = (125, 155, 230)
PINK = (255, 135, 175)
PINK_LO = (220, 70, 120)
SLIME_HI = (185, 250, 120)
SLIME_LO = (70, 175, 70)
WHITE = (255, 255, 255)
SHADE = (35, 15, 70)


# ================================================================ geometry, in unit coordinates
def rot(x, y, a):
    c, s = math.cos(a), math.sin(a)
    return x * c - y * s, x * s + y * c


def ellipse_pts(x, y, rx, ry, a0=0.0, a1=2 * math.pi, n=128, tilt=0.0):
    out = []
    for i in range(n + 1):
        t = a0 + (a1 - a0) * i / n
        px, py = rot(rx * math.cos(t), ry * math.sin(t), tilt)
        out.append((x + px, y + py))
    return out


def circle_pts(x, y, r, n=128):
    return ellipse_pts(x, y, r, r, n=n)


def arc_pts(x, y, r, a0, a1, n=64):
    """Degrees, counter-clockwise from +x."""
    return ellipse_pts(x, y, r, r, math.radians(a0), math.radians(a1), n)


def rrect_pts(x0, y0, x1, y1, r=0.0, n=12):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    r = min(r, (x1 - x0) / 2, (y1 - y0) / 2)
    if r <= 0:
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    pts = []
    for cx, cy, a in ((x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270)):
        for i in range(n + 1):
            t = math.radians(a + 90 * i / n)
            pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return pts


def star_pts(x, y, ro, ri, n=5, phase=90.0):
    pts = []
    for i in range(2 * n):
        r = ro if i % 2 == 0 else ri
        a = math.radians(phase + i * 180 / n)
        pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    return pts


def heart_pts(x, y, s, n=120):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        hx = 16 * math.sin(t) ** 3
        hy = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((x + hx / 17 * s, y + (hy + 2) / 17 * s))
    return pts


def mirror(pts):
    return [(-x, y) for x, y in pts]


def moved(pts, dx, dy):
    return [(x + dx, y + dy) for x, y in pts]


# ================================================================ the canvas
class Canvas:
    """A square picture `size` px, drawn at SS x in unit coordinates."""

    def __init__(self, size):
        self.size = size
        self.S = size * SS
        self.T = []
        self.img = Image.new("RGBA", (self.S, self.S), (0, 0, 0, 0))

    @contextmanager
    def at(self, cx, cy, s=1.0, deg=0.0):
        self.T.append((cx, cy, s, math.radians(deg)))
        try:
            yield
        finally:
            self.T.pop()

    def P(self, x, y):
        for cx, cy, s, a in reversed(self.T):
            x, y = rot(x * s, y * s, a)
            x, y = x + cx, y + cy
        return ((x + 1) / 2 * self.S, (1 - y) / 2 * self.S)

    def scale(self):
        k = 1.0
        for _, _, s, _ in self.T:
            k *= s
        return k

    def L(self, u):
        """Local units to pixels."""
        return u * self.scale() / 2 * self.S

    def L0(self, u):
        """Absolute units (the whole picture) to pixels."""
        return u / 2 * self.S

    def mask(self):
        return Image.new("L", (self.S, self.S), 0)

    # -------- drawing into a mask
    def poly(self, m, pts, v=255):
        ImageDraw.Draw(m).polygon([self.P(*p) for p in pts], fill=v)
        return m

    def line(self, m, pts, w, v=255, caps=True):
        q = [self.P(*p) for p in pts]
        wp = max(1, round(self.L(w)))
        d = ImageDraw.Draw(m)
        d.line(q, fill=v, width=wp, joint="curve")
        if caps:
            r = wp / 2
            for x, y in (q[0], q[-1]):
                d.ellipse((x - r, y - r, x + r, y + r), fill=v)
        return m

    def text(self, m, s, x, y, h, v=255, font=FONT_BLACK):
        f = ImageFont.truetype(font, max(4, round(self.L(h))))
        ImageDraw.Draw(m).text(self.P(x, y), s, font=f, fill=v, anchor="mm")
        return m

    # -------- new masks
    def disk(self, x, y, r):
        return self.poly(self.mask(), circle_pts(x, y, r))

    def ell(self, x, y, rx, ry, tilt=0.0):
        return self.poly(self.mask(), ellipse_pts(x, y, rx, ry, tilt=math.radians(tilt)))

    def rect(self, x0, y0, x1, y1, r=0.0):
        return self.poly(self.mask(), rrect_pts(x0, y0, x1, y1, r))

    def shape(self, pts):
        return self.poly(self.mask(), pts)

    def stroke(self, pts, w):
        return self.line(self.mask(), pts, w)


# ================================================================ mask operations
_LUT6 = [255 if v > 6 else 0 for v in range(256)]
_LUT128 = [255 if v >= 128 else 0 for v in range(256)]


def union(*ms):
    out = ms[0]
    for m in ms[1:]:
        out = ImageChops.lighter(out, m)
    return out


def cut(m, *holes):
    for h in holes:
        m = ImageChops.subtract(m, h)
    return m


def inter(a, b):
    return ImageChops.multiply(a, b)


def dilate(m, r):
    if r < 1:
        return m
    return m.filter(ImageFilter.GaussianBlur(r / 2)).point(_LUT6)


def rounded(m, r):
    """Rounds every corner by about r px (convex and concave)."""
    return m.filter(ImageFilter.GaussianBlur(r)).point(_LUT128)


def over(m, part, gap):
    """`part` laid on `m` with a transparent gap of `gap` px round it."""
    return union(cut(m, dilate(part, gap)), part)


def scaled(m, k):
    return m.point(lambda v: int(v * k))


# ================================================================ painting colour
def _gradient(c, m, c0, c1):
    bb = m.getbbox() or (0, 0, c.S, c.S)
    y0, y1 = bb[1], max(bb[3], bb[1] + 1)
    t = np.clip((np.arange(c.S, dtype=np.float32) - y0) / (y1 - y0), 0, 1)[:, None]
    rows = np.array(c0, np.float32) * (1 - t) + np.array(c1, np.float32) * t
    arr = np.broadcast_to(rows[:, None, :], (c.S, c.S, 3))
    return Image.fromarray(np.ascontiguousarray(arr).astype(np.uint8), "RGB")


def paint(c, m, fill, alpha=1.0):
    a = m if alpha >= 1 else scaled(m, alpha)
    if isinstance(fill[0], tuple):
        layer = _gradient(c, m, fill[0], fill[1]).convert("RGBA")
    else:
        layer = Image.new("RGBA", (c.S, c.S), tuple(fill) + (0,))
    layer.putalpha(a)
    c.img.alpha_composite(layer)


def sticker(c, m, fill, ow=0.03, bevel=0.05, shade=0.30, light=0.38, ink=INK):
    """A chunky cartoon part: ink outline, gradient fill, a lit top and a shaded foot."""
    if ow:
        paint(c, dilate(m, c.L0(ow)), ink)
    paint(c, m, fill)
    if bevel:
        k = max(2, round(c.L0(bevel)))
        sh = ImageChops.subtract(m, ImageChops.offset(m, 0, -k))
        sh = inter(sh.filter(ImageFilter.GaussianBlur(k * 0.35)), m)
        paint(c, sh, SHADE, shade)
        hi = ImageChops.subtract(m, ImageChops.offset(m, k // 2, k))
        hi = inter(hi.filter(ImageFilter.GaussianBlur(k * 0.35)), m)
        paint(c, hi, WHITE, light)


def gloss(c, x, y, rx, ry, tilt=-20, alpha=0.55, clip=None):
    m = c.ell(x, y, rx, ry, tilt).filter(ImageFilter.GaussianBlur(c.L0(0.01)))
    if clip is not None:
        m = inter(m, clip)
    paint(c, m, WHITE, alpha)


def sparkle(c, x, y, r, colour=WHITE, alpha=0.9):
    m = c.shape(star_pts(x, y, r, r * 0.28, 4))
    paint(c, m, colour, alpha)


def outline_all(c, ow=0.03, ink=INK):
    """An ink outline round everything drawn so far."""
    a = c.img.getchannel("A").point(_LUT6)
    under = Image.new("RGBA", (c.S, c.S), ink + (0,))
    under.putalpha(dilate(a, c.L0(ow)))
    under.alpha_composite(c.img)
    c.img = under


def background(c, inner, outer, ring, seed=1, stars=9):
    """The round badge every pass and product sits on: it fills the square, so a
    shop that shows it square still sees no transparent corners, and its ring
    sits inside the circle a pass icon is cropped to."""
    n = c.S
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    x = xx / n * 2 - 1
    y = 1 - yy / n * 2
    r = np.sqrt(x * x + (y - 0.15) ** 2)
    t = np.clip(r / 1.15, 0, 1) ** 1.3
    arr = np.array(inner, np.float32) * (1 - t[..., None]) + np.array(outer, np.float32) * t[..., None]
    c.img = Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")
    rng = np.random.default_rng(seed)
    for _ in range(stars):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0.55, 0.86)
        sparkle(c, d * math.cos(a), d * math.sin(a), rng.uniform(0.025, 0.055), MOON_HI, rng.uniform(0.35, 0.8))
    for _ in range(30):
        a = rng.uniform(0, 2 * math.pi)
        d = rng.uniform(0.3, 0.9)
        paint(c, c.disk(d * math.cos(a), d * math.sin(a), rng.uniform(0.004, 0.009)), WHITE, rng.uniform(0.3, 0.7))
    ringm = cut(c.disk(0, 0, 0.955), c.disk(0, 0, 0.905))
    paint(c, dilate(ringm, c.L0(0.012)), INK)
    paint(c, ringm, ring)


def finish(c):
    return c.img.resize((c.size, c.size), Image.LANCZOS)


# ================================================================ HUD icons: white, glow in alpha
def hud_icon(draw, size=256, glow=0.55):
    c = Canvas(size)
    m = draw(c)
    full = m
    # The glow is only outside the silhouette: holes (eyes, cut-outs) stay clear.
    flood = full.point(_LUT128)
    ImageDraw.floodfill(flood, (0, 0), 128)
    outside = flood.point([255 if v == 128 else 0 for v in range(256)])
    a = full.resize((size, size), Image.LANCZOS)
    out = outside.resize((size, size), Image.LANCZOS)
    halo = a.filter(ImageFilter.GaussianBlur(size * 0.028))
    A = np.asarray(a, np.float32)
    H = np.clip(np.asarray(halo, np.float32) * 1.7, 0, 255) * glow * (np.asarray(out, np.float32) / 255)
    alpha = np.maximum(A, H).astype(np.uint8)
    img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    img.putalpha(Image.fromarray(alpha))
    return img


def i_build(c):
    with c.at(0.04, -0.02, 0.84, -40):
        handle = c.rect(-0.13, -0.98, 0.13, 0.32, 0.12)
        grip = c.rect(-0.17, -0.98, 0.17, -0.42, 0.14)
        head = c.rect(-0.5, 0.3, 0.36, 0.74, 0.1)
        claw = rounded(c.shape([(-0.4, 0.72), (-0.86, 0.6), (-0.86, 0.44), (-0.4, 0.32)]), c.L(0.06))
        face = c.rect(0.34, 0.22, 0.64, 0.82, 0.1)
        m = over(handle, grip, c.L(0.05))
        m = over(m, union(head, claw), c.L(0.05))
        m = over(m, face, c.L(0.05))
    return m


def i_rating(c):
    m = c.shape(star_pts(0, -0.04, 0.9, 0.42))
    m = rounded(m, c.L(0.07))
    # A shine, cut in.
    return cut(m, c.stroke(arc_pts(0, -0.04, 0.3, 105, 160, 24), 0.07))


def i_residents(c):
    roof = c.stroke([(-0.8, 0.02), (0, 0.78), (0.8, 0.02)], 0.2)
    chimney = c.rect(0.38, 0.3, 0.58, 0.74, 0.03)
    body = c.shape([(-0.56, -0.8), (0.56, -0.8), (0.56, 0.0), (0, 0.52), (-0.56, 0.0)])
    body = rounded(body, c.L(0.04))
    m = union(over(chimney, roof, c.L(0.05)), cut(body, dilate(roof, c.L(0.07))))
    door = union(c.rect(-0.17, -0.8, 0.17, -0.34), c.disk(0, -0.34, 0.17))
    heart = c.shape(heart_pts(0, 0.06, 0.2))
    return cut(m, door, heart)


def i_book(c):
    pages = c.rect(-0.58, -0.86, 0.62, -0.58, 0.06)
    cover = c.rect(-0.66, -0.66, 0.66, 0.84, 0.12)
    m = over(pages, cover, c.L(0.05))
    m = cut(m, c.rect(-0.44, -0.66, -0.37, 0.84))  # the spine
    for x in (-0.06, 0.34):  # a monster on the cover
        m = cut(m, c.disk(x, 0.28, 0.13))
        m = union(m, c.disk(x + 0.02, 0.25, 0.055))
    m = cut(m, c.stroke(arc_pts(0.14, 0.12, 0.26, 215, 325, 24), 0.08))
    m = union(m, c.shape([(0.06, -0.06), (0.14, -0.06), (0.1, -0.18)]))
    for x in (-0.12, 0.4):  # little horns
        m = cut(m, rounded(c.shape([(x - 0.08, 0.48), (x + 0.08, 0.48), (x + (0.06 if x < 0 else -0.06), 0.68)]), c.L(0.015)))
    return m


def i_moon(c):
    with c.at(-0.04, -0.02, 1, -20):
        m = cut(c.disk(0, 0, 0.8), c.disk(0.36, 0.2, 0.66))
    m = rounded(m, c.L(0.03))
    m = union(m, c.shape(star_pts(0.42, 0.42, 0.24, 0.07, 4)))
    m = union(m, c.disk(0.6, -0.12, 0.07))
    return m


def i_store(c):
    body = c.shape([(-0.66, -0.82), (0.66, -0.82), (0.56, 0.3), (-0.56, 0.3)])
    body = rounded(body, c.L(0.06))
    handle = c.stroke(arc_pts(0, 0.3, 0.3, 0, 180, 48), 0.12)
    m = over(handle, body, c.L(0.05))
    m = cut(m, c.rect(-0.6, 0.12, 0.6, 0.18))
    return cut(m, rounded(c.shape(star_pts(0, -0.33, 0.33, 0.15)), c.L(0.03)))


def i_daily(c):
    body = c.rect(-0.74, -0.8, 0.74, 0.5, 0.14)
    m = cut(body, c.rect(-0.74, 0.22, 0.74, 0.28))
    for x in (-0.36, 0.36):
        ring = c.rect(x - 0.08, 0.3, x + 0.08, 0.76, 0.08)
        m = over(m, ring, c.L(0.05))
    tick = c.stroke([(-0.32, -0.28), (-0.08, -0.52), (0.38, -0.02)], 0.16)
    return cut(m, tick)


def i_bus(c):
    wheels = union(c.rect(-0.58, -0.88, -0.3, -0.5, 0.08), c.rect(0.3, -0.88, 0.58, -0.5, 0.08))
    body = c.rect(-0.68, -0.64, 0.68, 0.8, 0.24)
    m = over(wheels, body, c.L(0.05))
    glass = c.rect(-0.52, 0.1, 0.52, 0.54, 0.1)
    m = cut(m, glass)
    m = union(m, c.rect(-0.03, 0.1, 0.03, 0.54))
    m = cut(m, c.rect(-0.26, 0.62, 0.26, 0.69, 0.03))  # the destination sign
    for x in (-0.4, 0.4):  # headlights are eyes
        m = cut(m, c.disk(x, -0.22, 0.15))
        m = union(m, c.disk(x + (0.03 if x < 0 else -0.03), -0.25, 0.07))
    m = cut(m, c.stroke(arc_pts(0, -0.2, 0.16, 215, 325, 24), 0.07))
    return m


def i_pitch(c):
    with c.at(-0.14, 0.02, 0.95, 12):
        cone = rounded(c.shape([(-0.42, -0.16), (0.32, -0.56), (0.32, 0.56), (-0.42, 0.16)]), c.L(0.04))
        back = c.rect(-0.64, -0.2, -0.4, 0.2, 0.07)
        grip = c.rect(-0.3, -0.56, -0.14, -0.1, 0.06)
        rim = c.rect(0.28, -0.62, 0.42, 0.62, 0.07)
        m = union(grip, back, cone)
        m = over(m, rim, c.L(0.04))
        for r in (0.24, 0.44):
            m = union(m, c.stroke(arc_pts(0.46, 0, r, -38, 38, 24), 0.09))
    return m


def i_boo(c):
    with c.at(0.0, 0.02, 0.92, -10):
        m = union(c.disk(0, 0.2, 0.58), c.rect(-0.58, -0.5, 0.58, 0.2))
        for x in (-0.435, -0.145, 0.145, 0.435):
            m = union(m, c.disk(x, -0.52, 0.145))
        for s in (-1, 1):
            m = union(m, c.ell(s * 0.62, 0.02, 0.2, 0.11, s * 35))
        for x in (-0.21, 0.21):
            m = cut(m, c.ell(x, 0.3, 0.1, 0.14))
        m = cut(m, c.ell(0, -0.02, 0.13, 0.17))
    return m


def i_cash(c):
    m = c.disk(0, 0, 0.82)
    m = cut(m, c.disk(0, 0, 0.68))
    m = union(m, c.disk(0, 0, 0.61))
    return cut(m, c.text(c.mask(), "$", 0, 0.02, 0.95))


def i_till(c):
    drawer = c.rect(-0.8, -0.84, 0.8, -0.5, 0.07)
    drawer = cut(drawer, c.rect(-0.22, -0.7, 0.22, -0.64, 0.03))
    pad = rounded(c.shape([(-0.7, -0.42), (0.7, -0.42), (0.54, 0.12), (-0.54, 0.12)]), c.L(0.05))
    for j, y in enumerate((-0.3, -0.1)):
        for i in range(4):
            x = -0.42 + i * 0.28 + j * 0.0
            pad = cut(pad, c.rect(x - 0.08, y - 0.06, x + 0.08, y + 0.06, 0.03))
    post = c.rect(0.16, 0.06, 0.3, 0.3)
    screen = c.rect(-0.08, 0.24, 0.64, 0.6, 0.08)
    screen = cut(screen, c.rect(0.02, 0.33, 0.54, 0.51, 0.04))
    paper = c.shape([(-0.5, 0.1), (-0.2, 0.1), (-0.2, 0.68), (-0.25, 0.74), (-0.3, 0.68), (-0.35, 0.74),
                     (-0.4, 0.68), (-0.45, 0.74), (-0.5, 0.68)])
    paper = cut(paper, c.rect(-0.44, 0.48, -0.26, 0.52), c.rect(-0.44, 0.34, -0.26, 0.38))
    m = union(drawer, over(union(post, paper), pad, c.L(0.04)))
    m = over(m, screen, c.L(0.04))
    return m


HUD = [
    # file, drawing, HUD button, tint on the sheet
    ("Icon_Build", i_build, "BuildButton (left)", PUMPKIN),
    ("Icon_Rating", i_rating, "RatingButton (left), rating stars", GOLD),
    ("Icon_Residents", i_residents, "ResidentsButton (left)", TEAL),
    ("Icon_Book", i_book, "BookButton (left), the Monster Book", PURPLE_HI),
    ("Icon_Moon", i_moon, "ProgressionButton (right): Moon Shards, the Moon Tree", MOON),
    ("Icon_Store", i_store, "store button (passes and products)", GOOD),
    ("Icon_Daily", i_daily, "daily reward / daily requests", PINK),
    ("Icon_Bus", i_bus, "Night Bus timer; Call the Bus", PUMPKIN),
    ("Icon_Pitch", i_pitch, "the Pitch prompt on a guest", TEAL),
    ("Icon_Boo", i_boo, "boo (scare / emote)", MOON),
    ("Icon_Cash", i_cash, "the cash counter", GOLD),
    ("Icon_Till", i_till, "the till readout / collect", GOLD),
]


# ================================================================ the panel 9-slices
PANEL_SIZE = 512
PANEL_INSET = 24  # room for the frame's glow
PANEL_RADIUS = 72
PANEL_LINE = 8
PANEL_SLICE = 112  # SliceCenter = Rect(112, 112, 400, 400)


def _panel_mask(inset, radius):
    n = PANEL_SIZE * SS
    m = Image.new("L", (n, n), 0)
    k = inset * SS
    ImageDraw.Draw(m).rounded_rectangle((k, k, n - k - 1, n - k - 1), radius=radius * SS, fill=255)
    return m


def panel_fill():
    a = _panel_mask(PANEL_INSET, PANEL_RADIUS).resize((PANEL_SIZE,) * 2, Image.LANCZOS)
    img = Image.new("RGBA", (PANEL_SIZE,) * 2, (255, 255, 255, 0))
    img.putalpha(a)
    return img


def panel_frame():
    outer = _panel_mask(PANEL_INSET, PANEL_RADIUS)
    inner = _panel_mask(PANEL_INSET + PANEL_LINE, PANEL_RADIUS - PANEL_LINE)
    line = ImageChops.subtract(outer, inner).resize((PANEL_SIZE,) * 2, Image.LANCZOS)
    glow = line.filter(ImageFilter.GaussianBlur(7))
    outside = ImageChops.invert(_panel_mask(PANEL_INSET + PANEL_LINE // 2, PANEL_RADIUS).resize((PANEL_SIZE,) * 2, Image.LANCZOS))
    L = np.asarray(line, np.float32)
    G = np.clip(np.asarray(glow, np.float32) * 2.0, 0, 255) * 0.55 * (np.asarray(outside, np.float32) / 255)
    # A faint inner sheen just inside the line, so the edge reads as lit.
    sheen = np.asarray(glow, np.float32) * 0.25 * (1 - np.asarray(outside, np.float32) / 255)
    alpha = np.clip(np.maximum(L, G + sheen), 0, 255).astype(np.uint8)
    img = Image.new("RGBA", (PANEL_SIZE,) * 2, (255, 255, 255, 0))
    img.putalpha(Image.fromarray(alpha))
    return img


# ================================================================ props for the colour art
def coin(c, x, y, r, tilt=0.0):
    with c.at(x, y, r, tilt):
        m = c.disk(0, 0, 1)
        sticker(c, m, (GOLD_HI, GOLD_LO), ow=0.028, bevel=0.04)
        paint(c, cut(c.disk(0, 0, 0.8), c.disk(0, 0, 0.7)), (200, 120, 25), 0.75)
        sym = c.text(c.mask(), "$", 0.02, -0.04, 1.15)
        paint(c, sym, (190, 110, 20), 0.9)
        gloss(c, -0.42, 0.48, 0.28, 0.14, -40, 0.6, m)


def coin_flat(c, x, y, rx):
    """A coin lying flat, seen from the front and a little above."""
    ry, th = rx * 0.38, rx * 0.26
    side = union(c.ell(x, y - th, rx, ry), c.rect(x - rx, y - th, x + rx, y))
    sticker(c, side, (GOLD_LO, (170, 95, 20)), ow=0.022, bevel=0)
    top = c.ell(x, y, rx, ry)
    sticker(c, top, (GOLD_HI, GOLD), ow=0.016, bevel=0)
    paint(c, cut(c.ell(x, y, rx * 0.72, ry * 0.72), c.ell(x, y, rx * 0.6, ry * 0.6)), GOLD_LO, 0.8)


def coin_stack(c, x, y, rx, n):
    th = rx * 0.26
    for i in range(n):
        coin_flat(c, x + (0.012 if i % 2 else -0.01), y + i * th * 1.05, rx)


def clock(c, x, y, r, frac, pie=PUMPKIN):
    """A small clock with `frac` of its face filled: 0.25 = 15 min of an hour."""
    with c.at(x, y, r):
        face = c.disk(0, 0, 1)
        sticker(c, face, (MOON_HI, MOON), ow=0.026, bevel=0.03)
        if frac >= 0.999:
            p = c.disk(0, 0, 0.8)
        else:
            p = c.shape([(0, 0)] + arc_pts(0, 0, 0.8, 90 - 360 * frac, 90, 48))
        paint(c, p, pie, 0.9)
        for k in range(12):
            a = math.radians(90 - 30 * k)
            q = 0.86 if k % 3 else 0.8
            paint(c, c.stroke([(q * math.cos(a), q * math.sin(a)), (0.94 * math.cos(a), 0.94 * math.sin(a))], 0.07), INK)
        a = math.radians(90 - 360 * frac)
        paint(c, c.stroke([(0, 0), (0, 0.62)], 0.14), INK)
        paint(c, c.stroke([(0, 0), (0.6 * math.cos(a), 0.6 * math.sin(a))], 0.14), INK)
        paint(c, c.disk(0, 0, 0.14), INK)


def label(c, s, x, y, h, fill=(WHITE, (255, 225, 140)), ow=0.05):
    m = c.text(c.mask(), s, x, y, h)
    sticker(c, m, fill, ow=ow, bevel=0.02, shade=0.25, light=0.0)


def plus_badge(c, x, y, r, col=(GOOD, (60, 160, 70))):
    with c.at(x, y, r):
        sticker(c, c.disk(0, 0, 1), col, ow=0.03, bevel=0.04)
        paint(c, union(c.rect(-0.55, -0.16, 0.55, 0.16, 0.08), c.rect(-0.16, -0.55, 0.16, 0.55, 0.08)), WHITE)


def register(c, x, y, s, body=(PURPLE_HI, PURPLE_LO)):
    with c.at(x, y, s):
        paper = c.shape([(-0.48, 0.0), (-0.2, 0.0), (-0.2, 0.7), (-0.25, 0.76), (-0.3, 0.7), (-0.35, 0.76),
                         (-0.4, 0.7), (-0.45, 0.76), (-0.48, 0.7)])
        sticker(c, paper, (WHITE, MUTED), ow=0.02, bevel=0)
        for yy in (0.5, 0.36, 0.22):
            paint(c, c.rect(-0.43, yy - 0.02, -0.25, yy + 0.02), LINE)
        post = c.rect(0.14, 0.0, 0.3, 0.3)
        sticker(c, post, (PURPLE_LO, PURPLE_LO), ow=0.02, bevel=0)
        screen = c.rect(-0.1, 0.22, 0.66, 0.6, 0.08)
        sticker(c, screen, body, ow=0.025)
        disp = c.rect(0.0, 0.31, 0.56, 0.51, 0.04)
        sticker(c, disp, (TEAL_HI, TEAL_LO), ow=0.0, bevel=0)
        pad = rounded(c.shape([(-0.72, -0.4), (0.72, -0.4), (0.56, 0.14), (-0.56, 0.14)]), c.L(0.05))
        sticker(c, pad, body, ow=0.028)
        for j, yy in enumerate((-0.27, -0.06)):
            for i in range(4):
                xx = -0.42 + i * 0.28
                k = c.rect(xx - 0.09, yy - 0.065, xx + 0.09, yy + 0.065, 0.03)
                sticker(c, k, (MOON_HI, MOON) if (i + j) % 3 else (PUMPKIN_HI, PUMPKIN), ow=0.0, bevel=0.012, light=0)
        drawer = c.rect(-0.84, -0.86, 0.84, -0.44, 0.07)
        sticker(c, drawer, (PUMPKIN_HI, PUMPKIN_LO), ow=0.028)
        paint(c, c.rect(-0.22, -0.68, 0.22, -0.6, 0.04), INK, 0.8)


def house(c, x, y, s):
    with c.at(x, y, s):
        chim = c.rect(0.36, 0.3, 0.56, 0.78, 0.04)
        sticker(c, chim, (PUMPKIN_HI, PUMPKIN_LO))
        body = rounded(c.shape([(-0.62, -0.8), (0.62, -0.8), (0.62, 0.05), (0, 0.55), (-0.62, 0.05)]), c.L(0.03))
        sticker(c, body, (PURPLE_HI, PURPLE_LO))
        roof = c.stroke([(-0.84, 0.0), (0, 0.76), (0.84, 0.0)], 0.22)
        sticker(c, roof, (TEAL_HI, TEAL_LO))
        door = union(c.rect(-0.2, -0.8, 0.2, -0.3), c.disk(0, -0.3, 0.2))
        sticker(c, door, (PUMPKIN, PUMPKIN_LO), ow=0.02, bevel=0)
        paint(c, c.disk(0.1, -0.55, 0.035), GOLD)
        win = c.disk(0, 0.12, 0.2)
        sticker(c, win, (GOLD_HI, PUMPKIN), ow=0.02, bevel=0)
        for xx in (-0.08, 0.08):  # someone lives here
            paint(c, c.ell(xx, 0.12, 0.045, 0.065), INK)
            paint(c, c.disk(xx - 0.015, 0.14, 0.017), WHITE)


def bus_front(c, x, y, s, body=(PUMPKIN_HI, PUMPKIN_LO)):
    with c.at(x, y, s):
        for xx in (-0.44, 0.44):
            sticker(c, c.rect(xx - 0.15, -0.9, xx + 0.15, -0.5, 0.08), ((70, 55, 95), INK), bevel=0)
        for sx in (-1, 1):
            sticker(c, c.rect(sx * 0.72, 0.12, sx * 0.84, 0.42, 0.04), (PURPLE_HI, PURPLE_LO), ow=0.02, bevel=0)
        b = c.rect(-0.72, -0.66, 0.72, 0.8, 0.26)
        sticker(c, b, body)
        sign = c.rect(-0.3, 0.6, 0.3, 0.72, 0.04)
        sticker(c, sign, (GOLD_HI, GOLD), ow=0.015, bevel=0)
        glass = c.rect(-0.56, 0.08, 0.56, 0.52, 0.1)
        sticker(c, glass, (MOON_HI, MOON_LO), ow=0.022, bevel=0)
        paint(c, c.rect(-0.03, 0.08, 0.03, 0.52), INK)
        gloss(c, -0.3, 0.38, 0.16, 0.05, -25, 0.7, glass)
        gloss(c, 0.3, 0.38, 0.16, 0.05, -25, 0.7, glass)
        for sx in (-1, 1):  # headlights are eyes
            e = c.disk(sx * 0.4, -0.22, 0.17)
            sticker(c, e, (WHITE, (225, 225, 245)), ow=0.022, bevel=0)
            paint(c, c.disk(sx * 0.4 - sx * 0.04, -0.25, 0.09), INK)
            paint(c, c.disk(sx * 0.4 - sx * 0.04 - 0.03, -0.21, 0.032), WHITE)
        paint(c, c.stroke(arc_pts(0, -0.22, 0.17, 215, 325, 24), 0.06), INK)
        paint(c, c.ell(-0.28, -0.46, 0.06, 0.03), PINK, 0.8)
        paint(c, c.ell(0.28, -0.46, 0.06, 0.03), PINK, 0.8)
        bumper = c.rect(-0.76, -0.66, 0.76, -0.54, 0.05)
        sticker(c, bumper, (MOON, MOON_LO), ow=0.02, bevel=0)


def heart(c, x, y, s, face=True):
    with c.at(x, y, s):
        m = c.shape(heart_pts(0, 0, 1))
        sticker(c, m, (PINK, PINK_LO), bevel=0.05)
        gloss(c, -0.45, 0.42, 0.2, 0.12, 30, 0.6, m)
        if face:
            for xx in (-0.28, 0.28):
                paint(c, c.ell(xx, 0.05, 0.1, 0.13), INK)
                paint(c, c.disk(xx - 0.03, 0.1, 0.04), WHITE)
            paint(c, c.stroke(arc_pts(0, -0.08, 0.14, 210, 330, 24), 0.06), INK)
            for xx in (-0.5, 0.5):
                paint(c, c.ell(xx, -0.12, 0.09, 0.05), (255, 190, 210), 0.8)


def zz(c, x, y, h):
    """A sleepy Z."""
    m = c.stroke([(x - h / 2, y + h / 2), (x + h / 2, y + h / 2), (x - h / 2, y - h / 2), (x + h / 2, y - h / 2)], h * 0.28)
    sticker(c, m, (WHITE, MOON), ow=0.02, bevel=0)


def bell(c, x, y, s):
    with c.at(x, y, s):
        sticker(c, c.disk(0, 0.62, 0.1), (GOLD_HI, GOLD_LO), bevel=0)
        dome = c.shape(arc_pts(0, -0.1, 0.62, 0, 180, 64))
        sticker(c, dome, (GOLD_HI, GOLD_LO))
        gloss(c, -0.25, 0.25, 0.14, 0.08, 40, 0.65, dome)
        sticker(c, c.rect(-0.82, -0.32, 0.82, -0.1, 0.08), (PURPLE_HI, PURPLE_LO), bevel=0.02)


def crown(c, x, y, s):
    with c.at(x, y, s):
        pts = [(-0.8, -0.4), (0.8, -0.4), (0.9, 0.45), (0.45, 0.05), (0, 0.6), (-0.45, 0.05), (-0.9, 0.45)]
        m = rounded(c.shape(pts), c.L(0.04))
        sticker(c, m, (GOLD_HI, GOLD_LO), bevel=0.05)
        band = c.rect(-0.8, -0.42, 0.8, -0.18, 0.04)
        sticker(c, band, (GOLD, (205, 125, 25)), ow=0.02, bevel=0.02)
        for px, py in ((-0.9, 0.45), (0, 0.6), (0.9, 0.45)):
            sticker(c, c.disk(px, py, 0.1), (GOLD_HI, GOLD), ow=0.02, bevel=0)
        for px, col in ((-0.48, (TEAL_HI, TEAL_LO)), (0, (PINK, PINK_LO)), (0.48, (TEAL_HI, TEAL_LO))):
            g = c.shape([(px, -0.18), (px + 0.1, -0.3), (px, -0.42), (px - 0.1, -0.3)])
            g = c.disk(px, -0.3, 0.08)
            sticker(c, g, col, ow=0.016, bevel=0)
            paint(c, c.disk(px - 0.025, -0.27, 0.025), WHITE, 0.9)
        big = c.shape(star_pts(0, 0.12, 0.17, 0.08))
        sticker(c, big, (PINK, PINK_LO), ow=0.016, bevel=0)


def gift(c, x, y, s):
    with c.at(x, y, s):
        box = c.rect(-0.7, -0.8, 0.7, 0.12, 0.06)
        sticker(c, box, (PURPLE_HI, PURPLE_LO))
        lid = c.rect(-0.82, 0.08, 0.82, 0.4, 0.07)
        sticker(c, lid, (PURPLE_HI, PURPLE))
        paint(c, c.rect(-0.14, -0.8, 0.14, 0.4), TEAL)
        paint(c, c.rect(-0.14, -0.8, -0.08, 0.4), TEAL_HI, 0.8)
        paint(c, c.rect(0.08, -0.8, 0.14, 0.4), TEAL_LO, 0.8)


def slime(c, x, y, s):
    with c.at(x, y, s):
        m = union(c.ell(0, -0.2, 0.62, 0.42), c.ell(0, 0.12, 0.44, 0.48), c.disk(0.08, 0.6, 0.12))
        m = rounded(m, c.L(0.05))
        sticker(c, m, (SLIME_HI, SLIME_LO), bevel=0.05)
        gloss(c, -0.22, 0.38, 0.12, 0.07, 30, 0.7, m)
        for xx in (-0.2, 0.2):
            sticker(c, c.ell(xx, 0.0, 0.13, 0.16), (WHITE, (230, 235, 245)), ow=0.016, bevel=0)
            paint(c, c.disk(xx + 0.02, -0.03, 0.075), INK)
            paint(c, c.disk(xx - 0.01, 0.02, 0.028), WHITE)
        paint(c, c.stroke(arc_pts(0, -0.2, 0.12, 210, 330, 24), 0.05), INK)
        # A bow on its head, because it is a present.
        for sx in (-1, 1):
            b = c.shape([(0.08, 0.6), (0.08 + sx * 0.26, 0.74), (0.08 + sx * 0.26, 0.46)])
            sticker(c, rounded(b, c.L(0.02)), (PUMPKIN_HI, PUMPKIN_LO), ow=0.02, bevel=0)
        sticker(c, c.disk(0.08, 0.6, 0.07), (PUMPKIN, PUMPKIN_LO), ow=0.02, bevel=0)


def sack(c, x, y, s):
    with c.at(x, y, s):
        body = rounded(union(c.ell(0, -0.25, 0.68, 0.58), c.shape([(-0.3, 0.2), (0.3, 0.2), (0.18, 0.5), (-0.18, 0.5)])), c.L(0.04))
        sticker(c, body, (PURPLE_HI, PURPLE_LO))
        top = c.shape([(-0.26, 0.5), (0.26, 0.5), (0.4, 0.78), (0.14, 0.66), (0, 0.8), (-0.14, 0.66), (-0.4, 0.78)])
        sticker(c, rounded(top, c.L(0.02)), (PURPLE_HI, PURPLE), bevel=0)
        sticker(c, c.rect(-0.3, 0.38, 0.3, 0.52, 0.06), (GOLD, GOLD_LO), ow=0.02, bevel=0)
        sym = c.text(c.mask(), "$", 0, -0.28, 0.7)
        sticker(c, sym, (GOLD_HI, GOLD_LO), ow=0.025, bevel=0)


def stanchion(c, x, y, s):
    with c.at(x, y, s):
        sticker(c, c.ell(0, -0.92, 0.32, 0.1), (GOLD, GOLD_LO), bevel=0)
        sticker(c, c.rect(-0.08, -0.92, 0.08, 0.5, 0.04), (GOLD_HI, GOLD_LO), bevel=0)
        sticker(c, c.disk(0, 0.58, 0.16), (GOLD_HI, GOLD_LO), bevel=0.02)


# ================================================================ Gloom, the bat concierge
def gloom(c):
    with c.at(0, -0.02, 0.97):
        for sx in (-1, 1):  # wings, behind
            def S(pts):
                return [(sx * px, py) for px, py in pts]
            a, b = (0.95, 0.1), (0.32, -0.3)
            wing = c.shape(S([(0.3, 0.32), (0.5, 0.52), (0.76, 0.62), (0.99, 0.54), a, b]))
            n = (0.536, -0.844)
            bones = []
            for t in (1 / 6, 0.5, 5 / 6):
                px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                wing = cut(wing, c.disk(sx * (px + n[0] * 0.05), py + n[1] * 0.05, 0.14))
            for t in (0.0, 1 / 3, 2 / 3):
                px, py = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
                bones.append((px, py))
            wing = rounded(wing, c.L(0.015))
            sticker(c, wing, ((120, 70, 185), (70, 38, 125)), bevel=0.04)
            for px, py in bones:
                paint(c, inter(c.stroke(S([(0.4, 0.3), (0.78, 0.5), (px, py)]) if px > 0.9 else S([(0.42, 0.28), (px, py)]), 0.025), wing), PURPLE_HI, 0.75)
        for sx in (-1, 1):  # feet
            sticker(c, c.ell(sx * 0.16, -0.56, 0.1, 0.07), (PURPLE_LO, (50, 28, 90)), bevel=0)
        for sx in (-1, 1):  # ears
            ear = rounded(c.shape([(sx * 0.14, 0.3), (sx * 0.44, 0.86), (sx * 0.5, 0.18)]), c.L(0.03))
            sticker(c, ear, (PURPLE_HI, PURPLE_LO), bevel=0.03)
            inner = rounded(c.shape([(sx * 0.24, 0.32), (sx * 0.43, 0.72), (sx * 0.44, 0.28)]), c.L(0.02))
            paint(c, inner, (PINK, (200, 100, 170)), 0.85)
        body = c.disk(0, -0.04, 0.52)
        sticker(c, body, ((165, 110, 235), (95, 55, 165)), bevel=0.06)
        tuft = c.shape([(-0.12, 0.42), (-0.06, 0.6), (0.0, 0.45), (0.06, 0.64), (0.12, 0.44)])
        sticker(c, rounded(tuft, c.L(0.012)), ((165, 110, 235), (140, 90, 210)), ow=0.02, bevel=0)
        face = union(c.disk(-0.16, 0.0, 0.25), c.disk(0.16, 0.0, 0.25), c.ell(0, -0.13, 0.3, 0.2))
        paint(c, face.filter(ImageFilter.GaussianBlur(c.L0(0.008))), (200, 170, 245), 0.9)
        for sx in (-1, 1):  # big eyes
            ex = sx * 0.17
            sticker(c, c.ell(ex, 0.03, 0.14, 0.165), (WHITE, (225, 225, 245)), ow=0.022, bevel=0)
            iris = c.disk(ex + sx * -0.015, 0.0, 0.11)
            paint(c, iris, (TEAL_HI, TEAL_LO))
            paint(c, c.disk(ex + sx * -0.015, -0.005, 0.065), INK)
            paint(c, c.disk(ex - 0.045, 0.045, 0.035), WHITE)
            paint(c, c.disk(ex + 0.03, -0.05, 0.016), WHITE)
            paint(c, c.ell(sx * 0.35, -0.13, 0.075, 0.045), PINK, 0.65)
        paint(c, c.stroke(arc_pts(0, -0.1, 0.075, 220, 320, 24), 0.024), INK)
        fang = c.shape([(0.02, -0.155), (0.075, -0.155), (0.05, -0.215)])
        sticker(c, fang, (WHITE, WHITE), ow=0.012, bevel=0)
        for sx in (-1, 1):  # a teal bow tie
            w = rounded(c.shape([(0, -0.34), (sx * 0.2, -0.25), (sx * 0.2, -0.45)]), c.L(0.025))
            sticker(c, w, (TEAL_HI, TEAL_LO), ow=0.022, bevel=0.02)
        sticker(c, c.rect(-0.05, -0.39, 0.05, -0.29, 0.03), (TEAL, TEAL_LO), ow=0.018, bevel=0)
    outline_all(c, 0.012)


# ================================================================ passes (GDD §10.2)
BG_NIGHT = ((120, 72, 195), (34, 20, 64))


def p_autocollect(c):
    background(c, *BG_NIGHT, (TEAL_HI, TEAL_LO), seed=11)
    arrow = c.stroke(arc_pts(-0.05, -0.1, 0.62, 25, 150, 48), 0.09)
    sticker(c, arrow, (TEAL_HI, TEAL), ow=0.025, bevel=0)
    a = math.radians(25)
    tip = (-0.05 + 0.62 * math.cos(a), -0.1 + 0.62 * math.sin(a))
    head = c.shape([(tip[0] + 0.15, tip[1] + 0.08), (tip[0] - 0.12, tip[1] + 0.07), (tip[0] + 0.05, tip[1] - 0.18)])
    sticker(c, rounded(head, c.L(0.01)), (TEAL_HI, TEAL), ow=0.025, bevel=0)
    register(c, -0.12, -0.2, 0.5)
    coin(c, 0.42, 0.5, 0.15, 15)
    coin(c, 0.62, 0.15, 0.12, -10)
    coin(c, 0.06, 0.66, 0.11, 5)


def p_nightmanager(c):
    background(c, (80, 95, 200), (24, 22, 70), (MOON_HI, MOON_LO), seed=12)
    with c.at(-0.08, 0.08, 1, -15):
        m = rounded(cut(c.disk(0, 0, 0.62), c.disk(0.34, 0.18, 0.52)), c.L(0.02))
    sticker(c, m, (MOON_HI, MOON_LO), bevel=0.05)
    paint(c, c.stroke(arc_pts(-0.32, 0.12, 0.08, 200, 340, 24), 0.03), INK)  # a sleeping eye
    paint(c, c.ell(-0.32, -0.04, 0.06, 0.035), PINK, 0.7)
    zz(c, 0.3, 0.52, 0.14)
    zz(c, 0.5, 0.3, 0.1)
    zz(c, 0.18, 0.72, 0.08)
    bell(c, 0.36, -0.42, 0.34)
    clock(c, -0.4, -0.5, 0.2, 1.0, TEAL)


def p_residentwing(c):
    background(c, *BG_NIGHT, (TEAL_HI, TEAL_LO), seed=13)
    house(c, -0.06, -0.02, 0.72)
    plus_badge(c, 0.5, 0.42, 0.22)


def p_extrafloor(c):
    background(c, *BG_NIGHT, (GOLD_HI, GOLD_LO), seed=14)
    with c.at(-0.08, 0, 1):
        for i, (y0, y1) in enumerate(((-0.68, -0.34), (-0.34, 0.0))):
            f = c.rect(-0.44, y0, 0.44, y1, 0.04)
            sticker(c, f, (PURPLE_HI, PURPLE_LO), bevel=0.03)
            for xx in (-0.26, 0.0, 0.26):
                if i == 0 and xx == 0:
                    sticker(c, c.rect(-0.08, y0, 0.08, y0 + 0.22, 0.04), (PUMPKIN, PUMPKIN_LO), ow=0.015, bevel=0)
                    continue
                sticker(c, c.rect(xx - 0.07, (y0 + y1) / 2 - 0.07, xx + 0.07, (y0 + y1) / 2 + 0.08, 0.03),
                        (GOLD_HI, PUMPKIN), ow=0.015, bevel=0)
        glow = c.rect(-0.5, 0.06, 0.5, 0.46, 0.06).filter(ImageFilter.GaussianBlur(c.L0(0.05)))
        paint(c, glow, TEAL_HI, 0.7)
        new = c.rect(-0.44, 0.1, 0.44, 0.42, 0.04)
        sticker(c, new, (TEAL_HI, TEAL_LO), bevel=0.03)
        for xx in (-0.26, 0.0, 0.26):
            sticker(c, c.rect(xx - 0.07, 0.19, xx + 0.07, 0.33, 0.03), (MOON_HI, MOON), ow=0.015, bevel=0)
        roof = rounded(c.shape([(-0.52, 0.44), (0.52, 0.44), (0.36, 0.62), (-0.36, 0.62)]), c.L(0.02))
        sticker(c, roof, (PUMPKIN_HI, PUMPKIN_LO), bevel=0.02)
        sparkle(c, -0.56, 0.4, 0.07)
        sparkle(c, 0.4, 0.7, 0.05)
    arrow = c.shape([(0.62, 0.42), (0.8, 0.12), (0.69, 0.12), (0.69, -0.3), (0.55, -0.3), (0.55, 0.12), (0.44, 0.12)])
    sticker(c, rounded(arrow, c.L(0.012)), (GOLD_HI, GOLD_LO), bevel=0.03)


def p_viplobby(c):
    background(c, (150, 70, 170), (40, 16, 60), (GOLD_HI, GOLD_LO), seed=15)
    rope = c.stroke(arc_pts(0, 0.05, 0.62, 205, 335, 48), 0.08)
    for sx in (-1, 1):
        stanchion(c, sx * 0.58, -0.38, 0.42)
    sticker(c, rope, ((230, 60, 110), (150, 25, 70)), ow=0.022, bevel=0)
    crown(c, 0, 0.2, 0.5)
    sparkle(c, -0.5, 0.55, 0.07, GOLD_HI)
    sparkle(c, 0.55, 0.6, 0.05, GOLD_HI)


PASSES = [
    ("Pass_AutoCollectTill", p_autocollect, "Auto-Collect Till (149)"),
    ("Pass_NightManager", p_nightmanager, "Night Manager (249)"),
    ("Pass_ResidentWingPlus", p_residentwing, "Resident Wing+ (249)"),
    ("Pass_ExtraFloor", p_extrafloor, "Extra Floor (299)"),
    ("Pass_VipLobby", p_viplobby, "VIP Lobby (399)"),
]


# ================================================================ developer products (GDD §10.2)
BG_CASH = ((135, 80, 200), (38, 22, 70))


def d_starter(c):
    background(c, *BG_NIGHT, (PUMPKIN_HI, PUMPKIN_LO), seed=21)
    gift(c, 0.02, -0.3, 0.5)
    slime(c, 0.04, 0.3, 0.44)
    coin_stack(c, -0.56, -0.62, 0.17, 3)
    coin(c, 0.6, -0.36, 0.16, -12)
    clock(c, 0.56, 0.36, 0.15, 0.5, TEAL)
    sparkle(c, -0.5, 0.42, 0.07)


def d_callbus(c):
    background(c, (75, 100, 205), (20, 22, 68), (PUMPKIN_HI, PUMPKIN_LO), seed=22)
    for sx in (-1, 1):
        for r in (0.66, 0.8):
            paint(c, c.stroke(arc_pts(sx * 0.3, 0.36, r - 0.4, 90 - sx * 35 - 22, 90 - sx * 35 + 22, 24), 0.05), WHITE, 0.85)
        for k, yy in enumerate((-0.1, -0.3)):
            paint(c, c.stroke([(sx * 0.66, yy), (sx * (0.82 - 0.06 * k), yy)], 0.045), MOON_HI, 0.8)
    bus_front(c, 0, -0.02, 0.56)


def boost(c, frac, coins):
    background(c, *BG_CASH, (GOLD_HI, GOLD_LO), seed=23 + coins)
    if coins >= 2:
        coin_stack(c, -0.52, -0.6, 0.2, 3)
    coin(c, -0.18, 0.12, 0.42, -8)
    label(c, "2x", 0.28, -0.42, 0.6)
    clock(c, 0.5, 0.42, 0.22, frac)


def d_2xcash15(c):
    boost(c, 0.25, 1)


def d_2xcash60(c):
    boost(c, 1.0, 2)


def d_2xfriend(c):
    background(c, (40, 160, 160), (14, 40, 66), (PINK, PINK_LO), seed=26)
    heart(c, -0.14, 0.1, 0.56)
    label(c, "2x", 0.3, -0.44, 0.56, fill=(WHITE, (255, 205, 225)))
    clock(c, 0.5, 0.44, 0.2, 0.5, PINK)
    sparkle(c, -0.62, -0.3, 0.07)


def d_cash_s(c):
    background(c, *BG_CASH, (GOLD_HI, GOLD_LO), seed=27, stars=6)
    coin_stack(c, -0.14, -0.42, 0.42, 3)
    coin(c, 0.4, 0.12, 0.3, -14)
    sparkle(c, -0.4, 0.4, 0.07, GOLD_HI)


def d_cash_m(c):
    background(c, *BG_CASH, (GOLD_HI, GOLD_LO), seed=28, stars=9)
    coin_stack(c, -0.36, -0.5, 0.26, 4)
    coin_stack(c, 0.22, -0.56, 0.26, 3)
    coin(c, 0.46, 0.14, 0.2, -14)
    coin(c, -0.06, 0.38, 0.17, 10)
    sparkle(c, 0.5, 0.52, 0.06, GOLD_HI)


def d_cash_l(c):
    background(c, (160, 90, 210), (44, 22, 74), (GOLD_HI, GOLD_LO), seed=29, stars=13)
    sack(c, 0.02, 0.08, 0.56)
    coin_stack(c, -0.56, -0.62, 0.2, 4)
    coin_stack(c, 0.5, -0.62, 0.2, 3)
    coin(c, -0.06, -0.6, 0.18, 6)
    coin(c, 0.56, 0.18, 0.15, -12)
    coin(c, -0.58, 0.26, 0.13, 14)
    for x, y, r in ((0.3, 0.68, 0.07), (-0.36, 0.62, 0.06), (0.66, -0.14, 0.05)):
        sparkle(c, x, y, r, GOLD_HI)


PRODUCTS = [
    ("Product_StarterPack", d_starter, "Starter Pack (99)"),
    ("Product_CallTheBus", d_callbus, "Call the Bus (39)"),
    ("Product_2xCash15m", d_2xcash15, "2x Cash, 15 min (49)"),
    ("Product_2xCash1h", d_2xcash60, "2x Cash, 1 h (149)"),
    ("Product_2xFriendship", d_2xfriend, "2x Friendship, 30 min (79)"),
    ("Product_CashSmall", d_cash_s, "Cash pack small (49)"),
    ("Product_CashMedium", d_cash_m, "Cash pack medium (149)"),
    ("Product_CashLarge", d_cash_l, "Cash pack large (449)"),
]


# ================================================================ the review sheet
def tinted(icon, colour, size):
    arr = np.asarray(icon.resize((size, size), Image.LANCZOS), np.float32).copy()
    arr[..., :3] = np.array(colour, np.float32)
    return Image.fromarray(arr.astype(np.uint8))


def nine_slice(img, w, h, s):
    n = img.width
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    xs = [(0, s, 0, s), (s, n - s, s, w - s), (n - s, n, w - s, w)]
    ys = [(0, s, 0, s), (s, n - s, s, h - s), (n - s, n, h - s, h)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            if dx1 > dx0 and dy1 > dy0:
                out.paste(img.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.LANCZOS), (dx0, dy0))
    return out


def circle_crop(img):
    n = img.width * 4
    m = Image.new("L", (n, n), 0)
    ImageDraw.Draw(m).ellipse((0, 0, n - 1, n - 1), fill=255)
    out = img.copy()
    out.putalpha(ImageChops.multiply(img.getchannel("A"), m.resize(img.size, Image.LANCZOS)))
    return out


def sheet(hud, panels, portrait, passes, products):
    W = 1600
    font = ImageFont.truetype(FONT_LABEL, 15)
    head = ImageFont.truetype(FONT_LABEL, 22)
    H = 1470
    img = Image.new("RGBA", (W, H), INK + (255,))
    d = ImageDraw.Draw(img)

    def title(y, s):
        d.text((30, y), s, font=head, fill=TEXT)

    # HUD icons, tinted as the HUD might, large and at button size.
    title(20, "HUD icons: white on transparent, tinted here (256 px; shown at 104 and 36)")
    cell = 128
    for i, (name, im, colour) in enumerate(hud):
        x, y = 30 + (i % 12) * cell, 60
        big = tinted(im, colour, 104)
        img.alpha_composite(big, (x + 8, y))
        small = tinted(im, colour, 36)
        img.alpha_composite(small, (x + 8, y + 112))
        btn = Image.new("RGBA", (52, 44), PANEL + (255,))
        img.alpha_composite(btn, (x + 56, y + 108))
        img.alpha_composite(tinted(im, TEXT, 32), (x + 66, y + 114))
        d.text((x + 8, y + 158), name.removeprefix("Icon_"), font=font, fill=MUTED)

    # The panel, built from its two 9-slices, and Gloom on one.
    title(262, f"Panel 9-slices: PanelFill (tinted Panel) + PanelFrame (tinted Line), SliceCenter {PANEL_SLICE}..{PANEL_SIZE - PANEL_SLICE}; Gloom (512, colour)")
    fill, frame = panels
    for k, (pw, ph, sc, x) in enumerate(((520, 240, 0.75, 30), (300, 180, 0.5, 590))):
        s = round(PANEL_SLICE * sc)
        f = fill.resize((round(PANEL_SIZE * sc),) * 2, Image.LANCZOS)
        fr = frame.resize((round(PANEL_SIZE * sc),) * 2, Image.LANCZOS)
        img.alpha_composite(_tint_any(nine_slice(f, pw, ph, s), PANEL), (x, 300))
        img.alpha_composite(_tint_any(nine_slice(fr, pw, ph, s), LINE), (x, 300))
    img.alpha_composite(_tint_any(nine_slice(fill.resize((256, 256), Image.LANCZOS), 250, 250, 56), PANEL), (930, 290))
    img.alpha_composite(_tint_any(nine_slice(frame.resize((256, 256), Image.LANCZOS), 250, 250, 56), LINE), (930, 290))
    img.alpha_composite(portrait.resize((220, 220), Image.LANCZOS), (945, 305))
    night = Image.new("RGBA", (250, 250), (34, 20, 64, 255))
    img.alpha_composite(night, (1210, 290))
    img.alpha_composite(portrait.resize((250, 250), Image.LANCZOS), (1210, 290))
    img.alpha_composite(portrait.resize((64, 64), Image.LANCZOS), (1490, 476))

    # Passes, circle-cropped as Roblox shows them.
    title(568, "Pass icons (512, colour), cropped to the circle as Roblox shows them; and at 64")
    for i, (name, im, label_) in enumerate(passes):
        x, y = 30 + i * 310, 606
        img.alpha_composite(circle_crop(im.resize((220, 220), Image.LANCZOS)), (x, y))
        img.alpha_composite(circle_crop(im.resize((64, 64), Image.LANCZOS)), (x + 228, y + 156))
        d.text((x, y + 228), label_, font=font, fill=MUTED)

    # Products, square.
    title(880, "Developer product icons (512, colour), square; and at 64")
    for i, (name, im, label_) in enumerate(products):
        x, y = 30 + (i % 4) * 390, 918 + (i // 4) * 272
        img.alpha_composite(im.resize((220, 220), Image.LANCZOS), (x, y))
        img.alpha_composite(im.resize((64, 64), Image.LANCZOS), (x + 232, y + 156))
        d.text((x, y + 228), label_, font=font, fill=MUTED)
    return img.convert("RGB")


def _tint_any(im, colour):
    arr = np.asarray(im, np.float32).copy()
    arr[..., :3] = np.array(colour, np.float32)
    return Image.fromarray(arr.astype(np.uint8))


# ================================================================ main
def main():
    for sub in ("hud", "panel", "pass", "product"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    hud = []
    for name, fn, _, colour in HUD:
        im = hud_icon(fn)
        im.save(OUT / "hud" / f"{name}.png")
        hud.append((name, im, colour))

    fill, frame = panel_fill(), panel_frame()
    fill.save(OUT / "panel" / "PanelFill.png")
    frame.save(OUT / "panel" / "PanelFrame.png")

    c = Canvas(512)
    gloom(c)
    portrait = finish(c)
    portrait.save(OUT / "Gloom.png")

    passes = []
    for name, fn, label_ in PASSES:
        c = Canvas(512)
        fn(c)
        im = finish(c)
        im.save(OUT / "pass" / f"{name}.png")
        passes.append((name, im, label_))

    products = []
    for name, fn, label_ in PRODUCTS:
        c = Canvas(512)
        fn(c)
        im = finish(c)
        im.save(OUT / "product" / f"{name}.png")
        products.append((name, im, label_))

    sheet(hud, (fill, frame), portrait, passes, products).save(OUT / "_sheet.png")
    print(f"wrote {len(hud)} HUD icons, 2 panels, Gloom, {len(passes)} passes, {len(products)} products, _sheet.png")


if __name__ == "__main__":
    main()
