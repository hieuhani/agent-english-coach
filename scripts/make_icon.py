"""Render the english-coach icon: a speech bubble with "Aa" and a green check badge.

Usage: python3 scripts/make_icon.py plugins/english-coach/assets/icon.png  (macOS, needs Pillow)
"""
import sys
from PIL import Image, ImageDraw, ImageFont

OUT = sys.argv[1]
SIZE, SS = 1024, 4  # final size, supersampling factor
S = SIZE * SS
s = lambda v: int(v * SS)  # design units are in 1024px space

img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

# Background: rounded square with a vertical indigo-to-blue gradient
grad = Image.new("RGBA", (S, S))
top, bottom = (79, 70, 229), (37, 99, 235)
gd = ImageDraw.Draw(grad)
for y in range(S):
    t = y / (S - 1)
    gd.line([(0, y), (S, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)) + (255,))
mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=s(224), fill=255)
img.paste(grad, (0, 0), mask)

d = ImageDraw.Draw(img)
white, ink, green = (255, 255, 255, 255), (49, 46, 129, 255), (34, 197, 94, 255)

# Speech bubble with a tail at the bottom left
d.rounded_rectangle([s(150), s(210), s(874), s(700)], radius=s(120), fill=white)
d.polygon([(s(260), s(660)), (s(420), s(660)), (s(230), s(840))], fill=white)

# "Aa" centered in the bubble
font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", s(330))
text = "Aa"
l, t, r, b = d.textbbox((0, 0), text, font=font)
cx, cy = s(480), s(450)
d.text((cx - (r - l) / 2 - l, cy - (b - t) / 2 - t), text, font=font, fill=ink)

# Green check badge overlapping the bubble's bottom-right corner
bx, by, br = s(800), s(760), s(140)
d.ellipse([bx - br - s(26), by - br - s(26), bx + br + s(26), by + br + s(26)], fill=bottom + (255,))
d.ellipse([bx - br, by - br, bx + br, by + br], fill=green)
d.line([(bx - s(70), by + s(2)), (bx - s(18), by + s(56)), (bx + s(78), by - s(58))],
       fill=white, width=s(42), joint="curve")
for px, py in [(bx - s(70), by + s(2)), (bx + s(78), by - s(58))]:  # round line caps
    d.ellipse([px - s(21), py - s(21), px + s(21), py + s(21)], fill=white)

img.resize((SIZE, SIZE), Image.LANCZOS).save(OUT, optimize=True)
