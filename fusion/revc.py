# AgriWing-100 Rev B geometry library (executed inside Fusion; needs adsk, math, design, __file__)
import math
BASE = __file__.rsplit('/', 1)[0] + '/'
AF = []
for ln in open(BASE + 'mh60.dat').read().splitlines()[1:]:
    p = ln.split()
    if len(p) == 2: AF.append((float(p[0]), float(p[1])))
T0 = 0.1008
def af_points(t=T0, te=0.0025):
    n = len(AF); out = []
    for i, (x, y) in enumerate(AF):
        ramp = max(0.0, (x - 0.7) / 0.3); sgn = 1 if i < n // 2 else -1
        out.append((x, y * t / T0 + sgn * te * ramp))
    return out
def naca00(t, n=40):
    xs = [0.5 * (1 - math.cos(math.pi * i / n)) for i in range(n + 1)]
    yt = lambda x: 5 * t * (0.2969 * math.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1036 * x**4)
    up = [(x, yt(x)) for x in reversed(xs)]; lo = [(x, -yt(x)) for x in xs[1:]]
    return up + lo            # TE -> LE -> TE, closed (sharp TE)

SWEEP = math.radians(20.0); Y_JOINT = 130.0; SEMI = 500.0; WASHOUT = 7.0
def w_chord(y): return 248.0 + (136.0 - 248.0) * abs(y) / SEMI
def w_xqc(y): return abs(y) * math.tan(SWEEP)
def w_twist(y): return -WASHOUT * max(0.0, abs(y) - Y_JOINT) / (SEMI - Y_JOINT)
def w_le(y): return w_xqc(y) - 0.25 * w_chord(y)
# centerbody stations: (y, LE x, chord, t/c, dz)
CB = [(0.0, -95.0, 330.0, 0.180, 0.0), (60.0, -80.0, 305.0, 0.160, 0.0),
      (Y_JOINT, w_le(Y_JOINT), w_chord(Y_JOINT), T0, 0.0)]
Z_THRUST = 2.0

def plane_y(comp, y, name):
    pin = comp.constructionPlanes.createInput()
    pin.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(y / 10))
    pl = comp.constructionPlanes.add(pin); pl.name = name; pl.isLightBulbOn = False; return pl
def plane_z(comp, z, name):
    pin = comp.constructionPlanes.createInput()
    pin.setByOffset(comp.xYConstructionPlane, adsk.core.ValueInput.createByReal(z / 10))
    pl = comp.constructionPlanes.add(pin); pl.name = name; pl.isLightBulbOn = False; return pl
def P3(sk, x, y, z): return sk.modelToSketchSpace(adsk.core.Point3D.create(x / 10, y / 10, z / 10))

def airfoil_sketch(comp, y, le, c, t, tw, dz, name):
    sk = comp.sketches.add(plane_y(comp, y, 'PL_' + name)); sk.name = name
    a = math.radians(tw); col = adsk.core.ObjectCollection.create()
    for x, z in af_points(t):
        xl = (x - 0.25) * c; zl = z * c
        X = le + 0.25 * c + xl * math.cos(a) + zl * math.sin(a)
        Z = -xl * math.sin(a) + zl * math.cos(a) + dz
        col.add(P3(sk, X, y, Z))
    sp = sk.sketchCurves.sketchFittedSplines.add(col)
    sk.sketchCurves.sketchLines.addByTwoPoints(sp.startSketchPoint, sp.endSketchPoint)
    sk.isVisible = False
    return sk
def fin_sketch(comp, z, le_x, y_c, c, t, name):
    sk = comp.sketches.add(plane_z(comp, z, 'PL_' + name)); sk.name = name
    pts = naca00(t); col = adsk.core.ObjectCollection.create()
    for x, yy in pts[:-1]:
        col.add(P3(sk, le_x + x * c, y_c + yy * c, z))
    sp = sk.sketchCurves.sketchFittedSplines.add(col); sp.isClosed = True
    sk.isVisible = False
    return sk
def loft(comp, sketches, op, name):
    li = comp.features.loftFeatures.createInput(op)
    for s in sketches: li.loftSections.add(s.profiles.item(0))
    li.isSolid = True
    f = comp.features.loftFeatures.add(li); f.name = name; return f
def poly(comp, plane, pts, name):
    sk = comp.sketches.add(plane); sk.name = name
    P = [P3(sk, *p) for p in pts]
    for i in range(len(P)): sk.sketchCurves.sketchLines.addByTwoPoints(P[i], P[(i + 1) % len(P)])
    sk.isVisible = False; return sk
def box(comp, name, x0, x1, y0, y1, z0, z1, op=None, bodies=None):
    op = op or adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    sk = comp.sketches.add(plane_z(comp, z0, 'PL_' + name)); sk.name = name
    sk.sketchCurves.sketchLines.addTwoPointRectangle(P3(sk, x0, y0, z0), P3(sk, x1, y1, z0))
    sk.isVisible = False
    ei = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), op)
    ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal((z1 - z0) / 10))
    if bodies: ei.participantBodies = bodies
    f = comp.features.extrudeFeatures.add(ei); f.name = name
    if op == adsk.fusion.FeatureOperations.NewBodyFeatureOperation: f.bodies.item(0).name = name
    return f
def cyl_z(comp, name, cx, cy, r, z0, z1, op=None, bodies=None):
    op = op or adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    sk = comp.sketches.add(plane_z(comp, z0, 'PL_' + name)); sk.name = name
    sk.sketchCurves.sketchCircles.addByCenterRadius(P3(sk, cx, cy, z0), r / 10); sk.isVisible = False
    ei = comp.features.extrudeFeatures.createInput(sk.profiles.item(0), op)
    ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal((z1 - z0) / 10))
    if bodies: ei.participantBodies = bodies
    f = comp.features.extrudeFeatures.add(ei); f.name = name
    if op == adsk.fusion.FeatureOperations.NewBodyFeatureOperation: f.bodies.item(0).name = name
    return f
def rod(comp, name, p0, p1, r, op=None, bodies=None):
    """Cylinder between two 3D points (mm)."""
    op = op or adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    sk3 = comp.sketches.add(comp.xYConstructionPlane); sk3.name = name + '_path'
    ln = sk3.sketchCurves.sketchLines.addByTwoPoints(adsk.core.Point3D.create(*[v / 10 for v in p0]), adsk.core.Point3D.create(*[v / 10 for v in p1]))
    sk3.isVisible = False
    path = comp.features.createPath(ln, False)
    pi = comp.constructionPlanes.createInput(); pi.setByDistanceOnPath(path, adsk.core.ValueInput.createByReal(0))
    pl = comp.constructionPlanes.add(pi); pl.isLightBulbOn = False
    sk = comp.sketches.add(pl); sk.name = name + '_sec'
    sk.sketchCurves.sketchCircles.addByCenterRadius(sk.modelToSketchSpace(adsk.core.Point3D.create(*[v / 10 for v in p0])), r / 10)
    sk.isVisible = False
    swi = comp.features.sweepFeatures.createInput(sk.profiles.item(0), path, op)
    if bodies: swi.participantBodies = bodies
    f = comp.features.sweepFeatures.add(swi); f.name = name
    if op == adsk.fusion.FeatureOperations.NewBodyFeatureOperation: f.bodies.item(0).name = name
    return f
def combine(comp, target, tools, op, keep=True, name=None):
    tc = adsk.core.ObjectCollection.create()
    for t in tools: tc.add(t)
    ci = comp.features.combineFeatures.createInput(target, tc)
    ci.operation = op; ci.isKeepToolBodies = keep
    f = comp.features.combineFeatures.add(ci)
    if name: f.name = name
    return f
CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
INTER = adsk.fusion.FeatureOperations.IntersectFeatureOperation

import bisect as _bis
def _updown(t):
    pts = af_points(t); i0 = min(range(len(pts)), key=lambda i: pts[i][0])
    return sorted(pts[:i0+1]), sorted(pts[i0:])
def _interp(S, x):
    xs = [s[0] for s in S]; j = max(1, min(len(S)-1, _bis.bisect_left(xs, x)))
    (a, b), (c, d) = S[j-1], S[j]
    return b + (d - b) * (x - a) / (c - a) if c != a else b
def inner_wing_sketch(comp, y, wall, name, xc_min=0.02, min_gap=1.6, xc_max=1.0):
    """Inset (vertical offset) twisted section of the wing at span y; truncated at LE/TE where too thin."""
    c = w_chord(y); le = w_le(y); tw = math.radians(w_twist(y))
    up, lo = _updown(T0); U = []; L = []
    for k in range(1, 140):
        xc = 0.5 * (1 - math.cos(math.pi * k / 140))
        if xc < xc_min or xc > xc_max: continue
        zu = _interp(up, xc) * c - wall; zl = _interp(lo, xc) * c + wall
        if zu - zl < min_gap: break
        U.append((xc, zu)); L.append((xc, zl))
    def xf(xc, z):
        xl = (xc - 0.25) * c
        return (le + 0.25 * c + xl * math.cos(tw) + z * math.sin(tw), -xl * math.sin(tw) + z * math.cos(tw))
    sk = comp.sketches.add(plane_y(comp, y, 'PL_' + name)); sk.name = name
    cu = adsk.core.ObjectCollection.create(); cl = adsk.core.ObjectCollection.create()
    for xc, z in U: X, Z = xf(xc, z); cu.add(P3(sk, X, y, Z))
    for xc, z in L: X, Z = xf(xc, z); cl.add(P3(sk, X, y, Z))
    s1 = sk.sketchCurves.sketchFittedSplines.add(cu); s2 = sk.sketchCurves.sketchFittedSplines.add(cl)
    ln = sk.sketchCurves.sketchLines
    ln.addByTwoPoints(s1.startSketchPoint, s2.startSketchPoint); ln.addByTwoPoints(s1.endSketchPoint, s2.endSketchPoint)
    sk.isVisible = False
    return sk
def copy_body(comp, b, name):
    if design.designType == adsk.fusion.DesignTypes.DirectDesignType:
        nb = comp.bRepBodies.add(adsk.fusion.TemporaryBRepManager.get().copy(b))
    else:
        nb = comp.features.copyPasteBodies.add(b).bodies.item(0)
    nb.name = name; return nb
def slab_y(comp, name, y0, y1, x0=-200, x1=400, z0=-60, z1=120):
    return box(comp, name, x0, x1, y0, y1, z0, z1)

# ---------------- blended winglet (line + arc + line path in YZ) ----------------
BW_Y0, BW_Y1, BW_R, BW_TH = 440.0, 468.0, 42.0, 80.0    # joint station, arc start, radius, final angle (deg)
BW_TOP = 45.0
def bw_path_point(s):
    """Return (y, z, theta_rad) at arc-length s along the winglet path (s=0 at the joint)."""
    L1 = BW_Y1 - BW_Y0; La = BW_R * math.radians(BW_TH)
    if s <= L1: return (BW_Y0 + s, 0.0, 0.0)
    if s <= L1 + La:
        th = (s - L1) / BW_R
        return (BW_Y1 + BW_R * math.sin(th), BW_R - BW_R * math.cos(th), th)
    th = math.radians(BW_TH); y2 = BW_Y1 + BW_R * math.sin(th); z2 = BW_R - BW_R * math.cos(th); d = s - L1 - La
    return (y2 + d * math.cos(th), z2 + d * math.sin(th), th)
def bw_len(): return (BW_Y1 - BW_Y0) + BW_R * math.radians(BW_TH) + BW_TOP
# stations: (s, chord, LE x, twist deg, t/c)
def bw_stations():
    L1 = BW_Y1 - BW_Y0; La = BW_R * math.radians(BW_TH); le468 = w_le(BW_Y1)
    return [(0.0, w_chord(BW_Y0), w_le(BW_Y0), w_twist(BW_Y0), T0),
            (L1, w_chord(BW_Y1), le468, w_twist(BW_Y1), T0),
            (L1 + La * 0.25, 128.0, le468 + 12.0, -5.0, 0.098),
            (L1 + La * 0.50, 112.0, le468 + 26.0, -4.0, 0.095),
            (L1 + La * 0.75, 96.0, le468 + 40.0, -3.0, 0.092),
            (L1 + La, 84.0, le468 + 52.0, -2.5, 0.09),
            (bw_len(), 58.0, le468 + 80.0, -2.0, 0.08)]
def bw_section_pts(s, c, le, tw, t, inset=0.0, xc_min=0.0, min_gap=None):
    y0, z0, th = bw_path_point(s); a = math.radians(tw)
    if inset <= 0:
        pts2 = [(x, z * c) for x, z in af_points(t)]
    else:
        up, lo = _updown(t); U = []; L = []
        for k in range(1, 140):
            xc = 0.5 * (1 - math.cos(math.pi * k / 140))
            if xc < xc_min: continue
            zu = _interp(up, xc) * c - inset; zl = _interp(lo, xc) * c + inset
            if zu - zl < (min_gap or 1.2):
                if U: break
                continue
            U.append((xc, zu)); L.append((xc, zl))
        pts2 = list(reversed(U)) + L
    out = []
    for x, zl in pts2:
        xl = (x - 0.25) * c
        X = le + 0.25 * c + xl * math.cos(a) + zl * math.sin(a)
        h = -xl * math.sin(a) + zl * math.cos(a)
        out.append((X, y0 - h * math.sin(th), z0 + h * math.cos(th)))
    return out
def bw_plane(comp, s, name):
    """Plane through path point, normal to path tangent: rotate an XZ-parallel plane about the X-parallel line through the point."""
    y0, z0, th = bw_path_point(s)
    pin = comp.constructionPlanes.createInput()
    pin.setByOffset(comp.xZConstructionPlane, adsk.core.ValueInput.createByReal(y0 / 10))
    base = comp.constructionPlanes.add(pin); base.isLightBulbOn = False
    if th == 0: base.name = name; return base
    sk = comp.sketches.add(base); sk.name = name + '_axis'; sk.isVisible = False
    ln = sk.sketchCurves.sketchLines.addByTwoPoints(P3(sk, -300, y0, z0), P3(sk, 500, y0, z0))
    pin2 = comp.constructionPlanes.createInput()
    pin2.setByAngle(ln, adsk.core.ValueInput.createByReal(th), base)
    pl = comp.constructionPlanes.add(pin2); pl.name = name; pl.isLightBulbOn = False
    return pl
def bw_sketch(comp, s, c, le, tw, t, name, inset=0.0, closed_te=False):
    pl = bw_plane(comp, s, 'PL_' + name)
    sk = comp.sketches.add(pl); sk.name = name
    pts = bw_section_pts(s, c, le, tw, t, inset)
    col = adsk.core.ObjectCollection.create()
    for X, Y, Z in pts: col.add(P3(sk, X, Y, Z))
    sp = sk.sketchCurves.sketchFittedSplines.add(col)
    sk.sketchCurves.sketchLines.addByTwoPoints(sp.startSketchPoint, sp.endSketchPoint)
    sk.isVisible = False
    return sk, pts

# ---------------- detailed propulsion models (from datasheet dims) ----------------
def revolve_x(comp, name, prof_xr, zt, op=None):
    """Revolve a (x, r) polyline about the thrust line (y=0, z=zt)."""
    op = op or adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    sk = comp.sketches.add(comp.xZConstructionPlane); sk.name = name + '_prof'; sk.isVisible = False
    Pp = [P3(sk, x, 0, zt + r) for x, r in prof_xr]
    L = sk.sketchCurves.sketchLines
    for i in range(len(Pp) - 1): L.addByTwoPoints(Pp[i], Pp[i + 1])
    ax = L.addByTwoPoints(Pp[-1], Pp[0])
    ri = comp.features.revolveFeatures.createInput(sk.profiles.item(0), ax, op)
    ri.setAngleExtent(False, adsk.core.ValueInput.createByString('360 deg'))
    b = comp.features.revolveFeatures.add(ri).bodies.item(0); b.name = name; return b
def prop_blade(comp, name, x_hub, zt, sign, radius=114.3):
    """9x6 blade: sections on planes normal to z (blade along +/-z), pitch 6in -> twist from geometric pitch."""
    pitch = 152.4; secs = []
    for k, (rr, c) in enumerate(((18, 14), (40, 19), (65, 20), (90, 16), (radius - 2, 8))):
        beta = math.atan(pitch / (2 * math.pi * rr))
        z = zt + sign * rr
        sk = comp.sketches.add(plane_z(comp, z, f'PL_{name}_{k}')); sk.name = f'{name}_{k}'; sk.isVisible = False
        col = adsk.core.ObjectCollection.create()
        for xx, yy in naca00(0.10 if k < 2 else 0.08)[:-1]:
            u = (xx - 0.35) * c; v = yy * c
            # chord line rotated by pitch angle beta in the x-y plane (rotation direction by sign)
            X = x_hub + u * math.sin(beta) + v * math.cos(beta)
            Y = sign * (u * math.cos(beta) - v * math.sin(beta))
            col.add(P3(sk, X, Y, z))
        sp = sk.sketchCurves.sketchFittedSplines.add(col); sp.isClosed = True
        secs.append(sk)
    b = loft(comp, secs, adsk.fusion.FeatureOperations.NewBodyFeatureOperation, name).bodies.item(0); b.name = name; return b
