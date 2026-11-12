"""89-103 Fundamentals: the basic building blocks (ideal model, follower, integrator,
first-order and active filters, log/antilog, rectifier, comparator, Schmitt trigger,
sine oscillators)."""
from lib import Sch, X, VIN, VOUT, sub
from reg import circuit

F = 'Fundamentals'
VREF = sub('V', 'REF')
RL = sub('R', 'L')


def out_term(s, o, dx=1.6, label=VOUT, dot=True, jx=0.6):
    j = X(o, jx)
    s.wire(o, X(o, dx))
    s.term(X(o, dx), label, 'right')
    if dot:
        s.dot(j)
    return j


def gnd_plus(s, p, dx=0.7):
    q = X(p, -dx); s.wire(p, q); s.gnd(q, lead=0.5)


@circuit(89, F, 'Op-Amp Symbol and Ideal Model')
def c89():
    s = Sch()
    u = s.opamp((2, 0)); n, p, o = u.in1, u.in2, u.out
    s.term((0, n[1]), r'$V_{-}$'); s.wire((0, n[1]), n)
    s.term((0, p[1]), r'$V_{+}$'); s.wire((0, p[1]), p)
    s.wire(o, X(o, 1.4)); s.term(X(o, 1.4), VOUT, 'right')
    s.text(X(n, 0.5, 1.0), 'inverting input (−)', ha='left', fs=10)
    s.text(X(p, 0.5, -1.0), 'non-inverting input (+)', ha='left', fs=10)
    return s, [r'$V_{\mathrm{OUT}} = A\,(V_{+} - V_{-})$, where A is the open-loop gain',
               r'Ideal model: $A \rightarrow \infty$, input impedance $\rightarrow \infty$, output impedance $= 0$',
               'With negative feedback the loop drives the two inputs to the same voltage; power pins are not shown']


@circuit(90, F, 'Voltage Follower')
def c90():
    s = Sch()
    u = s.opamp((3, 0), 'U1', plus_top=True); n, p, o = u.in1, u.in2, u.out
    s.term((0, p[1]), VIN); s.wire((0, p[1]), p)
    jo = out_term(s, o)
    j = X(n, -0.7); yb = n[1] - 1.4
    s.wire(n, j, (j[0], yb), (jo[0], yb), jo)
    return s, [r'$V_{\mathrm{OUT}} = V_{\mathrm{IN}}$:   a non-inverting stage with a gain of exactly 1',
               'The output feeds straight back to the (−) input; the source sees a very high impedance',
               'and the load sees a very low one, so the stage isolates one from the other']


@circuit(91, F, 'Basic Integrator')
def c91():
    s = Sch()
    u = s.opamp((6, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    s.term((0, n[1]), VIN); s.R((0, n[1]), j, 'R1'); s.wire(j, n)
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 2.0, 'C', 'C1')
    gnd_plus(s, p)
    return s, [r'$V_{\mathrm{OUT}}(t) = -\dfrac{1}{R1\,C1}\int_0^t V_{\mathrm{IN}}\,dt + V_{\mathrm{OUT}}(0)$',
               'The input current V_IN/R1 charges C1 because the (−) input is held at virtual ground'.replace('V_IN', r'$V_{\mathrm{IN}}$'),
               'In practice a resistor across C1 (10 to 100 times R1) caps the DC gain so offsets cannot drift the output to a rail']


@circuit(92, F, 'Basic Differentiator')
def c92():
    s = Sch()
    u = s.opamp((6, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    s.term((0, n[1]), VIN); s.C((0, n[1]), j, 'C1'); s.wire(j, n)
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 2.0, 'R', 'R1')
    gnd_plus(s, p)
    return s, [r'$V_{\mathrm{OUT}} = -R1\,C1\,\dfrac{dV_{\mathrm{IN}}}{dt}$',
               'Gain rises with frequency, so noise is amplified; a small resistor R_S in series with C1'.replace('R_S', r'$R_{\mathrm{S}}$'),
               r'(and often a small capacitor across R1) limits the high-frequency gain:  $f_{\mathrm{limit}} = 1/(2\pi R_{\mathrm{S}}\,C1)$']


@circuit(93, F, 'First-Order Inverting Low-Pass Filter')
def c93():
    s = Sch()
    u = s.opamp((6, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    s.term((0, n[1]), VIN); s.R((0, n[1]), j, 'R1'); s.wire(j, n)
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 1.8, 'R', 'R2')
    y2 = n[1] + 3.4
    s.wire((j[0], n[1] + 1.8), (j[0], y2)); s.C((j[0], y2), (jo[0], y2), 'C1')
    s.wire((jo[0], y2), (jo[0], n[1] + 1.8)); s.dot((j[0], n[1] + 1.8), (jo[0], n[1] + 1.8))
    gnd_plus(s, p)
    return s, [r'Low-frequency gain $= -\dfrac{R2}{R1}$;   corner $f_{\mathrm{c}} = \dfrac{1}{2\pi R2\,C1}$',
               'Above the corner C1 shunts R2 and the gain falls at 20 dB per decade']


@circuit(94, F, 'First-Order Inverting High-Pass Filter')
def c94():
    s = Sch()
    u = s.opamp((7.5, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    s.term((0, n[1]), VIN); s.C((0, n[1]), (3.2, n[1]), 'C1'); s.R((3.2, n[1]), j, 'R1'); s.wire(j, n)
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 2.0, 'R', 'R2')
    gnd_plus(s, p)
    return s, [r'High-frequency gain $= -\dfrac{R2}{R1}$;   corner $f_{\mathrm{c}} = \dfrac{1}{2\pi R1\,C1}$',
               'Below the corner C1 dominates the input impedance and the gain falls at 20 dB per decade']


@circuit(95, F, 'Multiple-Feedback Band-Pass Filter')
def c95():
    s = Sch()
    u = s.opamp((8.0, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    a = (3.2, n[1])
    s.term((0, n[1]), VIN); s.R((0, n[1]), a, 'R1'); s.dot(a)
    j = X(n, -0.7)
    s.C(a, j, 'C2', loc='bottom'); s.wire(j, n); s.dot(j)
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 1.8, 'R', 'R2', dots=False)
    s.loop(a, jo, n[1] + 3.4, 'C', 'C1', dots=False); s.dot(jo)
    s.R(a, (a[0], a[1] - 2.6), 'R3', loc='left'); s.gnd((a[0], a[1] - 2.6))
    gnd_plus(s, p)
    return s, [r'With C1 = C2 = C:   $f_0 = \dfrac{1}{2\pi C\sqrt{R2\,(R1\parallel R3)}}$',
               r'$Q = \dfrac{1}{2}\sqrt{\dfrac{R2}{R1\parallel R3}}$;   gain at $f_0$:  $A_0 = -\dfrac{R2}{2\,R1}$',
               'R3 lets the centre frequency be trimmed without changing the gain at the peak']


@circuit(96, F, 'State-Variable (KHN) Filter')
def c96():
    s = Sch()
    u1 = s.opamp((4.0, 0), 'U1'); n1, p1, o1 = u1.in1, u1.in2, u1.out
    j1 = X(n1, -0.8)
    s.term((0, n1[1]), VIN); s.R((0, n1[1]), j1, 'R1'); s.wire(j1, n1); s.dot(j1)
    jo1 = X(o1, 0.6); s.wire(o1, jo1); s.dot(jo1)
    s.loop(j1, jo1, n1[1] + 2.0, 'R', 'R2', dots=False)
    u2 = s.opamp((jo1[0] + 3.0, o1[1]), 'U2'); n2, p2, o2 = u2.in1, u2.in2, u2.out
    j2 = X(n2, -0.6)
    s.R(jo1, j2, 'R6'); s.wire(j2, n2); s.dot(j2)
    jo2 = X(o2, 0.6); s.wire(o2, jo2); s.dot(jo2)
    s.loop(j2, jo2, n2[1] + 2.0, 'C', 'C1', dots=False)
    gnd_plus(s, p2, dx=0.4)
    u3 = s.opamp((jo2[0] + 3.0, o2[1]), 'U3'); n3, p3, o3 = u3.in1, u3.in2, u3.out
    j3 = X(n3, -0.6)
    s.R(jo2, j3, 'R7'); s.wire(j3, n3); s.dot(j3)
    jo3 = X(o3, 0.6); s.wire(o3, X(o3, 1.6)); s.dot(jo3)
    s.loop(j3, jo3, n3[1] + 2.0, 'C', 'C2', dots=False)
    gnd_plus(s, p3, dx=0.4)
    s.term(X(o3, 1.6), sub('V', 'LP'), 'right')
    s.text(X(jo1, 0, -0.45), sub('V', 'HP'), va='top', fs=10)
    s.text(X(jo2, -0.15, -0.5), sub('V', 'BP'), ha='right', va='top', fs=10)
    yt = n1[1] + 3.6
    s.dot((jo3[0], n3[1] + 2.0)); s.wire(jo3, (jo3[0], yt)); s.R((jo3[0], yt), (j1[0], yt), 'R3', loc='top')
    s.wire((j1[0], yt), (j1[0], n1[1] + 2.0)); s.dot((j1[0], n1[1] + 2.0))
    yb = p1[1] - 2.6
    xq = p1[0] - 0.4
    s.wire(jo2, (jo2[0], yb)); s.R((jo2[0], yb), (xq, yb), 'R4', loc='bottom')
    s.wire((xq, yb), (xq, p1[1]), p1); s.dot((xq, yb))
    s.R((xq, yb), (xq, yb - 2.4), 'R5', loc='left'); s.gnd((xq, yb - 2.4))
    return s, [r'With R6 = R7 = R and C1 = C2 = C:   $f_0 = \dfrac{1}{2\pi RC}$',
               r'With R1 = R2 = R3:   $Q = \dfrac{1}{3}\left(1 + \dfrac{R4}{R5}\right)$, set independently of $f_0$',
               r'U1 sums the input with the two fed-back outputs; U2 and U3 are integrators.',
               r'High-pass $V_{\mathrm{HP}}$ (U1), band-pass $V_{\mathrm{BP}}$ (U2) and low-pass $V_{\mathrm{LP}}$ (U3) outputs are all available']


@circuit(97, F, 'Basic Logarithmic Amplifier')
def c97():
    s = Sch()
    u = s.opamp((6, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    s.term((0, n[1]), VIN); s.R((0, n[1]), j, 'R1'); s.wire(j, n)
    jo = out_term(s, o)
    yt = n[1] + 3.2
    xm = (j[0] + jo[0]) / 2
    q = s.npn((xm, yt - 0.75), 'Q1', theta=90, lloc='top')
    c, e, b = q.collector, q.emitter, q.base
    s.wire(j, (j[0], c[1]), c); s.wire(e, (jo[0], e[1]), jo); s.dot(j)
    s.gnd(b, lead=0.0)
    gnd_plus(s, p)
    return s, [r'$V_{\mathrm{OUT}} = -\dfrac{kT}{q}\,\ln\dfrac{V_{\mathrm{IN}}}{I_{\mathrm{S}}\,R1}$   for $V_{\mathrm{IN}} > 0$',
               r'The input current $V_{\mathrm{IN}}/R1$ flows into the collector of Q1 (base grounded, collector at virtual ground),',
               r'so the output sits one base-emitter drop below ground, falling about 60 mV per decade of input at 25 °C',
               r'$I_{\mathrm{S}}$ and kT/q both vary with temperature; see 83 for a compensated version']


@circuit(98, F, 'Basic Antilog (Exponential) Amplifier')
def c98():
    s = Sch()
    u = s.opamp((6, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    q = s.npn((2.6, n[1] - 0.75), 'Q1', theta=90, flip=True, lloc='bottom')
    c, e, b = q.collector, q.emitter, q.base
    assert e[0] < c[0]
    s.term((0, n[1]), VIN)
    s.wire((0, n[1]), (e[0], n[1]), e)
    s.wire(c, (c[0], n[1]), j, n)
    s.gnd(b, lead=0.0)
    jo = out_term(s, o)
    s.loop(j, jo, n[1] + 2.0, 'R', 'R1')
    gnd_plus(s, p)
    return s, [r'$V_{\mathrm{OUT}} = I_{\mathrm{S}}\,R1\,e^{-qV_{\mathrm{IN}}/kT}$   for $V_{\mathrm{IN}} < 0$',
               r'The input drives the emitter of NPN Q1 (base grounded), so $V_{\mathrm{BE}} = -V_{\mathrm{IN}}$; the collector current',
               r'$I_{\mathrm{S}}\,e^{-qV_{\mathrm{IN}}/kT}$ is drawn from the virtual ground and returned through R1, making the output positive',
               'The output rises by a decade for each 60 mV more negative input at 25 °C; see 88 for a compensated version']


@circuit(99, F, 'Single-Diode Precision Half-Wave Rectifier')
def c99():
    s = Sch()
    u = s.opamp((5, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    s.term((0, n[1]), VIN); s.R((0, n[1]), j, 'R1'); s.wire(j, n)
    xk = o[0] + 2.6
    s.D((xk, o[1]), o, 'D1', loc='top')           # anode at the output node, cathode at U1
    s.wire((xk, o[1]), (xk + 1.4, o[1])); s.term((xk + 1.4, o[1]), VOUT, 'right'); s.dot((xk, o[1]))
    s.loop(j, (xk, o[1]), n[1] + 2.0, 'R', 'R2')
    s.R((xk, o[1]), (xk, o[1] - 2.6), RL, loc='right'); s.gnd((xk, o[1] - 2.6))
    gnd_plus(s, p)
    return s, [r'$V_{\mathrm{IN}} > 0$:  U1 output swings negative, D1 conducts and closes the loop:  $V_{\mathrm{OUT}} = -\dfrac{R2}{R1}\,V_{\mathrm{IN}}$',
               r'$V_{\mathrm{IN}} < 0$:  D1 is reverse-biased and $R_{\mathrm{L}}$ holds $V_{\mathrm{OUT}}$ near 0 V (needs $R_{\mathrm{L}} \ll R1 + R2$)',
               'D1 sits inside the loop, so its forward drop does not appear at the output;',
               'U1 saturates while D1 is off, which limits the usable frequency (see 52 for a faster two-diode version)']


@circuit(100, F, 'Open-Loop Comparator')
def c100():
    s = Sch()
    u = s.opamp((3, 0), 'U1', plus_top=True); n, p, o = u.in1, u.in2, u.out
    s.term((0, p[1]), VIN); s.wire((0, p[1]), p)
    s.term((0, n[1]), VREF); s.wire((0, n[1]), n)
    s.wire(o, X(o, 1.6)); s.term(X(o, 1.6), VOUT, 'right')
    return s, [r'$V_{\mathrm{OUT}} = V_{\mathrm{OH}}$ when $V_{\mathrm{IN}} > V_{\mathrm{REF}}$;   $V_{\mathrm{OUT}} = V_{\mathrm{OL}}$ when $V_{\mathrm{IN}} < V_{\mathrm{REF}}$',
               'With no feedback the full open-loop gain drives the output to one limit or the other;',
               'noise near the threshold can make it chatter (101 adds hysteresis)']


@circuit(101, F, 'Non-Inverting Schmitt Trigger')
def c101():
    s = Sch()
    u = s.opamp((5, 0), 'U1', plus_top=True); n, p, o = u.in1, u.in2, u.out
    j = X(p, -0.7)
    s.term((0, p[1]), VIN); s.R((0, p[1]), j, 'R1'); s.wire(j, p)
    s.term((1.2, n[1]), VREF); s.wire((1.2, n[1]), n)
    jo = out_term(s, o)
    s.loop(j, jo, p[1] + 2.0, 'R', 'R2')
    return s, [r'Rising threshold $V_{\mathrm{TH}} = V_{\mathrm{REF}}\left(1 + \dfrac{R1}{R2}\right) - V_{\mathrm{OL}}\dfrac{R1}{R2}$;   falling threshold $V_{\mathrm{TL}} = V_{\mathrm{REF}}\left(1 + \dfrac{R1}{R2}\right) - V_{\mathrm{OH}}\dfrac{R1}{R2}$',
               r'Hysteresis $V_{\mathrm{TH}} - V_{\mathrm{TL}} = (V_{\mathrm{OH}} - V_{\mathrm{OL}})\,R1/R2$:  R2 returns part of the output to the (+) input',
               'so the output snaps over and stays there until the input crosses the other threshold']


@circuit(102, F, 'Basic Wien-Bridge Oscillator')
def c102():
    s = Sch()
    u = s.opamp((8, 0), 'U1', plus_top=True); n, p, o = u.in1, u.in2, u.out
    jo = out_term(s, o)
    j = X(n, -0.8); s.wire(n, j)
    yb = n[1] - 1.6
    s.wire(j, (j[0], yb)); s.R((j[0], yb), (jo[0], yb), 'R4', loc='bottom'); s.wire((jo[0], yb), jo)
    s.dot((j[0], yb))
    s.R((j[0], yb), (j[0], yb - 2.6), 'R3', loc='left'); s.gnd((j[0], yb - 2.6))
    xa = 4.6
    yt = p[1] + 2.2
    s.wire(jo, (jo[0], yt)); s.C((jo[0], yt), (3.2, yt), 'C1', loc='top'); s.R((3.2, yt), (0.6, yt), 'R1', loc='top')
    s.wire((0.6, yt), (0.6, p[1]), (xa, p[1]), p); s.dot((xa, p[1]))
    xr, xc = xa - 1.5, xa
    s.dot((xr, p[1]))
    s.R((xr, p[1]), (xr, p[1] - 2.8), 'R2', loc='left'); s.gnd((xr, p[1] - 2.8))
    s.C((xc, p[1]), (xc, p[1] - 2.8), 'C2', loc='right'); s.gnd((xc, p[1] - 2.8))
    return s, [r'With R1 = R2 = R and C1 = C2 = C:   $f_0 = \dfrac{1}{2\pi RC}$',
               r'At $f_0$ the series R1-C1 arm and the parallel R2-C2 arm return one third',
               'of the output to the (+) input with no phase shift, so the loop needs a gain of 3:',
               'R4 = 2 R3.  Make R4 slightly larger to start, and add amplitude control',
               '(a lamp, thermistor or JFET, as in 29 and 34) to keep the sine wave clean']


@circuit(103, F, 'RC Phase-Shift Oscillator')
def c103():
    s = Sch()
    u = s.opamp((12.0, 0), 'U1'); n, p, o = u.in1, u.in2, u.out
    j = X(n, -0.7)
    jo = out_term(s, o)
    xs = [1.2, 4.2, 7.2]
    s.wire(j, n)
    for k, x in enumerate(xs):
        nxt = (xs[k + 1], n[1]) if k < 2 else (9.0, n[1])
        s.C((x, n[1]), (x + 1.8, n[1]), 'C%d' % (k + 1))
        s.wire((x + 1.8, n[1]), nxt)
    s.R((9.0, n[1]), j, 'R3'); s.dot(j)
    for k, x in enumerate((xs[1], xs[2])):
        s.dot((x, n[1])); s.R((x, n[1]), (x, n[1] - 2.6), 'R%d' % (k + 1), loc='left'); s.gnd((x, n[1] - 2.6))
    s.loop(j, jo, n[1] + 2.0, 'R', 'R4', dots=False)
    yt = n[1] + 3.6
    s.wire(jo, (jo[0], yt), (xs[0], yt), (xs[0], n[1]))
    gnd_plus(s, p)
    return s, [r'With C1 = C2 = C3 = C and R1 = R2 = R3 = R:   $f_0 = \dfrac{1}{2\pi RC\sqrt{6}}$',
               'R3 is the third leg of the RC ladder; it returns to the virtual ground at the (−) input.',
               r'The ladder shifts the phase by 180° at $f_0$ and attenuates by 29, so oscillation needs R4 = 29 R3',
               '(slightly more to start)']
