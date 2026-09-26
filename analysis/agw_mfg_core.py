"""Shared print-plan data for AgriWing-100 parts (Bambu 256^3): build orientation per part, STL reader, bed frame."""
import math, os, struct
import numpy as np
STL = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stl') + os.sep
BED = 256.0
H = np.array([0.2428, 0.9699, 0.0]); H /= np.linalg.norm(H)       # elevon hinge direction (plan view), right side
MIRROR = np.array([1, -1, 1])
PLAN = {  # part: (build 'up' vector, material, note)
    'CB_FrontRight': ((0, -1, 0), 'LW-ASA', 'root-rib face (y = 130) on the bed'),
    'CB_RearRight':  ((-1, 0, 0), 'LW-ASA', 'motor face (x = 246) on the bed'),
    'Hatch':         ((0, -1, 0), 'LW-ASA', 'standing on its left edge, brim'),
    'W1_R':          ((0, 1, 0), 'LW-ASA', 'standing on the root face'),
    'W2_R':          ((0, 1, 0), 'LW-ASA', 'standing on the y = 315 joint face'),
    'WingletBlend_R': ((1, 0, 0), 'LW-ASA', 'standing on its leading edge, brim'),
    'Elevon1_R':     (tuple(H), 'LW-ASA', 'standing on the inboard end (square to the hinge)'),
    'Elevon2_R':     ((0, 1, 0), 'LW-ASA', 'standing on the inboard end'),
    'ServoCover_R':  ((0, 0, 1), 'LW-ASA', 'outer face up'),
}
for k in list(PLAN):
    if k.endswith('_R') or k.endswith('Right'):
        up, mat, note = PLAN[k]
        PLAN[k[:-1] + 'L' if k.endswith('_R') else k.replace('Right', 'Left')] = (tuple(np.array(up) * MIRROR), mat, note)
def read_stl(p):
    with open(p, 'rb') as f:
        f.read(80); n = struct.unpack('<I', f.read(4))[0]
        a = np.frombuffer(f.read(n * 50), dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]))
    return a['v'].reshape(-1, 3, 3).astype(float)
def frame(up):
    z = np.array(up, float); z /= np.linalg.norm(z)
    t = np.array([0, 0, 1.0]) if abs(z[2]) < 0.9 else np.array([1.0, 0, 0])
    x = np.cross(t, z); x /= np.linalg.norm(x); y = np.cross(z, x)
    return np.stack([x, y, z])
def best_rotation(pts):
    best = None
    for d in np.arange(0, 180, 1.0):
        a = math.radians(d); R = np.array([[math.cos(a), -math.sin(a)], [math.sin(a), math.cos(a)]])
        q = pts[:, :2] @ R.T; w = q.max(0) - q.min(0)
        if best is None or max(w) < best[0]: best = (max(w), d, w, R)
    return best
