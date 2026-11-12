from lib import Sch, X, VIN, VOUT, sub
from reg import circuit
from c_basic import out_term, follower, gnd_plus
G = 'Signal Generation'


def quad_osc(hf):
    s = Sch()
    # --- U1: unity-gain two-pole low-pass (top row, signal flows right)
    u1 = s.opamp((6.0, 0.0), 'U1', plus_top=True); n1, p1, o1 = u1.in1, u1.in2, u1.out
    Xn = (2.0, p1[1]); Yn = (4.6, p1[1])
    s.R(Xn, Yn, 'R2'); s.wire(Yn, p1); s.dot(Xn, Yn)
    s.C(Yn, (Yn[0], -1.4), 'C1', loc='left'); s.gnd((Yn[0], -1.4))
    jo1 = (o1[0] + 0.6, o1[1])
    s.wire(n1, (5.4, n1[1]), (5.4, -1.0), (jo1[0], -1.0), jo1)
    s.wire(Xn, (Xn[0], 2.9)); s.C((Xn[0], 2.9), (jo1[0], 2.9), 'C2'); s.wire((jo1[0], 2.9), jo1)
    s.dot(jo1)
    k = (jo1[0] + 1.6, o1[1])
    s.wire(o1, k); s.dot(k); s.wire(k, (k[0] + 1.2, k[1])); s.term((k[0] + 1.2, k[1]), 'SINE', 'right')
    # --- U2: integrator (bottom row, pointing left)
    yi = -4.6
    u2 = s.opamp((k[0] - 1.8, yi), 'U2', left=True); n2, p2, o2 = u2.in1, u2.in2, u2.out
    s.wire(p2, (p2[0] + 0.5, p2[1])); s.gnd((p2[0] + 0.5, p2[1]), lead=0.4)
    jo2 = (o2[0] - 0.6, o2[1])
    jn = (n2[0] + 0.7, yi)
    if not hf:
        s.R(k, (k[0], yi), 'R3', loc='right'); s.wire((k[0], yi), n2); s.dot(jn)
        s.wire(jn, (jn[0], yi + 1.7)); s.C((jn[0], yi + 1.7), (jo2[0], yi + 1.7), 'C3'); s.wire((jo2[0], yi + 1.7), jo2)
    else:
        a = (k[0], yi + 2.6)
        s.R(k, a, 'R3', loc='right'); s.dot(a)
        s.R(a, (a[0], yi), 'R4', loc='right'); s.wire((a[0], yi), n2); s.dot(jn)
        s.C(a, (jo2[0], a[1]), 'C3', loc='top')
        s.wire((jo2[0], a[1]), jo2)
        s.wire(jn, (jn[0], yi + 1.3)); s.C((jn[0], yi + 1.3), (jo2[0], yi + 1.3), 'C4', loc='bottom'); s.dot((jo2[0], yi + 1.3))
    s.dot(jo2)
    # --- amplitude clamp and return path (left side)
    rn = 'R5' if hf else 'R4'
    zn = (Xn[0] - 2.2, o2[1])
    s.wire(o2, jo2)
    s.R(jo2, (Xn[0] - 0.0, zn[1]), rn, loc='bottom')
    s.wire((Xn[0], zn[1]), zn); s.dot(zn)
    s.wire(jo2, (jo2[0], o2[1] - 1.6)); s.term((jo2[0], o2[1] - 1.6), 'COSINE', 'bottom')
    s.R(zn, (zn[0], p1[1]), 'R1', loc='left'); s.wire((zn[0], p1[1]), Xn)
    m = (zn[0], zn[1] - 2.2); g = (zn[0], zn[1] - 4.4)
    s.Z(m, zn, 'D1', loc='right'); s.Z(m, g, 'D2', loc='right'); s.gnd(g)
    if hf:
        # small lead capacitor across the summing node, drawn under U2
        pass
    return s, u2, jn, jo2, yi


@circuit(26, G, 'Quadrature Sine Oscillator (Low Frequency)')
def c26():
    s, *_ = quad_osc(False)
    return s, [r'$f_0 \approx \dfrac{1}{2\pi\sqrt{R1\,R2\,C1\,C2}}$   with R1 = R2 and C2 = 2 C1',
               'U1 is a unity-gain two-pole low-pass filter (90° lag at $f_0$); U2 integrates its output (90° lead)',
               r'Make R3 C3 $\approx$ R1 C1 / 2 so the loop gain is about 2; the back-to-back zeners D1, D2 set the amplitude',
               'U2 output is the cosine; U1 output is the sine']


@circuit(27, G, 'Quadrature Sine Oscillator (Wideband)')
def c27():
    s, u2, jn, jo2, yi = quad_osc(True)
    return s, [r'$f_0 \approx \dfrac{1}{2\pi\sqrt{R1\,R2\,C1\,C2}}$   with R1 = R2 and C2 = 2 C1',
               'Same loop as the low-frequency version, with a wideband integrator for U2:',
               'C3 integrates; R4 with a small C4 keeps a fast op amp stable',
               r'Make R3 C3 $\approx$ R1 C1 / 2; zeners D1, D2 set the amplitude']


@circuit(28, G, 'Op-Amp Astable Multivibrator')
def c28():
    s = Sch()
    u = s.opamp((4, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -2.0); s.wire(j, n); s.dot(j)
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 2.0, 'R', 'R1', dots=False); s.dot(jo)
    s.C(j, (j[0], j[1] - 3.0), 'C1', loc='left'); s.gnd((j[0], j[1] - 3.0))
    q = X(p, -0.5); s.wire(p, q, (q[0], p[1] - 1.4)); qq = (q[0], p[1] - 1.4)
    s.R(qq, (jo[0], qq[1]), 'R2', loc='bottom'); s.wire((jo[0], qq[1]), jo); s.dot(qq)
    s.R(qq, (qq[0], qq[1] - 2.4), 'R3', loc='right'); s.gnd((qq[0], qq[1] - 2.4))
    return s, [r'$f = \dfrac{1}{2\,R1\,C1\,\ln\!\left(1 + \dfrac{2\,R3}{R2}\right)}$',
               'R2 and R3 set the switching thresholds; R1 and C1 set the timing',
               'The output is a square wave between the op-amp output limits']


@circuit(29, G, 'Wien-Bridge Oscillator with Lamp Amplitude Control')
def c29():
    s = Sch()
    u = s.opamp((5, 0), 'U1', plus_top=True); n, p, o = u.in1, u.in2, u.out
    jo = out_term(s, o)
    j = X(n, -0.8); s.wire(n, j)
    yb = n[1] - 1.6
    s.wire(j, (j[0], yb)); s.R((j[0], yb), (jo[0], yb), 'R3', loc='bottom'); s.wire((jo[0], yb), jo)
    s.lamp((j[0], yb), (j[0], yb - 2.6), 'LP1', loc='right'); s.gnd((j[0], yb - 2.6))
    s.dot((j[0], yb))
    jp = (p[0] - 2.4, p[1]); s.wire(jp, p); s.dot(jp)
    yt = p[1] + 2.2
    s.wire(jp, (jp[0], yt)); mid = (jp[0] + jo[0]) / 2
    s.R((jp[0], yt), (mid, yt), 'R1'); s.C((mid, yt), (jo[0], yt), 'C1'); s.wire((jo[0], yt), jo)
    # shunt arm R2 || C2
    xl, xr = jp[0] - 1.6, jp[0]
    yb2 = p[1] - 3.6
    s.wire(jp, (xl, jp[1]))
    s.R((xl, jp[1]), (xl, yb2), 'R2', loc='left'); s.C((xr, jp[1]), (xr, yb2), 'C2', loc='right')
    s.wire((xl, yb2), (xr, yb2)); s.gnd((xr, yb2))
    return s, [r'$f = \dfrac{1}{2\pi R1\,C1}$   with R1 = R2 and C1 = C2',
               'The bridge needs a gain of 3: oscillation settles where R3 = 2 R(lamp)',
               "The lamp's resistance rises as the signal heats it, which holds the amplitude steady"]


@circuit(30, G, 'Triangle and Square Wave Generator')
def c30():
    s = Sch()
    u1 = s.opamp((5.5, 0), 'U1'); n1, p1, o1 = u1.in1, u1.in2, u1.out
    j1 = X(n1, -0.7)
    a = (0.6, n1[1])
    s.R(a, (2.8, n1[1]), 'R1')
    s.RV((2.8, n1[1]), (4.8, n1[1]), None); s.text((3.8, n1[1] - 0.7), 'R2', va='top'); s.wire((4.8, n1[1]), n1)
    jo1 = (o1[0] + 0.6, o1[1])
    s.wire((j1[0], n1[1]), (j1[0], 1.8)); s.C((j1[0], 1.8), (jo1[0], 1.8), 'C1'); s.wire((jo1[0], 1.8), jo1)
    s.dot(j1, jo1)
    s.wire((jo1[0], 1.8), (jo1[0], 3.0)); s.term((jo1[0], 3.0), 'TRIANGLE', 'top'); s.dot((jo1[0], 1.8))
    gnd_plus(s, p1)
    # U2: non-inverting comparator with hysteresis
    x2 = jo1[0] + 3.6
    u2 = s.opamp((x2, o1[1] - 1.25), 'U2', plus_top=True); n2, p2, o2 = u2.in1, u2.in2, u2.out
    jp2 = X(p2, -0.7)
    s.wire(o1, jo1); s.R(jo1, jp2, 'R3', loc='bottom'); s.wire(jp2, p2); s.dot(jp2)
    s.wire(n2, X(n2, -0.6)); s.gnd(X(n2, -0.6), lead=0.4)
    jo2 = (o2[0] + 0.6, o2[1])
    yt = p2[1] + 2.0
    s.wire(jp2, (jp2[0], yt)); mid = (jp2[0] + jo2[0]) / 2 - 0.2
    s.R((jp2[0], yt), (mid, yt), 'R4'); s.RV((mid, yt), (jo2[0], yt), None); s.text(((mid + jo2[0]) / 2, yt + 0.75), 'R5', va='bottom')
    s.wire((jo2[0], yt), jo2); s.dot(jo2)
    s.wire(o2, (jo2[0] + 1.4, o2[1])); s.term((jo2[0] + 1.4, o2[1]), 'SQUARE', 'right')
    # square wave returns to the integrator input along the bottom
    yb = o2[1] - 2.6
    k = (jo2[0] + 0.7, o2[1]); s.dot(k)
    s.wire(k, (k[0], yb), (a[0], yb), a)
    return s, [r'Triangle peak $= V_{\mathrm{SQ}}\,\dfrac{R3}{R4+R5}$   ($V_{\mathrm{SQ}}$ = square-wave amplitude)',
               r'$f = \dfrac{R4+R5}{4\,R3\,(R1+R2)\,C1}$',
               'R2 tunes the frequency; R5 sets the triangle amplitude (and also shifts the frequency)']


@circuit(31, G, 'Pulse-Width Modulator')
def c31():
    s = Sch()
    u = s.opamp((6, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    jn = (3.6, n[1])
    s.term((jn[0], 3.6), VIN, 'top'); s.R((jn[0], 3.6), jn, 'R1', loc='right'); s.wire(jn, n); s.dot(jn)
    s.C(jn, (jn[0], -2.4), 'C1', loc='right'); s.gnd((jn[0], -2.4))
    K = (1.0, -4.0)
    s.R(K, (K[0], n[1]), 'R2', loc='left'); s.wire((K[0], n[1]), jn)
    pn = (p[0] - 0.8, -4.0)
    s.wire(p, (pn[0], p[1]), pn)
    s.R(K, pn, 'R4', loc='bottom'); s.dot(K, pn)
    s.R(pn, (pn[0], -6.0), 'R5', loc='right'); s.gnd((pn[0], -6.0))
    jo = (o[0] + 0.7, o[1])
    s.wire(o, (jo[0] + 1.6, o[1])); s.term((jo[0] + 1.6, o[1]), VOUT, 'right'); s.dot(jo)
    yb = -7.4
    s.R(jo, (jo[0], yb), 'R3', loc='right'); s.wire((jo[0], yb), (K[0], yb), K)
    m = (K[0] - 2.2, K[1]); g2 = (K[0] - 4.4, K[1])
    s.Z(m, K, 'D1'); s.Z(m, g2, 'D2'); s.gnd(g2, lead=0.4)
    return s, ['With no input this is a free-running square-wave oscillator (R2, C1 set the period;',
               'R4, R5 set the switching thresholds)',
               r'$V_{\mathrm{IN}}$ adds charging current through R1, changing the high and low times: the duty cycle',
               'follows the input while the period changes little',
               'Zeners D1, D2 fix the fed-back amplitude so timing does not depend on the supply']


def howland(s, x0, src, rnames, unames):
    """Howland current pump. src: point feeding the input resistor."""
    Ra, Rf, Ro, Rp, Rg = rnames
    u = s.opamp((x0, 0), unames); n, p, o = u.in1, u.in2, u.out
    jn = X(n, -0.7)
    s.R(src, jn, Ra); s.wire(jn, n)
    jo = (o[0] + 0.7, o[1])
    s.wire(o, jo); s.loop(jn, jo, n[1] + 2.0, 'R', Rf)
    L = (jo[0], -4.0)
    s.R(jo, L, Ro, loc='right'); s.dot(L)
    s.wire(L, (L[0] + 2.0, L[1])); s.term((L[0] + 2.0, L[1]), sub('I', 'OUT'), 'right')
    s.arrow((L[0] + 0.5, L[1] + 0.45), (L[0] + 1.6, L[1] + 0.45))
    q = (p[0] - 0.8, L[1])
    s.wire(p, (q[0], p[1]), q); s.dot(q)
    s.R(q, L, Rp, loc='bottom')
    s.R(q, (q[0], q[1] - 2.4), Rg, loc='left'); s.gnd((q[0], q[1] - 2.4))
    return u


HOWL_NOTES = [r'$I_{\mathrm{OUT}} = -\dfrac{R2}{R1\,R3}\,V_{\mathrm{IN}}$   (positive = current out of the terminal)',
              'Requires R5 = R1 and R2 = R3 + R4; the output resistance is then very high',
              'The load returns to ground; current flows in either direction']


@circuit(32, G, 'Bidirectional Current Source with Input Buffer')
def c32():
    s = Sch()
    u1 = s.opamp((1.6, -1.25), 'U1', plus_top=True); n1, p1, o1 = u1.in1, u1.in2, u1.out
    s.term((0, p1[1]), VIN); s.wire((0, p1[1]), p1)
    jo1 = (o1[0] + 0.5, o1[1]); s.dot(jo1)
    s.wire(n1, X(n1, -0.6), (n1[0] - 0.6, n1[1] - 1.0), (jo1[0], n1[1] - 1.0), jo1)
    s.wire(o1, jo1)
    howland(s, jo1[0] + 3.6, jo1, ('R1', 'R2', 'R3', 'R4', 'R5'), 'U2')
    return s, HOWL_NOTES + ['U1 keeps the source from loading R1, so the source impedance does not upset the balance']


@circuit(33, G, 'Bidirectional Current Source')
def c33():
    s = Sch()
    s.term((0, 0), VIN)
    howland(s, 3.4, (0, 0), ('R1', 'R2', 'R3', 'R4', 'R5'), 'U1')
    return s, HOWL_NOTES + ['The source must have low impedance compared with R1']


@circuit(34, G, 'Wien-Bridge Oscillator with JFET Gain Control')
def c34():
    s = Sch()
    u = s.opamp((6.0, -1.25), 'U1', plus_top=True); n, p, o = u.in1, u.in2, u.out   # + at y=0, - at y=-1.25
    jo = (o[0] + 0.6, o[1])
    # Wien series arm over the top, shunt arm on the left
    jp = (4.4, p[1]); s.wire(jp, p); s.dot(jp)
    yt = 1.9
    s.wire(jp, (jp[0], yt)); mid = (jp[0] + jo[0]) / 2
    s.R((jp[0], yt), (mid, yt), 'R1'); s.C((mid, yt), (jo[0], yt), 'C1'); s.wire((jo[0], yt), jo)
    xl, xr = 1.8, 3.2
    s.wire(jp, (xl, jp[1]))
    s.R((xl, jp[1]), (xl, -2.6), 'R2', loc='left'); s.C((xr, jp[1]), (xr, -2.6), 'C2', loc='right')
    s.wire((xl, -2.6), (xr, -2.6)); s.gnd((xr, -2.6)); s.dot((xr, jp[1]))
    # gain leg below
    jn = (5.4, n[1]); s.wire(n, jn)
    yr = -3.0
    s.wire(jn, (jn[0], yr)); s.R((jn[0], yr), (jo[0], yr), 'R3', loc='bottom'); s.wire((jo[0], yr), jo)
    s.dot((jn[0], yr), jo)
    Dn = (jn[0], -5.6)
    s.R((jn[0], yr), Dn, 'R4', loc='left'); s.dot(Dn)
    q1 = s.add(__import__('schemdraw').elements.JFetN().theta(0).anchor('drain').at((jn[0], -6.4)))
    s.wire(Dn, (jn[0], -6.4))
    s.text((jn[0] - 0.45, -7.0), 'Q1', ha='right')
    s.gnd(q1.source, lead=0.3)
    Gx = 7.7
    s.wire(Dn, (Gx, Dn[1])); Gn = (Gx, q1.gate[1])
    s.R((Gx, Dn[1]), Gn, 'R5', loc='right'); s.wire(q1.gate, Gn); s.dot(Gn)
    s.R(Gn, (Gx, -9.4), 'R6', loc='left'); s.gnd((Gx, -9.4))
    # peak detector
    J = (jo[0] + 0.9, o[1])
    s.wire(o, J); s.dot(J)
    s.wire(J, (J[0], 2.9)); s.term((J[0], 2.9), VOUT, 'top')
    P = (J[0] + 2.6, o[1]); E = (P[0] + 2.4, o[1])
    s.R(J, P, 'R7'); s.Z(E, P, 'D1'); s.dot(E)
    s.wire(E, (E[0] + 1.6, E[1])); s.D((E[0] + 1.6, E[1] - 2.2), (E[0] + 1.6, E[1]), 'D2', loc='right'); s.gnd((E[0] + 1.6, E[1] - 2.2))
    q2 = s.pnp((E[0] - 0.75, E[1] - 2.0), None)
    s.text((E[0] + 0.25, E[1] - 2.0), 'Q2', ha='left')
    s.wire(E, q2.emitter)
    s.wire(q2.base, (q2.base[0] - 0.6, q2.base[1])); s.gnd((q2.base[0] - 0.6, q2.base[1]), lead=0.3)
    B = (E[0], -4.4)
    s.wire(q2.collector, B); s.dot(B)
    vneg = -9.4
    s.Cpol((B[0], vneg), B, 'C3', loc='left')
    s.wire(B, (B[0] + 1.6, B[1])); s.R((B[0] + 1.6, B[1]), (B[0] + 1.6, -6.8), 'R8', loc='right')
    s.D((B[0] + 1.6, -6.8), (B[0] + 1.6, vneg), 'D3', loc='right')
    # Q3: NPN pulls the JFET gate negative
    q3 = s.npn((B[0] - 1.4, -5.4), None, left=True)
    s.wire(B, (B[0] - 1.4, B[1]), q3.base)
    s.text((q3.collector[0] - 0.35, -5.4), 'Q3', ha='right')
    cx = q3.collector
    s.wire(cx, (9.2, cx[1]), (9.2, Gn[1]), Gn)
    s.R(q3.emitter, (q3.emitter[0], vneg), 'R9', loc='left')
    s.wire((q3.emitter[0], vneg), (B[0] + 1.6, vneg)); s.dot((B[0], vneg))
    s.wire((B[0] + 1.6, vneg), (B[0] + 2.8, vneg)); s.term((B[0] + 2.8, vneg), r'$V^{-}$', 'right')
    s.dot((B[0] + 1.6, vneg))
    return s, [r'$f = \dfrac{1}{2\pi R1\,C1}$   with R1 = R2 and C1 = C2;   gain $= 1 + \dfrac{R3}{R4 + r_{DS}(Q1)} = 3$ at steady state',
               'When output peaks exceed the zener voltage of D1, Q2 charges C3; Q3 then pulls the gate of Q1',
               'negative, raising its channel resistance and lowering the gain until the amplitude settles',
               'With R5 = R6, R5 and R6 feed half the drain voltage back to the gate, which keeps the JFET resistance linear']


def bench_supply(s, neg):
    """Cascoded constant-current source into a programming resistor, buffered."""
    sgn = -1 if neg else 1
    yr = 1.0
    rail = r'$-V_{\mathrm{S}}$' if neg else r'$+V_{\mathrm{S}}$'
    s.term((-0.6, yr), rail, 'left'); s.wire((-0.6, yr), (6.05, yr))
    M = (1.0, -5.0); B2 = (2.6, -3.5); B1 = (4.4, -1.8)
    # zeners: cathode toward the rail for the positive version
    if not neg:
        s.Z(M, (M[0], yr), 'D1', loc='left'); s.Z(B2, (B2[0], yr), 'D2', loc='left')
    else:
        s.Z((M[0], yr), M, 'D1', loc='left'); s.Z((B2[0], yr), B2, 'D2', loc='left')
    s.dot((M[0], yr), (B2[0], yr), (4.4, yr))
    s.R(B2, (B2[0], M[1]), 'R1', loc='left'); s.wire(M, (B2[0], M[1])); s.dot((B2[0], M[1]))
    s.R((B2[0], M[1]), (B2[0], -7.6), 'R2', loc='left'); s.gnd((B2[0], -7.6))
    s.R((4.4, yr), B1, 'R3', loc='left'); s.R(B1, (4.4, B2[1]), 'R4', loc='left'); s.wire(B2, (4.4, B2[1]))
    s.dot(B1, B2, (4.4, B2[1]))
    tr = s.npn if neg else s.pnp
    q1 = tr((5.3, B1[1]), None, flip=neg); s.wire(B1, q1.base)
    q2 = tr((5.3, B2[1]), None, flip=neg); s.wire((4.4, B2[1]), q2.base)
    t1, b1 = q1.emitter, q1.collector
    t2, b2 = q2.emitter, q2.collector
    s.text((t1[0] + 0.35, B1[1]), 'Q1', ha='left'); s.text((t2[0] + 0.35, B2[1]), 'Q2', ha='left')
    s.R((t1[0], yr), t1, 'R5', loc='right')
    s.wire(b1, t2)
    N = (b2[0], -5.0); s.wire(b2, N); s.dot(N)
    s.wire(N, (N[0], -5.6)); s.term((N[0], -5.6))
    s.R((N[0], -5.6), (N[0], -8.2), sub('R', 'SET'), loc='right'); s.term((N[0], -8.2))
    s.gnd((N[0], -8.2), lead=0.5)
    u = s.opamp((8.2, N[1] - 1.25), 'U1', plus_top=True)
    s.wire(N, u.in2)
    jo = (u.out[0] + 0.6, u.out[1])
    follower(s, u, jo, dy=1.9)
    s.wire(u.out, (jo[0] + 1.4, jo[1])); s.term((jo[0] + 1.4, jo[1]), r'$V^{-}$' if neg else r'$V^{+}$', 'right'); s.dot(jo)
    if neg:
        s.pwr(u, r'$0\,$V', r'$-V_{\mathrm{S}}$')
    else:
        s.pwr(u, r'$+V_{\mathrm{S}}$', 'gnd')
    return s


SUP_NOTES = [r'Q1 and Q2 form a cascoded constant-current source:  $I_{\mathrm{C}} \approx \dfrac{V_{\mathrm{Z2}}\,R3/(R3+R4) - V_{\mathrm{BE}}}{R5}$',
             r'Output voltage $= I_{\mathrm{C}}\,R_{\mathrm{SET}}$; e.g. trimming $I_{\mathrm{C}}$ to 1 mA gives 1 V per k$\Omega$ of $R_{\mathrm{SET}}$',
             'D1 (higher voltage) pre-regulates the current in reference zener D2, so the output ignores supply changes',
             'U1 buffers the programming node so the load does not draw on the current source']


@circuit(35, G, 'Resistor-Programmed Low-Current Supply (Positive)')
def c35():
    s = bench_supply(Sch(), False)
    s.text((2.0, -5.3), '', ha='left')
    return s, SUP_NOTES


@circuit(36, G, 'Resistor-Programmed Low-Current Supply (Negative)')
def c36():
    s = bench_supply(Sch(), True)
    return s, [n.replace('V_{\\mathrm{BE}}', '|V_{\\mathrm{BE}}|') for n in SUP_NOTES[:1]] + \
        [SUP_NOTES[1].replace(r'Output voltage $= I_{\mathrm{C}}', r'Output voltage $= -I_{\mathrm{C}}')] + SUP_NOTES[2:3] + \
        ['Mirror image of the positive version: NPN transistors, zeners reversed, output referred to ground']


def zener_fb_ref(neg):
    s = Sch()
    u = s.opamp((5.0, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    jn = X(n, -0.8)
    s.R((1.6, n[1]), jn, 'R1'); s.wire(jn, n); s.gnd((1.6, n[1]), lead=0.5)
    jo = (o[0] + 0.7, o[1])
    yt = n[1] + 1.8
    s.wire(jn, (jn[0], yt))
    if neg:
        s.Z((jo[0], yt), (jn[0], yt), 'D1')      # anode at the (negative) output
    else:
        s.Z((jn[0], yt), (jo[0], yt), 'D1')      # cathode at the (positive) output
    s.wire((jo[0], yt), jo); s.dot(jn, jo)
    s.wire(o, (jo[0] + 1.4, o[1])); s.term((jo[0] + 1.4, o[1]), VOUT, 'right')
    a = (jo[0], o[1] - 3.0); b = (jo[0], o[1] - 5.4); c = (jo[0], o[1] - 8.0)
    s.R(jo, a, 'R2', loc='right'); s.R(a, b, None); s.text((a[0] + 0.45, (a[1] + b[1]) / 2), 'R3', ha='left')
    s.R(b, c, 'R4', loc='right'); s.gnd(c)
    wy = (a[1] + b[1]) / 2
    s.arrow((jo[0] - 1.0, wy), (jo[0] - 0.3, wy))
    q = X(p, -0.7); s.wire(p, q, (q[0], wy), (jo[0] - 1.0, wy))
    if neg:
        s.pwr(u, r'$0\,$V', r'$V^{-}$')
    else:
        s.pwr(u, r'$V^{+}$', 'gnd')
    return s, [r'$|V_{\mathrm{OUT}}| = \dfrac{V_{\mathrm{Z}}}{1-k}$,   k = fraction of $V_{\mathrm{OUT}}$ at the R3 wiper',
               r'Zener current $= \dfrac{|V_{\mathrm{OUT}}| - V_{\mathrm{Z}}}{R1}$, set by the output itself and so independent of the supply',
               'At power-up, positive feedback through the divider drives the output away from 0 V until D1 conducts']


@circuit(37, G, 'Positive Reference with Zener in the Feedback Loop')
def c37():
    return zener_fb_ref(False)


@circuit(39, G, 'Negative Reference with Zener in the Feedback Loop')
def c39():
    return zener_fb_ref(True)


def buffered_zener_ref(neg):
    s = Sch()
    x = 1.4
    top = (x, 2.2); Zn = (x, -0.6); bot = (x, -6.0)
    if not neg:
        s.rail(top, r'$V^{+}$', lead=0.3)
        s.R(top, Zn, 'R1', loc='left'); s.Z(bot, Zn, 'D1', loc='left'); s.gnd(bot, lead=0.6)
        rtop, rbot = Zn, bot
    else:
        s.rail((x, -7.4), r'$V^{-}$', up=False, lead=0.3)
        Zn = (x, -4.6); top = (x, 1.0)
        s.R((x, -7.4), Zn, 'R1', loc='left'); s.Z(Zn, top, 'D1', loc='left')
        s.wire(top, (x - 1.2, top[1])); s.gnd((x - 1.2, top[1]), lead=0.5)
        rtop, rbot = top, Zn
    xd = x + 2.2
    s.wire(rtop, (xd, rtop[1])); s.wire(rbot, (xd, rbot[1])); s.dot(rtop, rbot)
    h = (rtop[1] - rbot[1])
    a = (xd, rtop[1] - h * 0.3); b = (xd, rtop[1] - h * 0.7)
    s.R((xd, rtop[1]), a, 'R2', loc='right'); s.R(a, b, None); s.text((xd - 0.45, (a[1] + b[1]) / 2), 'R3', ha='right')
    s.R(b, (xd, rbot[1]), 'R4', loc='right')
    wy = (a[1] + b[1]) / 2
    s.arrow((xd + 1.6, wy), (xd + 0.3, wy))
    u = s.opamp((xd + 3.6, wy - 1.25), 'U1', plus_top=True)
    s.wire((xd + 1.6, wy), (xd + 3.6, wy))
    jo = (u.out[0] + 0.6, u.out[1])
    follower(s, u, jo, dy=1.9)
    s.wire(u.out, (jo[0] + 1.4, jo[1])); s.term((jo[0] + 1.4, jo[1]), VOUT, 'right'); s.dot(jo)
    if neg:
        s.pwr(u, r'$0\,$V', r'$V^{-}$')
    else:
        s.pwr(u, r'$V^{+}$', 'gnd')
    return s, top


@circuit(38, G, 'Positive Reference from a Buffered Zener')
def c38():
    s, _ = buffered_zener_ref(False)
    return s, [r'$V_{\mathrm{OUT}} = k\,V_{\mathrm{Z}}$,   k = divider fraction at the R3 wiper',
               'R1 sets the zener current; U1 buffers the divided reference so the load cannot pull it']


@circuit(40, G, 'Negative Reference from a Buffered Zener')
def c40():
    s, top = buffered_zener_ref(True)
    return s, [r'$V_{\mathrm{OUT}} = -k\,V_{\mathrm{Z}}$,   k = divider fraction at the R3 wiper',
               'R1 sets the zener current; U1 buffers the divided reference so the load cannot pull it']


def sink_source(source):
    s = Sch()
    cy = 1.8
    mf = s.mosfet((5.0, cy), 'n', 'gate_left')
    s.text((4.75, cy + 0.85), 'Q1', ha='right')
    q2 = s.npn((6.6, 0.4), None)
    s.text((q2.center[0] + 0.45, 0.4), 'Q2', ha='left')
    S = (mf['source'][0], 0.4)
    s.wire(mf['source'], S, q2.base); s.dot(S)
    Cy = 2.9
    D_c = (mf['drain'][0], Cy); xc = (q2.collector[0], Cy)
    s.wire(mf['drain'], D_c, xc, q2.collector)
    Ey = -1.8
    Eb = (q2.emitter[0], Ey); Rc = (S[0], Ey)
    s.wire(q2.emitter, Eb)
    s.R(S, Rc, 'R2', loc='left'); s.wire(Rc, Eb)
    u = s.opamp((1.2, cy - 0.625), 'U1', plus_top=True)     # (+) on top
    s.wire(u.out, mf['gate'])
    fx = u.in1[0] - 0.6
    if not source:
        s.term((-0.4, u.in2[1]), VIN); s.wire((-0.4, u.in2[1]), u.in2)
        s.wire(u.in1, (fx, u.in1[1]), (fx, Ey), Rc); s.dot(Rc)
        s.wire(xc, (xc[0], 4.6)); s.term((xc[0], 4.6), r'$V^{+}$ (through load)', 'top')
        s.arrow((xc[0] + 0.45, 4.3), (xc[0] + 0.45, 3.5)); s.text((xc[0] + 0.7, 3.9), sub('I', 'O'), ha='left')
        s.dot(xc)
        s.R(Eb, (Eb[0], -4.4), 'R1', loc='right'); s.gnd((Eb[0], -4.4)); s.dot(Eb)
    else:
        s.term((-0.4, u.in1[1]), VIN); s.wire((-0.4, u.in1[1]), u.in1)
        s.wire(u.in2, (fx, u.in2[1]), (fx, 3.7), (D_c[0], 3.7), D_c); s.dot(D_c)
        s.R(xc, (xc[0], 5.4), 'R1', loc='right')
        s.wire((xc[0], 5.4), (xc[0] + 1.4, 5.4)); s.gnd((xc[0] + 1.4, 5.4), lead=0.5); s.dot(xc, Eb)
        s.wire(Eb, (Eb[0], -3.6)); s.term((Eb[0], -3.6), r'$V^{-}$ (through load)', 'bottom')
        s.arrow((Eb[0] + 0.45, -2.3), (Eb[0] + 0.45, -3.1)); s.text((Eb[0] + 0.7, -2.7), sub('I', 'O'), ha='left')
    return s, None, None


@circuit(41, G, 'Voltage-Programmed Current Sink')
def c41():
    s, Eb, f = sink_source(False)
    # connect feedback line to the emitter/R1 node
    return s, [r'$I_{\mathrm{O}} = \dfrac{V_{\mathrm{IN}}}{R1}$   for $V_{\mathrm{IN}} \geq 0$',
               'Q1 supplies Q2 base current from the load side, so nearly all the load current passes through R1',
               'R2 keeps Q2 turned off cleanly at low currents']


@circuit(42, G, 'Voltage-Programmed Current Source')
def c42():
    s, xc, f = sink_source(True)
    return s, [r'$I_{\mathrm{O}} = -\dfrac{V_{\mathrm{IN}}}{R1}$   for $V_{\mathrm{IN}} \leq 0$ (current flows out toward the load)',
               'Same pass pair as the current sink, placed between R1 and the load',
               'R2 keeps Q2 turned off cleanly at low currents']
