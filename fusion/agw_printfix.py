# AgriWing Rev D print fixes: 45 deg battery-rail wedges, planar joint faces (W1/W2/winglet), 45 deg servo-bay roof,
# printed horn -> slot for a 1.5 mm G10 horn. Right side built, left mirrored for wing parts; centerbody both sides direct.
import math
tbm = adsk.fusion.TemporaryBRepManager.get(); BO = adsk.fusion.BooleanTypes
Un, Sb, In = BO.UnionBooleanType, BO.DifferenceBooleanType, BO.IntersectionBooleanType
root = design.rootComponent
C = {o.component.name: o.component for o in root.occurrences}
wc, cb, hw = C['WingC'], C['Centerbody'], C['Hardware']
LOG = []
P = lambda x, y, z=0.0: adsk.core.Point3D.create(x / 10, y / 10, z / 10)
V = adsk.core.Vector3D.create
def cp(b): return tbm.copy(b)
def op(t, tool, k, tag=''):
    try: tbm.booleanOperation(t, tool, k)
    except Exception as e: LOG.append(('FAIL', tag, str(e)[:60]))
    return t
def tbox(x0, x1, y0, y1, z0, z1): return tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), V(1, 0, 0), V(0, 1, 0), (x1 - x0) / 10, (y1 - y0) / 10, (z1 - z0) / 10))
def wedge_yz(x0, x1, y0, ztop, h, sgn):
    """Triangular prism along x: legs from (y0, ztop) down to (y0, ztop-h) and across to (y0+sgn*h, ztop-h); 45 deg hypotenuse."""
    r2 = math.sqrt(0.5)
    q = tbox(x0, x1, min(y0, y0 + sgn * h), max(y0, y0 + sgn * h), ztop - h, ztop)
    n = (0.0, sgn * r2, r2); w = (0.0, r2, -sgn * r2); D = 100.0
    c = (0.5 * (x0 + x1), y0 + n[1] * D / 2, ztop + n[2] * D / 2)
    hs = tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P(*c), V(1, 0, 0), V(*w), (x1 - x0 + 2) / 10, 200.0 / 10, D / 10))
    op(q, hs, Sb, 'wedge cut')
    return q
def replace(comp, name, t, tag):
    old = comp.bRepBodies.itemByName(name); ap = old.appearance; v0 = old.volume
    if comp.bRepBodies.itemByName(name + '_' + tag): old.deleteMe()
    else: old.name = name + '_' + tag; old.isLightBulbOn = False
    nb = comp.bRepBodies.add(t); nb.name = name; nb.appearance = ap
    LOG.append((name, round(v0, 2), round(nb.volume, 2), nb.lumps.count)); return nb
# 1) battery rails: 45 deg wedge on the bed side (front pieces print root-rib down, so +y side for the right piece)
for name, sg in (('CB_FrontRight', 1), ('CB_FrontLeft', -1)):
    t = cp(cb.bRepBodies.itemByName(name))
    for yr in (2.5, 52.5):
        w = wedge_yz(-51.4, 16.6, sg * yr, -9.5, 7.3, sg)
        op(w, cp(cb.bRepBodies.itemByName('CB_OML_ref')), In, 'wedge in oml')
        op(t, w, Un, f'{name} rail wedge {yr}')
    replace(cb, name, t, 'prePrint')
# 2) planar joint faces
w1 = cp(wc.bRepBodies.itemByName('W1_R')); w2 = cp(wc.bRepBodies.itemByName('W2_R')); bw = cp(wc.bRepBodies.itemByName('WingletBlend_R'))
op(w2, tbox(-300, 600, 315.0, 441.0, -80, 120), In, 'W2 >= 315')
op(bw, tbox(-300, 600, 440.0, 700.0, -80, 200), In, 'BW >= 440')
op(w2, tbox(-300, 600, 300.0, 440.0, -80, 120), In, 'W2 <= 440')
op(w1, tbox(-300, 600, 100.0, 315.0, -80, 120), In, 'W1 <= 315')
# 3) servo bay: stepped 45 deg roof above the y = 204.6 end (bay x 86..121, z up to top skin - 0.8)
OML = wc.bRepBodies.itemByName('WingOML_R')
dn = cp(OML); m = adsk.core.Matrix3D.create(); m.translation = V(0, 0, -0.08); tbm.transform(dn, m)
for d in range(1, 16):
    r = tbox(86.0 + d, 121.0 - d, 204.0, 204.6 + d, -40, 40); op(r, cp(dn), In, 'roof oml')
    zc = tbox(86.0, 121.0, 204.0, 205.0 + d, -40, 13.3 - d); op(r, zc, In, 'roof z')
    op(w1, r, Sb, f'roof {d}')
# 4) horn: remove the printed horn, cut a 1.7 x 16 x 5 slot for a 1.5 mm G10 horn
e1 = cp(wc.bRepBodies.itemByName('Elevon1_R'))
horn = cp(e1); op(horn, cp(OML), Sb, 'horn = outside oml'); op(e1, horn, Sb, 'e1 - horn')
hb = horn.boundingBox; hx0, hx1 = hb.minPoint.x * 10, hb.maxPoint.x * 10; hy0, hy1 = hb.minPoint.y * 10, hb.maxPoint.y * 10
yc = 0.5 * (hy0 + hy1); zs = hb.maxPoint.z * 10
slot = tbox(hx0, hx1, yc - 0.85, yc + 0.85, zs - 6.0, zs + 5.0); op(e1, slot, Sb, 'horn slot')
g10 = cp(horn); op(g10, tbox(hx0 - 1, hx1 + 1, yc - 0.75, yc + 0.75, -80, 80), In, 'g10 thickness')
tab = tbox(hx0 + 0.2, hx1 - 0.2, yc - 0.75, yc + 0.75, zs - 5.0, zs + 0.5); op(tab, cp(OML), In, 'tab in oml'); op(g10, tab, Un, 'g10 + tab')
LOG.append(('horn', [round(v, 1) for v in (hx0, hx1, hy0, hy1, zs)]))
mm = adsk.core.Matrix3D.create(); mm.setCell(1, 1, -1.0)
for n, t in (('W1_R', w1), ('W2_R', w2), ('WingletBlend_R', bw), ('Elevon1_R', e1)):
    replace(wc, n, t, 'prePrint'); tl = cp(t); tbm.transform(tl, mm); replace(wc, n[:-1] + 'L', tl, 'prePrint')
for s, t in (('R', g10), ('L', None)):
    if s == 'L': t = cp(g10); tbm.transform(t, mm)
    old = hw.bRepBodies.itemByName('HornG10_' + s)
    if old: old.deleteMe()
    nb = hw.bRepBodies.add(t); nb.name = 'HornG10_' + s
RESULT = LOG
