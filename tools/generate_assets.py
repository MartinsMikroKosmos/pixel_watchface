#!/usr/bin/env python3
"""Generates the bitmap resources for the watch face.

Run from the project root:  python3 tools/generate_assets.py
"""
import math
import os

from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "watchface", "src", "main", "res", "drawable-nodpi")
S = 4  # supersampling factor

GOLD = (190, 148, 98, 255)
GOLD_DARK = (150, 110, 70, 255)
SUN = (247, 196, 82, 255)
SUN_EDGE = (240, 170, 60, 255)
CLOUD = (244, 246, 250, 255)
CLOUD_SHADE = (205, 212, 224, 255)
RAIN = (110, 160, 220, 255)
BOLT = (245, 190, 60, 255)
MOON = (236, 214, 150, 255)


def save(img, name, size):
    img = img.resize(size, Image.LANCZOS)
    img.save(os.path.join(OUT, name + ".png"))


def canvas(w, h):
    img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def ell(d, cx, cy, r, fill):
    d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=fill)


# ---------------------------------------------------------------- background
def background():
    n = 450
    img = Image.new("RGB", (n, n))
    px = img.load()
    warm = (247, 222, 186)   # peach, top left
    cream = (250, 244, 234)  # center
    blue = (200, 220, 244)   # bottom right
    for y in range(n):
        for x in range(n):
            # diagonal position 0 (top left) .. 1 (bottom right)
            t = (x * 0.55 + y * 0.45) / n
            t = min(max(t, 0.0), 1.0)
            if t < 0.5:
                k = t / 0.5
                c = [warm[i] + (cream[i] - warm[i]) * k for i in range(3)]
            else:
                k = (t - 0.5) / 0.5
                k = k * k * (3 - 2 * k)
                c = [cream[i] + (blue[i] - cream[i]) * k for i in range(3)]
            px[x, y] = tuple(int(v) for v in c)
    # soft glow blobs for a painted look
    glow = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse([-60, -40, 200, 220], fill=(245, 205, 150, 90))
    g.ellipse([180, 120, 360, 300], fill=(255, 250, 242, 120))
    g.ellipse([300, 260, 520, 500], fill=(185, 208, 240, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    img.convert("RGB").save(os.path.join(OUT, "bg_gradient.png"))


# ------------------------------------------------------------- weather icons
def sun(d, cx, cy, r, rays=True):
    if rays:
        for i in range(8):
            a = math.radians(i * 45)
            x1, y1 = cx + math.cos(a) * (r + 3), cy + math.sin(a) * (r + 3)
            x2, y2 = cx + math.cos(a) * (r + 8), cy + math.sin(a) * (r + 8)
            d.line([x1 * S, y1 * S, x2 * S, y2 * S], fill=SUN_EDGE, width=int(2.4 * S))
    ell(d, cx, cy, r, SUN_EDGE)
    ell(d, cx - 0.6, cy - 0.6, r - 1.6, SUN)


def moon(d, cx, cy, r):
    ell(d, cx, cy, r, MOON)
    ell(d, cx + r * 0.55, cy - r * 0.45, r * 0.85, (0, 0, 0, 0))


def cloud(d, x, y, w, color=CLOUD, shade=CLOUD_SHADE):
    """Cloud with bottom-left corner at (x, y) and width w."""
    h = w * 0.36
    for dx, dy in ((0, 1.2), (0, 0)):
        c = shade if dy else color
        oy = dy
        d.rounded_rectangle([x * S, (y - h + oy) * S, (x + w) * S, (y + oy) * S],
                            radius=h / 2 * S, fill=c)
        ell(d, x + w * 0.34, y - h * 0.9 + oy, w * 0.24, c)
        ell(d, x + w * 0.62, y - h * 1.05 + oy, w * 0.30, c)


def drops(d, x, y, count, color=RAIN, snow=False):
    for i in range(count):
        cx = x + i * 9
        if snow:
            ell(d, cx, y + 4 + (i % 2) * 4, 2.4, (170, 195, 230, 255))
        else:
            d.line([cx * S, (y + 2 + (i % 2) * 3) * S, (cx - 2.5) * S, (y + 9 + (i % 2) * 3) * S],
                   fill=color, width=int(2.6 * S))


def weather_icons():
    size = 56
    icons = {}

    img, d = canvas(size, size); sun(d, 28, 28, 12); icons["wx_sunny"] = img
    img, d = canvas(size, size); moon(d, 28, 28, 14); icons["wx_clear_night"] = img
    img, d = canvas(size, size); sun(d, 22, 22, 10); cloud(d, 14, 46, 36); icons["wx_partly_cloudy"] = img
    img, d = canvas(size, size); moon(d, 22, 21, 11); cloud(d, 14, 46, 36); icons["wx_partly_cloudy_night"] = img
    img, d = canvas(size, size)
    cloud(d, 18, 34, 30, (225, 229, 236, 255), (195, 202, 214, 255)); cloud(d, 6, 44, 40)
    icons["wx_cloudy"] = img
    img, d = canvas(size, size); cloud(d, 8, 32, 40)
    for i, yy in enumerate((38, 44, 50)):
        d.rounded_rectangle([(10 + i * 3) * S, yy * S, (46 - i * 2) * S, (yy + 2.6) * S],
                            radius=1.3 * S, fill=(190, 198, 212, 255))
    icons["wx_fog"] = img
    img, d = canvas(size, size); cloud(d, 8, 34, 40); drops(d, 16, 36, 4); icons["wx_rain"] = img
    img, d = canvas(size, size); cloud(d, 8, 34, 40); drops(d, 16, 36, 4, snow=True); icons["wx_snow"] = img
    img, d = canvas(size, size); cloud(d, 8, 32, 40)
    d.polygon([(30 * S, 33 * S), (22 * S, 45 * S), (28 * S, 45 * S), (24 * S, 54 * S),
               (35 * S, 41 * S), (29 * S, 41 * S), (33 * S, 33 * S)], fill=BOLT)
    icons["wx_thunder"] = img
    img, d = canvas(size, size)
    for yy, l in ((20, 34), (29, 40), (38, 28)):
        d.rounded_rectangle([8 * S, yy * S, (8 + l) * S, (yy + 3) * S], radius=1.5 * S, fill=(160, 180, 205, 255))
    icons["wx_windy"] = img

    for name, im in icons.items():
        save(im, name, (size, size))


# ---------------------------------------------------------------- UI icons
def ui_icons():
    # watch
    img, d = canvas(16, 22)
    w = 1.8 * S
    d.rounded_rectangle([5 * S, 0.5 * S, 11 * S, 5 * S], radius=1 * S, fill=GOLD)
    d.rounded_rectangle([5 * S, 17 * S, 11 * S, 21.5 * S], radius=1 * S, fill=GOLD)
    d.ellipse([1.5 * S, 4 * S, 14.5 * S, 18 * S], fill=(0, 0, 0, 0), outline=GOLD, width=int(w))
    save(img, "ic_watch", (16, 22))

    # phone
    img, d = canvas(14, 22)
    d.rounded_rectangle([1 * S, 1 * S, 13 * S, 21 * S], radius=2.5 * S, outline=GOLD, width=int(1.8 * S))
    d.line([5.5 * S, 17.5 * S, 8.5 * S, 17.5 * S], fill=GOLD, width=int(1.6 * S))
    save(img, "ic_phone", (14, 22))

    # shoe (side view, pointing right)
    img, d = canvas(28, 20)
    d.polygon([(4 * S, 2 * S), (11 * S, 2 * S), (13 * S, 7 * S), (22 * S, 10 * S),
               (26 * S, 13 * S), (26 * S, 16 * S), (3 * S, 16 * S), (3 * S, 6 * S)], fill=GOLD_DARK)
    d.rounded_rectangle([3 * S, 15 * S, 26.5 * S, 18.5 * S], radius=1.6 * S, fill=GOLD)
    for i in range(3):
        d.line([(12 + i * 3) * S, (8 + i * 1) * S, (14 + i * 3) * S, (6 + i * 1) * S],
               fill=(250, 240, 225, 255), width=int(1.2 * S))
    save(img, "ic_shoe", (28, 20))

    # heart with pulse line
    img, d = canvas(28, 24)
    ell(d, 8, 8, 6.5, GOLD); ell(d, 20, 8, 6.5, GOLD)
    d.polygon([(2 * S, 10 * S), (26 * S, 10 * S), (14 * S, 22.5 * S)], fill=GOLD)
    d.line([(1 * S, 11 * S), (8 * S, 11 * S), (11 * S, 6 * S), (15 * S, 16 * S),
            (18 * S, 11 * S), (27 * S, 11 * S)], fill=(250, 240, 225, 255), width=int(1.8 * S), joint="curve")
    save(img, "ic_heart", (28, 24))


# ------------------------------------------------------------------ HR wave
def hr_wave():
    w, h = 150, 66
    img, d = canvas(w, h)
    pts = []
    for i in range(0, w * 2 + 1):
        x = i / 2
        t = (x - w * 0.48) / (w * 0.5)
        env = math.exp(-(t * 2.2) ** 2)
        y = h / 2 - math.sin(x / w * math.pi * 5.2 - 0.9) * (h * 0.42) * env
        pts.append((x, y, env))
    for (x1, y1, e1), (x2, y2, _) in zip(pts, pts[1:]):
        a = int(90 + 165 * min(1.0, e1 * 1.6))
        d.line([x1 * S, y1 * S, x2 * S, y2 * S], fill=GOLD[:3] + (a,), width=int(3.2 * S))
    save(img, "hr_wave", (w, h))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    background()
    weather_icons()
    ui_icons()
    hr_wave()
    print("assets written to", os.path.abspath(OUT))
