"""AgriWing-100 Rev D structural check (hand analysis, ultimate = 4 g limit x 1.5 = 6 g at AUW from mass_d.json).
Schrenk lift distribution over the blended planform; beam and joint checks. Allowables are conservative
assumptions for foamed LW-ASA (to be confirmed with coupons) and datasheet values for carbon."""
import json, math
M = json.load(open('mass_d.json')); AUW = M['auw'] / 1000.0
n_ult = 6.0; g = 9.81; b = 1.04; s = b / 2
def chord(y):
    ym = abs(y) * 1000
    return ((330 - 82 * ym / 130) if ym < 130 else (248 - 112 * ym / 500)) / 1000
N = 4000; ys = [s * (i + .5) / N for i in range(N)]; dy = s / N
Sh = sum(chord(y) * dy for y in ys)
sch = [(chord(y) + 4 * Sh * 2 / (math.pi * b) * math.sqrt(max(0, 1 - (2 * y / b) ** 2))) / 2 for y in ys]
L = AUW * g * n_ult; tot = sum(v * dy for v in sch); w = [v / tot * L / 2 for v in sch]
Mom = lambda y0: sum(wi * (y - y0) * dy for wi, y in zip(w, ys) if y > y0)
She = lambda y0: sum(wi * dy for wi, y in zip(w, ys) if y > y0)
A = {'LW-ASA tension across layers': 5.0, 'LW-ASA bearing': 8.0, 'CF rod flexure (pultruded)': 1200.0,
     'CF tube flexure (roll-wrapped)': 700.0, 'CF shear': 80.0, 'M3 heat-set insert pull-out in LW-ASA (N)': 150.0}
rows = []
def row(item, rev, load, cap, unit, note=''):
    rows.append(dict(item=item, rev=rev, load=round(load, 2), cap=round(cap, 2), unit=unit, sf=round(cap / load, 1) if load else None, note=note))
M0, M130 = Mom(0.0), Mom(0.130)
Zt64 = math.pi * (6**4 - 4**4) / (32 * 6); Zr6 = math.pi * 6**3 / 32; Zt86 = math.pi * (8**4 - 6**4) / (32 * 8)
# Rev C (for comparison)
row('6x4 swept spar at the wing root (y 130)', 'C', M130 * 1000 / Zt64 / math.cos(math.radians(20)), A['CF tube flexure (roll-wrapped)'], 'MPa')
row('Centre seam: 3 M3 inserts on the belly carry the wing bending', 'C', M0 * 1000 / 30.0 / 2, A['M3 heat-set insert pull-out in LW-ASA (N)'], 'N per insert', 'couple arm ~30 mm, two inserts effective')
# Rev D
row('O6 solid carbon joiner at the centreline', 'D', M0 * 1000 / Zr6, A['CF rod flexure (pultruded)'], 'MPa')
row('8x6 wing tube at the root (y 130)', 'D', M130 * 1000 / Zt86, A['CF tube flexure (roll-wrapped)'], 'MPa')
p_sock = 6 * M130 * 1000 / (8.0 * 307.0 ** 2)
row('Wing tube bore in W1 (bearing, 307 mm bonded length)', 'D', p_sock, A['LW-ASA bearing'], 'MPa')
body = AUW - 2 * 0.105                                                       # everything but the two wing panels, kg
F_web = body * g * n_ult / 4
row('Joiner webs in the centre body (4 webs, bearing on O6)', 'D', F_web / (6.0 * 7.0), A['LW-ASA bearing'], 'MPa', 'web 7 mm thick')
# torsion about the spar line (x = 145): lift at the local quarter chord
T = sum(wi * ((y * 1000) * math.tan(math.radians(20)) - 145.0) / 1000 * dy for wi, y in zip(w, ys) if y > 0.130)
F_pin = abs(T) / 0.085
row('Anti-rotation pin O3 (85 mm ahead of the spar), bearing', 'D', F_pin / (3.0 * 26.0), A['LW-ASA bearing'], 'MPa', f'root torque {abs(T):.2f} N·m')
row('Magnets vs winglet side force (beta 10 deg, 25 m/s)', 'D', 1.3, 2 * 20.0, 'N', 'wings slide along y: drag has no pull-off component')
q = 0.5 * 1.225 * 25.0 ** 2
H = q * 0.0144 * 0.05 * 0.6
row('Servo torque at 25 m/s, 20 deg (ES08MD II 0.196 N·m)', 'D', H * 10 / 13.3, 0.196, 'N·m', f'hinge moment {H:.3f} N·m')
row('G10 horn bond (160 mm² epoxy)', 'D', H / 0.0133 / 160.0, 10.0, 'MPa')
row('Elevon torque rod O2 (elevon 2 share 40 %)', 'D', 16 * 0.4 * H * 1000 / (math.pi * 8.0), A['CF shear'], 'MPa')
row('Hatch retention (Cp -1.2 at 25 m/s): 2 magnets + front hood', 'D', q * 1.2 * 0.0234, 40.0, 'N')
row('Motor mount: 4 M3 inserts, 12 N thrust x 1.5', 'D', 12 * 1.5 / 4, A['M3 heat-set insert pull-out in LW-ASA (N)'], 'N per insert')
out = dict(auw_kg=AUW, n_ult=n_ult, M0=round(M0, 2), M130=round(M130, 2), V130=round(She(0.130), 1), allowables=A, rows=rows)
json.dump(out, open('agw_struct.json', 'w'), indent=1)
print(f'AUW {AUW:.3f} kg, ultimate lift/side {L/2:.1f} N, M(0) {M0:.2f} N·m, M(130) {M130:.2f} N·m')
for r in rows: print(f"[{r['rev']}] {r['item']:62s} {r['load']:8.2f} / {r['cap']:7.1f} {r['unit']:13s} SF {r['sf']}")
