# Teardrop every near-horizontal bore (in the part's print orientation) of the bodies in JOBS: [(component, body, up)].
import math
tbm = adsk.fusion.TemporaryBRepManager.get(); BO = adsk.fusion.BooleanTypes
root = design.rootComponent
C = {o.component.name: o.component for o in root.occurrences}
P = adsk.core.Point3D.create; V = adsk.core.Vector3D.create
def unit(v): n = math.sqrt(sum(q * q for q in v)); return tuple(q / n for q in v)
def dot(a, b): return sum(p * q for p, q in zip(a, b))
def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
LOG = []
for cname, bname, up in JOBS:
    comp = C[cname]; body = comp.bRepBodies.itemByName(bname); u = unit(up)
    bores = {}
    for f in body.faces:
        g = f.geometry
        if not isinstance(g, adsk.core.Cylinder): continue
        r = g.radius * 10; a = unit((g.axis.x, g.axis.y, g.axis.z))
        if r < 1.4 or r > 6.0 or abs(dot(a, u)) > 0.70: continue
        # concave (hole) test: a point just inside the radius, off the axis, must be outside the body
        if a[0] < 0 or (a[0] == 0 and a[1] < 0): a = tuple(-q for q in a)
        o = (g.origin.x * 10, g.origin.y * 10, g.origin.z * 10)
        # canonical axis point: remove the component along a
        s = dot(o, a); o0 = tuple(o[i] - s * a[i] for i in range(3))
        key = (tuple(round(q, 1) for q in o0), tuple(round(q, 3) for q in a), round(r, 2))
        # exact extent along the axis from the surface parameter range (v runs along the cylinder axis)
        ev = f.evaluator; pr = ev.parametricRange(); cs = []
        for uu in (pr.minPoint.x, (pr.minPoint.x + pr.maxPoint.x) / 2, pr.maxPoint.x):
            for vv in (pr.minPoint.y, pr.maxPoint.y):
                ok, pt = ev.getPointAtParameter(adsk.core.Point2D.create(uu, vv))
                if ok: cs.append(dot((pt.x * 10, pt.y * 10, pt.z * 10), a))
        lo, hi = min(cs), max(cs)
        # hole or boss? sample the point at radius*0.5 from the axis, mid-extent
        t = unit(tuple(u[i] - dot(u, a) * a[i] for i in range(3)))
        mid = (lo + hi) / 2; pc = tuple(o0[i] + mid * a[i] + 0.5 * r * t[i] for i in range(3))
        inside = body.pointContainment(P(*[q / 10 for q in pc]))
        if inside != adsk.fusion.PointContainment.PointOutsidePointContainment: continue
        k = bores.setdefault(key, [lo, hi]); k[0] = min(k[0], lo); k[1] = max(k[1], hi)
    t_body = tbm.copy(body); n = 0
    for (o0, a, r), (lo, hi) in bores.items():
        a = unit(a)
        t = unit(tuple(u[i] - dot(u, a) * a[i] for i in range(3))); b = cross(a, t)
        w1 = unit(tuple(t[i] + b[i] for i in range(3))); w2 = unit(tuple(t[i] - b[i] for i in range(3)))
        L = hi - lo; mid = (lo + hi) / 2; c = tuple(o0[i] + mid * a[i] for i in range(3))
        dia = tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P(*[q / 10 for q in c]), V(*a), V(*w1), L / 10, 2 * r / 10, 2 * r / 10))
        hc = tuple(c[i] + t[i] * 2 * r for i in range(3))
        half = tbm.createBox(adsk.core.OrientedBoundingBox3D.create(P(*[q / 10 for q in hc]), V(*a), V(*t), (L + 1) / 10, 4 * r / 10, 6 * r / 10))
        tbm.booleanOperation(dia, half, BO.IntersectionBooleanType)
        try: tbm.booleanOperation(t_body, dia, BO.DifferenceBooleanType); n += 1
        except Exception as e: LOG.append(('FAIL', bname, str(e)[:50]))
    old = body; ap = old.appearance; v0 = old.volume
    if comp.bRepBodies.itemByName(bname + '_preTD'): old.deleteMe()
    else: old.name = bname + '_preTD'; old.isLightBulbOn = False
    nb = comp.bRepBodies.add(t_body); nb.name = bname; nb.appearance = ap
    LOG.append((bname, n, [(k[2], round(v[1] - v[0], 1)) for k, v in bores.items()], round(v0, 2), round(nb.volume, 2), nb.lumps.count))
RESULT = LOG
