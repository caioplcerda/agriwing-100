"""Printability + print plan for AgriWing-100 parts (Bambu 256^3), same method as Dart-80 mfg.py.
Orients each part along its build direction, finds the best in-plane rotation, measures overhang
(faces within 45 deg of straight down) and bed contact, estimates mass, filament and time."""
import json, math, os
import numpy as np
from agw_mfg_core import *
RHO = 0.60                                   # LW-ASA foamed, g/cm3
FIL = 1.07                                   # solid ASA density for filament length/weight
FLOW = 3.5                                   # effective mm3/s incl. travel (thin-wall parts)
PRICE = 60.0                                 # $/kg LW-ASA
out = []
for f in sorted(os.listdir(STL)):
    if not f.endswith('.stl'): continue
    name = f[:-4]; up, mat, note = PLAN[name]
    tri = read_stl(STL + f) @ frame(up).T
    pts = tri.reshape(-1, 3); h = pts[:, 2].max() - pts[:, 2].min(); z0 = pts[:, 2].min()
    best = best_rotation(pts)
    e1 = tri[:, 1] - tri[:, 0]; e2 = tri[:, 2] - tri[:, 0]; cr = np.cross(e1, e2)
    area = 0.5 * np.linalg.norm(cr, axis=1); nz = cr[:, 2] / np.maximum(2 * area, 1e-12); zc = tri[:, :, 2].mean(1)
    base = area[(nz < -0.99) & (zc - z0 < 0.3)].sum()
    over = area[(nz < -math.cos(math.radians(45)) - 1e-3) & (zc - z0 > 0.3)].sum()
    vol = float(np.sum(np.einsum('ij,ij->i', tri[:, 0], np.cross(tri[:, 1], tri[:, 2]))) / 6.0) / 1000.0
    surf = float(area.sum()) / 100.0
    solid = name.startswith(('W1', 'W2', 'Winglet', 'Elevon'))
    vol_print = (surf * 0.08 + 0.06 * max(vol - surf * 0.08, 0)) if solid else vol
    mass = vol_print * RHO; fil_cm3 = mass / FIL; hours = fil_cm3 * 1000 / FLOW / 3600 + 0.25
    out.append(dict(part=name, material=mat, note=note, vol_cm3=round(vol, 1), solid=solid, mass_g=round(mass, 1), height=round(h),
                    footprint=round(best[0]), fits=bool(h <= BED and best[0] <= BED), base_mm2=round(base), overhang_mm2=round(over),
                    hours=round(hours, 1), cost=round(mass / 1000 * PRICE, 2)))
tot = dict(parts=len(out), mass=round(sum(o['mass_g'] for o in out)), hours=round(sum(o['hours'] for o in out), 1), cost=round(sum(o['cost'] for o in out), 2))
json.dump(dict(parts=out, total=tot), open('agw_mfg.json', 'w'), indent=1)
for o in out:
    print(f"{o['part']:15s} {o['vol_cm3']:6.1f}cm3 {o['mass_g']:5.1f}g h={o['height']:3d} fp={o['footprint']:3d} fit={o['fits']} base={o['base_mm2']:5d} over45={o['overhang_mm2']:5d} {o['hours']:4.1f}h")
print(tot)
