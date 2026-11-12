from lib import Sch, X, VIN, VOUT, sub
from reg import circuit
from c_basic import out_term
P = 'Signal Processing'
EIN = sub('E', 'IN'); EOUT = sub('E', 'OUT')
ROW = 3.4


def qa(s, base, label=None):
    """NPN, base below, collector left, emitter right (row at base.y + 0.75)."""
    q = s.npn(base, None, theta=90)
    if label:
        s.text((base[0], base[1] + 1.45), label, va='bottom')
    return q


def qb(s, base, label=None):
    """NPN, base below, emitter left, collector right."""
    q = s.npn(base, None, theta=90, flip=True)
    if label:
        s.text((base[0], base[1] + 1.45), label, va='bottom')
    return q


def qa_up(s, base, label=None):
    """NPN, base above, collector left, emitter right (row at base.y - 0.75)."""
    q = s.npn(base, None, theta=-90, flip=True)
    if label:
        s.text((base[0] + 0.3, base[1] + 0.25), label, ha='left', va='bottom')
    return q


def ref_amp(s, qc, E, names, ref_label, ytop=6.0):
    """Reference amplifier: holds the collector node of the second log transistor at 0 V.
    qc: collector point of that transistor (on ROW); E: emitter node to drive through names[1]."""
    un, rtop, cn, rref, rbias = names
    xu = qc[0] + 2.1
    u = s.opamp((xu, ROW), un)
    s.wire(qc, u.in1)
    K1 = (qc[0] + 0.6, ROW); K2 = (qc[0] + 1.0, ROW)
    W = (xu + 2.8, u.out[1])
    s.wire(u.out, W)
    s.wire(K1, (K1[0], 4.4)); s.C((K1[0], 4.4), (W[0], 4.4), cn)
    s.wire(E, (E[0], ytop)); s.R((E[0], ytop), (W[0], ytop), rtop); s.wire((W[0], ytop), W)
    s.R(K2, (K2[0], 0.8), rref, loc='left'); s.term((K2[0], 0.8), ref_label, 'bottom')
    xb = xu - 0.4
    s.wire(u.in2, (xb, u.in2[1]), (xb, 1.0)); s.R((xb, 1.0), (xu + 2.2, 1.0), rbias, loc='bottom'); s.gnd((xu + 2.2, 1.0), lead=0.5)
    s.dot(K1, K2, E, (W[0], 4.4))
    return W


def log_input(s, names, rin_label=VIN, cap=True):
    """Input amp U at (3,0): S node (2,0), output node O (6,-0.625). Returns S, O."""
    rin, un, cn = names
    u = s.opamp((3.0, 0), un)
    S = (2.0, 0)
    s.term((-1.4, 0), rin_label); s.R((-1.4, 0), (1.0, 0), rin); s.wire((1.0, 0), u.in1)
    s.wire(u.in2, (2.4, u.in2[1])); s.gnd((2.4, u.in2[1]), lead=0.5)
    O = (6.0, u.out[1]); s.wire(u.out, O)
    if cap:
        s.wire(S, (S[0], 1.3)); s.C((S[0], 1.3), (O[0], 1.3), cn, loc='bottom'); s.wire((O[0], 1.3), O)
        s.dot((S[0], 1.3))
    s.dot(S, O)
    return S, O


def anti_bottom(s, xb, names, in_label, out_label=EOUT):
    """Antilog cell below: Q3 base fed from above at x = xb; returns nothing."""
    q3n, r5, u3n, r6, q4n, u4n, r7 = names
    y = -4.4
    q3 = qa_up(s, (xb, y + 0.75), q3n)
    T = (xb - 3.8, y)
    s.wire(q3.collector, T)
    s.term((T[0] - 3.4, y), in_label); s.R((T[0] - 3.4, y), (T[0] - 0.8, y), r5); s.wire((T[0] - 0.8, y), T)
    u3 = s.opamp((T[0] + 0.8, -6.0), u3n)
    s.wire(T, (T[0], -6.0), u3.in1)
    s.wire(u3.in2, (T[0] + 0.4, u3.in2[1])); s.gnd((T[0] + 0.4, u3.in2[1]), lead=0.3)
    F = (xb + 1.6, y)
    s.wire(u3.out, (xb - 0.2, u3.out[1])); s.R((xb - 0.2, u3.out[1]), (F[0], u3.out[1]), r6, loc='bottom'); s.wire((F[0], u3.out[1]), F)
    q4 = qb(s, (xb + 3.0, y - 0.75), q4n)
    s.wire(q3.emitter, q4.emitter); s.gnd((xb + 3.0, y - 0.75), lead=0.4)
    Z = (xb + 4.6, y)
    u4 = s.opamp((xb + 5.4, y), u4n)
    s.wire(q4.collector, u4.in1)
    s.wire(u4.in2, (Z[0] + 0.4, u4.in2[1])); s.gnd((Z[0] + 0.4, u4.in2[1]), lead=0.4)
    jo = out_term(s, u4.out, dx=2.0, jx=0.7, label=out_label)
    s.loop(Z, jo, y + 1.5, 'R', r7)
    s.dot(T, F)


@circuit(83, P, 'Temperature-Compensated Logarithmic Amplifier')
def c83():
    s = Sch()
    S, O = log_input(s, (sub('R', 'IN'), 'U1', 'C1'))
    s.arrow((-0.6, -0.45), (0.4, -0.45)); s.text((-0.1, -0.6), sub('I', 'IN'), va='top')
    s.wire(O, (O[0], -2.6)); s.term((O[0], -2.6), VOUT, 'bottom')
    q1 = qa(s, (4.0, ROW - 0.75), 'Q1')
    s.wire(q1.collector, (S[0], ROW), (S[0], 1.3))
    s.gnd((4.0, ROW - 0.75), lead=0.45)
    q2 = qb(s, (8.6, ROW - 0.75), 'Q2')
    E = (6.6, ROW); s.wire(q1.emitter, q2.emitter)
    Bn = (8.6, O[1])
    s.R(O, Bn, 'R1', loc='bottom'); s.wire(Bn, (8.6, ROW - 0.75))
    s.RT(Bn, (8.6, -3.4), sub('RT', '1'), loc='right'); s.gnd((8.6, -3.4))
    s.dot(Bn)
    ref_amp(s, q2.collector, E, ('U2', 'R2', 'C2', 'R3', 'R4'), r'$V^{+}$')
    return s, [r'$V_{\mathrm{OUT}} = -\left(1 + \dfrac{R1}{RT_1}\right)\dfrac{kT}{q}\,\ln\dfrac{I_{\mathrm{IN}}}{I_{\mathrm{REF}}}$,   '
               r'$I_{\mathrm{IN}} = \dfrac{V_{\mathrm{IN}}}{R_{\mathrm{IN}}}$,   $I_{\mathrm{REF}} = \dfrac{V^{+}}{R3}$',
               r'With $1 + R1/RT_1 \approx 16.7$ at 25 $^\circ$C the output changes by about 1 V per decade of input current',
               r'$RT_1$ has a positive temperature coefficient (about +0.35 %/$^\circ$C) that cancels the drift of kT/q',
               'Q1 and Q2 must be a matched (monolithic) pair; U2 holds the Q2 collector at 0 V so it carries the reference current',
               'C1 and C2 keep the two loops stable']


@circuit(84, P, 'Square-Root Circuit Using Log and Antilog Stages')
def c84():
    s = Sch()
    # row 1: log of the input, then half of the log difference
    u1 = s.opamp((2.4, 0), 'U1')
    S = (1.6, 0)
    s.term((-1.6, 0), VIN); s.R((-1.6, 0), (0.8, 0), 'R1'); s.wire((0.8, 0), u1.in1)
    s.wire(u1.in2, (1.9, u1.in2[1])); s.gnd((1.9, u1.in2[1]), lead=0.4)
    N1 = (7.2, u1.out[1])
    s.R(u1.out, (6.6, u1.out[1]), 'R2'); s.wire((6.6, u1.out[1]), N1)
    q1 = qa_up(s, (4.4, 2.95), None); s.text((3.9, 3.3), 'Q1', ha='right', va='bottom')
    s.wire(q1.collector, (S[0], 2.2), S)
    s.wire((4.4, 2.95), (4.4, 3.4), (5.0, 3.4)); s.gnd((5.0, 3.4), lead=0.3)
    s.wire(q1.emitter, (N1[0], 2.2), N1)
    s.D(N1, (N1[0], -2.6), 'D1', loc='left'); s.gnd((N1[0], -2.6))
    q2 = qb(s, (8.1, N1[1] - 0.75), None); s.text((8.1, -2.0), 'Q2', va='top')
    s.wire(N1, q2.emitter)
    N2 = (q2.collector[0], N1[1])
    s.wire((8.1, N1[1] - 0.75), (8.1, -1.8), (N2[0], -1.8), N2)
    s.R(N2, (N2[0], 2.4), 'R3', loc='right'); s.term((N2[0], 2.4), r'$V^{+}$', 'top')
    N3 = (11.4, N1[1])
    s.R(N2, N3, 'R4'); s.R(N3, (N3[0], -2.8), 'R5', loc='right'); s.gnd((N3[0], -2.8))
    s.dot(S, N1, N2, N3)
    # link to row 2
    yl = -3.9
    s.wire(N3, (12.4, N3[1]), (12.4, yl), (0.2, yl), (0.2, -5.4))
    # row 2: antilog of half the difference
    u2 = s.opamp((1.2, -6.65), 'U2', plus_top=True)       # + at -5.4
    s.wire((0.2, -5.4), u2.in2)
    M = (0.6, -7.6)
    s.wire(u2.in1, (M[0], u2.in1[1]), M)
    s.R(M, (M[0], -10.0), 'R7', loc='left'); s.gnd((M[0], -10.0))
    q3 = s.npn((2.6, -8.35), None, theta=90); s.text((2.95, -8.7), 'Q3', ha='left')
    s.wire(M, q3.collector)
    s.wire((2.6, -8.35), (2.6, -8.8), (q3.collector[0], -8.8), q3.collector)
    s.R(M, (-1.8, M[1]), 'R6', loc='bottom'); s.term((-1.8, M[1]), r'$V^{+}$')
    Pn = (4.6, -7.6)
    s.wire(q3.emitter, Pn)
    s.wire(u2.out, (Pn[0], u2.out[1])); s.R((Pn[0], u2.out[1]), Pn, 'R8', loc='right')
    s.D(Pn, (Pn[0], -10.0), 'D2', loc='left'); s.gnd((Pn[0], -10.0))
    q4 = qb(s, (6.5, -8.35), None); s.text((6.5, -7.35), 'Q4', va='bottom')
    s.wire(Pn, q4.emitter); s.gnd((6.5, -8.35), lead=0.3)
    Z = (8.0, -7.6)
    u3 = s.opamp((8.8, -7.6), 'U3')
    s.wire(q4.collector, u3.in1)
    s.wire(u3.in2, (8.4, u3.in2[1])); s.gnd((8.4, u3.in2[1]), lead=0.3)
    jo = out_term(s, u3.out, dx=1.9, jx=0.7)
    s.loop(Z, jo, -6.2, 'R', 'R9')
    s.dot(M, Pn)
    return s, [r'$V_{\mathrm{OUT}} \approx \dfrac{R9}{R6}\sqrt{\dfrac{R3\,V^{+}}{R1}\,V_{\mathrm{IN}}}$   ($V_{\mathrm{IN}} > 0$)',
               'U1 with Q1 and Q2 forms the logarithm of the input;',
               'the R4/R5 divider (R4 = R5) halves it, and U2 with Q3 and Q4',
               'takes the antilogarithm, giving the square root',
               'Q1/Q2 and Q3/Q4 are matched pairs; D1 and D2 protect',
               'the transistors from reverse base-emitter voltage']


@circuit(85, P, 'Log-Antilog Multiplier/Divider')
def c85():
    s = Sch()
    S, O = log_input(s, ('R1', 'U1', 'C1'), rin_label=sub('E', '1'))
    q1 = qa(s, (4.0, ROW - 0.75), 'Q1')
    s.wire(q1.collector, (S[0], ROW), (S[0], 1.3))
    s.wire((4.0, ROW - 0.75), (q1.collector[0], ROW - 0.75), q1.collector)
    q2 = qb(s, (8.6, ROW - 0.75), 'Q2')
    E = (6.6, ROW); s.wire(q1.emitter, q2.emitter)
    s.wire(O, (8.6, O[1]), (8.6, ROW - 0.75))
    ref_amp(s, q2.collector, E, ('U2', 'R2', 'C2', 'R4', 'R3'), sub('E', '2'))
    s.wire(O, (O[0], -3.65))
    anti_bottom(s, 6.0, ('Q3', 'R5', 'U3', 'R6', 'Q4', 'U4', 'R7'), sub('E', '3'))
    return s, [r'$E_{\mathrm{OUT}} = \dfrac{R4\,R7}{R1\,R5}\cdot\dfrac{E_1\,E_3}{E_2}$   for $E_1, E_2, E_3 > 0$   (R1 = R4 = R5 = R7 gives $E_1 E_3 / E_2$)',
               r'U1 output $= V_{\mathrm{BE2}} - V_{\mathrm{BE1}} = \dfrac{kT}{q}\ln\dfrac{I_2}{I_1}$; Q3 and Q4 add it to the log of $I_3$ and take the antilog',
               'Because the same log voltage is used again, temperature effects cancel and no thermistor is needed',
               'Q1/Q2 and Q3/Q4 must be matched pairs;  C1 and C2 keep the loops stable']


@circuit(86, P, 'Log-Antilog Cube Generator')
def c86():
    s = Sch()
    S, O = log_input(s, ('R1', 'U1', 'C1'), rin_label=EIN)
    q1 = qa(s, (4.0, ROW - 0.75), 'Q1')
    s.wire(q1.collector, (S[0], ROW), (S[0], 1.3))
    s.gnd((4.0, ROW - 0.75), lead=0.45)
    q2 = qb(s, (8.6, ROW - 0.75), 'Q2')
    E = (6.6, ROW); s.wire(q1.emitter, q2.emitter)
    Bn = (8.6, O[1])
    s.R(O, Bn, 'R2', loc='bottom'); s.wire(Bn, (8.6, ROW - 0.75))
    s.R(Bn, (8.6, -2.5), 'R3', loc='right'); s.gnd((8.6, -2.5)); s.dot(Bn)
    ref_amp(s, q2.collector, E, ('U2', 'R5', 'C2', 'R4', 'R6'), r'$V^{+}$')
    G = (O[0], -2.6)
    s.R(O, G, 'R10', loc='left'); s.R(G, (G[0] + 1.6, G[1]), None); s.text((G[0] + 0.8, G[1] + 0.45), 'R9', va='bottom')
    s.gnd((G[0] + 1.6, G[1]), lead=0.25)
    s.wire(G, (G[0], -3.65)); s.dot(G)
    anti_bottom(s, 6.0, ('Q3', 'R7', 'U3', 'R11', 'Q4', 'U4', 'R12'), r'$V^{+}$')
    return s, [r'$E_{\mathrm{OUT}} = R12\,\dfrac{V^{+}}{R7}\left(\dfrac{E_{\mathrm{IN}}\,R4}{R1\,V^{+}}\right)^{3}$   for $E_{\mathrm{IN}} > 0$',
               r'The Q2 base sees $k_1 = R3/(R2+R3)$ of the U1 output and the Q3 base sees $k_2 = R9/(R9+R10)$;',
               r'the exponent is $k_2/k_1$, so choose the dividers for $k_2 = 3\,k_1$ to get a cube (other ratios give other powers)',
               'Q1/Q2 and Q3/Q4 must be matched pairs']


@circuit(87, P, 'Fast Logarithmic Amplifier')
def c87():
    s = Sch()
    q1 = qa(s, (4.0, ROW - 0.75), 'Q1')
    S = (2.0, 1.0)
    s.wire(q1.collector, (S[0], ROW), S)
    s.term((-1.4, S[1]), VIN); s.R((-1.4, S[1]), (1.0, S[1]), sub('R', 'IN')); s.wire((1.0, S[1]), S)
    u1 = s.opamp((2.6, S[1] - 1.25), 'U1', plus_top=True)      # + at S level
    s.wire(S, u1.in2)
    B = (5.2, u1.out[1]); s.wire(u1.out, B)
    s.wire(B, (B[0], 2.2), (4.0, 2.2), (4.0, ROW - 0.75))
    yl = -1.0
    s.wire(u1.in1, (2.4, u1.in1[1]), (2.4, yl), (B[0], yl), B)
    u2 = s.opamp((8.4, yl), 'U2')
    J = (7.2, yl); J2 = (7.8, yl)
    s.R((B[0], yl), J, 'R1', loc='bottom'); s.wire(J, u2.in1)
    s.wire(u2.in2, (8.0, u2.in2[1])); s.gnd((8.0, u2.in2[1]), lead=0.4)
    yc = -2.9
    s.wire(S, (S[0], yc)); s.C((S[0], yc), (J[0], yc), 'C1', loc='bottom'); s.wire((J[0], yc), J)
    Oe = (11.4, u2.out[1]); s.wire(u2.out, Oe)
    s.wire(J2, (J2[0], 0.4)); s.C((J2[0], 0.4), (Oe[0], 0.4), 'C2'); s.wire((Oe[0], 0.4), Oe)
    s.wire(Oe, (Oe[0], -3.6)); s.term((Oe[0], -3.6), VOUT, 'bottom')
    Bn = (13.6, Oe[1])
    s.R(Oe, Bn, 'R2', loc='bottom'); s.RT(Bn, (Bn[0], -4.4), sub('RT', '1'), loc='right'); s.gnd((Bn[0], -4.4))
    q2 = qb(s, (13.6, ROW - 0.75), 'Q2')
    s.wire(Bn, (13.6, ROW - 0.75))
    E = (6.6, ROW); s.wire(q1.emitter, q2.emitter)
    ref_amp(s, q2.collector, E, ('U3', 'R3', 'C3', 'R4', 'R5'), sub('V', 'REF'))
    s.dot(S, B, (B[0], yl), J, J2, Oe, Bn)
    return s, [r'$V_{\mathrm{OUT}} = -\left(1 + \dfrac{R2}{RT_1}\right)\dfrac{kT}{q}\,\ln\dfrac{V_{\mathrm{IN}}\,R4}{R_{\mathrm{IN}}\,V_{\mathrm{REF}}}$   ($V_{\mathrm{IN}} > 0$; about 1 V per decade)',
               'U1 copies the input node voltage to the base of Q1, so Q1 runs with zero collector-base voltage and its',
               'collector can be the input node; U2 then works as an integrator and does not need to drive a large capacitance',
               'C1 feeds fast input changes straight to U2 for speed;  RT1 (positive tempco) cancels the kT/q drift',
               'Q1 and Q2 must be a matched pair']


@circuit(88, P, 'Temperature-Compensated Antilog (Exponential) Amplifier')
def c88():
    s = Sch()
    u1 = s.opamp((2.0, 0), 'U1')
    K = (1.0, 0)
    s.wire(K, u1.in1)
    q1 = qa_up(s, (7.0, ROW + 0.75), None)
    s.text((6.5, ROW + 0.9), 'Q1', ha='right')
    s.wire(q1.collector, (K[0], ROW), K)
    s.R((K[0], ROW), (K[0], 6.4), 'R3', loc='left'); s.term((K[0], 6.4), sub('E', 'REF'), 'top')
    O = (4.8, u1.out[1]); s.wire(u1.out, O)
    s.C((K[0], 1.4), (O[0], 1.4), 'C1', loc='bottom'); s.wire((O[0], 1.4), O)
    s.wire(u1.in2, (1.4, u1.in2[1])); s.R((1.4, u1.in2[1]), (1.4, -3.6), 'R5', loc='left'); s.gnd((1.4, -3.6))
    E = (8.6, ROW)
    s.wire(O, (E[0], O[1])); s.R((E[0], O[1]), E, 'R4', loc='right')
    Nn = (7.0, 5.4)
    s.wire((7.0, ROW + 0.75), Nn)
    s.term((3.0, Nn[1]), EIN); s.R((3.0, Nn[1]), Nn, 'R1')
    s.RT(Nn, (9.6, Nn[1]), sub('RT', '1')); s.gnd((9.6, Nn[1]), lead=0.5)
    q2 = qb(s, (10.6, ROW - 0.75), None); s.text((10.95, ROW - 1.1), 'Q2', ha='left')
    s.wire(q1.emitter, q2.emitter); s.gnd((10.6, ROW - 0.75), lead=0.4)
    u2 = s.opamp((13.0, ROW), 'U2')
    Z = (12.2, ROW)
    s.wire(q2.collector, u2.in1)
    s.wire(u2.in2, (12.6, u2.in2[1])); s.R((12.6, u2.in2[1]), (12.6, 0.0), 'R7', loc='left'); s.gnd((12.6, 0.0))
    jo = out_term(s, u2.out, dx=2.0, jx=0.8, label=EOUT)
    s.loop(Z, jo, ROW + 1.5, 'R', 'R6')
    s.loop(Z, jo, ROW + 2.8, 'C', 'C2', dots=False)
    s.dot(K, (K[0], 1.4), (K[0], ROW), O, E, Nn)
    return s, [r'$E_{\mathrm{OUT}} = R6\,\dfrac{E_{\mathrm{REF}}}{R3}\,\exp\!\left(-\dfrac{q}{kT}\,\dfrac{RT_1}{R1 + RT_1}\,E_{\mathrm{IN}}\right)$',
               r'With $(R1 + RT_1)/RT_1 \approx 16.7$ at 25 $^\circ$C the output falls one decade for each +1 V of $E_{\mathrm{IN}}$',
               'U1 holds the Q1 collector current at E_REF/R3; the input shifts the Q1 base, and Q2 converts the change'.replace('E_REF', r'$E_{\mathrm{REF}}$'),
               r'into an exponentially related collector current.  $RT_1$ (positive tempco) cancels the kT/q drift; Q1 and Q2 are matched']
