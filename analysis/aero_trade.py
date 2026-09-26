import aerosandbox as asb, aerosandbox.numpy as np, math, json
d = np.loadtxt('mh60.dat', skiprows=1)
i0 = int(np.argmin(d[:,0])); up = d[:i0+1][::-1]; lo = d[i0:]
xs = 0.5*(1-np.cos(np.linspace(0, np.pi, 81)))
yu = np.interp(xs, up[:,0], up[:,1]); yl = np.interp(xs, lo[:,0], lo[:,1])
cam = (yu+yl)/2; thk = (yu-yl)
def af(t, camber_scale):
    """thickness scaled to t/c; camber line scaled by camber_scale"""
    yt = thk*t/thk.max()/2; yc = cam*camber_scale
    coords = np.concatenate([np.stack([xs[::-1], (yc+yt)[::-1]],1), np.stack([xs[1:], (yc-yt)[1:]],1)])
    return asb.Airfoil(name=f'mh60m_{t}_{camber_scale}', coordinates=coords)
t20 = math.tan(math.radians(20))
def wle(y): return y*t20 - 0.25*(248+(136-248)*y/500)
def wc(y):  return 248+(136-248)*y/500
f = lambda v: float(np.asarray(v).ravel()[0])
def build(washout, cb_camber_scale, xcg):
    tw = lambda y: -washout*max(0, y-130)/370
    s = [asb.WingXSec(xyz_le=[-0.095,0,0], chord=0.330, airfoil=af(0.18, cb_camber_scale)),
         asb.WingXSec(xyz_le=[-0.080,0.060,0], chord=0.305, airfoil=af(0.16, cb_camber_scale))]
    for y in (130,320,500): s.append(asb.WingXSec(xyz_le=[wle(y)/1000,y/1000,0], chord=wc(y)/1000, twist=tw(y), airfoil=af(0.1008,1.0)))
    w = asb.Wing(name='Main', symmetric=True, xsecs=s)
    le = wle(500)
    wl = asb.Wing(name='Winglet', symmetric=True, xsecs=[asb.WingXSec(xyz_le=[(le+4)/1000,.498,-.002],chord=.128,airfoil=asb.Airfoil('naca0009')),
         asb.WingXSec(xyz_le=[(le+38)/1000,.507,.045],chord=.096,airfoil=asb.Airfoil('naca0009')),asb.WingXSec(xyz_le=[(le+72)/1000,.518,.092],chord=.062,airfoil=asb.Airfoil('naca0008'))])
    return asb.Airplane(xyz_ref=[xcg,0,0], wings=[w,wl], s_ref=w.area(), c_ref=w.mean_aerodynamic_chord(), b_ref=w.span())
def evaluate(ap, mass=1.10):
    S=ap.s_ref; q=0.5*1.225*15**2; CLreq=mass*9.81/(q*S)
    al=np.arange(1,6.1,0.5); R=[]
    for a in al:
        r=asb.AeroBuildup(airplane=ap, op_point=asb.OperatingPoint(velocity=15,alpha=float(a))).run_with_stability_derivatives(alpha=True,beta=False,p=False,q=False,r=False)
        R.append((f(r['CL']),f(r['CD']),f(r['Cm']),f(r['x_np'])))
    R=np.array(R); a_req=float(np.interp(CLreq,R[:,0],al))
    return {'alpha':round(a_req,2),'Cm':round(float(np.interp(a_req,al,R[:,2])),4),'LD':round(CLreq/float(np.interp(a_req,al,R[:,1])),1),'x_np_mm':round(float(np.interp(a_req,al,R[:,3]))*1000,1),'MAC':round(ap.c_ref*1000,1)}
res={}
for wo in (2.0,4.0):
    for cs in (1.786,1.0):
        res[f'washout{wo}_cbcamber{cs}']=evaluate(build(wo,cs,0.0563))
for k,v in res.items(): print(k,v)
json.dump(res,open('aero_trade.json','w'),indent=1)
