import numpy as np, matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.tri as mtri, glob, os
T = sorted(glob.glob('case/postProcessing/surfs/*/'), key=lambda p: float(p.rstrip('/').split('/')[-1]))[-1]
q = 0.5*15**2
def load(name, cols):
    d = np.loadtxt(T+name, comments='#'); return d
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
# --- body Cp, upper and lower, plan view (x forward up)
b = load('p_body.raw', 4); x,y,z,p = b.T; cp = p/q
# split upper/lower by comparing with local mid-surface: use nearest-neighbour camber proxy via binned median z
from scipy.spatial import cKDTree
fig, axs = plt.subplots(1, 2, figsize=(11, 5.2), constrained_layout=True)
for ax, sel, title in ((axs[0], None, 'Upper surface'), (axs[1], None, 'Lower surface')):
    pass
# classify: for each point, compare z with z of opposite surface points at same (x,y) using a 2D grid median
gx = np.round(x/0.004); gy = np.round(y/0.004)
key = gx*100000+gy
order = np.argsort(key); kk = key[order]; zz = z[order]
uniq, idx = np.unique(kk, return_index=True)
med = np.zeros_like(z)
bounds = list(idx)+[len(kk)]
for i in range(len(uniq)):
    s = order[bounds[i]:bounds[i+1]]; m = (z[s].max()+z[s].min())/2; med[s] = m
up = z >= med
lev = np.linspace(-1.2, 0.6, 37)
for ax, m, title in ((axs[0], up, 'Upper surface Cp'), (axs[1], ~up, 'Lower surface Cp')):
    tri = mtri.Triangulation(y[m]*1000, -x[m]*1000)
    # mask long triangles
    xt = tri.x[tri.triangles]; yt = tri.y[tri.triangles]
    maxe = np.max(np.hypot(np.roll(xt,1,axis=1)-xt, np.roll(yt,1,axis=1)-yt), axis=1)
    tri.set_mask(maxe > 12)
    cs = ax.tricontourf(tri, np.clip(cp[m], -1.2, 0.6), levels=lev, cmap='RdBu_r')
    ax.set_aspect('equal'); ax.set_title(title); ax.set_xlabel('y  [mm]'); ax.set_ylabel('−x  [mm]  (nose up)')
fig.colorbar(cs, ax=axs, shrink=0.8, label='Cp')
fig.savefig('cp_surfaces.png', dpi=150); plt.close(fig)
# --- section cuts: velocity magnitude
fig, axs = plt.subplots(2, 1, figsize=(10, 6.5), constrained_layout=True)
for ax, nm, title in ((axs[0], 'cutRoot', 'Section y = 60 mm (centerbody)'), (axs[1], 'cutMid', 'Section y = 320 mm (wing)')):
    d = load(f'U_{nm}.raw', 6); X, Y, Z, ux, uy, uz = d.T
    m = (X > -0.15) & (X < 0.45) & (np.abs(Z) < 0.12)
    V = np.sqrt(ux**2+uy**2+uz**2)/15
    tri = mtri.Triangulation(X[m]*1000, Z[m]*1000)
    xt = tri.x[tri.triangles]; yt = tri.y[tri.triangles]
    maxe = np.max(np.hypot(np.roll(xt,1,axis=1)-xt, np.roll(yt,1,axis=1)-yt), axis=1); tri.set_mask(maxe > 8)
    cs = ax.tricontourf(tri, np.clip(V[m], 0, 1.4), levels=np.linspace(0, 1.4, 29), cmap='viridis')
    ax.set_aspect('equal'); ax.set_title(title+'  ·  |U|/U∞'); ax.set_xlabel('x [mm]'); ax.set_ylabel('z [mm]')
fig.colorbar(cs, ax=axs, shrink=0.8, label='|U| / U∞')
fig.savefig('sections_U.png', dpi=150); plt.close(fig)
print('ok', T, len(x))
