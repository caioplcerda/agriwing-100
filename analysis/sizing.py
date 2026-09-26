"""Conceptual sizing: hand-launched flying wing for crop mapping. SI units."""
import math, json
RHO, G = 1.225, 9.81
CELL = {"m": 0.070, "Wh": 16.2}                 # Molicel P45B
FIXED_G = {                                       # grams, non-structure, non-battery
    "motor 2216-1100KV": 70, "ESC 40A": 25, "folding prop 9x6 + spinner": 18,
    "FC Matek H743-WLITE": 10, "GPS M10 + compass": 15, "airspeed sensor + pitot": 18,
    "ELRS RX (MAVLink telemetry)": 5, "2x servo 9g metal gear": 26,
    "Pi 5 4GB + heatsink": 55, "2x Pi Camera Module 3 (RGB, NoIR)": 16,
    "5V 5A BEC + wiring + connectors": 60, "pack wiring + BMS/balance": 30,
}
P_AVIONICS = 7.5    # W: Pi 5 capturing (~5.5) + FC/GPS/RX (1.2) + servos (0.8)
ETA = 0.50 * 0.80 * 0.95                          # prop * motor * ESC (launch-sized prop at cruise)
USABLE = 0.80                                     # Li-ion 4.2->3.0 V, keep 20 % reserve
TAPER, SWEEP_DEG = 0.55, 25

def structure_g(S):          # EPP core + carbon spar + tape/film + printed pod; ~1.2 kg/m2 + pod
    return 1200 * S + 140

def design(span, series, parallel, v_cruise=15.0, cd0=0.038, e=0.85, mission=0.80):
    cr = None
    # chord from span and aspect-driven planform: pick mean chord = span/5.2 (AR~5.2)
    c_mean = span / 5.2
    S = span * c_mean
    cr = 2 * c_mean / (1 + TAPER)
    n = series * parallel
    batt = n * CELL["m"] * 1000
    m_g = structure_g(S) + sum(FIXED_G.values()) + batt
    W = m_g / 1000 * G
    AR = span**2 / S
    k = 1 / (math.pi * e * AR)
    def power(v):
        cl = 2 * W / (RHO * v**2 * S)
        cd = cd0 + k * cl**2
        return W * v * cd / cl, cl, cl / cd
    P_aero, cl, LD = power(v_cruise)
    P_elec = P_aero / ETA + P_AVIONICS
    E = n * CELL["Wh"] * USABLE
    t_h = E / P_elec * mission                             # turns, climb, headwind legs
    v_stall = math.sqrt(2 * W / (RHO * S * 1.0))            # CLmax 1.0 reflexed section, low sweep
    v_minP = (2 * W / (RHO * S) * math.sqrt(k / (3 * cd0))) ** 0.5
    return {"span_m": span, "pack": f"{series}S{parallel}P", "S_m2": round(S, 3), "AR": round(AR, 2),
            "root_chord_m": round(cr, 3), "tip_chord_m": round(cr * TAPER, 3), "mass_g": round(m_g),
            "wing_loading_g_dm2": round(m_g / (S * 100), 1), "CL_cruise": round(cl, 3), "L/D": round(LD, 1),
            "P_elec_W": round(P_elec, 1), "energy_usable_Wh": round(E, 1), "endurance_min": round(t_h * 60),
            "range_km": round(t_h * 3.6 * v_cruise, 1), "v_stall_ms": round(v_stall, 1),
            "v_min_power_ms": round(v_minP, 1), "batt_frac": round(batt / m_g, 2),
            "I_cruise_A": round(P_elec / (3.6 * series), 1)}

rows = [design(b, s, p) for b in (1.0, 1.2, 1.4) for s, p in ((3, 1), (3, 2), (4, 2))]
for r in rows: print(r)
json.dump(rows, open("trade.json", "w"), indent=1)
