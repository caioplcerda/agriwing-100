# AgriWing Rev D: straight carry-through spar. O6 solid CF joiner across the centerbody (x=145, z=2.3, y -275..275),
# 8x6 CF tube glued in each wing (y 131..438), wings slide on along y. Old swept spar, swept pin and swept seam dowels
# are filled; new O3 anti-rotation pin (x=60) and seam dowels run along y. Right side built, left mirrored.
import math
LIB = './revc.py'
W = {'adsk': adsk, 'math': math, 'design': design, '__file__': LIB}; exec(open(LIB).read(), W)
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
def rod(p0, p1, r): return tbm.createCylinderOrCone(P(*p0), r / 10, P(*p1), r / 10)
def tbox(x0, x1, y0, y1, z0, z1): return tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), V(1, 0, 0), V(0, 1, 0), (x1 - x0) / 10, (y1 - y0) / 10, (z1 - z0) / 10))
le, ch = W['w_le'], W['w_chord']; t20 = math.tan(math.radians(20)); ZS = 2.0
XS, ZJ = 145.0, 2.3; XP = 60.0
def ydowel(y0, xc, z0, h): x0 = le(y0) + xc * ch(y0); return rod((x0, y0 - h, z0), (x0, y0 + h, z0), 1.6)
def sdowel(y0, xc, z0, h): x0 = le(y0) + xc * ch(y0); return rod((x0 - h * t20, y0 - h, z0), (x0 + h * t20, y0 + h, z0), 1.6)
OMLw = wc.bRepBodies.itemByName('WingOML_R'); OMLb = cb.bRepBodies.itemByName('CB_OML_ref'); BWo = wc.bRepBodies.itemByName('BW_outer_ref')
xp_old = le(130) + 0.62 * ch(130)
# ---------- wing parts (right)
def fill(t, rods, env, tag):
    for i, r in enumerate(rods):
        f = r; op(f, cp(env), In, f'{tag} fill env {i}'); op(t, f, Un, f'{tag} fill {i}')
def wing_part(name, y0, y1, env, fills, cuts):
    t = cp(wc.bRepBodies.itemByName(name))
    e = cp(env); op(e, tbox(-300, 600, y0, y1, -80, 200), In, name + ' env')
    fill(t, fills, e, name)
    for i, c in enumerate(cuts): op(t, c, Sb, f'{name} cut {i}')
    return t
old_spar = lambda: rod((120 * t20, 120, ZS), (470 * t20, 470, ZS), 3.1)
new_tube = lambda: rod((XS, 129.0, ZJ), (XS, 438.0, ZJ), 4.05)
W1n = wing_part('W1_R', 130.0, 315.0, OMLw,
                [old_spar(), rod((xp_old - 5 * t20, 125, 2.5), (xp_old + 51 * t20, 181, 2.5), 1.6), sdowel(315.0, 0.12, 1.5, 16), sdowel(315.0, 0.62, 1.5, 16)],
                [new_tube(), rod((XP, 128.0, ZJ), (XP, 160.0, ZJ), 1.6), ydowel(315.0, 0.12, 1.5, 16), ydowel(315.0, 0.62, 1.5, 16)])
W2n = wing_part('W2_R', 315.0, 440.0, OMLw,
                [old_spar(), sdowel(315.0, 0.12, 1.5, 16), sdowel(315.0, 0.62, 1.5, 16), sdowel(440.0, 0.14, 1.2, 13), sdowel(440.0, 0.58, 1.2, 13)],
                [new_tube(), ydowel(315.0, 0.12, 1.5, 16), ydowel(315.0, 0.62, 1.5, 16), ydowel(440.0, 0.14, 1.2, 13), ydowel(440.0, 0.58, 1.2, 13)])
BWn = wing_part('WingletBlend_R', 439.0, 700.0, BWo,
                [old_spar(), sdowel(440.0, 0.14, 1.2, 13), sdowel(440.0, 0.58, 1.2, 13)],
                [ydowel(440.0, 0.14, 1.2, 13), ydowel(440.0, 0.58, 1.2, 13)])
# ---------- centerbody (right pieces)
cbF = cp(cb.bRepBodies.itemByName('CB_FrontRight'))
envF = cp(OMLb); op(envF, tbox(-200, 95.0, 0.0, 131.0, -80, 200), In, 'envF')
fill(cbF, [rod((60 * t20, 60, ZS), (135 * t20, 135, ZS), 3.1), rod((xp_old - 40 * t20, 90, 2.5), (xp_old + 5 * t20, 135, 2.5), 1.6)], envF, 'CBF')
boss = rod((XP, 100.0, ZJ), (XP, 130.0, ZJ), 4.0); op(boss, cp(envF), In, 'pin boss env'); op(cbF, boss, Un, 'pin boss')
op(cbF, rod((XP, 104.0, ZJ), (XP, 131.0, ZJ), 1.6), Sb, 'pin socket')
cbR = cp(cb.bRepBodies.itemByName('CB_RearRight'))
envR = cp(OMLb); op(envR, tbox(95.0, 400, 0.0, 131.0, -80, 200), In, 'envR')
for y0, y1 in ((18.0, 40.0), (108.0, 131.0)):
    web = tbox(XS - 3.5, XS + 3.5, y0, y1, -40, 40); op(web, cp(envR), In, 'web env'); op(cbR, web, Un, f'web {y0}')
op(cbR, rod((XS, -1.0, ZJ), (XS, 132.0, ZJ), 3.05), Sb, 'joiner bore')
# ---------- replace + mirror
mm = adsk.core.Matrix3D.create(); mm.setCell(1, 1, -1.0)
def replace(comp, name, t):
    old = comp.bRepBodies.itemByName(name); ap = old.appearance; v0 = old.volume
    if comp.bRepBodies.itemByName(name + '_preJoin'): old.deleteMe()
    else: old.name = name + '_preJoin'; old.isLightBulbOn = False
    nb = comp.bRepBodies.add(t); nb.name = name; nb.appearance = ap
    LOG.append((name, round(v0, 2), round(nb.volume, 2), nb.lumps.count)); return nb
for n, t in (('W1_R', W1n), ('W2_R', W2n), ('WingletBlend_R', BWn)):
    replace(wc, n, t); tl = cp(t); tbm.transform(tl, mm); replace(wc, n[:-1] + 'L', tl)
for n, t in (('CB_FrontRight', cbF), ('CB_RearRight', cbR)):
    replace(cb, n, t); tl = cp(t); tbm.transform(tl, mm); replace(cb, n.replace('Right', 'Left'), tl)
# ---------- hardware
cf = hw.bRepBodies.itemByName('Spar_R_6x4_CF').appearance
for n in ('Spar_R_6x4_CF', 'Spar_L_6x4_CF', 'Pin_R_3mm_CF', 'Pin_L_3mm_CF', 'Joiner_O6_CF', 'WingTube_R_8x6_CF', 'WingTube_L_8x6_CF', 'PinY_R_3mm_CF', 'PinY_L_3mm_CF'):
    b = hw.bRepBodies.itemByName(n)
    if b: b.deleteMe()
def addhw(name, body):
    b = hw.bRepBodies.add(body); b.name = name; b.appearance = cf
tube = rod((XS, 131.0, ZJ), (XS, 438.0, ZJ), 4.0); op(tube, rod((XS, 130.0, ZJ), (XS, 439.0, ZJ), 3.0), Sb, 'tube id')
addhw('Joiner_O6_CF', rod((XS, -275.0, ZJ), (XS, 275.0, ZJ), 3.0))
addhw('WingTube_R_8x6_CF', cp(tube)); tl = cp(tube); tbm.transform(tl, mm); addhw('WingTube_L_8x6_CF', tl)
addhw('PinY_R_3mm_CF', rod((XP, 105.0, ZJ), (XP, 158.0, ZJ), 1.5)); addhw('PinY_L_3mm_CF', rod((XP, -158.0, ZJ), (XP, -105.0, ZJ), 1.5))
# receiver off the spar line: x 118..138, y 18..30 (right side, beside the FC)
rx = hw.bRepBodies.itemByName('RX_ELRS'); ap = rx.appearance; bb = rx.boundingBox
t = cp(rx); m = adsk.core.Matrix3D.create(); m.translation = V((118.0 - bb.minPoint.x * 10) / 10, (18.0 - bb.minPoint.y * 10) / 10, 0); tbm.transform(t, m)
rx.deleteMe(); nr = hw.bRepBodies.add(t); nr.name = 'RX_ELRS'; nr.appearance = ap
RESULT = LOG
