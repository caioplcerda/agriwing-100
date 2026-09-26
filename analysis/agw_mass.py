"""AgriWing-100 Rev D mass & balance. Printed masses from the print plan (agw_mfg.json, slicer model),
centroids from CAD (agw_cad.json), bought parts from datasheets. Battery position solved for the target CG."""
import json
cad = json.load(open('agw_cad.json')); mf = {p['part']: p for p in json.load(open('agw_mfg.json'))['parts']}
CF = 1.55                                                     # g/cm3 carbon (pultruded / roll-wrapped)
def xm(names): v = sum(cad[n][0] for n in names); return sum(cad[n][0] * cad[n][1] for n in names) / v
def pm(names): return sum(mf[n]['mass_g'] for n in names)
groups = [
 ('Centerbody, 4 printed pieces (LW-ASA)', ['CB_FrontRight', 'CB_FrontLeft', 'CB_RearRight', 'CB_RearLeft'], 14),
 ('Hatch (LW-ASA)', ['Hatch'], 2),
 ('Wing W1 x2 (solid, 2 walls + 6 % gyroid)', ['W1_R', 'W1_L'], 8),
 ('Wing W2 x2 (solid)', ['W2_R', 'W2_L'], 4),
 ('Blended winglets x2 (solid)', ['WingletBlend_R', 'WingletBlend_L'], 2),
 ('Elevon 1 x2 (solid, round nose)', ['Elevon1_R', 'Elevon1_L'], 2),
 ('Elevon 2 x2 (solid, round nose)', ['Elevon2_R', 'Elevon2_L'], 1),
 ('Servo covers x2', ['ServoCover_R', 'ServoCover_L'], 0),
]
I = [(n, round(pm(p), 1), round(xm(p), 1), c) for n, p, c in groups]
hw = [
 ('Carbon joiner rod O6 solid, 550 mm', cad['Joiner_O6_CF'][0] * CF, cad['Joiner_O6_CF'][1], 9),
 ('Carbon wing tubes 8x6, 2 x 307 mm', 2 * cad['WingTube_R_8x6_CF'][0] * CF, 145.0, 10),
 ('Carbon elevon torque rods O2, 2 x 280 mm', 2 * cad['TorqueRod_R'][0] * CF, cad['TorqueRod_R'][1], 3),
 ('Carbon anti-rotation pins O3 (2) + seam dowels O3 (8)', 2 * cad['PinY_R_3mm_CF'][0] * CF + 3.5, 150.0, 4),
 ('G10 control horns 1.5 mm (2)', 2.0, cad['HornG10_R'][1], 3),
 ('PETG filament hinge pins 1.75 mm (2)', 1.0, 200.0, 0),
 ('Magnets 10x3 N52 (8)', 14.4, 60.0, 6),
 ('M3 bolts + heat-set inserts (7), M2.5/M2 inserts, grommets', 16.0, 70.0, 8),
 ('Servo EMAX ES08MD II (2)', 26.0, 103.9, 20),
 ('Servo arms + 1.2 mm pushrods (2)', 3.0, 130.0, 3),
 ('Raspberry Pi 5 4 GB + heatsink + SD', 56.0, 60.0, 75),
 ('Camera Module 3 + NoIR (+720 nm LP) + cables', 16.0, 52.5, 65),
 ('Matek H743-WLITE', 22.0, 117.0, 70),
 ('ELRS receiver', 5.0, cad['RX_ELRS'][1], 15),
 ('Matek M10Q-5883 GPS', 8.0, 0.0, 30),
 ('ASPD-4525 + pitot + tubing', 7.0, -75.0, 40),
 ('ESC 40 A', 25.0, 205.5, 20),
 ('SunnySky X2216 1100 KV + cross mount', 73.0, 261.0, 30),
 ('Folding prop 9x6 + spinner + adapter', 18.0, 288.0, 12),
 ('BEC 5 V 5 A, wiring, XT30', 60.0, 40.0, 25),
 ('Epoxy / CA (joints, tubes)', 8.0, 120.0, 0),
]
I += [(n, round(m, 1), round(x, 1), c) for n, m, x, c in hw]
BATT = ['Li-ion 3S2P Molicel P45B flat + BMS', 445.0, -23.9, 55]      # cells 6.8 mm forward of Rev C (limited by the airspeed sensor)
NP, MAC = 83.3, 222.0                                                    # CFD neutral point (Rev C) and mean aerodynamic chord, mm
allr = I + [BATT]
auw = sum(i[1] for i in allr); cg = sum(i[1] * i[2] for i in allr) / auw
printed = sum(i[1] for i in I[:len(groups)]); cost = sum(i[3] for i in allr)
sm = (NP - cg) / MAC * 100
print(f'printed {printed:.0f} g ; AUW {auw:.0f} g ; CG x = {cg:.1f} mm ; static margin {sm:.1f} % ; parts ${cost}')
json.dump({'items': allr, 'auw': round(auw), 'printed': round(printed), 'cg': round(cg, 1), 'sm': round(sm, 1), 'x_batt': BATT[2], 'cost': cost}, open('mass_d.json', 'w'), indent=1)
