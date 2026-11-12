from lib import Sch, X, VIN, VOUT, sub
from reg import circuit
from c_basic import out_term, follower, gnd_plus
P = 'Signal Processing'
INP = r'$\mathrm{IN}+$'
INM = r'$\mathrm{IN}-$'
EIN = sub('E', 'IN')
EOUT = sub('E', 'OUT')


def buf(s, plus_y, x=2.0, label='U1', term_x=0.4, text=None, dy=1.0):
    """Voltage follower with (+) on top at plus_y; returns output junction."""
    u = s.opamp((x, plus_y - 1.25), label, plus_top=True)
    s.term((term_x, plus_y), text); s.wire((term_x, plus_y), u.in2)
    jo = X(u.out, 0.6)
    follower(s, u, jo, dy=dy)
    s.wire(u.out, X(u.out, 0.83)); s.dot(jo)
    return u, X(u.out, 0.83)


@circuit(43, P, 'Buffered Difference Amplifier')
def c43():
    s = Sch()
    u1, a = buf(s, 4.25, label='U1', text=INM)
    u2, b = buf(s, -3.0, label='U2', text=INP)
    u3 = s.opamp((9.0, 0), 'U3'); n, p, o = u3.in1, u3.in2, u3.out
    A = (7.6, a[1]); B = (7.6, b[1])
    s.R(a, A, 'R1'); s.wire(A, (A[0], 0), n)
    jo = out_term(s, o, dx=2.4, jx=1.0)
    s.R(A, (jo[0], A[1]), 'R2'); s.wire((jo[0], A[1]), jo); s.dot(A)
    s.R(b, B, 'R3', loc='bottom'); s.wire(B, (B[0], p[1]), p)
    s.R(B, (B[0], -6.2), 'R4', loc='right'); s.gnd((B[0], -6.2)); s.dot(B)
    return s, [r'$V_{\mathrm{OUT}} = \dfrac{R2}{R1}\,(V_{\mathrm{IN+}} - V_{\mathrm{IN-}})$   with   $\dfrac{R4}{R3} = \dfrac{R2}{R1}$',
               'U1 and U2 give both inputs a very high input impedance',
               'Common-mode rejection is set by how well R2/R1 matches R4/R3']


@circuit(44, P, 'Difference Amplifier with Single-Resistor Gain Control')
def c44():
    s = Sch()
    u1, a = buf(s, 2.5, label='U1', text=INP, dy=1.0)
    u2, b = buf(s, -2.5, label='U2', text=INM, dy=1.0)
    u3 = s.opamp((9.4, -1.25), 'U3', plus_top=True); n, p, o = u3.in1, u3.in2, u3.out   # + at y=0
    A = (8.2, a[1]); Bn = (8.2, b[1])
    s.R(a, (7.4, a[1]), 'R1'); s.wire((7.4, a[1]), A, (A[0], p[1]), p); s.dot(A)
    s.R(b, (7.4, b[1]), 'R3', loc='bottom'); s.wire((7.4, b[1]), Bn, (Bn[0], n[1]), n); s.dot(Bn)
    s.R(Bn, (Bn[0], -5.2), 'R4', loc='left'); s.gnd((Bn[0], -5.2))
    Pn = (8.2, 4.8)
    s.R(A, Pn, 'R2', loc='left')
    # U4: inverting stage from V_OUT back to the reference node P
    u4 = s.opamp((12.2, Pn[1] + 0.625), 'U4', left=True)
    s.wire(u4.out, Pn); jp = X(u4.out, -0.5); s.dot(jp)
    jn = X(u4.in1, 0.6)
    s.wire(u4.in1, jn)
    s.loop(jn, jp, u4.in1[1] + 1.6, 'R', 'R6')
    s.loop(jn, jp, u4.in1[1] + 2.9, 'C', 'C1', dots=False)
    s.wire(u4.in2, X(u4.in2, 0.6)); s.gnd(X(u4.in2, 0.6), lead=0.4)
    jo = (13.6, o[1])
    s.wire(o, (15.0, o[1])); s.term((15.0, o[1]), VOUT, 'right'); s.dot(jo)
    s.wire(jn, (jo[0], jn[1])); s.R((jo[0], jn[1]), jo, 'R5', loc='right')
    return s, [r'$V_{\mathrm{OUT}} = \dfrac{R5}{R6}\,(V_{\mathrm{IN+}} - V_{\mathrm{IN-}})$   with R1 = R2 = R3 = R4',
               'U4 feeds an inverted copy of the output back to the reference end of R2; U3 runs open-loop inside that loop',
               'Gain is set by R5 alone without disturbing the matched resistors; C1 keeps the loop stable']


@circuit(45, P, 'Attenuating Difference Amplifier for High Common-Mode Voltage')
def c45():
    s = Sch()
    u1 = s.opamp((3.0, 0.625), 'U1'); n1, p1, o1 = u1.in1, u1.in2, u1.out
    j1 = X(n1, -0.7)
    s.term((-0.4, n1[1]), INP); s.R((-0.4, n1[1]), j1, 'R1'); s.wire(j1, n1)
    jo1 = X(o1, 0.6)
    s.loop(j1, jo1, n1[1] + 1.7, 'R', 'R3')
    s.loop(j1, jo1, n1[1] + 3.0, 'C', 'C1', dots=False)
    q = X(p1, -0.7); s.wire(p1, q); s.R(q, X(q, 0, -2.3), 'R2', loc='left'); s.gnd(X(q, 0, -2.3))
    u2 = s.opamp((11.2, 0.0), 'U2'); n2, p2, o2 = u2.in1, u2.in2, u2.out
    S2 = (9.6, n2[1]); j2 = X(n2, -0.6)
    s.R(jo1, (8.4, o1[1]), 'R4'); s.wire(o1, jo1)
    s.wire((8.4, o1[1]), S2, n2)
    s.dot(S2, j2)
    jo2 = out_term(s, o2, dx=2.2, jx=0.7)
    s.loop(j2, jo2, n2[1] + 1.7, 'R', 'R6', dots=False)
    s.loop(j2, jo2, n2[1] + 3.0, 'C', 'C2', dots=False)
    q2 = X(p2, -0.6); s.wire(p2, q2); s.R(q2, X(q2, 0, -2.3), 'R5', loc='right'); s.gnd(X(q2, 0, -2.3))
    yb = -4.6
    s.term((-0.4, yb), INM); s.wire((-0.4, yb), (3.6, yb)); s.R((3.6, yb), (6.4, yb), 'R7', loc='bottom')
    s.wire((6.4, yb), (S2[0], yb), S2)
    return s, [r'$V_{\mathrm{OUT}} = \dfrac{R6}{R7}\,(V_{\mathrm{IN+}} - V_{\mathrm{IN-}})$   with R3 = R4 and R1 = R6 = R7 = 10 R3',
               'Both op-amp inputs sit at ground or virtual ground.  The common-mode range is wide because U1 runs',
               r"at a gain of 1/10, so its output swings only $V_{\mathrm{IN+}}/10$; beyond that the limit is the resistors' voltage rating",
               'Common-mode rejection depends on matching R1 to R7 and R3 to R4; C1 and C2 limit the bandwidth']


@circuit(46, P, 'Three-Op-Amp Instrumentation Amplifier')
def c46():
    s = Sch()
    u1 = s.opamp((2.0, 3.0), 'U1', plus_top=True)     # + at 4.25
    u2 = s.opamp((2.0, -3.0), 'U2')                   # - at -3, + at -4.25
    s.term((0.0, u1.in2[1]), INP); s.wire((0.0, u1.in2[1]), u1.in2)
    s.term((0.0, u2.in2[1]), INM); s.wire((0.0, u2.in2[1]), u2.in2)
    A = (5.0, u1.out[1]); D = (5.0, u2.out[1]); B = (5.0, 1.0); C = (5.0, -1.0)
    s.wire(u1.out, A); s.wire(u2.out, D)
    s.R(A, B, 'R1', loc='right'); s.R(B, C, sub('R', 'G'), loc='right'); s.R(C, D, 'R2', loc='right')
    s.wire(u1.in1, (1.4, u1.in1[1]), (1.4, B[1]), B); s.wire(u2.in1, (1.4, u2.in1[1]), (1.4, C[1]), C)
    s.dot(A, B, C, D)
    u3 = s.opamp((9.0, -0.625), 'U3', plus_top=True)  # + at 0.625
    Pn = (8.2, A[1]); Q = (8.2, D[1])
    s.R(A, (7.6, A[1]), 'R3'); s.wire((7.6, A[1]), Pn, (Pn[0], u3.in2[1]), u3.in2)
    s.R(Pn, (10.8, Pn[1]), 'R4'); s.gnd((10.8, Pn[1]), lead=0.5); s.dot(Pn)
    s.R(D, (7.6, D[1]), 'R5', loc='bottom'); s.wire((7.6, D[1]), Q, (Q[0], u3.in1[1]), u3.in1)
    jo = out_term(s, u3.out, dx=2.2, jx=0.8)
    s.R(Q, (jo[0], Q[1]), 'R6', loc='bottom'); s.wire((jo[0], Q[1]), jo); s.dot(Q)
    return s, [r'$V_{\mathrm{OUT}} = \dfrac{R4}{R3}\left(1 + \dfrac{2\,R1}{R_{\mathrm{G}}}\right)(V_{\mathrm{IN+}} - V_{\mathrm{IN-}})$',
               r'with R1 = R2, R3 = R5 and R4 = R6;   one resistor ($R_{\mathrm{G}}$) sets the gain',
               'U1 and U2 amplify the difference signal but pass common-mode voltage at unity gain; U3 removes it',
               'Common-mode rejection depends on matching R3 to R5 and R4 to R6']


@circuit(47, P, 'Two-Op-Amp Instrumentation Amplifier')
def c47():
    s = Sch()
    u1 = s.opamp((3.0, 0), 'U1'); u2 = s.opamp((10.0, 0), 'U2')
    n1 = X(u1.in1, -0.7); s.wire(n1, u1.in1)
    s.R(n1, (0.0, 0), 'R1'); s.gnd((0.0, 0), lead=0.5)
    T = (5.8, 1.6); jo1 = (5.8, u1.out[1])
    s.wire(u1.out, jo1, T)
    s.wire(n1, (n1[0], T[1])); s.R((n1[0], T[1]), T, 'R2'); s.dot(n1, T)
    n2 = X(u2.in1, -0.7); s.wire(n2, u2.in1)
    s.R(T, (n2[0], T[1]), 'R3'); s.wire((n2[0], T[1]), n2)
    jo2 = out_term(s, u2.out, dx=2.0, jx=0.8)
    s.R((n2[0], T[1]), (jo2[0], T[1]), 'R4'); s.wire((jo2[0], T[1]), jo2); s.dot((n2[0], T[1]))
    for u, t, x in ((u1, INM, 0.9), (u2, INP, 7.6)):
        q = X(u.in2, -0.7)
        s.wire(u.in2, q, (q[0], -2.4), (x, -2.4)); s.term((x, -2.4), t)
    return s, [r'$V_{\mathrm{OUT}} = \left(1 + \dfrac{R4}{R3}\right)(V_{\mathrm{IN+}} - V_{\mathrm{IN-}})$   with R1 = R4 and R2 = R3',
               'Both inputs go straight to (+) inputs, so the input impedance is very high',
               'Common-mode rejection depends on how well R2/R1 matches R3/R4']


@circuit(48, P, 'Thermistor Bridge Amplifier with T-Network Feedback')
def c48():
    s = Sch()
    xl, xr, yt, yb = 0.0, 2.4, 4.0, -4.2
    s.wire((xl, yt), (xr, yt)); s.rail((1.2, yt), r'$V^{+}$', lead=0.6); s.dot((1.2, yt))
    A = (xl, 0.0); B = (xr, -1.25)
    s.R((xl, yt), A, 'R1', loc='left'); s.RT(A, (xl, yb), sub('RT', '1'), loc='left'); s.gnd((xl, yb))
    s.RT((xr, yt), B, sub('RT', '2'), loc='right'); s.R(B, (xr, yb), 'R2', loc='right'); s.gnd((xr, yb))
    u = s.opamp((7.6, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    jn = (6.8, 0); jp = (6.8, p[1])
    s.wire(A, (3.4, 0)); s.R((3.4, 0), jn, 'R3'); s.wire(jn, n)
    s.wire(B, (3.4, B[1])); s.R((3.4, B[1]), jp, 'R4', loc='bottom'); s.wire(jp, p)
    s.R(jp, (jp[0], -4.2), 'R5', loc='right'); s.gnd((jp[0], -4.2)); s.dot(A, B, jp)
    T = (10.6, 2.2); jo = (10.6, o[1])
    s.wire(jn, (jn[0], T[1])); s.R((jn[0], T[1]), T, 'R6'); s.dot(jn, T)
    s.R(T, jo, 'R7', loc='left'); s.R(T, (13.2, T[1]), 'R8'); s.gnd((13.2, T[1]), lead=0.5)
    s.wire(o, (12.6, o[1])); s.term((12.6, o[1]), VOUT, 'right'); s.dot(jo)
    return s, [r'Effective feedback resistance   $R_{\mathrm{F}} = R6 + R7 + \dfrac{R6\,R7}{R8}$;   gain $\approx R_{\mathrm{F}}/R3$  (R3 = R4)',
               r'The T network gives a large $R_{\mathrm{F}}$ from moderate resistor values; R8 adjusts the gain',
               'Make R5 equal to the effective feedback resistance and trim it for best common-mode rejection',
               r'$RT_1$ and $RT_2$ are thermistors (e.g. sensing and reference); the output is zero at bridge balance']


@circuit(49, P, 'Bridge Amplifier with a Sensor in Each Arm')
def c49():
    s = Sch()
    u = s.opamp((6.0, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    jn = X(n, -0.8); jp = X(p, -0.8)
    V = (0.6, -0.625)
    s.term(V, r'$V^{+}$'); J = (1.4, -0.625); s.wire(V, J); s.dot(J)
    s.wire(J, (J[0], n[1])); s.RT((J[0], n[1]), jn, sub('RT', '1')); s.wire(jn, n)
    s.wire(J, (J[0], p[1])); s.R((J[0], p[1]), jp, 'R2', loc='bottom'); s.wire(jp, p)
    s.RT(jp, (jp[0], -4.0), sub('RT', '2'), loc='left'); s.gnd((jp[0], -4.0)); s.dot(jp)
    jo = out_term(s, o)
    s.loop(jn, jo, n[1] + 1.9, 'R', 'R1')
    return s, [r'$V_{\mathrm{OUT}} = V^{+}\left[\left(1 + \dfrac{R1}{RT_1}\right)\dfrac{RT_2}{R2 + RT_2} - \dfrac{R1}{RT_1}\right]$',
               r'When the two arms track ($R1/RT_1 = R2/RT_2$) this reduces to $V_{\mathrm{OUT}} = V^{+}\,(1 - R1/RT_1)$',
               r'$RT_1$ and $RT_2$ are the sensing elements (thermistors shown)']


@circuit(50, P, 'Precision Rectifier (Ideal Diode)')
def c50():
    s = Sch()
    u = s.opamp((4.0, -1.25), 'U1', plus_top=True); n, p, o = u.in1, u.in2, u.out   # + at 0
    s.term((1.0, p[1]), EIN); s.wire((1.0, p[1]), p)
    K = (o[0] + 1.0, o[1] + 2.4)
    s.wire(o, (K[0], o[1])); s.D((K[0], o[1]), K, 'D1', loc='right')
    q = X(n, -0.6)
    s.wire(n, q, (q[0], n[1] - 1.4), (K[0] + 1.2, n[1] - 1.4), (K[0] + 1.2, K[1]))
    s.wire(K, (K[0] + 2.4, K[1])); s.term((K[0] + 2.4, K[1]), EOUT, 'right'); s.dot(K, (K[0] + 1.2, K[1]))
    return s, [r'$E_{\mathrm{OUT}} = E_{\mathrm{IN}}$ for $E_{\mathrm{IN}} > 0$;   output follows the load (normally 0 V) for $E_{\mathrm{IN}} < 0$',
               'D1 sits inside the feedback loop, so its forward drop is divided by the open-loop gain',
               'For negative inputs the op-amp output swings to its negative limit; recovery from that limits the speed',
               r'A load resistance from $E_{\mathrm{OUT}}$ to ground defines the output while D1 is off']


@circuit(51, P, 'Active Clamp to a Reference Voltage')
def c51():
    s = Sch()
    u = s.opamp((5.0, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    yt = 2.4
    jn = X(n, -0.7)
    E = (jn[0], yt)
    s.term((0.0, yt), EIN); s.R((0.0, yt), (2.8, yt), 'R1'); s.wire((2.8, yt), E)
    s.wire(E, jn, n)
    K = (o[0] + 1.0, yt)
    s.wire(E, K); s.D(K, (K[0], o[1]), 'D1', loc='right'); s.wire((K[0], o[1]), o)
    s.wire(K, (K[0] + 1.6, yt)); s.term((K[0] + 1.6, yt), EOUT, 'right'); s.dot(E, K)
    s.term((1.6, p[1]), sub('E', 'REF')); s.wire((1.6, p[1]), p)
    return s, [r'$E_{\mathrm{OUT}} = E_{\mathrm{IN}}$ while $E_{\mathrm{IN}} < E_{\mathrm{REF}}$;   otherwise $E_{\mathrm{OUT}}$ is held at $E_{\mathrm{REF}}$',
               'When the input tries to rise past the reference, the op-amp output falls, D1 conducts and',
               'the loop pulls the output node back to E_REF; D1 drops no voltage because it is inside the loop'.replace('E_REF', r'$E_{\mathrm{REF}}$'),
               'R1 limits the input current the op amp must sink while clamping']


@circuit(52, P, 'Inverting Half-Wave Precision Rectifier')
def c52():
    s = Sch()
    u = s.opamp((5.0, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    jA = (3.6, 0); jB = (4.3, 0)
    s.term((0.0, 0), EIN); s.R((0.0, 0), (2.6, 0), 'R1'); s.wire((2.6, 0), n)
    O = (8.2, o[1]); K = (8.2, 1.8)
    s.wire(o, O); s.D(O, K, 'D1', loc='right')
    s.wire(jB, (jB[0], K[1])); s.R((jB[0], K[1]), K, 'R2')
    s.loop((jB[0], K[1]), K, 3.1, 'C', 'C1')
    s.wire(K, (9.8, K[1])); s.term((9.8, K[1]), EOUT, 'right')
    yb = -4.2
    s.D((jA[0], yb), (O[0], yb), 'D2', loc='bottom')
    s.wire(jA, (jA[0], yb)); s.wire((O[0], yb), O)
    q = (4.6, p[1]); s.wire(p, q); s.R(q, (q[0], -3.0), 'R3', loc='right'); s.gnd((q[0], -3.0))
    s.dot(jA, jB, O)
    return s, [r'$E_{\mathrm{OUT}} = -\dfrac{R2}{R1}\,E_{\mathrm{IN}}$ for $E_{\mathrm{IN}} < 0$;   $E_{\mathrm{OUT}} = 0$ for $E_{\mathrm{IN}} > 0$',
               'For positive inputs D2 closes the loop and keeps the op amp out of saturation, so it recovers quickly',
               r'C1 trims the high-frequency response;  R3 $\approx$ R1 $\parallel$ R2 balances bias currents']


def halfwave(s, x0, y0, names):
    """Inverting half-wave stage whose output node H = -E_IN for E_IN > 0, else 0.
    Returns (input node, H)."""
    rin, rfb, cfb, d1, d2, un = names
    u = s.opamp((x0 + 4.0, y0), un); n, p, o = u.in1, u.in2, u.out
    jA = (x0 + 2.6, y0); jn = (x0 + 3.3, y0)
    T = (x0 - 0.2, y0)
    s.R(T, (x0 + 2.0, y0), rin); s.wire((x0 + 2.0, y0), n)
    O = (x0 + 7.2, o[1]); H = (x0 + 7.2, y0 + 2.0)
    s.wire(o, O); s.D(H, O, d1, loc='right')
    s.wire(jn, (jn[0], H[1])); s.R((jn[0], H[1]), H, rfb)
    if cfb:
        s.loop((jn[0], H[1]), H, y0 + 3.3, 'C', cfb)
    yb = y0 - 3.0
    s.D(O, (O[0], yb), d2, loc='right'); s.wire((O[0], yb), (jA[0], yb), jA)
    s.wire(p, X(p, -0.6)); s.gnd(X(p, -0.6), lead=0.5)
    s.dot(jA, jn, O, H if not cfb else jn)
    if cfb:
        s.dot(H)
    return T, H


@circuit(53, P, 'Precision Full-Wave Rectifier with Averaging Output')
def c53():
    s = Sch()
    T, H = halfwave(s, 0.0, 0.0, ('R1', 'R2', 'C1', 'D1', 'D2', 'U1'))
    s.term((-1.0, 0), EIN); s.wire((-1.0, 0), T); s.dot(T)
    u2 = s.opamp((12.0, H[1]), 'U2'); n2, p2, o2 = u2.in1, u2.in2, u2.out
    S = (10.6, H[1]); jf = (11.3, H[1])
    s.R(H, (9.8, H[1]), 'R3', loc='bottom'); s.wire((9.8, H[1]), n2)
    yb = -4.4
    s.wire(T, (T[0], yb)); s.R((3.0, yb), (6.0, yb), 'R4', loc='bottom'); s.wire((T[0], yb), (3.0, yb))
    s.wire((6.0, yb), (S[0], yb), S)
    s.wire(p2, X(p2, -0.5)); s.gnd(X(p2, -0.5), lead=0.5)
    jo = out_term(s, o2, dx=2.0, label=EOUT, jx=0.7)
    s.loop(jf, jo, H[1] + 1.7, 'R', 'R5')
    s.wire(jf, (jf[0], H[1] + 3.0)); s.Cpol((jf[0], H[1] + 3.0), (jo[0], H[1] + 3.0), 'C2'); s.wire((jo[0], H[1] + 3.0), (jo[0], H[1] + 1.7))
    s.dot(S, (jf[0], H[1] + 1.7), (jo[0], H[1] + 1.7))
    return s, [r'$E_{\mathrm{OUT}} = \dfrac{R5}{R4}\,\overline{|E_{\mathrm{IN}}|}$   with R1 = R2 = R4 = 2 R3',
               'U1 delivers the inverted positive half-cycles at the D1–R2 node; U2 adds them at twice the weight of the input, giving a full-wave output',
               r'C2 averages the result.  For an rms reading of sine waves make R5 $\approx$ 1.11 R4  ($\pi / 2\sqrt{2}$)',
               'Leave out C2 for a fast full-wave rectifier; C1 trims the high-frequency response of U1']


@circuit(54, P, 'Low-Drift Peak Detector')
def c54():
    s = Sch()
    u1 = s.opamp((3.0, 0), 'U1'); n1, p1, o1 = u1.in1, u1.in2, u1.out
    s.term((0.4, p1[1]), VIN); s.wire((0.4, p1[1]), p1)
    jn = X(n1, -0.6); s.wire(jn, n1)
    O1 = (5.8, o1[1]); s.wire(o1, O1)
    s.loop(jn, O1, 1.4, 'D', 'D3')
    M = (8.2, o1[1]); N = (10.6, o1[1])
    s.D(O1, M, 'D1', loc='bottom'); s.D(M, N, 'D2', loc='bottom')
    s.C(N, (N[0], -2.4), 'C1', loc='right'); s.gnd((N[0], -2.4))
    u2 = s.opamp((13.4, o1[1] - 1.25), 'U2', plus_top=True)
    s.R(N, (12.6, N[1]), 'R2'); s.wire((12.6, N[1]), u2.in2)
    J = (16.2, u2.out[1])
    s.wire(u2.out, (17.4, J[1])); s.term((17.4, J[1]), VOUT, 'right')
    yb = -4.4
    q = (12.8, u2.in1[1]); s.wire(u2.in1, q, (q[0], yb))
    s.wire(M, (M[0], yb)); s.R((M[0], yb), (11.4, yb), 'R1', loc='bottom'); s.wire((11.4, yb), (q[0], yb), (J[0], yb), J)
    s.wire(J, (J[0], 3.0)); s.R((J[0], 3.0), (jn[0], 3.0), 'R3'); s.wire((jn[0], 3.0), (jn[0], 1.4))
    s.dot(J, M, N, (q[0], yb), (jn[0], 1.4))
    return s, [r'C1 charges to the most positive input;   $V_{\mathrm{OUT}}$ = peak of $V_{\mathrm{IN}}$',
               'R1 holds the D1/D2 junction at the output voltage, so D2 has no bias across it and C1 is not discharged by its leakage',
               'D3 stops U1 from saturating between peaks; R3 closes one loop around both amplifiers so the offset of U2 cancels',
               'Use a low-leakage capacitor for C1 and a low-bias-current op amp for U2']


@circuit(55, P, 'Absolute-Value Circuit with Sign Output')
def c55():
    s = Sch()
    T, H = halfwave(s, 0.0, 0.0, ('R1', 'R2', None, 'D1', 'D2', 'U1'))
    s.term((-1.4, 0), VIN); s.wire((-1.4, 0), T); s.dot(T)
    u2 = s.opamp((12.0, H[1]), 'U2'); n2, p2, o2 = u2.in1, u2.in2, u2.out
    S = (10.6, H[1]); jf = (11.3, H[1])
    s.R(H, (9.8, H[1]), 'R3', loc='bottom'); s.wire((9.8, H[1]), n2)
    yb = -4.2
    s.wire(T, (T[0], yb)); s.R((3.0, yb), (6.0, yb), 'R4', loc='bottom'); s.wire((T[0], yb), (3.0, yb))
    s.wire((6.0, yb), (S[0], yb), S)
    s.wire(p2, X(p2, -0.5)); s.gnd(X(p2, -0.5), lead=0.5)
    jo = out_term(s, o2, dx=2.0, jx=0.7, label=r'$|V_{\mathrm{IN}}|$')
    s.loop(jf, jo, H[1] + 1.7, 'R', 'R5')
    s.dot(S, (T[0], yb))
    # sign comparator
    yc = -7.0
    u3 = s.opamp((4.0, yc - 1.25), 'U3', plus_top=True)       # + at yc
    s.wire((T[0], yb), (T[0], yc), u3.in2)
    s.wire(u3.in1, X(u3.in1, -0.6)); s.gnd(X(u3.in1, -0.6), lead=0.5)
    Z = (8.6, u3.out[1])
    s.R(u3.out, Z, 'R6')
    s.Z((Z[0], Z[1] - 2.4), Z, 'D3', loc='right'); s.gnd((Z[0], Z[1] - 2.4))
    s.wire(Z, (10.4, Z[1])); s.term((10.4, Z[1]), 'SIGN', 'right'); s.dot(Z)
    return s, [r'$|V_{\mathrm{IN}}|$ output $= \dfrac{R5}{R4}\,|V_{\mathrm{IN}}|$   with R1 = R2 = R4 = 2 R3',
               r'SIGN is high (about $V_{\mathrm{Z}}$ of D3) for $V_{\mathrm{IN}} > 0$ and about $-0.7$ V for $V_{\mathrm{IN}} < 0$',
               'U1 and U2 form a precision full-wave rectifier; U3 is a comparator whose output R6 and D3 clamp to logic levels']


def sh_switch(s, c, label):
    """Series 4-terminal N-MOSFET switch, gate down, drain/source leads exactly at c[1]
    (so the signal wires are straight); substrate lead up to the negative supply."""
    m = s.mosfet((c[0], c[1] - 0.25), 'n', 'gate_down', body='out')
    b = m['body']; top = (b[0], b[1] + 0.55)
    s.wire(b, top); s.term(top, r'$V^{-}$', 'top')
    s.text((c[0] - 0.45, c[1] + 0.55), label, ha='right')
    return m


@circuit(56, P, 'Sample-and-Hold')
def c56():
    s = Sch()
    y = 2.0
    s.term((0.0, y), VIN)
    q1 = sh_switch(s, (2.4, y), 'Q1')
    s.wire((0.0, y), q1['drain'])
    H = (4.6, y); s.wire(q1['source'], H)
    s.C(H, (H[0], -1.2), 'C1', loc='right'); s.gnd((H[0], -1.2))
    u = s.opamp((8.2, y - 1.25), 'U1', plus_top=True)
    s.R(H, (7.4, y), 'R1'); s.wire((7.4, y), u.in2)
    jo = out_term(s, u.out, dx=1.8, jx=0.7)
    follower(s, u, jo, dy=1.0)
    g = q1['gate']; s.wire(g, (g[0], -0.4)); s.term((g[0], -0.4), 'SAMPLE', 'bottom')
    s.dot(H)
    return s, [r'While SAMPLE is high Q1 conducts and C1 follows $V_{\mathrm{IN}}$; when it goes low C1 holds the last value',
               'U1 buffers C1 so the load does not discharge it; R1 protects the op-amp input',
               r'The Q1 substrate returns to $V^{-}$, so its body diodes stay reverse-biased for any input or held voltage;',
               r'drive SAMPLE to $V^{+}$ to sample and to $V^{-}$ to hold (a JFET or analog switch can replace Q1)',
               'Droop is set by C1 leakage, switch leakage and U1 bias current; use a low-leakage film capacitor']


@circuit(57, P, 'Low-Leakage Sample-and-Hold')
def c57():
    s = Sch()
    y = 2.0
    s.term((0.0, y), VIN)
    q1 = sh_switch(s, (2.2, y), 'Q1'); q2 = sh_switch(s, (5.8, y), 'Q2')
    s.wire((0.0, y), q1['drain'])
    J = (4.0, y); s.wire(q1['source'], J, q2['drain'])
    H = (7.6, y); s.wire(q2['source'], H)
    s.C(H, (H[0], -1.6), 'C1', loc='left'); s.gnd((H[0], -1.6))
    u = s.opamp((9.0, y - 1.25), 'U1', plus_top=True)
    s.wire(H, u.in2)
    jo = X(u.out, 0.6); s.wire(u.out, X(u.out, 2.4)); s.term(X(u.out, 2.4), VOUT, 'right')
    follower(s, u, jo, dy=1.0)
    jr = X(u.out, 1.3)
    s.wire(J, (J[0], 4.2)); s.R((J[0], 4.2), (jr[0], 4.2), 'R1'); s.wire((jr[0], 4.2), jr)
    ga, gb = q1['gate'], q2['gate']
    yg = -0.3
    s.wire(ga, (ga[0], yg), (gb[0], yg), gb); m = ((ga[0] + gb[0]) / 2, yg)
    s.wire(m, (m[0], -1.0)); s.term((m[0], -1.0), 'SAMPLE', 'bottom')
    s.dot(J, H, jo, jr, m)
    return s, [r'Q1 and Q2 conduct together while sampling; in hold, R1 drives their junction to $V_{\mathrm{OUT}}$',
               'Since the output equals the voltage on C1, Q2 then has almost no voltage across it and adds almost no leakage',
               'Only U1 bias current and the capacitor itself discharge C1: use a low-leakage, low-absorption film type',
               r'Both substrates return to $V^{-}$ so no body diode conducts; drive SAMPLE between $V^{+}$ and $V^{-}$']


@circuit(58, P, 'Integrator with Leakage-Guarded Reset')
def c58():
    s = Sch()
    u = s.opamp((7.0, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    S = (2.5, 0); O = (10.0, o[1])
    s.term((-1.0, 0), VIN); s.R((-1.0, 0), (1.8, 0), 'R1'); s.wire((1.8, 0), S)
    s.R(S, (5.4, 0), 'R3'); s.wire((5.4, 0), n)
    s.wire(o, O); s.wire(O, (11.4, O[1])); s.term((11.4, O[1]), VOUT, 'right')
    yc = 1.9
    s.wire(S, (S[0], yc)); s.C((S[0], yc), (O[0], yc), 'C1', loc='bottom'); s.wire((O[0], yc), O)
    ych = 5.0
    q1 = s.mosfet((4.3, ych + 0.25), 'p', 'gate_up'); q2 = s.mosfet((8.2, ych + 0.25), 'p', 'gate_up')
    s.text((4.3 - 0.35, ych + 1.0), 'Q1', ha='right'); s.text((8.2 - 0.35, ych + 1.0), 'Q2', ha='right')
    J = (6.25, ych)
    s.wire((S[0], yc), (S[0], ych), q1['source']); s.wire(q1['drain'], J, q2['source'])
    s.wire(q2['drain'], (O[0], ych), (O[0], yc))
    s.R(J, (J[0], 3.1), 'R2', loc='right'); s.gnd((J[0], 3.1))
    yr = 6.9
    s.wire(q1['gate'], (q1['gate'][0], yr), (q2['gate'][0], yr), q2['gate'])
    s.wire((q2['gate'][0], yr), (11.4, yr)); s.term((11.4, yr), r'$\overline{\mathrm{RESET}}$', 'right')
    # (+) input network
    Pn = (6.2, p[1]); yt, yb = -2.2, -4.2
    s.wire(p, Pn, (Pn[0], yt))
    s.wire((3.4, yt), (Pn[0], yt))
    s.R((3.4, yt), (3.4, yb), 'R4', loc='left')
    s.C((4.6, yt), (4.6, yb), 'C2', loc='right')
    q3 = s.mosfet((6.45, -3.2), 'p', 'gate_right'); s.text((7.0, -4.05), 'Q3', ha='left')
    s.wire((3.4, yb), q3['source']); s.gnd((4.6, yb), lead=0.4)
    s.wire(q3['gate'], (9.6, q3['gate'][1])); s.term((9.6, q3['gate'][1]), r'$\overline{\mathrm{RESET}}$', 'right')
    s.dot((Pn[0], yt), (4.6, yt), (4.6, yb))
    s.dot(S, O, (S[0], yc), (O[0], yc), J, (q2['gate'][0], yr))
    return s, [r'$V_{\mathrm{OUT}} = -\dfrac{1}{R1\,C1}\int V_{\mathrm{IN}}\,dt$;   pulling $\overline{\mathrm{RESET}}$ low discharges C1 and C2',
               'While integrating, R2 grounds the Q1/Q2 junction: Q2 leakage flows to ground and Q1 has almost no voltage across it',
               'R4 = R1 and C2 = C1 balance bias current and the R3 path;   use MOSFETs without gate-protection diodes',
               'Choose low-leakage, low-absorption capacitors (polypropylene, polystyrene or PTFE)']
