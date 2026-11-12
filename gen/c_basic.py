from lib import Sch, X, VIN, VOUT, sub
from reg import circuit
B = 'Basic Circuits'
M = lambda s: '$' + s + '$'


def out_term(s, o, dx=1.6, label=VOUT, dot=True, jx=0.6):
    """Wire from op-amp output to an output terminal; returns junction point."""
    j = X(o, jx)
    s.wire(o, X(o, dx))
    s.term(X(o, dx), label, 'right')
    if dot:
        s.dot(j)
    return j


@circuit(1, B, 'Inverting Amplifier')
def c01():
    s = Sch()
    u = s.opamp((6, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    s.term((0, n[1]), VIN); s.R((0, n[1]), j, 'R1'); s.wire(j, n)
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 2.0, 'R', 'R2')
    s.wire(p, X(p, -0.7)); s.gnd(X(p, -0.7), lead=0.5)
    return s, [r'$V_{\mathrm{OUT}} = -\dfrac{R2}{R1}\,V_{\mathrm{IN}}$', r'Input resistance $= R1$']


@circuit(2, B, 'Non-Inverting Amplifier')
def c02():
    s = Sch()
    u = s.opamp((4, 0), 'U1', plus_top=True); n, p, o = u.in1, u.in2, u.out   # (+) on top, (-) below
    s.term((0, p[1]), VIN); s.wire((0, p[1]), p)
    j = X(n, -0.7); s.wire(n, j)
    jo = out_term(s, o)
    yb = n[1] - 1.6
    s.wire(j, (j[0], yb)); s.R((j[0], yb), (jo[0], yb), 'R2', loc='bottom'); s.wire((jo[0], yb), jo)
    s.dot((j[0], yb))
    s.R((j[0], yb), (j[0], yb - 2.6), 'R1', loc='left'); s.gnd((j[0], yb - 2.6))
    return s, [r'$V_{\mathrm{OUT}} = \left(1 + \dfrac{R2}{R1}\right) V_{\mathrm{IN}}$']


@circuit(3, B, 'Four-Resistor Difference Amplifier')
def c03():
    s = Sch()
    u = s.opamp((6, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    jn = X(n, -0.7); jp = X(p, -1.4)
    s.term((0, n[1]), sub('V', '1')); s.R((0, n[1]), jn, 'R1'); s.wire(jn, n)
    s.term((0, p[1]), sub('V', '2')); s.R((0, p[1]), jp, 'R3', loc='bottom'); s.wire(jp, p); s.dot(jp)
    jo = out_term(s, o)
    s.loop(jn, jo, n[1] + 2.0, 'R', 'R2')
    s.R(jp, X(jp, 0, -2.6), 'R4', loc='right'); s.gnd(X(jp, 0, -2.6))
    return s, [r'$V_{\mathrm{OUT}} = \dfrac{R4}{R3+R4}\left(1+\dfrac{R2}{R1}\right)V_2 - \dfrac{R2}{R1}\,V_1$',
               r'With $R3 = R1$ and $R4 = R2$:   $V_{\mathrm{OUT}} = \dfrac{R2}{R1}\,(V_2 - V_1)$',
               'Common-mode rejection depends on matching R2/R1 to R4/R3']


@circuit(4, B, 'Inverting Summer')
def c04():
    s = Sch()
    u = s.opamp((7.5, -1.0), 'U1'); n, p, o = u.in1, u.in2, u.out
    bx = n[0] - 1.0
    ys = [n[1] + 3.0, n[1] + 1.5, n[1]]
    for i, y in enumerate(ys):
        s.term((0, y), sub('V', str(i + 1))); s.R((0, y), (bx, y), 'R%d' % (i + 1))
    s.wire((bx, ys[0]), (bx, n[1])); s.wire((bx, n[1]), n); s.dot((bx, ys[0]), (bx, ys[1]), (bx, n[1]))
    jo = out_term(s, o)
    s.wire((bx, ys[0]), (bx, ys[0] + 1.2)); s.R((bx, ys[0] + 1.2), (jo[0], ys[0] + 1.2), 'R4'); s.wire((jo[0], ys[0] + 1.2), jo)
    s.wire(p, X(p, -0.7)); s.R(X(p, -0.7), X(p, -0.7, -2.5), 'R5', loc='left'); s.gnd(X(p, -0.7, -2.5))
    return s, [r'$V_{\mathrm{OUT}} = -R4\left(\dfrac{V_1}{R1} + \dfrac{V_2}{R2} + \dfrac{V_3}{R3}\right)$',
               r'Optional R5 $\approx$ R1 $\parallel$ R2 $\parallel$ R3 $\parallel$ R4 equalizes the resistance seen by each input,',
               'so bias currents cause less output offset']


@circuit(5, B, 'Non-Inverting Summer')
def c05():
    s = Sch()
    u = s.opamp((6, 0), 'U1', plus_top=True); n, p, o = u.in1, u.in2, u.out
    jp = X(p, -1.0)
    s.term((0, p[1] + 1.2), sub('V', '1')); s.R((0, p[1] + 1.2), (jp[0], p[1] + 1.2), 'R1')
    s.term((0, p[1]), sub('V', '2')); s.R((0, p[1]), jp, 'R2', loc='bottom')
    s.wire((jp[0], p[1] + 1.2), jp); s.wire(jp, p); s.dot(jp)
    j = X(n, -0.7); s.wire(n, j)
    jo = out_term(s, o)
    yb = n[1] - 1.6
    s.wire(j, (j[0], yb)); s.R((j[0], yb), (jo[0], yb), 'R4', loc='bottom'); s.wire((jo[0], yb), jo); s.dot((j[0], yb))
    s.R((j[0], yb), (j[0], yb - 2.5), 'R3', loc='left'); s.gnd((j[0], yb - 2.5))
    return s, [r'$V_{\mathrm{OUT}} = \left(1+\dfrac{R4}{R3}\right)\dfrac{R2\,V_1 + R1\,V_2}{R1+R2}$',
               r'With $R1 = R2$ and $R3 = R4$:   $V_{\mathrm{OUT}} = V_1 + V_2$',
               'Keep source resistances small compared with R1 and R2']


@circuit(6, B, 'High-Resistance Inverting Amplifier')
def c06():
    s = Sch()
    u = s.opamp((6, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    s.term((0, n[1]), VIN); s.R((0, n[1]), j, 'R1'); s.wire(j, n)
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 1.8, 'R', 'R2')
    s.wire((j[0], n[1] + 1.8), (j[0], n[1] + 3.4)); s.C((j[0], n[1] + 3.4), (jo[0], n[1] + 3.4), 'C1')
    s.wire((jo[0], n[1] + 3.4), (jo[0], n[1] + 1.8)); s.dot((j[0], n[1] + 1.8), (jo[0], n[1] + 1.8))
    s.wire(p, X(p, -0.7)); s.R(X(p, -0.7), X(p, -0.7, -2.5), 'R3', loc='left'); s.gnd(X(p, -0.7, -2.5))
    return s, [r'$V_{\mathrm{OUT}} = -\dfrac{R2}{R1}\,V_{\mathrm{IN}}$',
               'R1 and R2 can be in the megohm range when U1 has FET inputs (very low bias current)',
               'A few picofarads at C1 cancel stray capacitance at the inverting input and keep the loop stable',
               r'R3 $\approx$ R1 $\parallel$ R2 (optional) reduces offset from bias current']


@circuit(7, B, 'Buffered Inverting Amplifier')
def c07():
    s = Sch()
    u1 = s.opamp((1.5, -1.25), 'U1', plus_top=True); p1, n1, o1 = u1.in2, u1.in1, u1.out   # + on top
    s.term((0, p1[1]), VIN); s.wire((0, p1[1]), p1)
    jf = X(n1, -0.6); s.wire(n1, jf); s.wire(jf, (jf[0], n1[1] - 1.0)); s.wire((jf[0], n1[1] - 1.0), (o1[0] + 0.5, n1[1] - 1.0))
    s.wire((o1[0] + 0.5, n1[1] - 1.0), (o1[0] + 0.5, o1[1])); s.dot((o1[0] + 0.5, o1[1]))
    u2 = s.opamp((o1[0] + 5.0, o1[1]), 'U2'); n, p, o = u2.in1, u2.in2, u2.out
    j = X(n, -0.7)
    s.R(o1, j, 'R1'); s.wire(j, n)
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 1.8, 'R', 'R2')
    s.wire((j[0], n[1] + 1.8), (j[0], n[1] + 3.4)); s.C((j[0], n[1] + 3.4), (jo[0], n[1] + 3.4), 'C1')
    s.wire((jo[0], n[1] + 3.4), (jo[0], n[1] + 1.8)); s.dot((j[0], n[1] + 1.8), (jo[0], n[1] + 1.8))
    s.wire(p, X(p, -0.7)); s.gnd(X(p, -0.7), lead=0.5)
    return s, [r'$V_{\mathrm{OUT}} = -\dfrac{R2}{R1}\,V_{\mathrm{IN}}$',
               'U1 (follower) gives a very high input impedance; U2 sets the gain',
               'Pick a fast, unity-gain-stable part for U2; small C1 sets the closed-loop bandwidth']


@circuit(8, B, 'AC-Coupled Non-Inverting Amplifier')
def c08():
    s = Sch()
    u = s.opamp((7, 0), 'U1', plus_top=True); n, p, o = u.in1, u.in2, u.out
    jp = X(p, -2.2)
    s.term((0, p[1]), VIN); s.C((0, p[1]), jp, 'C1'); s.wire(jp, p); s.dot(jp)
    s.R(jp, X(jp, 0, -3.0), 'R1', loc='left'); s.gnd(X(jp, 0, -3.0))
    j = X(n, -0.6); s.wire(n, j)
    jo = out_term(s, o)
    yb = n[1] - 1.6
    s.wire(j, (j[0], yb)); s.R((j[0], yb), (jo[0], yb), 'R3', loc='bottom'); s.wire((jo[0], yb), jo); s.dot((j[0], yb))
    s.R((j[0], yb), (j[0], yb - 2.5), 'R2', loc='right'); s.gnd((j[0], yb - 2.5))
    return s, [r'$V_{\mathrm{OUT}} = \left(1+\dfrac{R3}{R2}\right)V_{\mathrm{IN}}$  (mid-band)',
               r'Input resistance $\approx$ R1;  low-frequency corner $f_L = \dfrac{1}{2\pi R1\,C1}$',
               r'R1 $\approx$ R2 $\parallel$ R3 keeps bias-current offset low']


def gnd_plus(s, p, R=None, dx=0.7, L=2.5):
    """Tie (+) input to ground, optionally through resistor R."""
    q = X(p, -dx)
    s.wire(p, q)
    if R:
        s.R(q, X(q, 0, -L), R, loc='left'); s.gnd(X(q, 0, -L))
    else:
        s.gnd(q, lead=0.5)


@circuit(9, B, 'Differentiator with Noise Limiting')
def c09():
    s = Sch()
    u = s.opamp((8.5, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    s.term((0, n[1]), VIN); s.R((0, n[1]), (3.6, n[1]), 'R1'); s.C((3.6, n[1]), j, 'C1'); s.wire(j, n)
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 1.8, 'R', 'R2')
    s.wire((j[0], n[1] + 1.8), (j[0], n[1] + 3.4)); s.C((j[0], n[1] + 3.4), (jo[0], n[1] + 3.4), 'C2')
    s.wire((jo[0], n[1] + 3.4), (jo[0], n[1] + 1.8)); s.dot((j[0], n[1] + 1.8), (jo[0], n[1] + 1.8))
    gnd_plus(s, p, 'R3')
    return s, [r'$V_{\mathrm{OUT}} \approx -R2\,C1\,\dfrac{dV_{\mathrm{IN}}}{dt}$   for $f \ll f_h$',
               r'Unity-gain frequency $f_0 = \dfrac{1}{2\pi R2\,C1}$;   roll-off $f_h = \dfrac{1}{2\pi R1\,C1} = \dfrac{1}{2\pi R2\,C2}$',
               r'Choose $f_0 \ll f_h \ll$ the op-amp gain-bandwidth; R1 and C2 tame high-frequency noise']


@circuit(10, B, 'Resettable Integrator')
def c10():
    s = Sch()
    u = s.opamp((6, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    s.term((0, n[1]), VIN); s.R((0, n[1]), j, 'R1'); s.wire(j, n)
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 1.8, 'C', 'C1')
    y2 = n[1] + 3.4
    s.wire((j[0], n[1] + 1.8), (j[0], y2)); mid = (j[0] + jo[0]) / 2
    s.R((j[0], y2), (mid, y2), 'R2'); s.SW((mid, y2), (jo[0], y2), 'S1')
    s.wire((jo[0], y2), (jo[0], n[1] + 1.8)); s.dot((j[0], n[1] + 1.8), (jo[0], n[1] + 1.8))
    gnd_plus(s, p, 'R3')
    return s, [r'$V_{\mathrm{OUT}} = -\dfrac{1}{R1\,C1}\int V_{\mathrm{IN}}\,dt$',
               r'Unity-gain frequency $f_0 = \dfrac{1}{2\pi R1\,C1}$',
               'Close S1 to reset (R2 limits the discharge current); open S1 to integrate',
               r'R3 $\approx$ R1 (optional) cancels the bias-current error term']


@circuit(11, B, 'Wideband Integrator')
def c11():
    s = Sch()
    u = s.opamp((6, -2.6), 'U1'); n, p, o = u.in1, u.in2, u.out
    a = (n[0] - 1.2, 0)
    s.term((0, 0), VIN); s.R((0, 0), a, 'R1')
    jo = X(o, 0.8)
    s.C(a, (jo[0], 0), 'C1'); s.wire((jo[0], 0), jo); s.dot(a)
    jn = (a[0], n[1])
    s.R(a, (a[0], -1.2 - 0.0), 'R2', loc='left')
    s.wire((a[0], -1.2), jn); s.wire(jn, n); s.dot(jn, (a[0], -1.2))
    s.C((a[0], -1.2), (jo[0], -1.2), 'C2', loc='bottom'); s.dot((jo[0], -1.2))
    s.wire(o, X(o, 1.6)); s.term(X(o, 1.6), VOUT, 'right'); s.dot(jo)
    gnd_plus(s, p)
    return s, [r'$V_{\mathrm{OUT}} \approx -\dfrac{1}{R1\,C1}\int V_{\mathrm{IN}}\,dt$',
               'C1 is the integrating capacitor; R2 with a small C2 isolates the inverting input',
               'from C1 so that a fast op amp stays stable and settles quickly']


@circuit(12, B, 'Transimpedance Amplifier')
def c12():
    s = Sch()
    u = s.opamp((4, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    s.term((0, n[1]), sub('I', 'IN')); s.wire((0, n[1]), j); s.wire(j, n)
    s.arrow((0.7, n[1] + 0.45), (2.0, n[1] + 0.45))
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 1.8, 'R', 'R1')
    gnd_plus(s, p, 'R2')
    return s, [r'$V_{\mathrm{OUT}} = -I_{\mathrm{IN}}\,R1$   (current flowing into the input)',
               r'R2 $\approx$ R1 (optional) cancels the bias-current offset']


@circuit(13, B, 'Single-Supply Inverting Amplifier with Mid-Rail Reference')
def c13():
    s = Sch()
    u = s.opamp((5, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    s.term((0, n[1]), None); s.R((0, n[1]), j, 'R1'); s.wire(j, n)
    jo = X(o, 0.7); s.wire(o, X(o, 1.7)); s.term(X(o, 1.7)); s.dot(jo)
    s.loop(j, jo, n[1] + 2.4, 'R', 'R2')
    yr = p[1] - 3.2
    q = X(p, -0.7); s.wire(p, q); s.R(q, (q[0], yr), 'R3', loc='left'); s.dot((q[0], yr))
    s.term((0, yr), r'$V^{+}/2$'); s.wire((0, yr), (o[0] + 1.7, yr)); s.term((o[0] + 1.7, yr))
    s.pwr(u, r'$V^{+}$', 'gnd')
    s.arrow((0, n[1] - 0.4), (0, yr + 0.35)); s.text((-0.3, (n[1] + yr) / 2), VIN, ha='right')
    s.arrow((o[0] + 1.7, n[1] - 1.0), (o[0] + 1.7, yr + 0.35)); s.text((o[0] + 2.0, (n[1] - 0.6 + yr) / 2), VOUT, ha='left')
    return s, [r'$V_{\mathrm{OUT}} = -\dfrac{R2}{R1}\,V_{\mathrm{IN}}$',
               r'Input and output voltages are measured from the $V^{+}/2$ rail, not from ground',
               r'The $V^{+}/2$ rail must be low impedance (see the buffered mid-supply reference)']


@circuit(14, B, 'Buffered Mid-Supply Reference')
def c14():
    s = Sch()
    u = s.opamp((4, 0), 'U1', plus_top=True); n, p, o = u.in1, u.in2, u.out
    x = 1.2
    s.rail((x, p[1] + 2.6), r'$V^{+}$', lead=0.4)
    s.R((x, p[1] + 2.6), (x, p[1]), 'R1', loc='left'); s.wire((x, p[1]), p); s.dot((x, p[1]))
    s.R((x, p[1]), (x, p[1] - 3.0), 'R2', loc='left'); s.gnd((x, p[1] - 3.0))
    jo = out_term(s, o, label=sub('V', 'REF'))
    s.wire(n, X(n, -0.6)); s.wire(X(n, -0.6), (n[0] - 0.6, n[1] - 1.5)); s.wire((n[0] - 0.6, n[1] - 1.5), (jo[0], n[1] - 1.5)); s.wire((jo[0], n[1] - 1.5), jo)
    s.pwr(u, r'$V^{+}$', 'gnd')
    return s, [r'$V_{\mathrm{REF}} = V^{+}\,\dfrac{R2}{R1+R2}$',
               r'With R1 = R2 the follower supplies a stiff $V^{+}/2$ rail for single-supply circuits',
               'A capacitor across R2 (optional) filters supply noise']


@circuit(15, B, 'Non-Inverting Amplifier with Input-Capacitance Neutralization')
def c15():
    s = Sch()
    u = s.opamp((6, 0), 'U1', plus_top=True); n, p, o = u.in1, u.in2, u.out
    jp = X(p, -2.4)
    s.term((0, p[1]), VIN); s.R((0, p[1]), jp, sub('R', 'S'), loc='bottom'); s.wire(jp, p); s.dot(jp)
    s.C(jp, X(jp, 0, -2.6), sub('C', 'S'), loc='left'); s.gnd(X(jp, 0, -2.6))
    jo = out_term(s, o)
    yt = p[1] + 2.0
    s.wire(jp, (jp[0], yt)); s.C((jp[0], yt), (jo[0], yt), sub('C', 'N')); s.wire((jo[0], yt), jo)
    j = X(n, -0.6); s.wire(n, j)
    yb = n[1] - 1.6
    s.wire(j, (j[0], yb)); s.R((j[0], yb), (jo[0], yb), 'R2', loc='bottom'); s.wire((jo[0], yb), jo); s.dot((j[0], yb))
    s.R((j[0], yb), (j[0], yb - 2.5), 'R1', loc='left'); s.gnd((j[0], yb - 2.5))
    return s, [r'$V_{\mathrm{OUT}} = \left(1+\dfrac{R2}{R1}\right)V_{\mathrm{IN}}$',
               r'$C_{\mathrm{S}}$ is the stray capacitance from (+) to ground; $C_{\mathrm{N}}$ returns a matching charge from the output',
               r'Full cancellation at $C_{\mathrm{N}} = \dfrac{R1}{R2}\,C_{\mathrm{S}}$; use slightly less to avoid peaking']


def follower(s, u, jo, dy=1.5, plus_top=True):
    """Tie (-) to the output junction jo with a loop below (plus_top) or above."""
    n = u.in1
    q = X(n, -0.6)
    y = n[1] - dy if plus_top else n[1] + dy
    s.wire(n, q, (q[0], y), (jo[0], y), jo)


@circuit(16, B, 'Integrator with Bias-Current Cancellation')
def c16():
    s = Sch()
    u = s.opamp((7, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7); a = X(n, -2.0)
    s.term((0, n[1]), VIN); s.R((0, n[1]), a, 'R1', loc='bottom'); s.wire(a, j, n); s.dot(a)
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 1.6, 'C', 'C1')
    # compensating current from a diode-referenced trimmer
    s.R(a, (a[0], n[1] + 4.4), 'R2', loc='left')
    yt = n[1] + 4.4
    pot_x = a[0] + 2.4
    s.wire((a[0], yt), (pot_x - 1.0, yt))
    base = (pot_x - 1.0, yt)
    s.R((pot_x, yt + 1.6), (pot_x, yt - 1.6), None)
    s.arrow(base, (pot_x - 0.3, yt)); s.text((pot_x + 0.45, yt), 'R3', ha='left')
    top = (pot_x, yt + 1.6); bot = (pot_x, yt - 1.6)
    s.dot(top)
    dx = pot_x + 2.2
    s.wire(top, (dx, top[1])); s.D((dx, top[1]), (dx, bot[1]), 'D1', loc='right'); s.wire((dx, bot[1]), bot)
    s.dot((dx, top[1]), bot)
    s.wire(bot, (bot[0], bot[1])); s.gnd((dx, bot[1]))
    s.R(top, (top[0], top[1] + 2.0), 'R4', loc='left'); s.rail((top[0], top[1] + 2.0), r'$V^{+}$', lead=0.3)
    s.wire(p, X(p, -0.7)); s.gnd(X(p, -0.7), lead=0.5)
    return s, [r'$V_{\mathrm{OUT}} = -\dfrac{1}{R1\,C1}\int V_{\mathrm{IN}}\,dt$',
               'R2 feeds a small trim current into the summing node to cancel the input bias current;',
               'set R3 so the output does not drift with the input at zero',
               "D1's forward drop changes with temperature in roughly the same way as the bias current"]


@circuit(17, B, 'Comparator with Logic-Level Output Clamp')
def c17():
    s = Sch()
    u = s.opamp((2, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    s.term((0, n[1]), r'$V_{\mathrm{A}}$'); s.wire((0, n[1]), n)
    s.term((0, p[1]), r'$V_{\mathrm{B}}$'); s.wire((0, p[1]), p)
    k = X(o, 3.2)
    s.R(o, k, 'R1'); s.dot(k)
    s.Z((k[0], k[1] - 2.6), k, 'D1', loc='right'); s.gnd((k[0], k[1] - 2.6))
    s.wire(k, X(k, 1.4)); s.term(X(k, 1.4), VOUT, 'right')
    s.pwr(u, r'$V^{+}$', r'$V^{-}$')
    return s, [r'$V_{\mathrm{OUT}}$ is high ($\approx V_{\mathrm{Z}}$) when $V_{\mathrm{B}} > V_{\mathrm{A}}$, and about $-0.6$ V otherwise',
               'D1 clamps the swing to a level a logic input can accept; R1 limits the clamp current',
               'Pick the zener voltage for the logic family being driven']


@circuit(18, B, 'Photodiode Light-Threshold Detector')
def c18():
    s = Sch()
    u = s.opamp((4, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    x = 1.5
    s.wire((x, n[1]), n); s.dot((x, n[1]))
    s.PD((x, n[1]), (x, n[1] + 2.6), 'D1', loc='right'); s.rail((x, n[1] + 2.6), r'$V^{+}$', lead=0.4)
    s.R((x, n[1]), (x, n[1] - 3.2), 'R1', loc='left'); s.rail((x, n[1] - 3.2), r'$V^{-}$', up=False, lead=0.4)
    q = X(p, -0.8); s.wire(p, q); s.R(q, X(q, 0, -2.2), 'R2', loc='right'); s.gnd(X(q, 0, -2.2))
    k = X(o, 3.0)
    s.R(o, k, 'R3'); s.dot(k)
    s.Z((k[0], k[1] - 2.4), k, 'D2', loc='right'); s.gnd((k[0], k[1] - 2.4))
    s.wire(k, X(k, 1.4)); s.term(X(k, 1.4), VOUT, 'right')
    return s, [r'The output switches low when the photocurrent exceeds the current drawn by R1 ($\approx |V^{-}|/R1$)',
               'R2 (optional) matches the resistance at the inverting input to reduce bias-current error',
               'R3 and zener D2 limit the output swing to a logic-compatible level']


@circuit(19, B, 'Window Comparator')
def c19():
    s = Sch()
    u1 = s.opamp((3, 0.8), 'U1', plus_top=True); u2 = s.opamp((3, -2.05), 'U2', plus_top=True)
    s.term((0, u1.in2[1]), sub('V', 'HI')); s.wire((0, u1.in2[1]), u1.in2)
    s.term((0, u2.in1[1]), sub('V', 'LO')); s.wire((0, u2.in1[1]), u2.in1)
    xb = 1.8; yi = (u1.in1[1] + u2.in2[1]) / 2
    s.term((0, yi), VIN); s.wire((0, yi), (xb, yi)); s.dot((xb, yi))
    s.wire((xb, yi), (xb, u1.in1[1]), u1.in1); s.wire((xb, yi), (xb, u2.in2[1]), u2.in2)
    o1, o2 = u1.out, u2.out
    xd = o1[0] + 0.6; xa = xd + 2.6
    s.D((xa, o1[1]), (xd, o1[1]), 'D1'); s.wire(o1, (xd, o1[1]))
    s.D((xa, o2[1]), (xd, o2[1]), 'D2', loc='bottom'); s.wire(o2, (xd, o2[1]))
    s.wire((xa, o1[1]), (xa, o2[1])); s.dot((xa, yi))
    s.wire((xa, yi), (xa + 1.6, yi)); s.term((xa + 1.6, yi), VOUT, 'right')
    s.R((xa, o1[1]), (xa, o1[1] + 2.6), 'R1', loc='right'); s.rail((xa, o1[1] + 2.6), r'$V^{+}$', lead=0.3)
    s.dot((xa, o1[1]))
    return s, [r'$V_{\mathrm{OUT}}$ is high only while $V_{\mathrm{LO}} < V_{\mathrm{IN}} < V_{\mathrm{HI}}$',
               'If either op amp output goes low, its diode pulls the output low (wired-AND)',
               'R1 pulls the output high when both diodes are reverse biased']


@circuit(20, B, 'Multi-Window Level Classifier')
def c20():
    s = Sch()
    refs = ['4', '3', '2', '1']
    outs = [r'$V_{\mathrm{IN}} > V_4$', r'$V_3 < V_{\mathrm{IN}} < V_4$',
            r'$V_2 < V_{\mathrm{IN}} < V_3$', r'$V_1 < V_{\mathrm{IN}} < V_2$']
    yb = -0.9
    s.term((0, yb), VIN, 'left')
    prev = (0, yb)
    x0 = 1.6
    for k in range(4):
        u = s.opamp((x0, 2.55), 'U%d' % (k + 1))
        n, p, o = u.in1, u.in2, u.out
        sk = (x0 - 0.6, yb)
        s.wire(prev, sk); s.dot(sk)
        s.wire(sk, (sk[0], p[1]), p)
        s.wire(n, X(n, -0.6), (n[0] - 0.6, 3.7)); s.term((n[0] - 0.6, 3.7), r'$V_%s$' % refs[k], 'top')
        jx = o[0] + 0.55
        s.wire(o, (jx, o[1]))
        ytop = 5.3 if k % 2 == 0 else 4.6
        s.wire((jx, o[1]), (jx, ytop)); s.term((jx, ytop), outs[k], 'top')
        if k < 3:
            s.dot((jx, o[1]))
            q = s.mosfet((jx, 1.0), 'p', 'gate_up')
            s.text((jx, 0.2), 'Q%d' % (k + 1))
            s.wire((jx, o[1]), q['gate'])
            src, drn = q['source'], q['drain']
            s.wire((src[0], yb), src)
            nxt = (drn[0], yb)
            s.wire(drn, nxt); s.dot(drn)
            s.R(nxt, (nxt[0], yb - 2.6), 'R%d' % (k + 1), loc='right')
            s.rail((nxt[0], yb - 2.6), r'$V^{-}$', up=False, lead=0.3)
            s.wire(sk, (src[0], yb))
            prev = nxt
            x0 = drn[0] + 0.6
    return s, [r'References: $V_4 > V_3 > V_2 > V_1$',
               'A comparator that reads high turns off the P-channel switch to the stages after it,',
               'so only the stage whose window holds the input reads high',
               r'R1 to R3 pull a disconnected (+) input to $V^{-}$; make them much larger than the switch on-resistance',
               'Each P-channel switch has its body tied to its source, the side toward the input, so its body diode stays reverse-biased']


def trim_pot(s, x, y, name):
    """Vertical trimmer between +V (top) and -V (bottom), wiper to the right.
    Returns the wiper connection point."""
    top, bot = (x, y + 1.5), (x, y - 1.5)
    s.R(top, bot, None)
    s.text((x - 0.45, y), name, ha='right')
    s.arrow((x + 1.0, y), (x + 0.3, y))
    s.wire(top, (x, y + 1.9)); s.term((x, y + 1.9), r'$+V$', 'top')
    s.wire(bot, (x, y - 1.9)); s.term((x, y - 1.9), r'$-V$', 'bottom')
    return (x + 1.0, y)


ZF = r'$Z_{\mathrm{F}}$'


@circuit(21, B, 'Offset Trim for an Inverting Stage')
def c21():
    s = Sch()
    u = s.opamp((7, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    s.term((1.0, n[1]), VIN); s.R((1.0, n[1]), j, 'R1'); s.wire(j, n)
    jo = out_term(s, o)
    s.wire(j, (j[0], n[1] + 1.8)); s.Zbox((j[0], n[1] + 1.8), (jo[0], n[1] + 1.8), ZF); s.wire((jo[0], n[1] + 1.8), jo); s.dot(j)
    q = X(p, -1.0); s.wire(p, q); s.dot(q)
    s.R(q, X(q, 0, -2.4), 'R2', loc='right'); s.gnd(X(q, 0, -2.4))
    w = trim_pot(s, -1.2, q[1] - 1.4, 'R4')
    k = (q[0] - 2.4, w[1])
    s.R(w, k, 'R3', loc='bottom'); s.wire(k, (k[0], q[1]), q)
    return s, [r'Trim range at the (+) input $\approx \pm V\,\dfrac{R2}{R3}$   (R2 $\ll$ R3)',
               r'$Z_{\mathrm{F}}$ can be any feedback network: resistor, capacitor or nonlinear element',
               'Keep R2 small so its noise and bias-current drop are negligible']


@circuit(22, B, 'Offset Trim for a Non-Inverting Stage')
def c22():
    s = Sch()
    u = s.opamp((7.5, 0), 'U1', plus_top=True); n, p, o = u.in1, u.in2, u.out
    s.term((5.0, p[1]), VIN); s.wire((5.0, p[1]), p)
    j = X(n, -0.7); s.wire(n, j)
    jo = out_term(s, o)
    yb = n[1] - 1.6
    s.wire(j, (j[0], yb)); s.Zbox((j[0], yb), (jo[0], yb), ZF, loc='bottom'); s.wire((jo[0], yb), jo); s.dot((j[0], yb))
    xn = (j[0], yb - 2.6)
    s.R((j[0], yb), xn, 'R2', loc='right'); s.dot(xn)
    s.R(xn, X(xn, 0, -2.4), 'R3', loc='right'); s.gnd(X(xn, 0, -2.4))
    w = trim_pot(s, 0.3, xn[1], 'R5')
    s.R(w, xn, 'R4', loc='bottom')
    return s, [r'Trim range at the (+) input $\approx \pm V\,\dfrac{R3}{R4}$   (R3 $\ll$ R4)',
               r'Gain $\approx 1 + \dfrac{Z_{\mathrm{F}}}{R2 + R3}$']


@circuit(23, B, 'Offset Trim for a Voltage Follower')
def c23():
    s = Sch()
    u = s.opamp((7, 0), 'U1', plus_top=True); n, p, o = u.in1, u.in2, u.out
    s.term((4.5, p[1]), VIN); s.wire((4.5, p[1]), p)
    j = X(n, -0.7); s.wire(n, j)
    jo = out_term(s, o)
    yb = n[1] - 1.6
    s.wire(j, (j[0], yb)); s.R((j[0], yb), (jo[0], yb), 'R1', loc='bottom'); s.wire((jo[0], yb), jo); s.dot((j[0], yb))
    w = trim_pot(s, 0.3, yb - 2.0, 'R3')
    s.wire((j[0], yb), (j[0], yb - 2.0)); s.R(w, (j[0], yb - 2.0), 'R2', loc='bottom')
    return s, [r'Trim range $\approx \pm V\,\dfrac{R1}{R2}$',
               r'Gain $= 1 + \dfrac{R1}{R2}$, which stays close to 1 because R2 $\gg$ R1']


@circuit(24, B, 'Offset Trim for a Difference Amplifier')
def c24():
    s = Sch()
    u = s.opamp((8, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    jn = X(n, -0.7); jp = X(p, -1.6)
    s.term((1.0, n[1]), sub('V', '1')); s.R((1.0, n[1]), jn, 'R1'); s.wire(jn, n)
    s.term((1.0, p[1]), sub('V', '2')); s.R((1.0, p[1]), jp, 'R3', loc='bottom'); s.wire(jp, p); s.dot(jp)
    jo = out_term(s, o)
    s.loop(jn, jo, n[1] + 1.8, 'R', 'R2')
    jj = X(jp, 0, -3.4)
    s.R(jp, jj, 'R4', loc='right'); s.dot(jj)
    s.R(jj, X(jj, 0, -2.4), 'R5', loc='right'); s.gnd(X(jj, 0, -2.4))
    w = trim_pot(s, 0.6, jj[1] - 0.4, 'R7')
    s.R(w, (jj[0], w[1]), 'R6', loc='bottom'); s.wire((jj[0], w[1]), jj)
    return s, [r'Gain $= \dfrac{R2}{R1}$ with R3 = R1 and R4 + R5 = R2',
               r'Trim range at the (+) input $\approx \pm V\,\dfrac{R5}{R6}\cdot\dfrac{R3}{R3+R4}$   (R5 $\ll$ R6)']


@circuit(25, B, 'Offset Trim by Summing-Node Injection')
def c25():
    s = Sch()
    u = s.opamp((7, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.9)
    s.term((1.0, n[1]), VIN); s.R((1.0, n[1]), j, 'R1', loc='bottom'); s.wire(j, n)
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 1.8, 'R', 'R2')
    w = trim_pot(s, 0.3, n[1] + 4.0, 'R4')
    s.R(w, (j[0], w[1]), 'R3'); s.wire((j[0], w[1]), (j[0], n[1] + 1.8)); s.dot((j[0], n[1] + 1.8))
    s.wire(p, X(p, -0.7)); s.gnd(X(p, -0.7), lead=0.5)
    return s, [r'Input-referred trim range $\approx \pm V\,\dfrac{R1 \parallel R2}{R3}$',
               r'Suited to R1 $\parallel$ R2 of about 10 k$\Omega$ or less, so R3 stays a practical value',
               r'Example: $\pm$15 V supplies with R3 $\approx$ 2000 (R1 $\parallel$ R2) give about $\pm$7.5 mV']
