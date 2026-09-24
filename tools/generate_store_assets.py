#!/usr/bin/env python3
"""Generates the Google Play store graphics from the watch face preview.

Run from the project root:  python3 tools/generate_store_assets.py
Output: playstore/  (icon 512x512, feature graphic 1024x500, screenshot)
"""
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(ROOT, "watchface", "src", "main", "res")
OUT = os.path.join(ROOT, "playstore")

PREVIEW = os.path.join(RES, "drawable", "preview.png")
BG = os.path.join(RES, "drawable-nodpi", "bg_gradient.png")
FONT = "/System/Library/Fonts/Avenir Next.ttc"

GOLD = (176, 132, 84)
GOLD_LIGHT = (205, 170, 125)
DARK = (46, 38, 30)


def round_face(size):
    """The preview cut to a circle, with transparent corners."""
    face = Image.open(PREVIEW).convert("RGBA").resize((size, size), Image.LANCZOS)
    mask = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size * 4 - 1, size * 4 - 1], fill=255)
    face.putalpha(mask.resize((size, size), Image.LANCZOS))
    return face


def backdrop(w, h):
    return Image.open(BG).convert("RGBA").resize((w, h), Image.LANCZOS)


def paste_with_shadow(canvas, face, x, y, blur=18, offset=8):
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    alpha = face.split()[3].point(lambda a: a * 0.45)
    shadow.paste((60, 40, 20, 255), (x, y + offset), alpha)
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(blur)))
    canvas.alpha_composite(face, (x, y))


def icon():
    img = backdrop(512, 512)
    paste_with_shadow(img, round_face(420), 46, 40, blur=14, offset=6)
    img.convert("RGB").save(os.path.join(OUT, "icon_512.png"))


def feature_graphic():
    w, h = 1024, 500
    img = backdrop(w, h)
    face = round_face(420)
    paste_with_shadow(img, face, w - 420 - 70, (h - 420) // 2)

    d = ImageDraw.Draw(img)
    title = ImageFont.truetype(FONT, 84, index=0)
    sub = ImageFont.truetype(FONT, 30, index=0)
    d.text((70, 150), "Pixel Sand", font=title, fill=DARK)
    d.line([(74, 262), (330, 262)], fill=GOLD_LIGHT, width=3)
    d.text((72, 286), "Wear OS Watch Face", font=sub, fill=GOLD)
    img.convert("RGB").save(os.path.join(OUT, "feature_graphic_1024x500.png"))


def screenshot():
    # Play wants square Wear OS screenshots without a round mask
    Image.open(PREVIEW).convert("RGB").save(os.path.join(OUT, "screenshot_1.png"))


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    icon()
    feature_graphic()
    screenshot()
