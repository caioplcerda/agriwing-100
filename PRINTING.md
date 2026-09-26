# Printing guide: AgriWing-100 Rev D

Enclosed printer (ASA), 256 × 256 mm bed, 0.4 mm nozzle. Nothing needs support; three parts take a brim, and the 0.8 mm servo covers take a 2-layer raft.

| Part | Orientation | Height mm | Support | Mass g | Hours |
|---|---|---:|---|---:|---:|
| `CB_FrontLeft` | root-rib face (y = 130) on the bed | 130 | none | 37 | 3.0 |
| `CB_FrontRight` | root-rib face (y = 130) on the bed | 130 | none | 37 | 3.0 |
| `CB_RearLeft` | motor face (x = 246) on the bed | 151 | none | 35 | 2.8 |
| `CB_RearRight` | motor face (x = 246) on the bed | 151 | none | 35 | 2.8 |
| `Elevon1_L` | standing on the inboard end (square to the hinge) | 174 | none | 11 | 1.0 |
| `Elevon1_R` | standing on the inboard end (square to the hinge) | 174 | none | 11 | 1.0 |
| `Elevon2_L` | standing on the inboard end | 123 | none | 7 | 0.7 |
| `Elevon2_R` | standing on the inboard end | 123 | none | 7 | 0.7 |
| `Hatch` | standing on its left edge, brim | 136 | brim | 19 | 1.7 |
| `ServoCover_L` | outer face up | 3 | 2-layer raft | 0 | 0.3 |
| `ServoCover_R` | outer face up | 3 | 2-layer raft | 0 | 0.3 |
| `W1_L` | standing on the root face | 185 | none | 48 | 3.8 |
| `W1_R` | standing on the root face | 185 | none | 48 | 3.8 |
| `W2_L` | standing on the y = 315 joint face | 125 | none | 24 | 2.1 |
| `W2_R` | standing on the y = 315 joint face | 125 | none | 24 | 2.1 |
| `WingletBlend_L` | standing on its leading edge, brim | 154 | brim | 17 | 1.5 |
| `WingletBlend_R` | standing on its leading edge, brim | 154 | brim | 17 | 1.5 |
| **Total (17 parts)** | | | | **376** | **32.1** |

## Slicer settings (LW-ASA)

| Setting | Value |
|---|---|
| Target density | ≈0.6 g/cm³ foamed; calibrate flow and temperature with a 20 mm cube |
| Wing parts (W1, W2, winglets, elevons) | solid models: 2 walls, 3 top/bottom, 6 % gyroid |
| Centre body, hatch, servo covers | modelled thin-walled: 3 walls, infill off |
| Chamber | closed, 45–50 °C |

## After printing

- Horizontal bores are teardrops (peak up in print); ream the round part and fill the peak with thickened epoxy on assembly.
- Heat-set M3 inserts: centre-body seams and the motor mount. M2 pilot holes in the servo lugs.
- Glue the G10 horns into their slots and the 8×6 tube into W1 before joining W2.

The same data drive `analysis/agw_mfg.py`; re-run it after changing any STL.
