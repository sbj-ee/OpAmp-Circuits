"""Shared drawing helpers for the generic op-amp circuit set.

All coordinates are absolute schemdraw units. Style is set once here so the
88 drawings are consistent.
"""
import math
import io
import schemdraw
import schemdraw.elements as elm
from schemdraw.segments import Segment, SegmentCircle
import matplotlib
matplotlib.rcParams['mathtext.fontset'] = 'dejavusans'
matplotlib.rcParams['svg.fonttype'] = 'path'
matplotlib.rcParams['svg.hashsalt'] = 'opamp-generic'   # deterministic ids
matplotlib.rcParams['svg.id'] = None

INK = '#1b2733'
FS = 11          # component labels
FS_TITLE = 14
FS_NOTE = 11
from trim import trim_png, finish_svg
BG = '#ffffff'   # drawing background (opaque white)
schemdraw.config(lw=1.3, fontsize=FS, color=INK, font='DejaVu Sans', unit=2.5,
                 inches_per_unit=0.5, margin=0.3)
schemdraw.use('matplotlib')


def P(x, y):
    return (float(x), float(y))


class Sch:
    """Thin wrapper around a schemdraw Drawing with absolute-coordinate helpers."""

    def __init__(self):
        self.d = schemdraw.Drawing(show=False)
        self.counts = {'op amp': 0, 'transistor': 0, 'diode': 0}

    # ---- primitives -------------------------------------------------
    def add(self, e):
        return self.d.add(e)

    def wire(self, *pts, arrow=None):
        for a, b in zip(pts[:-1], pts[1:]):
            if a == b:
                continue
            self.add(elm.Line().at(a).to(b))

    def dot(self, *pts):
        for p in pts:
            self.add(elm.Dot(radius=0.09).at(p))

    def term(self, p, text=None, side='left', ofs=0.25):
        """Open terminal circle at p with an optional label."""
        self.add(elm.Dot(open=True, radius=0.11).at(p))
        if text:
            x, y = p
            if side == 'left':
                self.text((x - ofs, y), text, ha='right')
            elif side == 'right':
                self.text((x + ofs, y), text, ha='left')
            elif side == 'top':
                self.text((x, y + ofs), text, va='bottom')
            elif side == 'bottom':
                self.text((x, y - ofs), text, va='top')

    def text(self, p, s, ha='center', va='center', fs=FS, color=INK):
        self.add(elm.Label().at(p).label(s, halign=ha, valign=va, fontsize=fs, color=color))

    def gnd(self, p, lead=0.0):
        x, y = p
        if lead:
            self.wire(p, (x, y - lead))
        self.add(elm.Ground(lead=False).theta(0).at((x, y - lead)))

    def rail(self, p, text, up=True, lead=0.5):
        """Supply connection: short lead to an open terminal and label."""
        x, y = p
        q = (x, y + lead) if up else (x, y - lead)
        self.wire(p, q)
        self.term(q, text, side='top' if up else 'bottom')
        return q

    def arrow(self, a, b):
        self.add(elm.Arrow(headwidth=0.18, headlength=0.25).at(a).to(b))

    # ---- two-terminal parts ----------------------------------------
    def _two(self, cls, a, b, label=None, loc='top', ofst=None, flip=False, reverse=False, **kw):
        e = cls(**kw).at(a).to(b)
        if flip:
            e = e.flip()
        if reverse:
            e = e.reverse()
        e = self.add(e)
        if label:
            wide = cls in (elm.Diode, elm.Zener, elm.Photodiode, elm.Lamp, elm.Crystal, elm.Switch)
            self.plabel(a, b, label, loc, ofst, wide)
        return e

    def plabel(self, a, b, label, loc='top', ofst=None, wide=False):
        """Place a part label beside the midpoint of a two-terminal part."""
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        vert = abs(a[0] - b[0]) < 1e-6
        o = (0.68 if wide else 0.5) if ofst is None else ofst
        if vert:
            if loc in ('left', 'bottom'):
                self.text((mx - o, my), label, ha='right')
            else:
                self.text((mx + o, my), label, ha='left')
        else:
            if loc in ('bottom', 'right'):
                self.text((mx, my - o), label, va='top')
            else:
                self.text((mx, my + o), label, va='bottom')

    def R(self, a, b, label=None, loc='top', **kw):
        return self._two(elm.Resistor, a, b, label, loc, **kw)

    def C(self, a, b, label=None, loc='top', **kw):
        return self._two(elm.Capacitor, a, b, label, loc, **kw)

    def Cpol(self, a, b, label=None, loc='top', **kw):
        """Polarized capacitor; the '+' plate is the one at b (end point)."""
        e = self._two(elm.Capacitor, a, b, label, loc, **kw)
        ax, ay = a; bx, by = b
        L = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / L, (by - ay) / L
        mx, my = (ax + bx) / 2, (ay + by) / 2
        vert = abs(ax - bx) < 1e-6
        if vert:
            side = 1 if loc in ('left', 'bottom') else -1     # opposite the label
            px, py = mx + side * 0.45, my + uy * 0.42
        else:
            side = -1 if loc in ('top', 'left') else 1
            px, py = mx + ux * 0.42, my + side * 0.45
        self.text((px, py), '+', fs=12)
        return e

    def D(self, a, b, label=None, loc='top', **kw):
        """Diode, anode at a, cathode at b."""
        self.counts['diode'] += 1
        return self._two(elm.Diode, a, b, label, loc, **kw)

    def Z(self, a, b, label=None, loc='top', **kw):
        """Zener, anode at a, cathode at b."""
        self.counts['diode'] += 1
        return self._two(elm.Zener, a, b, label, loc, **kw)

    def PD(self, a, b, label=None, loc='top', **kw):
        """Photodiode, anode at a, cathode at b."""
        self.counts['diode'] += 1
        return self._two(elm.Photodiode, a, b, label, loc, **kw)

    def SW(self, a, b, label=None, loc='top', **kw):
        return self._two(elm.Switch, a, b, label, loc, **kw)

    def RV(self, a, b, label=None, loc='top', **kw):
        """Adjustable (variable) resistor: resistor with a diagonal arrow."""
        e = self._two(elm.Resistor, a, b, label, loc, **kw)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        self.add(elm.Arrow(headwidth=0.16, headlength=0.22, lw=1.1)
                 .at((mx - 0.55, my - 0.55)).to((mx + 0.6, my + 0.6)))
        return e

    def RT(self, a, b, label=None, loc='top', **kw):
        """Thermistor: zigzag resistor with the standard 'hockey-stick' line."""
        e = self._two(elm.Resistor, a, b, label, loc, **kw)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        vert = abs(a[0] - b[0]) < 1e-6
        if vert:
            p0, p1 = (mx - 0.5, my - 0.6), (mx + 0.5, my + 0.6)
            tail = (p0[0] - 0.3, p0[1])
        else:
            p0, p1 = (mx - 0.6, my - 0.5), (mx + 0.6, my + 0.5)
            tail = (p0[0] - 0.3, p0[1])
        self.add(elm.Line(lw=1.1).at(tail).to(p0))
        self.add(elm.Line(lw=1.1).at(p0).to(p1))
        return e

    def POT(self, a, b, label=None, loc='bottom', tap_side='left'):
        """Potentiometer from a to b; returns wiper point (arrow tip at the
        resistor body). Wiper arrow comes from tap_side."""
        e = self._two(elm.Resistor, a, b, label, loc)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        vert = abs(a[0] - b[0]) < 1e-6
        if vert:
            s = -1 if tap_side == 'left' else 1
            tip = (mx + s * 0.3, my)
            base = (mx + s * 1.0, my)
        else:
            s = 1 if tap_side == 'top' else -1
            tip = (mx, my + s * 0.3)
            base = (mx, my + s * 1.0)
        self.add(elm.Arrow(headwidth=0.18, headlength=0.25).at(base).to(tip))
        return base

    def lamp(self, a, b, label=None, loc='top', r=0.45):
        """Incandescent lamp: circle with a cross (IEC 60617 lamp)."""
        ax, ay = a; bx, by = b
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
        mx, my = (ax + bx) / 2, (ay + by) / 2
        self.wire(a, (mx - ux * r, my - uy * r)); self.wire((mx + ux * r, my + uy * r), b)
        self.circle((mx, my), r)
        k = r * 0.7071
        self.add(elm.Line().at((mx - k, my - k)).to((mx + k, my + k)))
        self.add(elm.Line().at((mx - k, my + k)).to((mx + k, my - k)))
        if label:
            self.plabel(a, b, label, loc, 0.75)

    def xtal(self, a, b, label=None, loc='top'):
        return self._two(elm.Crystal, a, b, label, loc)

    def circle(self, c, r):
        e = elm.Element()
        e.segments.append(SegmentCircle((0, 0), r, fill=False))
        self.add(e.at(c))

    # ---- op amp ------------------------------------------------------
    def opamp(self, inv, label=None, plus_top=False, left=False, scale=1.0):
        """Place an op amp so its (-) input sits at `inv`.

        plus_top: draw (+) on top (then `inv` is the lower input).
        left: op amp points left.
        Returns the element; use .in1 (-), .in2 (+), .out.
        """
        self.counts['op amp'] += 1
        e = elm.Opamp(leads=False)
        e = e.left() if left else e.right()
        if scale != 1.0:
            e = e.scale(scale)
        if plus_top != left:
            e = e.flip()
        e = e.anchor('in1').at(inv)
        e = self.add(e)
        if label:
            c = e.center
            self.text((c[0] + (0.15 if not left else -0.15), c[1]), label, fs=10)
        return e

    # ---- three-terminal parts ---------------------------------------
    def npn(self, base, label=None, flip=False, left=False, circle=False, theta=None, lloc=None, anchor='base'):
        self.counts['transistor'] += 1
        e = elm.BjtNpn(circle=circle)
        e = e.theta(0 if theta is None else theta)
        if left:
            e = e.reverse()
        if flip:
            e = e.flip()
        e = e.anchor(anchor).at(base)
        if label:
            e = e.label(label, loc=lloc or ('right' if not left else 'left'))
        return self.add(e)

    def pnp(self, base, label=None, flip=False, left=False, circle=False, theta=None, lloc=None, anchor='base'):
        self.counts['transistor'] += 1
        e = elm.BjtPnp(circle=circle)
        e = e.theta(0 if theta is None else theta)
        if left:
            e = e.reverse()
        if flip:
            e = e.flip()
        e = e.anchor(anchor).at(base)
        if label:
            e = e.label(label, loc=lloc or ('right' if not left else 'left'))
        return self.add(e)

    def nfet(self, gate, label=None, left=False, flip=False, kind='mos', theta=None, lloc=None, anchor='gate'):
        self.counts['transistor'] += 1
        cls = elm.AnalogNFet if kind == 'mos' else elm.JFetN
        e = cls()
        e = e.theta(0 if theta is None else theta)
        if left:
            e = e.reverse()
        if flip:
            e = e.flip()
        e = e.anchor(anchor).at(gate)
        if label:
            e = e.label(label, loc=lloc or ('right' if not left else 'left'))
        return self.add(e)

    def pfet(self, gate, label=None, left=False, flip=False, kind='mos', theta=None, lloc=None, anchor='gate'):
        self.counts['transistor'] += 1
        cls = elm.AnalogPFet if kind == 'mos' else elm.JFetP
        e = cls()
        e = e.theta(0 if theta is None else theta)
        if left:
            e = e.reverse()
        if flip:
            e = e.flip()
        e = e.anchor(anchor).at(gate)
        if label:
            e = e.label(label, loc=lloc or ('right' if not left else 'left'))
        return self.add(e)

    def loop(self, a, b, y, part='R', label=None, loc='top', dots=True, **kw):
        """Wire from a vertically to y, part horizontally, back down to b."""
        a2, b2 = (a[0], y), (b[0], y)
        self.wire(a, a2)
        getattr(self, part)(a2, b2, label, loc, **kw)
        self.wire(b2, b)
        if dots:
            self.dot(a, b)

    def Zbox(self, a, b, label=None, loc='top'):
        return self._two(elm.ResistorIEC, a, b, label, loc)

    def pwr(self, u, top=None, bot=None, lead=0.45):
        """Supply pins: top/bot are a label string, 'gnd', or None."""
        a, b = u.vd, u.vs
        hi, lo = (a, b) if a[1] > b[1] else (b, a)
        if top == 'gnd':
            pass
        elif top:
            self.rail(hi, top, up=True, lead=lead)
        if bot == 'gnd':
            self.gnd(lo, lead=lead)
        elif bot:
            self.rail(lo, bot, up=False, lead=lead)

    def mosfet(self, center, kind='n', orient='gate_left', swap=False, label=None, lpos=None, body='source'):
        """Standard enhancement MOSFET, arrow on the body.

        orient: gate_left | gate_right | gate_up | gate_down.  swap exchanges
        drain and source.  body='source' ties the body to the source (3-terminal);
        body='out' draws a separate substrate lead (4-terminal) on the side opposite
        the gate, returned as 'body'.  Returns dict with 'gate', 'drain', 'source'.
        """
        self.counts['transistor'] += 1
        cx, cy = center
        def T(p):
            x, y = p
            if swap:
                y = -y
            if orient == 'gate_right':
                x = -x
            elif orient == 'gate_up':
                x, y = y, -x
            elif orient == 'gate_down':
                x, y = -y, x
            return (cx + x, cy + y)
        L = lambda *pts: self.wire(*[T(p) for p in pts])
        L((-1.0, 0), (-0.45, 0))
        L((-0.45, -0.55), (-0.45, 0.55))
        for a, b in ((0.35, 0.65), (-0.15, 0.15), (-0.65, -0.35)):
            L((-0.25, a), (-0.25, b))
        L((-0.25, 0.5), (0.25, 0.5), (0.25, 1.0))
        L((-0.25, -0.5), (0.25, -0.5), (0.25, -1.0))
        if body == 'source':
            L((0.25, 0.0), (0.25, -0.5))
        else:
            L((0.25, 0.0), (0.9, 0.0))
        if kind == 'n':
            self.add(elm.Arrow(headwidth=0.2, headlength=0.22).at(T((0.25, 0))).to(T((-0.25, 0))))
        else:
            self.add(elm.Line().at(T((-0.25, 0))).to(T((-0.05, 0))))
            self.add(elm.Arrow(headwidth=0.2, headlength=0.22).at(T((-0.05, 0))).to(T((0.25, 0))))
        pts = dict(gate=T((-1.0, 0)), drain=T((0.25, 1.0)), source=T((0.25, -1.0)), center=(cx, cy))
        if body != 'source':
            pts['body'] = T((0.9, 0.0))
        if label:
            lp = lpos or T((0.65, 0))
            self.text(lp, label, ha='left' if lp[0] >= cx else 'right')
        return pts

    # ---- output -----------------------------------------------------
    def finish(self, path_noext, title, notes=(), title_gap=0.9):
        from matplotlib.textpath import TextPath
        from matplotlib.font_manager import FontProperties
        fp = FontProperties(family='DejaVu Sans')
        def width_units(txt, fs):
            try:
                ext = TextPath((0, 0), txt, size=fs, prop=fp).get_extents()
                return ext.width / 72.0 / 0.5
            except Exception:
                return len(txt) * fs * 0.6 / 72.0 / 0.5
        d = self.d
        bb = d.get_bbox()
        cx = (bb.xmin + bb.xmax) / 2
        ytitle = bb.ymax + title_gap
        self.text((cx, ytitle), title, fs=FS_TITLE, va='bottom')
        half = width_units(title, FS_TITLE) / 2
        y = bb.ymin - 1.0
        for n in notes:
            if n is None:
                y -= 0.4
                continue
            tall = any(t in n for t in (r'\frac', r'\dfrac', r'\sqrt', r'\int'))
            if tall:
                y -= 0.35
            self.text((cx, y), n, fs=FS_NOTE, va='center')
            half = max(half, width_units(n, FS_NOTE) / 2)
            y -= 1.15 if tall else 0.75
        # invisible extent markers so wide text is never clipped
        pad = 0.4
        for xx in (cx - half - pad, cx + half + pad):
            self.add(elm.Line(color='none').at((xx, ytitle + 0.9)).to((xx, y + 0.2)))
        # opaque white background (figure + axes), never transparent
        d.draw(show=False)
        fig = d.fig.getfig()
        fig.set_facecolor(BG); fig.patch.set_alpha(1.0)
        d.fig.ax.set_facecolor(BG)
        fig.subplots_adjust(0, 0, 1, 1)
        kw = dict(bbox_inches='tight', pad_inches=0, transparent=False, facecolor=BG,
                  bbox_extra_artists=d.fig.ax.get_default_bbox_extra_artists())
        # PNG: 300 dpi RGB on white, trimmed; the same crop box is applied to the SVG
        fig.savefig(path_noext + '.png', dpi=300, **kw)
        box = trim_png(path_noext + '.png')
        desc = describe(title, self.counts)
        buf = io.StringIO()
        fig.savefig(buf, format='svg', metadata={'Title': title, 'Description': desc}, **kw)
        svg = finish_svg(buf.getvalue(), box, title, desc)
        with open(path_noext + '.svg', 'w', encoding='utf-8') as f:
            f.write(svg)


def describe(title, counts):
    """One-line accessible description of a drawing."""
    parts = []
    for k, v in counts.items():
        if v:
            parts.append(f'{v} {k}' + ('s' if v > 1 else ''))
    body = ', '.join(parts[:-1]) + (' and ' if len(parts) > 1 else '') + parts[-1] if parts else 'passive parts'
    return (f'{title}: schematic diagram using {body}, drawn with generic symbols; '
            'the text below the drawing gives the design equations and notes.')


def X(p, dx=0.0, dy=0.0):
    return (float(p[0]) + dx, float(p[1]) + dy)

VIN = r'$V_{\mathrm{IN}}$'
VOUT = r'$V_{\mathrm{OUT}}$'
def sub(base, s):
    return r'$%s_{\mathrm{%s}}$' % (base, s)
