import numpy as np, glob, json, math, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, matplotlib.tri as mtri
from matplotlib.path import Path
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from scipy.spatial import cKDTree
from scipy.interpolate import griddata
from stl import mesh as stlmesh
CASE = sys.argv[1] if len(sys.argv) > 1 else 'case'; STL = sys.argv[2] if len(sys.argv) > 2 else 'oml_full.stl'; TAG = sys.argv[3] if len(sys.argv) > 3 else 'cruise'
ALPHA = float(sys.argv[4]) if len(sys.argv) > 4 else 4.8
T = sorted(glob.glob(f'{CASE}/postProcessing/surfs/*/'), key=lambda p: float(p.rstrip('/').split('/')[-1]))[-1]
q = 0.5*15**2
BG, INK = '#12151a', '#e8ecf1'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'axes.edgecolor':'#3a414c','figure.facecolor':BG,'axes.facecolor':BG,'savefig.facecolor':BG})
b = np.loadtxt(T+'p_body.raw', comments='#'); tree = cKDTree(b[:,:3]); cpv = b[:,3]/q
m = stlmesh.Mesh.from_file(STL); V = m.vectors/1000.0
Vh = V[V[:,:,1].mean(axis=1) >= -1e-4]
cen = Vh.mean(axis=1); _, idx = tree.query(cen); cpf = cpv[idx]
Vm = Vh.copy(); Vm[:,:,1] *= -1
allV = np.concatenate([Vh, Vm]); allcp = np.concatenate([cpf, cpf])
cmap = plt.get_cmap('RdBu_r'); norm = plt.Normalize(-1.2, 0.6)
def view(fname, elev, azim, title):
    fig = plt.figure(figsize=(12, 7)); ax = fig.add_subplot(111, projection='3d'); ax.set_facecolor(BG)
    pc = Poly3DCollection(allV*1000, facecolors=cmap(norm(allcp)), edgecolors='none', linewidths=0)
    ax.add_collection3d(pc)
    ax.set_xlim(-100, 300); ax.set_ylim(-530, 530); ax.set_zlim(-120, 140); ax.set_box_aspect((400, 1060, 260))
    ax.view_init(elev=elev, azim=azim); ax.set_axis_off()
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); cb = fig.colorbar(sm, ax=ax, shrink=0.55, pad=0.0); cb.set_label('Cp')
    fig.suptitle(title, color=INK, fontsize=13, y=0.93)
    fig.savefig(fname, dpi=140, bbox_inches='tight'); plt.close(fig)
view(f'img_{TAG}_cp_top.png', 38, -125, f'Surface pressure, upper side · 15 m/s, α = {ALPHA}° (OpenFOAM k-ω SST)')
view(f'img_{TAG}_cp_bottom.png', -35, -125, f'Surface pressure, lower side · 15 m/s, α = {ALPHA}°')
# --- section velocity with true airfoil mask (from STL slice)
def slice_poly(y0):
    segs=[]
    for tri in V:
        d = tri[:,1]-y0; s = np.sign(d)
        if s.max() <= 0 or s.min() >= 0: continue
        pts=[]
        for i in range(3):
            a, b2 = tri[i], tri[(i+1)%3]
            if (a[1]-y0)*(b2[1]-y0) < 0:
                t = (y0-a[1])/(b2[1]-a[1]); pts.append(a+(b2-a)*t)
        if len(pts)==2: segs.append((pts[0][[0,2]], pts[1][[0,2]]))
    P = np.array([p for s in segs for p in s])
    return P
fig, axs = plt.subplots(2, 1, figsize=(12, 8), constrained_layout=True)
for ax, nm, y0, title in ((axs[0], 'cutRoot', 0.06, 'Centerbody section  y = 60 mm'), (axs[1], 'cutMid', 0.32, 'Wing section  y = 320 mm')):
    d = np.loadtxt(T+f'U_{nm}.raw', comments='#'); X, Z = d[:,0], d[:,2]; Vm_ = np.linalg.norm(d[:,3:6], axis=1)/15
    xg, zg = np.meshgrid(np.linspace(-0.15, 0.45, 700), np.linspace(-0.10, 0.10, 240))
    Vg = griddata((X, Z), Vm_, (xg, zg), method='linear')
    P = slice_poly(y0 + 1e-4)
    if len(P):
        ctr = P.mean(axis=0); ang = np.arctan2(P[:,1]-ctr[1], P[:,0]-ctr[0])
        # airfoil outline: split upper/lower by chord line, sort by x
        c_ = np.array([P[:,0].min()+0.3*(P[:,0].max()-P[:,0].min()), np.median(P[:,1])])
        poly = P[np.argsort(np.arctan2(P[:,1]-c_[1], P[:,0]-c_[0]))]
        inside = Path(poly).contains_points(np.c_[xg.ravel(), zg.ravel()], radius=-0.0015).reshape(xg.shape) | Path(poly).contains_points(np.c_[xg.ravel(), zg.ravel()], radius=0.0015).reshape(xg.shape)
        Vg = np.where(inside, np.nan, Vg)
        ax.fill(poly[:,0]*1000, poly[:,1]*1000, color='#2b313a', zorder=3)
    cs = ax.contourf(xg*1000, zg*1000, np.clip(Vg, 0, 1.4), levels=np.linspace(0, 1.4, 57), cmap='turbo')
    ug = griddata((X,Z), d[:,3], (xg,zg)); wg = griddata((X,Z), d[:,5], (xg,zg))
    if len(P): ug = np.where(inside, np.nan, ug); wg = np.where(inside, np.nan, wg)
    ax.streamplot(xg*1000, zg*1000, ug, wg, density=1.4, color=(1,1,1,0.35), linewidth=0.5, arrowsize=0.5)
    ax.set_aspect('equal'); ax.set_title(title, color=INK); ax.set_xlabel('x [mm]'); ax.set_ylabel('z [mm]')
fig.colorbar(cs, ax=axs, shrink=0.8, label='|U| / U∞')
fig.suptitle(f'Velocity field and streamlines · α = {ALPHA}°', color=INK, fontsize=13)
fig.savefig(f'img_{TAG}_sections.png', dpi=140); plt.close(fig)
# --- chordwise Cp at y = 320 mm
sel = np.abs(b[:,1]-0.32) < 0.006
xs, zs, cps = b[sel,0], b[sel,2], cpv[sel]
c0, c1 = xs.min(), xs.max(); xc = (xs-c0)/(c1-c0)
mid = np.interp(xs, [c0, c1], [zs[xs.argmin()], zs[xs.argmax()]])
fig, ax = plt.subplots(figsize=(9, 5), constrained_layout=True)
u = zs >= mid
ax.plot(xc[u][np.argsort(xc[u])], cps[u][np.argsort(xc[u])], '.', ms=3, color='#ff7a59', label='upper surface')
ax.plot(xc[~u][np.argsort(xc[~u])], cps[~u][np.argsort(xc[~u])], '.', ms=3, color='#59b8ff', label='lower surface')
ax.invert_yaxis(); ax.grid(alpha=0.15); ax.set_xlabel('x / c'); ax.set_ylabel('Cp  (suction up)'); ax.legend(frameon=False)
ax.set_title(f'Chordwise pressure, wing station y = 320 mm · α = {ALPHA}°', color=INK)
fig.savefig(f'img_{TAG}_cp_chord.png', dpi=140); plt.close(fig)
# --- wake plane x = 450 mm: streamwise vorticity proxy (in-plane velocity) + axial deficit
d = np.loadtxt(T+'U_cutWake.raw', comments='#'); Y, Z = d[:,1], d[:,2]
yg, zg = np.meshgrid(np.linspace(0, 0.62, 500), np.linspace(-0.12, 0.2, 260))
ux = griddata((Y,Z), d[:,3], (yg,zg)); vy = griddata((Y,Z), d[:,4], (yg,zg)); wz = griddata((Y,Z), d[:,5], (yg,zg))
dy = yg[0,1]-yg[0,0]; dz = zg[1,0]-zg[0,0]
omx = np.gradient(wz, dy, axis=1) - np.gradient(vy, dz, axis=0)
fig, ax = plt.subplots(figsize=(12, 5), constrained_layout=True)
lim = np.nanpercentile(np.abs(omx), 99.5)
cs = ax.contourf(yg*1000, zg*1000, omx, levels=np.linspace(-lim, lim, 41), cmap='RdBu_r', extend='both')
ax.streamplot(yg*1000, zg*1000, vy, wz, density=1.6, color=(1,1,1,0.45), linewidth=0.6, arrowsize=0.6)
ax.set_aspect('equal'); ax.set_xlabel('y [mm]'); ax.set_ylabel('z [mm]'); fig.colorbar(cs, ax=ax, label='streamwise vorticity ωx [1/s]')
ax.set_title(f'Wake plane x = 450 mm (looking forward) · tip vortex and downwash · α = {ALPHA}°', color=INK)
fig.savefig(f'img_{TAG}_wake.png', dpi=140); plt.close(fig)
print('done', TAG)
