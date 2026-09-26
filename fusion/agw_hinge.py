# AgriWing Rev D: round-nose elevons + concave cove (0.6 mm gap) so the elevons deflect +-25 deg;
# Elevon1 inboard end on a plane normal to the hinge (slides off square). Right side; left mirrored.
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
def obox(c, u, v, lu, lv, lw): return tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P(*c), V(*u), V(*v), lu / 10, lv / 10, lw / 10))
def tbox(x0, x1, y0, y1, z0, z1): return obox(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (1, 0, 0), (0, 1, 0), x1 - x0, y1 - y0, z1 - z0)
le, ch = W['w_le'], W['w_chord']
up, lo = W['_updown'](W['T0']); I = W['_interp']
HA, HB = (161.8, 152.0, 2.1), (240.9, 468.0, 8.8)
h = [HB[i] - HA[i] for i in range(3)]; L = math.sqrt(sum(v * v for v in h)); h = [v / L for v in h]
hp2 = (h[0], h[1]); n2 = math.hypot(*hp2); hp2 = (hp2[0] / n2, hp2[1] / n2)
pv = (hp2[1], -hp2[0])                                    # plan-view normal to the hinge, pointing aft
def ax(y):                                                # point on the hinge axis at span y
    f = (y - HA[1]) / (HB[1] - HA[1]); return tuple(HA[i] + f * (HB[i] - HA[i]) for i in range(3))
def half_t(y): c = ch(y); return (I(up, 0.75) - I(lo, 0.75)) * c / 2
r0, r1 = half_t(150.0) - 0.15, half_t(470.0) - 0.15
rr = lambda y: r0 + (r1 - r0) * (y - 150.0) / 320.0
def cone(y0, y1, dr=0.0): return tbm.createCylinderOrCone(P(*ax(y0)), (rr(y0) + dr) / 10, P(*ax(y1)), (rr(y1) + dr) / 10)
def aft_plane(off=0.0, aft=True):
    """Vertical half-space behind (aft) / ahead of the plan hinge line shifted by off (mm, + = aft)."""
    s = 1 if aft else -1; c0 = ax(310.0); c = (c0[0] + pv[0] * (off + s * 300), c0[1] + pv[1] * (off + s * 300), 0)
    return obox(c, (hp2[0], hp2[1], 0), (pv[0], pv[1], 0), 2000, 600, 400)
def end_plane(P0, keep_out=True, off=0.0):
    """Half-space s=(P-P0).h >= off (keep_out) or <= off, h = hinge direction."""
    s = 1 if keep_out else -1; c = (P0[0] + h[0] * (off + s * 300), P0[1] + h[1] * (off + s * 300), P0[2] + h[2] * (off + s * 300))
    return obox(c, tuple(h), (pv[0], pv[1], 0), 600, 600, 400)
OML = B('WingOML_R')
hinge_bore = tbm.createCylinderOrCone(P(*ax(140.0)), 0.095, P(*ax(475.0)), 0.095)
R0, R1 = (174.4, 158.0, 1.8), (239.9, 432.0, 8.8)
def rl(y): f = (y - R0[1]) / (R1[1] - R0[1]); return tuple(R0[i] + f * (R1[i] - R0[i]) for i in range(3))
torque_bore = tbm.createCylinderOrCone(P(*rl(150.0)), 0.105, P(*rl(438.0)), 0.105)
def kn(yc, r, hl=5.0): return tbm.createCylinderOrCone(P(*ax(yc - hl)), r / 10, P(*ax(yc + hl)), r / 10)
def web(yc, rk, hl=5.0, extra=0.0):
    """Knuckle web: from the hinge axis forward to the wing, 2*rk thick, span yc+-hl, oriented with the hinge."""
    c = ax(yc); d = rr(yc) + 3.0
    cc = (c[0] - pv[0] * d / 2, c[1] - pv[1] * d / 2, c[2])
    return obox(cc, tuple(h), (pv[0], pv[1], 0), 2 * hl, d, 2 * rk + extra)
def fwd_sector(yc, hl):
    """Everything ahead of the hinge axis over span yc+-hl (elevon relief at wing knuckles)."""
    c = ax(yc); cc = (c[0] - pv[0] * 20, c[1] - pv[1] * 20, c[2])
    return obox(cc, tuple(h), (pv[0], pv[1], 0), 2 * hl, 40, 60)
# Elevon1 inboard end: plane normal to h through the TE at y = 143 (area-neutral), 1 mm gap split +-0.5
PE = (le(143.0) + ch(143.0), 143.0, 0.0)
def elevon(y0, y1, wing_kn, inboard_end):
    e = cp(OML); op(e, aft_plane(0.0, True), In, 'e aft')
    nose = cone(y0 - 12, y1 + 12); op(nose, cp(OML), In, 'nose oml'); op(e, nose, Un, 'e nose')
    op(e, tbox(-300, 600, y0 - 12 if inboard_end else y0, y1, -80, 120), In, 'e span')
    if inboard_end: op(e, end_plane(PE, True, 0.5), In, 'e inboard end')
    for yc, r in wing_kn: op(e, kn(yc, r + 0.4, 5.4), Sb, f'e clr {yc}'); op(e, fwd_sector(yc, 5.4), Sb, f'e sector {yc}')
    op(e, cp(hinge_bore), Sb, 'e pin'); op(e, cp(torque_bore), Sb, 'e rod')
    return e
E1 = elevon(150.0, 314.5, ((158, 2.4), (230, 2.4), (300, 2.4)), True)
E2 = elevon(315.5, 438.8, ((325, 2.1), (400, 2.1)), False)
horn = cp(B('Elevon1_R')); op(horn, cp(OML), Sb, 'horn only'); op(E1, horn, Un, 'e1 horn')    # the printed horn sits outside the OML
# wing: remove everything aft of the hinge line and inside the cove, keep own knuckles
def wing_cut(name, y0, y1, own, inboard_end):
    w = cp(B(name))
    cut = aft_plane(0.0, True); op(cut, tbox(-300, 600, y0, y1, -80, 120), In, name + ' cut span')
    if inboard_end: op(cut, end_plane(PE, True, -0.5), In, name + ' cut end')
    cove = cone(y0 - 12, y1 + 12, 0.6); op(cove, tbox(-300, 600, y0, y1, -80, 120), In, name + ' cove span')
    if inboard_end: op(cove, end_plane(PE, True, -0.5), In, name + ' cove end')
    op(cut, cove, Un, name + ' cut+cove')
    for yc, r in own: op(cut, kn(yc, r), Sb, f'{name} keep {yc}'); op(cut, web(yc, r), Sb, f'{name} keep web {yc}')
    op(cut, cp(hinge_bore), Un, name + ' pin')
    op(w, cut, Sb, name + ' cut')
    # refill the root strip the elevon gave up (inboard of the end plane, forward of the TE), to the OML
    if inboard_end:
        fill = cp(OML); op(fill, aft_plane(0.0, True), In, 'fill aft'); op(fill, tbox(-300, 600, 130.0, 175.0, -80, 120), In, 'fill span')
        op(fill, end_plane(PE, False, -0.5), In, 'fill end'); op(fill, cp(hinge_bore), Sb, 'fill pin')
        op(w, fill, Un, name + ' fill')
    return w
W1n = wing_cut('W1_R', 130.0, 315.0, ((158, 2.4), (230, 2.4), (300, 2.4)), True)
W2n = wing_cut('W2_R', 315.0, 440.0, ((325, 2.1), (400, 2.1)), False)
mm = adsk.core.Matrix3D.create(); mm.setCell(1, 1, -1.0)
def replace(name, t):
    old = B(name); ap = old.appearance; v0 = old.volume
    if B(name + '_preHinge'): old.deleteMe()
    else: old.name = name + '_preHinge'; old.isLightBulbOn = False
    nb = wc.bRepBodies.add(t); nb.name = name; nb.appearance = ap
    LOG.append((name, round(v0, 2), round(nb.volume, 2), nb.lumps.count))
for n, t in (('Elevon1_R', E1), ('Elevon2_R', E2), ('W1_R', W1n), ('W2_R', W2n)):
    replace(n, t); tl = cp(t); tbm.transform(tl, mm); replace(n[:-1] + 'L', tl)
RESULT = {'log': LOG, 'r0r1': (round(r0, 2), round(r1, 2)), 'PE': PE}
