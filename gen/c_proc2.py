from lib import Sch, X, VIN, VOUT, sub
from reg import circuit
from c_basic import out_term, follower, gnd_plus
P = 'Signal Processing'


def composite(s, xs, names):
    """Shared skeleton of the composite (fast + precise) circuits.
    names = (R_S-to-U1, C_U1, R_U1-to-U2+, R_U2+-to-ground).
    Returns S node, U2 (-) node, U2 output junction."""
    r3, c3, r4, r5 = names
    S = (xs, 0)
    s.term((xs - 4.0, 0), VIN); s.R((xs - 4.0, 0), (xs - 1.2, 0), 'R1'); s.wire((xs - 1.2, 0), S)
    u2 = s.opamp((xs + 6.0, 0), 'U2'); n2, p2, o2 = u2.in1, u2.in2, u2.out
    jo = out_term(s, o2, dx=2.0, jx=0.8)
    u1 = s.opamp((xs + 2.0, -4.65), 'U1', plus_top=True)    # + at -3.4
    s.wire(S, (xs, -0.9)); s.R((xs, -0.9), (xs, -3.6), r3, loc='left'); s.wire((xs, -3.6), (xs, -4.65), u1.in1)
    j1 = (xs + 0.8, -4.65)
    jo1 = X(u1.out, 0.5)
    s.loop(j1, jo1, -6.0, 'C', c3, loc='bottom')
    s.wire(u1.in2, X(u1.in2, -0.6)); s.gnd(X(u1.in2, -0.6), lead=0.3)
    Pn = (xs + 5.2, p2[1])
    s.wire(u1.out, (Pn[0], u1.out[1])); s.R((Pn[0], u1.out[1]), Pn, r4, loc='right'); s.wire(Pn, p2)
    s.R(Pn, (xs + 2.8, Pn[1]), r5, loc='bottom'); s.gnd((xs + 2.8, Pn[1]), lead=0.5); s.dot(Pn, S)
    return S, n2, jo


@circuit(59, P, 'Composite Summing Amplifier (Fast with Low Input Current)')
def c59():
    s = Sch(); xs = 3.0
    S, n2, jo = composite(s, xs, ('R3', 'C3', 'R4', 'R5'))
    s.C(S, (xs + 4.6, 0), 'C2'); s.wire((xs + 4.6, 0), n2)
    s.loop(S, jo, 1.8, 'R', 'R2', dots=False)
    s.loop(S, jo, 3.1, 'C', 'C1', dots=False)
    s.dot((xs, 1.8), (jo[0], 1.8))
    return s, [r'$V_{\mathrm{OUT}} = -\dfrac{R2}{R1}\,V_{\mathrm{IN}}$  (add more input resistors to S for a summer)',
               'U1 has very low input current and holds the summing node S at 0 V at DC through the (+) input of U2',
               'U2 is a fast op amp that takes over above the U1 loop bandwidth through C2;  C1 sets the closed-loop bandwidth',
               'U1 adds its gain to the loop, which improves DC accuracy and lets U2 drive the load']
    

@circuit(60, P, 'Composite Integrator (Fast with Low Input Current)')
def c60():
    s = Sch(); xs = 3.0
    S, n2, jo = composite(s, xs, ('R4', 'C4', 'R5', 'R6'))
    M = (xs + 2.6, 0)
    s.R(S, M, 'R2', loc='bottom'); s.C(M, (xs + 5.0, 0), 'C2'); s.wire((xs + 5.0, 0), n2)
    s.loop(M, jo, 1.6, 'C', 'C3', loc='bottom', dots=False)
    s.loop(S, jo, 3.0, 'C', 'C1', loc='bottom', dots=False)
    # output clamp: D1/D2 antiparallel from S to N, R3 from N to ground, D3/D4 back-to-back zeners from N to output
    Nx = xs + 3.2; y1, y2 = 4.6, 6.3
    s.wire((xs, 3.0), (xs, y2)); s.wire((jo[0], 3.0), (jo[0], y1))
    s.D((xs, y1), (Nx, y1), 'D1', loc='bottom'); s.D((Nx, y2), (xs, y2), 'D2')
    s.wire((Nx, y1), (Nx, y2))
    zm = (Nx + jo[0]) / 2
    s.Z((zm, y1), (Nx, y1), 'D3', loc='bottom'); s.Z((zm, y1), (jo[0], y1), 'D4', loc='bottom')
    s.R((Nx, y2), (Nx + 2.6, y2), 'R3'); s.gnd((Nx + 2.6, y2), lead=0.4)
    s.dot(M, (M[0], 1.6), (jo[0], 1.6), (xs, 3.0), (jo[0], 3.0), (xs, y1), (Nx, y1), (Nx, y2))
    return s, [r'$V_{\mathrm{OUT}} = -\dfrac{1}{R1\,C1}\int V_{\mathrm{IN}}\,dt$;   C1 is the integrating capacitor',
               'U1 (low input current) sets the DC accuracy at S; U2 (fast) handles high frequencies through R2, C2 and C3',
               'D1 to D4 and R3 limit the output swing so the loop recovers quickly from overload']


@circuit(61, P, 'Twin-T Notch Filter with Adjustable Q')
def c61():
    s = Sch()
    yt, yb = 3.6, -2.0
    J = (0.0, 0.8)
    s.term((-1.0, J[1]), VIN); s.wire((-1.0, J[1]), J); s.dot(J)
    A = (2.6, yt); D = (2.6, yb); Bx = 5.2; G = (2.6, -0.3)
    s.wire(J, (0, yt)); s.R((0, yt), A, 'R1'); s.R(A, (Bx, yt), 'R2')
    s.wire(J, (0, yb)); s.C((0, yb), D, 'C1', loc='bottom'); s.C(D, (Bx, yb), 'C2', loc='bottom'); s.wire((Bx, yb), (Bx, yt))
    s.C(A, (G[0], 1.0), 'C3', loc='left'); s.wire((G[0], 1.0), G)
    s.R(D, G, 'R3', loc='left')
    s.dot(A, D, G, (Bx, yt))
    u1 = s.opamp((6.6, yt - 1.25), 'U1', plus_top=True)
    s.wire((Bx, yt), u1.in2)
    jo1 = X(u1.out, 0.8)
    follower(s, u1, jo1, dy=0.7)
    s.wire(u1.out, (11.6, jo1[1])); s.term((11.6, jo1[1]), VOUT, 'right')
    xr = 10.2
    u2 = s.opamp((8.6, -0.925), 'U2', plus_top=True, left=True)     # + at 0.325, out at -0.3
    wy = u2.in2[1]
    ra, rb = (xr, wy + 1.3), (xr, wy - 1.3)
    s.wire((xr, jo1[1]), ra); s.R(ra, rb, 'R4', loc='right'); s.gnd(rb)
    s.arrow((xr - 0.9, wy), (xr - 0.3, wy)); s.wire(u2.in2, (xr - 0.9, wy))
    jg = (5.9, G[1])
    s.wire(u2.out, jg, G)
    q = X(u2.in1, 0.4)
    s.wire(u2.in1, q, (q[0], -1.9), (jg[0], -1.9), jg)
    s.dot(jo1, (xr, jo1[1]), jg)
    return s, [r'$f_0 = \dfrac{1}{2\pi\,R1\,C1}$   with R1 = R2 = 2 R3 and C1 = C2 = C3/2',
               r'U2 drives the twin-T common node with the fraction k of the output picked off R4:   $Q \approx \dfrac{1}{4\,(1-k)}$',
               'k = 0 gives the passive twin-T (Q = 1/4); moving the wiper toward the output narrows the notch']


@circuit(62, P, 'Notch Filter Tuned by a Single Capacitor')
def c62():
    s = Sch()
    u1 = s.opamp((4.0, 0), 'U1'); n, p, o = u1.in1, u1.in2, u1.out
    J = (0.6, -0.625)
    s.term((-0.6, J[1]), VIN); s.wire((-0.6, J[1]), J); s.dot(J)
    jn = X(n, -0.7); jp = X(p, -0.7)
    s.wire(J, (J[0], n[1])); s.R((J[0], n[1]), jn, 'R1'); s.wire(jn, n)
    s.wire(J, (J[0], p[1])); s.R((J[0], p[1]), jp, 'R2', loc='bottom'); s.wire(jp, p)
    jo = out_term(s, o, dx=1.8, jx=0.8)
    s.loop(jn, jo, 1.8, 'R', 'R3')
    T = (jp[0], -4.4)
    s.C(jp, T, None)
    s.text((jp[0] - 0.5, (jp[1] + T[1]) / 2), 'C1', ha='right')
    s.arrow((jp[0] - 0.45, -3.4), (jp[0] + 0.45, -2.4))
    u2 = s.opamp((6.0, T[1] - 1.25 + 1.25 - 1.25), 'U2', plus_top=True)    # + at T
    s.wire(T, u2.in2)
    jo2 = X(u2.out, 0.7)
    s.wire(u2.out, jo2)
    q = X(u2.in1, -0.6); s.wire(u2.in1, q, (q[0], u2.in1[1] - 0.8), (jo2[0], u2.in1[1] - 0.8), jo2)
    M = (jp[0], -7.6)
    s.R(T, M, 'R4', loc='left'); s.R(M, (M[0], -10.0), 'R5', loc='left'); s.gnd((M[0], -10.0))
    s.wire(jo2, (jo2[0] + 0.8, jo2[1])); s.wire((jo2[0] + 0.8, jo2[1]), (jo2[0] + 0.8, M[1]))
    s.C((jo2[0] + 0.8, M[1]), M, 'C2', loc='bottom')
    s.dot(jp, T, M, jo2)
    return s, [r'$f_0 = \dfrac{1}{2\pi\,R4\sqrt{C1\,C2}}$   with R1 = R2 = R3, R4 = R5 = R1/2',
               'U2, R4, R5 and C2 make an inductance L = R4 R5 C2 (with series resistance R4 + R5 = R1) to ground',
               'At resonance the (+) input sits at half the input and U1 cancels it; one capacitor (C1) tunes the notch']



def sallen_key(s, first, second, top, shunt, names, vin_label=VIN, shunt_term=None):
    """Unity-gain Sallen-Key: VIN - first(n1) - N - second(n2) - B(+); top(n3) N->out; shunt(n4) B->gnd."""
    n1, n2, n3, n4 = names
    u = s.opamp((5.2, 1.25), 'U1'); n, p, o = u.in1, u.in2, u.out     # - at 1.25, + at 0
    s.term((-1.2, 0), vin_label)
    N = (1.8, 0); B = (4.4, 0)
    getattr(s, first)((-1.2, 0), N, n1, loc='bottom'); getattr(s, second)(N, B, n2, loc='bottom'); s.wire(B, p)
    jo = out_term(s, o, dx=2.0, jx=1.0)
    yt = 3.0
    q = (4.6, n[1]); s.wire(n, q, (q[0], yt))
    s.wire(N, (N[0], 0.6)); getattr(s, top)((N[0], 0.6), (N[0], yt), n3, loc='left'); s.wire((N[0], yt), (jo[0], yt), jo)
    if shunt_term:
        getattr(s, shunt)(B, (B[0], -2.6), n4, loc='right'); s.term((B[0], -2.6), shunt_term, 'bottom')
    else:
        getattr(s, shunt)(B, (B[0], -2.6), n4, loc='right'); s.gnd((B[0], -2.6))
    s.dot(N, B, (q[0], yt))
    return s


@circuit(63, P, 'Active Tuned Circuit')
def c63():
    s = Sch()
    sallen_key(s, 'C', 'C', 'R', 'R', ('C1', 'C2', 'R1', 'R2'), vin_label=sub('V', '1'), shunt_term=sub('V', '2'))
    return s, [r'$f_0 = \dfrac{1}{2\pi\sqrt{R1\,R2\,C1\,C2}}$',
               r'Drive the circuit at $V_1$ (through C1) with $V_2$ grounded, or at $V_2$ (through R2) with $V_1$ grounded',
               'R1/R2 and C1/C2 set the damping of the response']


@circuit(64, P, 'Two-Stage Active Tuned Circuit')
def c64():
    s = Sch()
    u1 = s.opamp((4.6, 1.25), 'U1'); n1, p1, o1 = u1.in1, u1.in2, u1.out
    X1 = (1.4, 0); B1 = (3.8, 0)
    s.C(X1, B1, 'C1', loc='bottom'); s.wire(B1, p1)
    s.R(B1, (B1[0], -2.6), 'R1', loc='right'); s.term((B1[0], -2.6), VIN, 'bottom')
    s.C(X1, (X1[0], -2.4), 'C2', loc='left'); s.gnd((X1[0], -2.4))
    jo1 = X(o1, 0.6); s.wire(o1, jo1)
    yt = 3.0
    q = (4.1, n1[1]); s.wire(n1, q, (q[0], yt))
    s.wire(X1, (X1[0], 0.6)); s.R((X1[0], 0.6), (X1[0], yt), 'R2', loc='left'); s.wire((X1[0], yt), (jo1[0], yt), jo1)
    u2 = s.opamp((13.0, o1[1] + 1.25), 'U2'); n2, p2, o2 = u2.in1, u2.in2, u2.out
    Y = (10.0, o1[1]); B2 = (12.2, o1[1])
    s.C(jo1, (9.4, o1[1]), 'C3', loc='bottom'); s.wire((9.4, o1[1]), Y); s.C(Y, B2, 'C4', loc='bottom'); s.wire(B2, p2)
    s.R(B2, (B2[0], -2.0), 'R4', loc='right'); s.gnd((B2[0], -2.0))
    jo2 = out_term(s, o2, dx=1.8, jx=0.7)
    yt2 = n2[1] + 1.6
    q2 = (12.5, n2[1]); s.wire(n2, q2, (q2[0], yt2))
    s.wire(Y, (Y[0], 1.4)); s.R((Y[0], 1.4), (Y[0], yt2), 'R3', loc='left'); s.wire((Y[0], yt2), (jo2[0], yt2), jo2)
    s.dot(X1, B1, jo1, (q[0], yt), Y, B2, (q2[0], yt2))
    return s, [r'$f_0 = \dfrac{1}{2\pi\sqrt{R1\,R2\,C1\,C2}}$   for each stage',
               'Use the same values in both stages (R3 = R2, R4 = R1, C3 = C2, C4 = C1) for a sharper overall response']


@circuit(65, P, 'Negative Capacitance Converter')
def c65():
    s = Sch()
    u = s.opamp((4.2, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    A = (1.0, 0)
    s.term((-0.6, 0), sub('C', 'EQ')); s.arrow((-0.4, 0.45), (0.5, 0.45)); s.wire((-0.6, 0), A)
    s.R(A, (3.4, 0), 'R2', loc='bottom'); s.wire((3.4, 0), n)
    jo = X(o, 0.8); s.wire(o, jo)
    s.loop(A, jo, 1.8, 'R', 'R3')
    B = (5.2, -3.2)
    s.R(jo, (jo[0], B[1]), 'R1', loc='right'); s.wire((jo[0], B[1]), B, (3.4, B[1]), (3.4, p[1]), p)
    s.C(B, (B[0], -5.4), 'C1', loc='right'); s.gnd((B[0], -5.4)); s.dot(B)
    return s, [r'$C_{\mathrm{EQ}} = -\dfrac{R1}{R3}\,C1$   seen at the terminal',
               r'R2 = R1 balances the bias currents.  DC error current at the terminal $\approx \dfrac{V_{\mathrm{OS}}}{R3} + \dfrac{I_{\mathrm{OS}}\,R2}{R3}$',
               'Accuracy falls as the op-amp loop gain drops at higher frequencies']


@circuit(66, P, 'Adjustable Capacitance Multiplier')
def c66():
    s = Sch()
    A = (0.0, 0)
    s.term((-1.2, 0), 'C'); s.arrow((-1.0, 0.45), (-0.2, 0.45)); s.wire((-1.2, 0), A)
    u1 = s.opamp((1.6, -1.25), 'U1', plus_top=True)
    s.wire(A, u1.in2)
    jo1 = X(u1.out, 0.5); s.wire(u1.out, jo1)
    follower(s, u1, jo1, dy=1.0)
    y = u1.out[1]
    s.R(jo1, (6.3, y), 'R1')
    s.R((6.3, y), (9.0, y), None)
    s.text((7.65, y + 0.5), 'R2', va='bottom')
    s.text((6.8, y - 0.5), sub('R', 'a'), va='top', fs=9); s.text((8.5, y - 0.5), sub('R', 'b'), va='top', fs=9)
    s.arrow((7.65, y - 1.6), (7.65, y - 0.3))
    u2 = s.opamp((10.6, -2.825), 'U2'); n2, p2, o2 = u2.in1, u2.in2, u2.out
    m = (10.0, n2[1])
    s.wire((7.65, y - 1.6), (7.65, n2[1])); s.R((7.65, n2[1]), m, 'R3', loc='bottom'); s.wire(m, n2)
    xc = 13.4; yc = -1.5
    s.wire(m, (m[0], yc)); s.C((m[0], yc), (xc, yc), 'C2', loc='bottom')
    s.wire((9.0, y), (xc, y), (xc, o2[1])); s.wire(o2, (xc, o2[1]))
    s.wire(p2, X(p2, -0.5)); s.gnd(X(p2, -0.5), lead=0.4)
    yb = -5.6
    s.wire((xc, o2[1]), (xc, yb)); s.C((xc, yb), (5.0, yb), 'C1', loc='bottom'); s.wire((5.0, yb), (A[0], yb), A)
    s.dot(A, jo1, m, (xc, yc), (xc, o2[1]))
    return s, [r'$C = \left(1 + \dfrac{R_{\mathrm{b}}}{R_{\mathrm{a}}}\right) C1$',
               r'$R_{\mathrm{a}}$ = R1 plus the part of R2 on the R1 side of the wiper;  $R_{\mathrm{b}}$ = the rest of R2',
               'U2 holds the wiper at 0 V, so it drives the far end of C1 with an inverted, scaled copy of the terminal voltage',
               'C2 stabilizes U2']


def gyrator(s, series, shunt, names):
    """Terminal A, `series` part from A to B (+), `shunt` from B to ground,
    follower (feedback resistor R_fb), R_top from A to the output."""
    n_series, n_shunt, n_top, n_fb, lab = names
    u = s.opamp((4.2, 1.25), 'U1'); n, p, o = u.in1, u.in2, u.out
    A = (0.8, 0); B = (3.4, 0)
    s.term((-0.6, 0), lab); s.arrow((-0.4, 0.45), (0.4, 0.45)); s.wire((-0.6, 0), A)
    getattr(s, series)(A, B, n_series, loc='bottom'); s.wire(B, p)
    getattr(s, shunt)(B, (B[0], -2.6), n_shunt, loc='right'); s.gnd((B[0], -2.6))
    jo = X(o, 0.7); s.wire(o, X(o, 1.4))
    jt = X(o, 1.4)
    q = (3.8, n[1]); s.wire(n, q, (q[0], 2.6)); s.R((q[0], 2.6), (jo[0], 2.6), n_fb); s.wire((jo[0], 2.6), jo)
    s.wire(A, (A[0], 4.4)); s.R((A[0], 4.4), (jt[0], 4.4), n_top); s.wire((jt[0], 4.4), jt)
    s.dot(A, B, jo)
    return s


@circuit(67, P, 'Simulated Inductor (Gyrator)')
def c67():
    s = Sch()
    gyrator(s, 'C', 'R', ('C1', 'R2', 'R1', 'R3', 'L'))
    return s, [r'$L \approx R1\,R2\,C1$',
               r'Series resistance $\approx$ R1;   parallel resistance $\approx$ R2',
               'R3 (equal to R2) balances bias currents; one terminal of the inductor is ground']


@circuit(68, P, 'Grounded Capacitance Multiplier')
def c68():
    s = Sch()
    gyrator(s, 'R', 'C', ('R2', 'C1', 'R1', 'R3', 'C'))
    return s, [r'$C \approx \dfrac{R2}{R1}\,C1$   with R1 $\ll$ R2;   series resistance $\approx$ R1',
               r'DC error current at the terminal $\approx \dfrac{V_{\mathrm{OS}}}{R1} + \dfrac{I_{\mathrm{OS}}\,R2}{R1}$',
               'R3 (equal to R2) balances bias currents; one terminal of the capacitor is ground']


@circuit(69, P, 'Second-Order High-Pass Filter (Unity-Gain Sallen-Key)')
def c69():
    s = Sch()
    sallen_key(s, 'C', 'C', 'R', 'R', ('C1', 'C2', 'R1', 'R2'))
    return s, [r'$f_{\mathrm{c}} = \dfrac{1}{2\pi\sqrt{R1\,R2\,C1\,C2}}$;   for a Butterworth response use C1 = C2 and R2 = 2 R1',
               'Use stable, low-loss capacitors (C0G ceramic or polypropylene film) so the corner frequency does not drift']


@circuit(70, P, 'Second-Order Low-Pass Filter (Unity-Gain Sallen-Key)')
def c70():
    s = Sch()
    sallen_key(s, 'R', 'R', 'C', 'C', ('R1', 'R2', 'C1', 'C2'))
    return s, [r'$f_{\mathrm{c}} = \dfrac{1}{2\pi\sqrt{R1\,R2\,C1\,C2}}$;   for a Butterworth response use R1 = R2 and C1 = 2 C2',
               'Use stable, low-loss capacitors (C0G ceramic or polypropylene film) so the corner frequency does not drift']


@circuit(71, P, 'Piecewise-Linear Amplifier with Temperature-Compensated Breakpoints')
def c71():
    s = Sch()
    u = s.opamp((4.0, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    S = (2.2, 0)
    s.term((-1.6, 0), VIN); s.R((-1.6, 0), (1.0, 0), 'R1'); s.wire((1.0, 0), n)
    s.wire(p, X(p, -0.6)); s.gnd(X(p, -0.6), lead=0.5)
    O = (7.2, o[1]); s.wire(o, O)
    Dn = (7.2, 1.6); T = (9.45, 1.6)
    s.wire(S, (S[0], Dn[1]), Dn); s.D(Dn, O, 'D1', loc='left')
    s.R(Dn, T, 'R2')
    q4 = s.pnp((10.2, 0.5), None, left=True, flip=True)
    s.text((10.55, 0.1), 'Q4', ha='left')
    s.wire(q4.collector, T); s.wire(q4.emitter, (q4.emitter[0], O[1]))
    s.wire(O, (11.4, O[1]))
    s.wire(q4.base, (10.6, 0.5), (10.6, 1.6)); s.wire(T, (10.6, 1.6), (12.4, 1.6)); s.term((12.4, 1.6), VOUT, 'right')
    s.dot(S, Dn, O, T, (10.6, 1.6), (q4.emitter[0], O[1]))
    # breakpoint network below
    xo = 11.4
    yq3, yq2 = -2.9, -4.6
    q3 = s.pnp((5.0, yq3 - 0.75), None, theta=90, flip=True)
    q2 = s.pnp((8.0, yq2 - 0.75), None, theta=90, flip=True)
    s.text((5.0 + 0.35, yq3 - 1.05), 'Q3', ha='left'); s.text((8.0 + 0.35, yq2 - 1.05), 'Q2', ha='left')
    s.wire(S, (S[0], yq2))
    s.wire(q3.collector, (S[0], yq3)); s.wire(q2.collector, (S[0], yq2))
    s.R(q3.emitter, (9.6, yq3), 'R4'); s.wire((9.6, yq3), (xo, yq3))
    s.wire(q2.emitter, (9.0, yq2)); s.R((9.0, yq2), (xo, yq2), 'R6', loc='bottom')
    s.wire((xo, O[1]), (xo, yq2))
    yB = -8.0
    s.wire(q3.base, (5.0, -5.2)); s.R((5.0, -5.2), (5.0, yB), 'R3', loc='left')
    s.R(q2.base, (8.0, yB), 'R5', loc='right')
    s.wire((5.0, yB), (8.0, yB))
    q1 = s.pnp((5.75, -9.3), None)
    s.text((6.85, -9.3), 'Q1', ha='left')
    s.wire(q1.emitter, (q1.emitter[0], yB))
    s.wire(q1.base, (5.2, -9.3), (5.2, -10.4), (q1.collector[0], -10.4)); s.wire(q1.collector, (q1.collector[0], -10.4))
    s.wire((q1.collector[0], -10.4), (q1.collector[0], -11.0)); s.term((q1.collector[0], -11.0), r'$V^{-}$', 'bottom')
    s.dot((S[0], yq3), (xo, yq3), (q1.emitter[0], yB), (q1.collector[0], -10.4))
    return s, [r'Small signals: gain $= -\dfrac{R2}{R1}$.  Q2 and Q3 add feedback current into the summing node as the output',
               'rises past each breakpoint, so the gain falls in steps (one per transistor, set by R4/R3 and R6/R5)',
               r'Q1 sets the bias node one $V_{\mathrm{BE}}$ above $V^{-}$ and Q4 adds one $V_{\mathrm{BE}}$ at the output; these cancel the',
               r'$V_{\mathrm{BE}}$ drift of Q2 and Q3 so the breakpoints stay put over temperature.  D1 stops U1 from saturating']


@circuit(72, P, 'High-Side Current Monitor')
def c72():
    s = Sch()
    A = (1.6, 4.0); L = (5.0, 4.0)
    s.term((0.0, 4.0), sub('V', 'S')); s.wire((0.0, 4.0), A)
    s.R(A, L, 'R1'); s.wire(L, (7.0, 4.0)); s.term((7.0, 4.0), 'TO LOAD', 'right')
    s.arrow((5.6, 4.45), (6.5, 4.45)); s.text((6.05, 4.6), sub('I', 'L'), va='bottom')
    u = s.opamp((3.4, -0.625), 'U1', plus_top=True)   # + at 0.625
    N = (A[0], -0.625)
    s.R(A, (A[0], 1.2), 'R2', loc='left'); s.wire((A[0], 1.2), N, u.in1)
    s.wire(L, (L[0], 2.2), (2.8, 2.2), (2.8, u.in2[1]), u.in2)
    q = s.mosfet((1.85, -2.6), 'p', 'gate_right', swap=True)
    s.text((1.2, -2.6), 'Q1', ha='right')
    s.wire(N, q['source'])
    s.wire(u.out, (6.2, u.out[1]), (6.2, q['gate'][1]), q['gate'])
    M = (q['drain'][0], -4.6)
    s.wire(q['drain'], M); s.R(M, (M[0], -7.0), 'R3', loc='left'); s.gnd((M[0], -7.0))
    s.wire(M, (4.0, M[1])); s.term((4.0, M[1]), VOUT, 'right')
    s.pwr(u, sub('V', 'S'), 'gnd')
    s.dot(A, L, N, M)
    return s, [r'$V_{\mathrm{OUT}} = \dfrac{R1\,R3}{R2}\,I_{\mathrm{L}}$',
               'U1 forces the drop across R2 to equal the drop across R1; Q1 passes that current into R3',
               r'U1 runs from the monitored supply $V_{\mathrm{S}}$, so its inputs must work close to its positive rail',
               'Q1 is a P-channel MOSFET, so no gate current flows and all of the R2 current reaches R3']
