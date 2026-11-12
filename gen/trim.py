"""Crop and finish the generator's PNG and SVG output (called from lib.Sch.finish).

PNG: trimmed to the drawing plus a 0.15 in margin, saved RGB (no alpha) at 300 DPI on white.
SVG: built in memory by the generator, then given the same crop box (size rounded up to
     whole points), a white <rect> exactly covering the viewBox, and accessible
     <title>/<desc> elements referenced by role="img" / aria-labelledby, before it is written.
"""
import math, re
from xml.sax.saxutils import escape
from PIL import Image, ImageChops
PAD = 45  # px at 300 dpi = 0.15 in
BG = (255, 255, 255)
DPI = 300


def trim_png(png, dpi=DPI):
    """Trim a white-background PNG in place; return the crop box in pixels."""
    im = Image.open(png)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA')
        flat = Image.new('RGBA', im.size, BG + (255,)); flat.alpha_composite(im)
        im = flat.convert('RGB')
    else:
        im = im.convert('RGB')
    W, H = im.size
    x0, y0, x1, y1 = ImageChops.difference(im, Image.new('RGB', im.size, BG)).getbbox()
    box = (max(0, x0 - PAD), max(0, y0 - PAD), min(W, x1 + PAD), min(H, y1 + PAD))
    im.crop(box).save(png, dpi=(dpi, dpi))
    return box


def finish_svg(txt, box, title, desc, dpi=DPI):
    """Apply crop box, white background and title/desc to matplotlib SVG text."""
    x0, y0, x1, y1 = box
    k = 72.0 / dpi
    vx, vy = x0 * k, y0 * k
    # whole-point size so 72-dpi rasterizers get no partially covered edge pixel;
    # the extra (< 1 pt) sliver at right/bottom is covered by the white rect
    vw, vh = math.ceil((x1 - x0) * k - 1e-6), math.ceil((y1 - y0) * k - 1e-6)
    a11y = ' role="img" aria-labelledby="svg-title svg-desc"'
    txt, n = re.subn(r'width="[0-9.]+pt" height="[0-9.]+pt" viewBox="[^"]*"',
                     f'width="{vw:.4f}pt" height="{vh:.4f}pt" viewBox="{vx:.4f} {vy:.4f} {vw:.4f} {vh:.4f}"{a11y}',
                     txt, count=1)
    assert n == 1, 'svg header not found'
    head = (f'\n <title id="svg-title">{escape(title)}</title>'
            f'\n <desc id="svg-desc">{escape(desc)}</desc>')
    # matplotlib writes <title> from the Title metadata; give it an id and add <desc>
    txt = re.sub(r'\n <title>[^<]*</title>', '', txt, count=1)
    txt, n = re.subn(r'(<svg\b[^>]*>)', lambda m: m.group(1) + head, txt, count=1)
    assert n == 1
    rect = f'\n <rect id="background" x="{vx:.4f}" y="{vy:.4f}" width="{vw:.4f}" height="{vh:.4f}" fill="#ffffff"/>'
    if '</defs>' in txt:
        txt = txt.replace('</defs>', '</defs>' + rect, 1)
    else:
        txt = txt.replace('</desc>', '</desc>' + rect, 1)
    return txt
