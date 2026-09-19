#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Composes the README images out of the example PDFs. Run through build-previews.sh."""
import os, subprocess, tempfile
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(HERE, "..", "examples")
BG, CARD, INK, MUTED, ACCENT = "#2E3440", "#3B4252", "#ECEFF4", "#A2ADC0", "#60c4de"
FONT = "/System/Library/Fonts/Supplemental/PTSans.ttc"
FALLBACK = "/System/Library/Fonts/Supplemental/Arial.ttf"
CJK = "/System/Library/Fonts/Hiragino Sans GB.ttc"   # PT Sans has no Han glyphs


def font(size, bold=False, cjk=False):
    paths = ([CJK] if cjk else []) + [FONT, FALLBACK]
    for path in paths:
        try:
            return ImageFont.truetype(path, size, index=1 if (bold and path == FONT) else 0)
        except OSError:
            continue
    return ImageFont.load_default()


def page(pdf, w, y=0, h=None, dpi=150):
    """Renders a crop of the first page at the given pixel width."""
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["pdftoppm", "-png", "-r", str(dpi), "-f", "1", "-l", "1", pdf,
                        os.path.join(d, "p")], check=True)
        im = Image.open(os.path.join(d, os.listdir(d)[0])).convert("RGB")
    im = im.crop((0, y, im.width, min(y + (h or im.height), im.height)))
    return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def rounded(im, r=10):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], r, fill=255)
    out = Image.new("RGB", im.size, BG)
    out.paste(im, (0, 0), mask)
    return out


def languages():
    """Three languages side by side — the point of the skill in one picture."""
    cols = [("en", "English"), ("ru", "Русский"), ("zh", "中文")]
    cw, gap, pad, top = 340, 26, 30, 64
    shots = [rounded(page(os.path.join(EX, f"demo-{c}.pdf"), cw, y=90, h=1900)) for c, _ in cols]
    ch = max(s.height for s in shots)
    W = pad * 2 + cw * 3 + gap * 2
    im = Image.new("RGB", (W, top + ch + pad), BG)
    d = ImageDraw.Draw(im)
    for i, ((code, label), shot) in enumerate(zip(cols, shots)):
        x = pad + i * (cw + gap)
        f = font(21, bold=True, cjk=(code == "zh"))
        d.text((x + 2, 26), label, font=f, fill=INK)
        d.text((x + 2 + d.textlength(label, font=f) + 10, 30),
               f'lang="{code}"', font=font(16), fill=MUTED)
        im.paste(shot, (x, top))
    im.save(os.path.join(HERE, "languages.png"))
    return im.size


def showcase():
    """A strip of the demo report: cover, charts, tables."""
    src = os.path.join(EX, "example-dark.pdf")
    bands = [(0, 1500), (3400, 1500), (7100, 1500)]
    cw, gap, pad = 340, 26, 30
    shots = [rounded(page(src, cw, y=y, h=h)) for y, h in bands]
    ch = max(s.height for s in shots)
    W = pad * 2 + cw * 3 + gap * 2
    im = Image.new("RGB", (W, ch + pad * 2), BG)
    for i, shot in enumerate(shots):
        im.paste(shot, (pad + i * (cw + gap), pad))
    im.save(os.path.join(HERE, "showcase.png"))
    return im.size


if __name__ == "__main__":
    print("languages.png", languages())
    print("showcase.png", showcase())
