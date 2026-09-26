# AgriWing Rev D: solid wing parts (slicer sets walls/infill). Each part = old Rev C part  U  (outer-shape region - functional voids).
# Adds the O2 carbon torque rod that couples Elevon1 and Elevon2. Right side built, left mirrored.
import math
LIB = './revc.py'
W = {'adsk': adsk, 'math': math, 'design': design, '__file__': LIB}; exec(open(LIB).read(), W)
tbm = adsk.fusion.TemporaryBRepManager.get(); BO = adsk.fusion.BooleanTypes
Un, Sb, In = BO.UnionBooleanType, BO.DifferenceBooleanType, BO.IntersectionBooleanType
root = design.rootComponent
wc = root.occurrences.itemByName('WingC:1').component
B = lambda n: wc.bRepBodies.itemByName(n)
LOG = []
P = lambda x, y, z=0.0: adsk.core.Point3D.create(x / 10, y / 10, z / 10)
V = adsk.core.Vector3D.create
def cp(b): return tbm.copy(b)
def op(t, tool, k, tag=''):
    try: tbm.booleanOperation(t, tool, k)
    except Exception as e: LOG.append(('FAIL', tag, str(e)[:60]))
    return t
def rod(p0, p1, r): return tbm.createCylinderOrCone(P(*p0), r / 10, P(*p1), r / 10)
def tbox(x0, x1, y0, y1, z0, z1):
    return tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), V(1, 0, 0), V(0, 1, 0), (x1 - x0) / 10, (y1 - y0) / 10, (z1 - z0) / 10))
def aft_of(A, Bp, aft=True):
    """Half-space behind (aft=True) or ahead of the plan-view line A-B (x,y)."""
    dx, dy = Bp[0] - A[0], Bp[1] - A[1]; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = uy, -ux
    if (nx < 0) == aft: nx, ny = -nx, -ny
    c = ((A[0] + Bp[0]) / 2 + nx * 300, (A[1] + Bp[1]) / 2 + ny * 300, 0)
    return tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P(*c), V(ux, uy, 0), V(nx, ny, 0), 200.0, 60.0, 40.0))
le, ch = W['w_le'], W['w_chord']
t20 = math.tan(math.radians(20)); ZS = 2.0
xh = lambda y: le(y) + 0.75 * ch(y); xte = lambda y: le(y) + ch(y)
up, lo = W['_updown'](W['T0'])
def hp(y):
    c = ch(y); tw = math.radians(W['w_twist'](y)); xc = 0.75
    zc = (W['_interp'](up, xc) + W['_interp'](lo, xc)) / 2 * c; xl = (xc - 0.25) * c
    return (le(y) + 0.25 * c + xl * math.cos(tw) + zc * math.sin(tw) - 0.5, y, -xl * math.sin(tw) + zc * math.cos(tw))
HA, HB = hp(152.0), hp(468.0)
def on_line(y):
    f = (y - HA[1]) / (HB[1] - HA[1]); return tuple(HA[i] + f * (HB[i] - HA[i]) for i in range(3))
OML = B('WingOML_R')
gap = aft_of((xh(149) - 1, 149), (xh(471) - 1, 471), True); op(gap, tbox(-300, 500, 149, 471, -80, 120), In, 'gap y')
ezone = aft_of((xh(150), 150), (xh(470), 470), True); op(ezone, tbox(-300, 500, 150, 470, -80, 120), In, 'ezone y')
hinge_bore = rod(on_line(150.0), on_line(470.0), 0.95)
# torque rod O2 (bore 2.1) at 80 % chord, 156..436, couples Elevon1 + Elevon2
R0, R1 = (174.4, 158.0, 1.8), (239.9, 432.0, 8.8)
def rline(y):
    f = (y - R0[1]) / (R1[1] - R0[1]); return tuple(R0[i] + f * (R1[i] - R0[i]) for i in range(3))
torque_bore = rod(rline(156.0), rline(436.0), 1.05)
def knuck(yc, r, h=5.4): return rod(on_line(yc - h), on_line(yc + h), r)
def dowel(y0, xc, z0, h):
    x0 = le(y0) + xc * ch(y0); return rod((x0 - h * t20, y0 - h, z0), (x0 + h * t20, y0 + h, z0), 1.6)
OML_dn = cp(OML); m = adsk.core.Matrix3D.create(); m.translation = V(0, 0, -0.08); tbm.transform(OML_dn, m)
bay = tbox(86.0, 121.0, 172.4, 204.6, -40, 40); op(bay, cp(OML_dn), In, 'bay')
for lug in (tbox(86.0, 91.5, 195.0, 199.0, -5.3, 6.2), tbox(116.1, 121.0, 195.0, 199.0, -5.3, 6.2)): op(bay, lug, Sb, 'lug')
xp = le(130) + 0.62 * ch(130)
VOIDS_W1 = [rod((125 * t20, 125, ZS), (320 * t20, 320, ZS), 3.1),                       # spar bore
            rod((xp - 5 * t20, 125, 2.5), (xp + 51 * t20, 181, 2.5), 1.6),               # root pin bore
            rod((35.0, 129.5, 2.5), (35.0, 133.7, 2.5), 5.1), rod((85.0, 129.5, 2.5), (85.0, 133.7, 2.5), 5.1),   # magnets
            bay, tbox(103.0, 117.0, 199.5, 206.0, -40, 4.5),                             # servo bay, arm slot
            rod((89.9, 192.0, 0.45), (89.9, 200.0, 0.45), 0.8), rod((117.7, 192.0, 0.45), (117.7, 200.0, 0.45), 0.8),
            rod((99.5, 125.0, 0.5), (100.0, 176.0, 0.5), 3.0),                           # servo lead channel to the root
            dowel(315.0, 0.12, 1.5, 16), dowel(315.0, 0.62, 1.5, 16),
            knuck(180, 2.8), knuck(262, 2.8), cp(hinge_bore)]
VOIDS_W2 = [rod((310 * t20, 310, ZS), (467 * t20, 467, ZS), 3.1),
            dowel(315.0, 0.12, 1.5, 16), dowel(315.0, 0.62, 1.5, 16), dowel(440.0, 0.14, 1.2, 13), dowel(440.0, 0.58, 1.2, 13),
            knuck(360, 2.5), knuck(435, 2.5), cp(hinge_bore)]
VOIDS_BW = [rod((436 * t20, 436, ZS), (467 * t20, 467, ZS), 3.1), dowel(440.0, 0.14, 1.2, 13), dowel(440.0, 0.58, 1.2, 13)]
VOIDS_E1 = [knuck(158, 2.8), knuck(230, 2.8), knuck(300, 2.8), cp(hinge_bore), cp(torque_bore)]
VOIDS_E2 = [knuck(325, 2.5), knuck(400, 2.5), cp(hinge_bore), cp(torque_bore)]
OWN_KN = {'W1_R': (158, 230, 300), 'W2_R': (325, 400)}
def solid(name, region, voids):
    old = B(name + '_hollowC') or B(name); t = cp(region)
    op(t, cp(old), Un, name + ' +old')
    for i, v in enumerate(voids): op(t, cp(v), Sb, f'{name} void {i}')   # after the union: Rev C ribs no longer block bores
    if name in OWN_KN:                                                   # Rev C ribs crossed the elevon zone: clear it, keep own knuckles
        cutter = cp(gap)
        for yc in OWN_KN[name]: op(cutter, rod(on_line(yc - 5.0), on_line(yc + 5.0), 2.4), Sb, name + ' keep knuckle')
        op(cutter, cp(hinge_bore), Un, name + ' cutter pin')
        op(t, cutter, Sb, name + ' clear elevon zone')
    if name.startswith('Elevon'): op(t, cp(torque_bore), Sb, name + ' torque bore')
    return t
reg_w1 = cp(OML); op(reg_w1, tbox(-300, 500, 130.0, 315.0, -80, 120), In, 'reg w1')
reg_w2 = cp(OML); op(reg_w2, tbox(-300, 500, 315.0, 440.0, -80, 120), In, 'reg w2')
reg_bw = cp(B('BW_outer_ref'))
reg_e1 = cp(OML); op(reg_e1, cp(ezone), In, 'e1 zone'); op(reg_e1, tbox(-300, 500, 150.0, 314.5, -80, 120), In, 'e1 y')
reg_e2 = cp(OML); op(reg_e2, cp(ezone), In, 'e2 zone'); op(reg_e2, tbox(-300, 500, 315.5, 438.8, -80, 120), In, 'e2 y')
NEW = {'W1_R': solid('W1_R', reg_w1, VOIDS_W1), 'W2_R': solid('W2_R', reg_w2, VOIDS_W2), 'WingletBlend_R': solid('WingletBlend_R', reg_bw, VOIDS_BW),
       'Elevon1_R': solid('Elevon1_R', reg_e1, VOIDS_E1), 'Elevon2_R': solid('Elevon2_R', reg_e2, VOIDS_E2)}
op(NEW['W1_R'], cp(NEW['W2_R']), Sb, 'W1 - W2 at the 315 joint')
op(NEW['W2_R'], cp(NEW['WingletBlend_R']), Sb, 'W2 - winglet at the 440 joint')
mm = adsk.core.Matrix3D.create(); mm.setCell(1, 1, -1.0)
def replace(name, t):
    old = B(name); ap = old.appearance; v0 = (B(name + '_hollowC') or old).volume
    if B(name + '_hollowC'): old.deleteMe()
    else: old.name = name + '_hollowC'; old.isLightBulbOn = False
    nb = wc.bRepBodies.add(t); nb.name = name; nb.appearance = ap
    LOG.append((name, round(v0, 1), round(nb.volume, 1), nb.lumps.count))
for n, t in NEW.items():
    replace(n, t)
    tl = cp(t); tbm.transform(tl, mm); replace(n[:-1] + 'L', tl)
RESULT = LOG
