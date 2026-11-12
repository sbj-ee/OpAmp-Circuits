from lib import Sch, X, VIN, VOUT, sub
from reg import circuit
from c_basic import out_term, follower, gnd_plus
import schemdraw.elements as elm
P = 'Signal Processing'
EIN = sub('E', 'IN'); EOUT = sub('E', 'OUT')


def ldr(s, a, b, label, side='left'):
    """Light-dependent resistor (photocell): resistor with two incoming light arrows."""
    s.R(a, b, None)
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    sg = -1 if side == 'left' else 1
    for dy in (0.35, -0.15):
        s.add(elm.Arrow(headwidth=0.14, headlength=0.18, lw=1.0).at((mx + sg * 1.05, my + dy + 0.45)).to((mx + sg * 0.4, my + dy)))
    s.text((mx - sg * 0.5, my), label, ha='right' if sg > 0 else 'left')


@circuit(73, P, 'Photodiode Servo Preamplifier with Lead Feedback')
def c73():
    s = Sch()
    u = s.opamp((5.2, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    jn = (4.2, 0); K = (4.2, 2.4)
    jo = out_term(s, o, dx=2.2, jx=1.0)
    s.wire((1.6, 0), n)
    s.PD((1.6, -2.4), (1.6, 0), 'D1', loc='left'); s.PD((2.8, 0), (2.8, -2.4), 'D2', loc='right')
    s.wire(p, (4.2, p[1]), (4.2, -2.4), (1.6, -2.4)); s.gnd((4.2, -2.4), lead=0.4)
    s.R(jn, K, 'R2', loc='left')
    s.R(K, (jo[0], K[1]), 'R3'); s.wire((jo[0], K[1]), jo)
    yz = 3.8; zm = (K[0] + jo[0]) / 2
    s.wire(K, (K[0], yz)); s.Z((zm, yz), (K[0], yz), 'D3'); s.Z((zm, yz), (jo[0], yz), 'D4'); s.wire((jo[0], yz), (jo[0], K[1]))
    s.wire(K, (-0.6, K[1])); s.R((-0.6, K[1]), (-0.6, 0.0), 'R1', loc='left'); s.C((-0.6, 0.0), (-0.6, -2.0), 'C1', loc='left'); s.gnd((-0.6, -2.0))
    s.dot(jn, K, (2.8, 0), (2.8, -2.4), (jo[0], K[1]), (4.2, -2.4))
    return s, ['D1 and D2 are connected in inverse parallel, so the output follows the difference in light on the two photodiodes',
               'R1 and C1 shunt part of the feedback to ground at low frequency, adding phase lead (rate feedback) for the servo loop',
               'Back-to-back zeners D3 and D4 limit the output swing, so the preamplifier saturates cleanly']


@circuit(74, P, 'Power Booster Driven by Supply-Current Sensing')
def c74():
    s = Sch()
    u = s.opamp((3.0, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    s.term((1.4, n[1]), r'$\mathrm{IN}-$'); s.wire((1.4, n[1]), n)
    s.term((1.4, p[1]), r'$\mathrm{IN}+$'); s.wire((1.4, p[1]), p)
    hi, lo = (u.vd, u.vs) if u.vd[1] > u.vs[1] else (u.vs, u.vd)
    yr, yA, yB, yn = 5.6, 3.0, -3.9, -6.6
    A = (hi[0], yA); B = (lo[0], yB)
    s.wire(hi, A); s.wire(lo, B)
    s.R((hi[0], yr), A, 'R1', loc='left'); s.R(B, (lo[0], yn), 'R2', loc='left')
    q1 = s.pnp((8.4, yA), None); q2 = s.npn((8.4, yB), None)
    s.text((9.5, yA), 'Q1', ha='left'); s.text((9.5, yB), 'Q2', ha='left')
    s.wire(A, q1.base); s.wire(B, q2.base)
    xc = q1.emitter[0]
    s.wire(q1.emitter, (xc, yr)); s.wire(q2.emitter, (xc, yn))
    s.wire((hi[0], yr), (xc, yr), (xc + 1.6, yr)); s.term((xc + 1.6, yr), r'$V^{+}$', 'right')
    s.wire((lo[0], yn), (xc, yn), (xc + 1.6, yn)); s.term((xc + 1.6, yn), r'$V^{-}$', 'right')
    Xo = (xc, o[1])
    s.wire(q1.collector, Xo, q2.collector)
    O = (5.6, o[1])
    s.wire(o, O); s.C((6.2, o[1]), (8.2, o[1]), 'C1'); s.wire(O, (6.2, o[1])); s.wire((8.2, o[1]), Xo)
    s.R(O, (O[0], -2.6), 'R3', loc='left'); s.gnd((O[0], -2.6))
    s.wire(Xo, (xc + 1.6, Xo[1])); s.term((xc + 1.6, Xo[1]), 'OUTPUT', 'right')
    s.dot(A, B, O, Xo, (xc, yr), (xc, yn))
    return s, ['The supply current of U1 flows through R1 and R2.  When U1 sources or sinks more than about',
               r'$V_{\mathrm{BE}}$/R1, Q1 or Q2 turns on and delivers the extra current to the load',
               'R3 loads U1 so that its supply current follows its output current;  C1 passes fast edges straight to the output',
               'Close the overall feedback loop from OUTPUT back to the inputs (not shown)']


@circuit(75, P, 'Two-Quadrant Multiplier with Lamp and Photocells')
def c75():
    s = Sch()
    u1 = s.opamp((2.0, 4.25), 'U1'); n1, p1, o1 = u1.in1, u1.in2, u1.out
    s.wire(n1, (0.0, n1[1]))
    s.R((0.0, n1[1]), (-2.4, n1[1]), 'R2'); s.gnd((-2.4, n1[1]), lead=0.5)
    Pn = (1.0, 2.4)
    s.wire(p1, (1.0, p1[1]), Pn)
    s.R(Pn, (1.0, -0.6), 'R1', loc='left'); s.wire((1.0, -0.6), (1.0, -1.6)); s.term((1.0, -1.6), sub('V', '1'), 'bottom')
    s.wire(Pn, (3.6, Pn[1]))
    ldr(s, (3.6, 2.4), (3.6, -0.1), 'PC1', side='right')
    q1 = s.npn((5.0, o1[1]), None)
    s.text((6.15, o1[1]), 'Q1', ha='left')
    s.wire(o1, q1.base)
    s.R(q1.collector, (q1.collector[0], 6.6), 'R3', loc='right'); s.term((q1.collector[0], 6.6), r'$V^{+}$', 'top')
    xl = q1.emitter[0]
    s.wire(q1.emitter, (xl, 2.4)); s.lamp((xl, 2.4), (xl, -0.1), None)
    s.text((xl - 0.6, 2.3), 'L1', ha='right')
    s.wire((3.6, -0.1), (3.6, -0.6), (xl, -0.6)); s.wire((xl, -0.1), (xl, -1.6)); s.term((xl, -1.6), r'$V^{-}$', 'bottom')
    # PC2: drawn with arrows from the lamp side
    s.R((7.9, 2.4), (7.9, -0.1), None)
    for dy in (0.35, -0.15):
        s.add(elm.Arrow(headwidth=0.14, headlength=0.18, lw=1.0).at((7.9 - 1.05, 1.15 + dy + 0.45)).to((7.9 - 0.4, 1.15 + dy)))
    s.text((8.4, 1.15), 'PC2', ha='left')
    s.wire((7.9, -0.1), (7.9, -1.6)); s.term((7.9, -1.6), sub('V', '2'), 'bottom')
    u2 = s.opamp((10.2, 4.25), 'U2'); n2, p2, o2 = u2.in1, u2.in2, u2.out
    m = (9.4, n2[1])
    s.wire((7.9, 2.4), (7.9, n2[1]), n2)
    jo = out_term(s, o2, dx=1.8, jx=0.7)
    s.loop(m, jo, n2[1] + 1.6, 'R', 'R5')
    s.wire(p2, (9.6, p2[1]))
    s.wire((9.6, p2[1]), (9.6, 2.6)); s.R((9.6, 2.6), (9.6, 0.4), 'R4', loc='right'); s.gnd((9.6, 0.4))
    s.dot(Pn, (xl, -0.6))
    return s, [r'$V_{\mathrm{OUT}} = -\dfrac{R5}{R1\,|V^{-}|}\,V_1 V_2$   ($V_1 > 0$; $V_2$ either polarity)',
               r'With R5 = R1 $\cdot$ $|V^{-}|$ / 10 V this gives $V_{\mathrm{OUT}} = -V_1 V_2$ / 10 V',
               r'U1 drives lamp L1 until photocell PC1 balances the current from $V_1$ through R1, so PC1 (and the matched',
               r'cell PC2, lit by the same lamp) has a resistance inversely proportional to $V_1$;  U2 scales $V_2$ by R5/PC2',
               'Slow (lamp and photocell response) but simple; PC1 and PC2 must be matched and share the same light']


@circuit(76, P, 'Long-Interval Timer')
def c76():
    s = Sch()
    u = s.opamp((5.0, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    xs = 3.6; S = (xs, 0)
    s.wire(S, n)
    yc, ysw = 2.0, 3.3
    K = (6.4, yc); M = (8.6, yc)
    s.wire(S, (xs, ysw)); s.C((xs, yc), K, 'C1', loc='bottom'); s.SW((xs, ysw), (K[0], ysw), 'RESET')
    s.wire((K[0], ysw), K)
    s.D(M, K, 'D1', loc='bottom'); s.D(M, (11.0, yc), 'D2', loc='bottom'); s.gnd((11.0, yc), lead=0.5)
    O = (8.6, o[1])
    s.wire(o, O); s.R(M, O, 'R5', loc='left')
    s.D(O, (11.0, O[1]), 'D3', loc='bottom'); V = (11.0, O[1])
    s.wire(V, (12.4, O[1])); s.term((12.4, O[1]), VOUT, 'right')
    s.R(V, (V[0], -3.4), sub('R', 'L'), loc='right'); s.gnd((V[0], -3.4))
    yn = -5.6
    s.wire(S, (xs, -0.6)); s.R((xs, -0.6), (xs, yn), 'R4', loc='left')
    D = (4.4, -3.6)
    s.wire(p, (4.4, p[1])); s.R((4.4, p[1]), D, 'R3', loc='right')
    s.R(D, (6.9, D[1]), 'R2', loc='bottom'); s.gnd((6.9, D[1]), lead=0.5)
    s.R(D, (4.4, yn), 'R1', loc='right')
    s.wire((xs, yn), (6.2, yn)); s.term((6.2, yn), r'$V^{-}$', 'right')
    s.dot(S, (xs, yc), K, M, O, V, D, (4.4, yn))
    return s, ['Opening RESET starts the interval.  R4 draws a small, nearly constant current from the summing node;',
               'U1 supplies it through R5, D1 and C1, so the C1/D1 node ramps up.  When it nears ground, D2 clamps the',
               'R5/D1 node, D1 cuts off, the loop opens and the output switches high, turning D3 on.',
               'The delay is proportional to C1 and to R4 (it scales with C1 R4).',
               'R1 and R2 set the reference level at the (+) input;  C1 must be a low-leakage capacitor']


@circuit(77, P, 'Fast Zero-Crossing Detector with Logic-Level Output')
def c77():
    s = Sch()
    u = s.opamp((5.0, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    jn = X(n, -0.8)
    s.term((0.0, 0), VIN); s.R((0.0, 0), (2.8, 0), 'R1'); s.wire((2.8, 0), n)
    # antiparallel clamp diodes from (-) to ground, drawn above the input
    xa, xb, y0, y1 = 2.0, jn[0], 1.2, 3.4
    s.wire(jn, (xb, y0)); s.wire((xb, y0), (xa, y0))
    s.D((xa, y0), (xa, y1), 'D1', loc='left'); s.D((xb, y1), (xb, y0), 'D2', loc='right')
    s.wire((xa, y1), (xb, y1), (xb + 1.2, y1)); s.gnd((xb + 1.2, y1), lead=0.5)
    s.wire(p, X(p, -0.8)); s.gnd(X(p, -0.8), lead=0.5)
    Z = (9.6, o[1])
    s.R(o, Z, 'R2')
    s.Z((Z[0], Z[1] - 2.6), Z, 'D3', loc='right'); s.gnd((Z[0], Z[1] - 2.6))
    s.wire(Z, (11.2, Z[1])); s.term((11.2, Z[1]), VOUT, 'right')
    s.dot(jn, (xb, y0), (xb, y1), Z)
    return s, [r'$V_{\mathrm{OUT}}$ switches as $V_{\mathrm{IN}}$ crosses zero: low for $V_{\mathrm{IN}} > 0$, high for $V_{\mathrm{IN}} < 0$',
               r'R2 and zener D3 clamp the output to logic levels (about $+V_{\mathrm{Z}}$ and $-0.7$ V)',
               'D1 and D2 hold the inverting input within a diode drop of ground, so large inputs do not overdrive the op amp',
               'Speed depends on the op-amp slew rate and the input overdrive; a dedicated comparator is faster still']


@circuit(78, P, 'Bootstrapped Follower for a Piezoelectric Sensor')
def c78():
    s = Sch()
    u = s.opamp((5.6, 1.25), 'U1'); n, p, o = u.in1, u.in2, u.out      # - at 1.25, + at 0
    Bn = (4.6, 0); Xn = (1.0, 0)
    s.wire(Bn, p)
    s.add(elm.Crystal().at(Bn).to((Bn[0], -2.6)))
    s.text((Bn[0] + 0.55, -1.3), 'sensor', ha='left')
    s.gnd((Bn[0], -2.6))
    s.R(Xn, Bn, 'R2', loc='bottom')
    s.R(Xn, (Xn[0], -2.6), 'R1', loc='left'); s.gnd((Xn[0], -2.6))
    jo = out_term(s, o, dx=2.0, jx=0.9)
    yt = 3.4
    q = (5.0, n[1]); s.wire(n, q, (q[0], 2.2))
    s.wire((q[0], 2.2), (q[0], yt)); s.R((q[0], yt), (jo[0], yt), 'R3'); s.wire((jo[0], yt), jo)
    s.wire(Xn, (Xn[0], 1.0)); s.C((Xn[0], 1.0), (Xn[0], 4.8), 'C1', loc='left')
    s.wire((Xn[0], 4.8), (jo[0], 4.8), (jo[0], yt))
    s.dot(Bn, Xn, (jo[0], yt))
    return s, [r'Low-frequency cutoff:   $f_{\mathrm{L}} = \dfrac{1}{2\pi\,R1\,C1}$',
               'C1 bootstraps R2 from the output, so at signal frequencies R2 carries almost no current and the',
               'input resistance seen by the sensor is many times R2;  R1 provides the DC path for the bias current',
               'R3 (equal to R1 + R2) balances bias currents']


@circuit(79, P, 'Transistor Temperature Probe Amplifier')
def c79():
    s = Sch()
    yt, yb = 4.4, -4.4
    s.wire((-0.8, yt), (2.0, yt)); s.gnd((-0.8, yt), lead=0.5)
    M = (0.0, 0.0)
    s.R((0.0, yt), M, 'R1', loc='left'); s.R(M, (0.0, yb), 'R2', loc='left')
    q1 = s.npn((2.6, 2.6), None)
    s.text((3.75, 2.6), 'Q1 (probe)', ha='left')
    xe = q1.emitter[0]; E = (xe, 1.25)
    s.wire(q1.collector, (xe, yt), (2.0, yt)); s.wire(q1.base, (2.0, 2.6), (2.0, yt))
    s.wire(q1.emitter, E)
    s.RV(M, (xe, 0.0), 'R3', loc='bottom'); s.wire((xe, 0.0), E)
    u = s.opamp((7.6, 0.0), 'U1', plus_top=True)       # - at 0, + at 1.25
    s.wire(E, u.in2)
    Nn = (6.4, 0.0); jx = (7.0, 0.0)
    s.wire((4.7, 0.0), u.in1)
    s.R(Nn, (6.4, -2.6), 'R4', loc='left'); s.gnd((6.4, -2.6))
    s.R((4.7, 0.0), (4.7, yb), 'R5', loc='left')
    jo = out_term(s, u.out, dx=2.0, jx=0.8)
    yf = -1.7
    s.wire(jx, (jx[0], yf)); s.RV((jx[0], yf), (jo[0], yf), 'R6', loc='bottom'); s.wire((jo[0], yf), jo)
    s.wire((-0.8, yb), (4.7, yb)); s.term((-0.8, yb), r'$V^{-}$')
    s.dot(M, E, (0.0, yt), (2.0, yt), Nn, jx, (0.0, yb))
    return s, [r'Q1 is the sensor: its base-emitter voltage falls by about 2 mV/$^\circ$C',
               r'Gain $= 1 + \dfrac{R6}{R4 \parallel R5}$;   R5 to $V^{-}$ adds an offset that R3 trims for 0 V at the reference temperature',
               'R6 sets the scale factor (output millivolts per degree)']


@circuit(80, P, 'Photodiode Transimpedance Amplifier (Reverse-Biased)')
def c80():
    s = Sch()
    u = s.opamp((5.0, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    jn = (4.2, 0)
    s.wire((2.4, 0), n)
    s.PD((2.4, -3.0), (2.4, 0), 'D1', loc='left'); s.wire((2.4, -3.0), (2.4, -3.6)); s.term((2.4, -3.6), r'$V^{-}$', 'bottom')
    s.arrow((3.6, 0.45), (2.8, 0.45)); s.text((3.2, 0.6), sub('I', 'D'), va='bottom')
    jo = out_term(s, o)
    s.loop(jn, jo, 2.0, 'R', 'R1')
    s.wire(p, X(p, -0.6)); s.gnd(X(p, -0.6), lead=0.5)
    return s, [r'$V_{\mathrm{OUT}} = R1\,I_{\mathrm{D}}$',
               'Reverse bias lowers the photodiode capacitance for a faster response, at the cost of some dark current']


@circuit(81, P, 'Photodiode Transimpedance Amplifier (Zero Bias)')
def c81():
    s = Sch()
    u = s.opamp((5.0, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    jn = (4.0, 0); jp = (4.0, p[1])
    s.wire((2.6, 0), n); s.wire((2.6, p[1]), p)
    s.PD((2.6, p[1]), (2.6, 0), 'D1', loc='left')
    jo = out_term(s, o)
    s.loop(jn, jo, 2.0, 'R', 'R1')
    s.R(jp, (jp[0], -3.8), 'R2', loc='right'); s.gnd((jp[0], -3.8))
    s.dot(jp)
    return s, [r'$V_{\mathrm{OUT}} \approx R1\,I_{\mathrm{D}}$   (R2 = R1 balances bias currents)',
               'With almost no voltage across the photodiode its leakage (dark) current is negligible']


@circuit(82, P, 'Bootstrapped AC Voltage Follower')
def c82():
    s = Sch()
    u = s.opamp((5.0, 1.25), 'U1'); n, p, o = u.in1, u.in2, u.out     # - at 1.25, + at 0
    Bn = (4.0, 0)
    s.term((0.0, 0), VIN); s.C((0.0, 0), Bn, 'C1'); s.wire(Bn, p)
    jo = X(o, 0.7); jb = X(o, 1.4)
    s.wire(o, X(o, 2.6)); s.term(X(o, 2.6), VOUT, 'right')
    q = X(n, -0.5); s.wire(n, q, (q[0], 3.0), (jo[0], 3.0), jo)
    Mn = (4.0, -2.8)
    s.R(Bn, Mn, 'R1', loc='left'); s.R(Mn, (4.0, -5.4), 'R2', loc='left'); s.gnd((4.0, -5.4))
    s.C(Mn, (jb[0], Mn[1]), 'C2', loc='bottom'); s.wire((jb[0], Mn[1]), jb)
    s.dot(Bn, jo, jb, Mn)
    return s, ['C2 drives the R1/R2 junction with the output, so almost no signal appears across R1 and the',
               'input resistance is many times R1 + R2;  R1 and R2 still provide the DC bias path (R1 = R2)',
               r'Low-frequency corner set by C1 and the bootstrapped input resistance']
