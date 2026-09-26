"""List connected flat-ceiling patches (face within 30 deg of straight down) per part, with area and radial width (bridge span)."""
import sys, math, numpy as np
from agw_mfg_core import read_stl, STL, PLAN
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
def patches(name, up, lim=30):
    tri = read_stl(STL + name + '.stl'); up = np.array(up, float); up /= np.linalg.norm(up)
    cr = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); ar = np.linalg.norm(cr, axis=1) / 2; n = cr / np.maximum(2 * ar[:, None], 1e-12)
    h = tri.mean(1) @ up; h0 = (tri.reshape(-1, 3) @ up).min()
    sel = np.flatnonzero((n @ up < -math.cos(math.radians(lim))) & (h - h0 > 0.3))
    if not len(sel): return []
    v = np.round(tri[sel].reshape(-1, 3), 3); uq, inv = np.unique(v, axis=0, return_inverse=True); inv = inv.reshape(-1, 3)
    rows = np.repeat(np.arange(len(sel)), 3); g = coo_matrix((np.ones(len(rows)), (rows, inv.ravel())), shape=(len(sel), len(uq))).tocsr()
    k, lab = connected_components(g @ g.T, directed=False)
    out = []
    for i in range(k):
        m = sel[lab == i]; a = ar[m].sum()
        if a < 20: continue
        p = tri[m].reshape(-1, 3); r = np.hypot(p[:, 1], p[:, 2])
        out.append((round(a / 100, 2), [round(q, 1) for q in p.min(0)], [round(q, 1) for q in p.max(0)], round(r.max() - r.min(), 1)))
    return sorted(out, reverse=True)
if __name__ == '__main__':
    for name in sys.argv[1:]:
        print(name)
        for p in patches(name, PLAN[name][0])[:8]: print('  ', p)
