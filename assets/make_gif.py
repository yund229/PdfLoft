"""Render the README demo GIF: a terminal typing pdfloft commands. Pure-PIL encoding."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 720, 460
DESK = (32, 35, 44)
TERM = (16, 18, 24)
TERM_BAR = (45, 48, 58)
GREEN = (80, 220, 120)
WHITE = (220, 224, 232)
GRAY = (130, 136, 148)
ACCENT = (90, 160, 255)


def load_font(size=16):
    for n in ("consola.ttf", "Courier New"):
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_terminal(lines, cursor=True):
    img = Image.new("RGB", (W, H), DESK)
    d = ImageDraw.Draw(img)
    tx0, ty0, tx1, ty1 = 60, 40, 660, 380
    d.rounded_rectangle((tx0, ty0, tx1, ty1), 10, fill=TERM, outline=(70, 75, 90))
    d.rectangle((tx0, ty0, tx1, ty0 + 30), fill=TERM_BAR)
    d.text((tx0 + 14, ty0 + 8), "cmd — pdfloft", fill=GRAY, font=load_font(13))
    for c in ("red", "yellow", "green"):
        x = tx1 - 60 + ("red yellow green".split().index(c)) * 18
        d.ellipse((x, ty0 + 10, x + 10, ty0 + 20), fill=c)
    f = load_font(16)
    y = ty0 + 46
    for line, color in lines:
        d.text((tx0 + 16, y), line, fill=color, font=f)
        y += 27
    if cursor:
        d.rectangle((tx0 + 16, y, tx0 + 26, y + 18), fill=WHITE)
    return img


def main():
    frames = []
    for i in range(1, 15):
        typed = "$ pdfloft merge report1.pdf report2.pdf -o full.pdf"[:i]
        frames.append(draw_terminal([(typed, WHITE)]))
    for done in (3, 6):
        filled = "#" * round(24 * done / 6)
        frames.append(draw_terminal([
            ("$ pdfloft merge report1.pdf report2.pdf -o full.pdf", WHITE),
            (f"[{filled:<24}] {done}/6 pages", ACCENT),
        ]))
    for _ in range(4):
        frames.append(draw_terminal([
            ("$ pdfloft merge report1.pdf report2.pdf -o full.pdf", WHITE),
            ("merged 2 PDFs -> full.pdf", GREEN),
            ("$ pdfloft split full.pdf", WHITE),
            ("split into 6 files in full_pages", GREEN),
            ("$ pdfloft info full.pdf", WHITE),
            ('{"pages": 6, "encrypted": false}', ACCENT),
        ], cursor=False))
    out = Path(__file__).resolve().parent / "demo.gif"
    pal = [f.convert("P", palette=Image.ADAPTIVE, colors=128) for f in frames]
    pal[0].save(out, save_all=True, append_images=pal[1:], duration=125, loop=0, optimize=True)
    print(f"demo -> {out} ({out.stat().st_size / 1024:.0f} KiB, {len(frames)} frames)")


if __name__ == "__main__":
    main()
