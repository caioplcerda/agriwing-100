import aerosandbox as asb, aerosandbox.numpy as np, json, math
d = np.loadtxt('mh60.dat', skiprows=1)
def af(t):
    c = d.copy(); c[:,1] = c[:,1]*t/0.1008
    return asb.Airfoil(name=f'mh60_t{t}', coordinates=c)
t20 = math.tan(math.radians(20))
def wle(y): return y*t20 - 0.25*(248+(136-248)*y/500)
def wc(y):  return 248+(136-248)*y/500
def tw(y):  return -2.0*max(0, y-130)/370
secs = [asb.WingXSec(xyz_le=[-0.095,0,0], chord=0.330, airfoil=af(0.18)),
        asb.WingXSec(xyz_le=[-0.080,0.060,0], chord=0.305, airfoil=af(0.16))]
for y in (130, 320, 500):
    secs.append(asb.WingXSec(xyz_le=[wle(y)/1000, y/1000, 0], chord=wc(y)/1000, twist=tw(y), airfoil=af(0.1008)))
wing = asb.Wing(name='Main', symmetric=True, xsecs=secs)
le_tip = wle(500)
wlet = asb.Wing(name='Winglet', symmetric=True, xsecs=[
    asb.WingXSec(xyz_le=[(le_tip+4)/1000, 0.498, -0.002], chord=0.128, airfoil=asb.Airfoil('naca0009')),
    asb.WingXSec(xyz_le=[(le_tip+38)/1000, 0.507, 0.045], chord=0.096, airfoil=asb.Airfoil('naca0009')),
    asb.WingXSec(xyz_le=[(le_tip+72)/1000, 0.518, 0.092], chord=0.062, airfoil=asb.Airfoil('naca0008'))])
import sys
MASS = float(sys.argv[1]) if len(sys.argv) > 1 else 1.011
XCG  = float(sys.argv[2])/1000 if len(sys.argv) > 2 else 0.0563
ap = asb.Airplane(name='AgriWing-100', xyz_ref=[XCG, 0, 0], wings=[wing, wlet],
                  s_ref=wing.area(), c_ref=wing.mean_aerodynamic_chord(), b_ref=wing.span())
out = {'S': float(wing.area()), 'MAC': float(wing.mean_aerodynamic_chord()), 'b': float(wing.span())}
# alpha sweep with AeroBuildup (NeuralFoil section data) and VLM (inviscid) for comparison
V = 15.0; rho = 1.225; q = 0.5*rho*V**2; W = MASS*9.81
rows = []
for a in np.arange(-4, 10.1, 1.0):
    op = asb.OperatingPoint(velocity=V, alpha=float(a))
    ab = asb.AeroBuildup(airplane=ap, op_point=op).run_with_stability_derivatives(alpha=True, beta=True, p=False, q=True, r=False)
    f=lambda v: float(np.asarray(v).ravel()[0]); rows.append({'alpha': float(a), 'CL': f(ab['CL']), 'CD': f(ab['CD']), 'Cm': f(ab['Cm']),
                 'x_np': f(ab['x_np']), 'Cma': f(ab['Cma']), 'Cnb': f(ab['Cnb']), 'Clb': f(ab['Clb'])})
out['polar'] = rows
# trim: CL needed at 15 m/s
CLreq = W/(q*out['S'])
al = np.array([r['alpha'] for r in rows]); cl = np.array([r['CL'] for r in rows]); cm = np.array([r['Cm'] for r in rows]); cd=np.array([r['CD'] for r in rows])
a_req = float(np.interp(CLreq, cl, al)); cm_at = float(np.interp(a_req, al, cm)); cd_at=float(np.interp(a_req, al, cd))
i = int(np.argmin(abs(al - a_req)))
out.update({'mass': MASS, 'xcg_mm': XCG*1000, 'CL_req': float(CLreq), 'alpha_req': a_req, 'Cm_at_req': cm_at, 'CD_at_req': cd_at,
            'LD_at_req': float(CLreq/cd_at), 'x_np_mm': rows[i]['x_np']*1000, 'SM_pct': (rows[i]['x_np']-XCG)/out['MAC']*100,
            'Cma': rows[i]['Cma'], 'Cnb': rows[i]['Cnb'], 'Clb': rows[i]['Clb']})
# alpha where Cm = 0 (trim without elevon)
out['alpha_Cm0'] = float(np.interp(0.0, cm[::-1], al[::-1])) if (cm.min() < 0 < cm.max()) else None
# VLM inviscid check at required alpha
vlm = asb.VortexLatticeMethod(airplane=ap, op_point=asb.OperatingPoint(velocity=V, alpha=a_req), spanwise_resolution=12, chordwise_resolution=10).run()
f=lambda v: float(np.asarray(v).ravel()[0]); out['VLM'] = {'CL': f(vlm['CL']), 'CDi': f(vlm['CD']), 'Cm': f(vlm['Cm'])}
json.dump(out, open('aero_results.json', 'w'), indent=1)
print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in out.items() if k != 'polar'}, indent=1))
for r in rows: print({k: round(v, 4) for k, v in r.items()})
