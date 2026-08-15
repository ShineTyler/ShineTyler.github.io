"""One-off generator for the static Open Graph cover image.

Run: python src/scripts/make_og_image.py
Output: src/assets/images/og/og-cover.png (1200x630, PNG)
Pillow is only needed here — the built site just copies the PNG.
"""
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_DIR = Path("C:/Windows/Fonts")
OUT = Path(__file__).resolve().parents[1] / "assets" / "images" / "og"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1200, 630
PAPER = (240, 231, 211)
INK = (47, 38, 29)
INK_SOFT = (107, 90, 65)
RED = (163, 59, 38)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONT_DIR / name
    if not path.exists():
        print(f"missing font {path}", file=sys.stderr)
        return ImageFont.load_default(size)
    return ImageFont.truetype(str(path), size)


def main() -> None:
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img, "RGB")

    # Subtle paper grain
    rng = random.Random(42)
    for _ in range(2600):
        x, y = rng.randrange(W), rng.randrange(H)
        shade = rng.choice((214, 226, 238))
        draw.point((x, y), fill=(shade, shade - 8, shade - 22))

    # Masthead rules
    draw.rectangle([80, 96, 1120, 100], fill=INK)
    draw.rectangle([80, 106, 1120, 108], fill=INK)

    draw.text((80, 150), "TYLER'S CORNER", font=font("georgiab.ttf", 108), fill=INK)
    draw.text((82, 300), "VOL. 01 — THE STUDENT EDITION", font=font("consolab.ttf", 30), fill=RED)
    draw.text(
        (82, 356),
        "Essays · Projects · Notes — building, learning and growing.",
        font=font("consola.ttf", 30),
        fill=INK_SOFT,
    )

    draw.rectangle([80, 470, 1120, 472], fill=INK)
    draw.text((82, 500), "ISSN 2994-0756", font=font("consola.ttf", 24), fill=INK_SOFT)
    draw.text((1018, 500), "shinetyler.github.io", font=font("consola.ttf", 24), fill=INK_SOFT)

    out_path = OUT / "og-cover.png"
    img.save(out_path, "PNG", optimize=True)
    print("wrote", out_path)


if __name__ == "__main__":
    main()
