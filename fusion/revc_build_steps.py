# AgriWing-100 Rev C build log: the Fusion 360 API snippets that built the Rev C wing, elevons, winglet and
# centre-body split, in order (each block was run in the Fusion 360 API console). Rev D scripts are the agw_*.py files.

design = adsk.fusion.Design.cast(app.activeProduct)
LIB='./revc.py'
W={'adsk':adsk,'math':math,'design':design,'__file__':LIB}; exec(open(LIB).read(), W)
root = design.rootComponent
wc = root.occurrences.itemByName('WingC:1').component
oml = wc.bRepBodies.itemByName('WingOML_R')
xh = lambda y: W['w_le'](y)+0.75*W['w_chord'](y); xte = lambda y: W['w_le'](y)+W['w_chord'](y)
pl = wc.xYConstructionPlane
def prism(name, pts):
    sk = W['poly'](wc, pl, pts, name+'_sk')
    ei = wc.features.extrudeFeatures.createInput(sk.profiles.item(0), W['NEW']); ei.setSymmetricExtent(adsk.core.ValueInput.createByString('80 mm'), True)
    b = wc.features.extrudeFeatures.add(ei).bodies.item(0); b.name = name; return b
t_el = prism('T_elevon', [(xh(150),150,0),(xh(470),470,0),(xte(470)+30,470,0),(xte(150)+30,150,0)])
t_gap = prism('T_gap', [(xh(149)-1,149,0),(xh(471)-1,471,0),(xte(471)+30,471,0),(xte(149)+30,149,0)])
Efull = W['copy_body'](wc, oml, 'E_full')
W['combine'](wc, Efull, [t_el], W['INTER'], keep=False)
E1 = W['copy_body'](wc, Efull, 'Elevon1_R'); E2 = W['copy_body'](wc, Efull, 'Elevon2_R')
b1 = W['box'](wc,'T_e1', -200,400, 140,314.5, -80,120).bodies.item(0); b2 = W['box'](wc,'T_e2', -200,400, 315.5,480, -80,120).bodies.item(0)
W['combine'](wc, E1, [b1], W['INTER'], keep=False); W['combine'](wc, E2, [b2], W['INTER'], keep=False)
wc.features.removeFeatures.add(Efull)
Wfull = W['copy_body'](wc, oml, 'W_full')
W['combine'](wc, Wfull, [t_gap], W['CUT'], keep=False)
W1 = W['copy_body'](wc, Wfull, 'W1_R'); W2 = W['copy_body'](wc, Wfull, 'W2_R')
s1 = W['box'](wc,'T_w1', -200,400, 120,315, -80,120).bodies.item(0); s2 = W['box'](wc,'T_w2', -200,400, 315,510, -80,120).bodies.item(0)
W['combine'](wc, W1, [s1], W['INTER'], keep=False); W['combine'](wc, W2, [s2], W['INTER'], keep=False)
wc.features.removeFeatures.add(Wfull)
oml.isLightBulbOn = False
[(b.name, round(b.volume,2)) for b in wc.bRepBodies]

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
LIB='./revc.py'
W={'adsk':adsk,'math':math,'design':design,'__file__':LIB}; exec(open(LIB).read(), W)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
out=[]
for seg,(ya,yb) in (('W1_R',(133.0,313.8)),('W2_R',(316.2,498.8))):
    s0 = W['inner_wing_sketch'](wc, ya, 0.6, f'CAVs_{seg}_a', xc_max=0.70)
    s1 = W['inner_wing_sketch'](wc, yb, 0.6, f'CAVs_{seg}_b', xc_max=0.70)
    cav = W['loft'](wc, [s0, s1], W['NEW'], f'Loft_cav_{seg}').bodies.item(0); cav.name = f'CAV_{seg}'
    b = wc.bRepBodies.itemByName(seg)
    W['combine'](wc, b, [cav], W['CUT'], keep=False, name=f'Hollow_{seg}')
    out.append((seg, round(b.volume,2), b.lumps.count))
out

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
LIB='./revc.py'
W={'adsk':adsk,'math':math,'design':design,'__file__':LIB}; exec(open(LIB).read(), W)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
W1 = wc.bRepBodies.itemByName('W1_R'); OML = wc.bRepBodies.itemByName('WingOML_R')
t = math.tan(math.radians(20)); ZS=2.0
def join_new(bodyname):
    b = wc.bRepBodies.itemByName(bodyname); W['combine'](wc, W1, [b], W['JOIN'], keep=False)
# spar sleeve + bore
W['rod'](wc,'SparSleeve_W1', (130.5*t,130.5,ZS), (314.0*t,314.0,ZS), 4.3); join_new('SparSleeve_W1')
# pin sleeve
xp = W['w_le'](130) + 0.62*W['w_chord'](130)
W['rod'](wc,'PinSleeve_W1', (xp,130.5,2.5), (xp+50*t,180,2.5), 2.6); join_new('PinSleeve_W1')
# magnet bosses at root
for i,xm in enumerate((35.0,85.0)):
    W['rod'](wc,f'MagBossW_{i}', (xm,130.5,2.5), (xm,137.0,2.5), 7.0); join_new(f'MagBossW_{i}')
# ribs (0.8 mm) = slab ∩ OML
for yr in (172.0, 205.0, 260.0):
    nm=f'RibW1_{int(yr)}'
    W['box'](wc, nm, -200, 400, yr-0.4, yr+0.4, -80, 120); rb = wc.bRepBodies.itemByName(nm)
    W['combine'](wc, rb, [OML], W['INTER'], keep=True); join_new(nm)
# bores
W['rod'](wc,'SparBoreW1', (125*t,125,ZS), (320*t,320,ZS), 3.1, op=W['CUT'], bodies=[W1])
W['rod'](wc,'PinBoreW1', (xp-5*t,125,2.5), (xp+51*t,181,2.5), 1.6, op=W['CUT'], bodies=[W1])
for i,xm in enumerate((35.0,85.0)):
    W['rod'](wc,f'MagPocketW_{i}', (xm,129.5,2.5), (xm,133.7,2.5), 5.1, op=W['CUT'], bodies=[W1])
(round(W1.volume,2), W1.lumps.count)

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
LIB='./revc.py'
W={'adsk':adsk,'math':math,'design':design,'__file__':LIB}; exec(open(LIB).read(), W)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
W1 = wc.bRepBodies.itemByName('W1_R'); OML = wc.bRepBodies.itemByName('WingOML_R')
def addwall(nm, *a):
    W['box'](wc, nm, *a); b = wc.bRepBodies.itemByName(nm)
    W['combine'](wc, b, [OML], W['INTER'], keep=True); W['combine'](wc, W1, [b], W['JOIN'], keep=False)
addwall('BayWallFwd', 85.2, 86.0, 172, 205, -40, 40)
addwall('BayWallAft', 121.0, 121.8, 172, 205, -40, 40)
addwall('TabLugFwd', 86.0, 91.5, 195.0, 199.0, -5.3, 6.2)
addwall('TabLugAft', 116.1, 121.0, 195.0, 199.0, -5.3, 6.2)
# M2 pilot holes through lugs at tab hole positions (along y)
for xhole in (89.9, 117.7):
    W['rod'](wc, f'TabHole_{xhole}', (xhole,192.0,0.45), (xhole,200.0,0.45), 0.8, op=W['CUT'], bodies=[W1])
# bottom opening (cover plate closes it), arm slot, wire holes
W['box'](wc,'BayOpening', 86.0, 121.0, 172.4, 204.6, -40, -1.0, op=W['CUT'], bodies=[W1])
W['box'](wc,'ArmSlot', 103.0, 117.0, 199.5, 206.0, -40, 4.5, op=W['CUT'], bodies=[W1])
W['rod'](wc,'WireHoleRib172', (100.0,168.0,0.5), (100.0,176.0,0.5), 3.0, op=W['CUT'], bodies=[W1])
W['rod'](wc,'WireHoleRoot', (99.5,128.0,0.5), (99.5,134.0,0.5), 4.0, op=W['CUT'], bodies=[W1])
(round(W1.volume,2), W1.lumps.count)

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
tl = design.timeline
(round(wc.bRepBodies.itemByName('W1_R').volume,2), [tl.item(i).name for i in range(tl.count-2, tl.count)])

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
tl = design.timeline
(round(wc.bRepBodies.itemByName('W1_R').volume,2), wc.bRepBodies.itemByName('W1_R').lumps.count, [tl.item(i).name for i in range(tl.count-2, tl.count)])

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
LIB='./revc.py'
W={'adsk':adsk,'math':math,'design':design,'__file__':LIB}; exec(open(LIB).read(), W)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
W1 = wc.bRepBodies.itemByName('W1_R'); W2 = wc.bRepBodies.itemByName('W2_R')
t = math.tan(math.radians(20)); ZS=2.0
W['rod'](wc,'SparSleeve_W2', (316.0*t,316.0,ZS), (460.0*t,460.0,ZS), 4.3)
W['combine'](wc, W2, [wc.bRepBodies.itemByName('SparSleeve_W2')], W['JOIN'], keep=False)
W['rod'](wc,'SparBoreW2', (310*t,310,ZS), (462*t,462,ZS), 3.1, op=W['CUT'], bodies=[W2])
# seam dowels: along spar direction (dx/dy = tan20) so both segments slide together on the spar axis
y0=315.0; c=W['w_chord'](y0); le=W['w_le'](y0)
dow=[]
for tag,xc in (('F',0.12),('R',0.62)):
    x0 = le + xc*c; z0 = 1.5
    a=(x0-15*t, y0-15, z0); b=(x0+15*t, y0+15, z0)
    W['rod'](wc, f'DowelSleeve1_{tag}', (x0-15*t, y0-15, z0), (x0-0.2*t, y0-0.2, z0), 2.6)
    W['combine'](wc, W1, [wc.bRepBodies.itemByName(f'DowelSleeve1_{tag}')], W['JOIN'], keep=False)
    W['rod'](wc, f'DowelSleeve2_{tag}', (x0+0.2*t, y0+0.2, z0), (x0+15*t, y0+15, z0), 2.6)
    W['combine'](wc, W2, [wc.bRepBodies.itemByName(f'DowelSleeve2_{tag}')], W['JOIN'], keep=False)
    W['rod'](wc, f'DowelBore_{tag}', (x0-16*t, y0-16, z0), (x0+16*t, y0+16, z0), 1.6, op=W['CUT'], bodies=[W1, W2])
    dow.append((tag, round(x0,1)))
(dow, round(W1.volume,2), round(W2.volume,2), W2.lumps.count)

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
tl = design.timeline
([(n, round(wc.bRepBodies.itemByName(n).volume,2), wc.bRepBodies.itemByName(n).lumps.count) for n in ('W1_R','W2_R')], tl.item(tl.count-1).name)

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
LIB='./revc.py'
W={'adsk':adsk,'math':math,'design':design,'__file__':LIB}; exec(open(LIB).read(), W)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
out=[]
for nm,(ya,yb) in (('Elevon1_R',(151.2,313.3)),('Elevon2_R',(316.7,468.8))):
    e = wc.bRepBodies.itemByName(nm)
    s0 = W['inner_wing_sketch'](wc, ya, 0.5, f'ECAV_{nm}_a', xc_min=0.775, min_gap=1.2)
    s1 = W['inner_wing_sketch'](wc, yb, 0.5, f'ECAV_{nm}_b', xc_min=0.775, min_gap=1.2)
    cav = W['loft'](wc, [s0,s1], W['NEW'], f'Loft_ecav_{nm}').bodies.item(0)
    W['combine'](wc, e, [cav], W['CUT'], keep=False, name=f'Hollow_{nm}')
    out.append((nm, round(e.volume,2), e.lumps.count))
out

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
LIB='./revc.py'
W={'adsk':adsk,'math':math,'design':design,'__file__':LIB}; exec(open(LIB).read(), W)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
B = {n: wc.bRepBodies.itemByName(n) for n in ('W1_R','W2_R','Elevon1_R','Elevon2_R')}
up, lo = W['_updown'](W['T0'])
def hp(y):
    c=W['w_chord'](y); le=W['w_le'](y); tw=math.radians(W['w_twist'](y)); xc=0.75
    zc = (W['_interp'](up,xc)+W['_interp'](lo,xc))/2*c; xl=(xc-0.25)*c
    X = le+0.25*c+xl*math.cos(tw)+zc*math.sin(tw); Z=-xl*math.sin(tw)+zc*math.cos(tw)
    return (X-0.5, y, Z)
A=hp(152.0); Bp=hp(468.0)
def on_line(y):
    f=(y-A[1])/(Bp[1]-A[1]); return (A[0]+f*(Bp[0]-A[0]), y, A[2]+f*(Bp[2]-A[2]))
plan = [(158,'W1_R','Elevon1_R',2.4),(180,'Elevon1_R','W1_R',2.4),(230,'W1_R','Elevon1_R',2.4),(262,'Elevon1_R','W1_R',2.4),(300,'W1_R','Elevon1_R',2.4),
        (325,'W2_R','Elevon2_R',2.1),(360,'Elevon2_R','W2_R',2.1),(400,'W2_R','Elevon2_R',2.1),(435,'Elevon2_R','W2_R',2.1),(462,'W2_R','Elevon2_R',2.0)]
for i,(yc,owner,other,r) in enumerate(plan):
    W['rod'](wc, f'Knuckle_{i}', on_line(yc-5), on_line(yc+5), r)
    W['combine'](wc, B[owner], [wc.bRepBodies.itemByName(f'Knuckle_{i}')], W['JOIN'], keep=False)
    W['rod'](wc, f'KnuckleClr_{i}', on_line(yc-5.4), on_line(yc+5.4), r+0.4, op=W['CUT'], bodies=[B[other]])
W['rod'](wc, 'HingePinBore', on_line(150.0), on_line(470.0), 0.95, op=W['CUT'], bodies=list(B.values()))
[(n, round(b.volume,2), b.lumps.count) for n,b in B.items()] + [('axis', [round(v,1) for v in A], [round(v,1) for v in Bp])]

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
tl = design.timeline
([(n, round(wc.bRepBodies.itemByName(n).volume,2), wc.bRepBodies.itemByName(n).lumps.count) for n in ('W1_R','W2_R','Elevon1_R','Elevon2_R')], tl.item(tl.count-1).name)

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
tl = design.timeline
([(n, round(wc.bRepBodies.itemByName(n).volume,2), wc.bRepBodies.itemByName(n).lumps.count) for n in ('W1_R','W2_R','Elevon1_R','Elevon2_R')], tl.item(tl.count-1).name)

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
tl = design.timeline
([(n, round(wc.bRepBodies.itemByName(n).volume,2), wc.bRepBodies.itemByName(n).lumps.count) for n in ('W1_R','W2_R','Elevon1_R','Elevon2_R')], tl.item(tl.count-1).name)

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
tl = design.timeline
([(n, round(wc.bRepBodies.itemByName(n).volume,2), wc.bRepBodies.itemByName(n).lumps.count) for n in ('W1_R','W2_R','Elevon1_R','Elevon2_R')], tl.item(tl.count-1).name)

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
tl = design.timeline
([(n, round(wc.bRepBodies.itemByName(n).volume,2), wc.bRepBodies.itemByName(n).lumps.count) for n in ('W1_R','W2_R','Elevon1_R','Elevon2_R')], tl.item(tl.count-1).name, tl.count)

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
tl = design.timeline
([(n, round(wc.bRepBodies.itemByName(n).volume,2), wc.bRepBodies.itemByName(n).lumps.count) for n in ('W1_R','W2_R','Elevon1_R','Elevon2_R')], tl.item(tl.count-1).name)

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
LIB='./revc.py'
W={'adsk':adsk,'math':math,'design':design,'__file__':LIB}; exec(open(LIB).read(), W)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
W2 = wc.bRepBodies.itemByName('W2_R'); OML = wc.bRepBodies.itemByName('WingOML_R')
out=[]
# 1) trim W2 at 440 + closing rib
W['box'](wc,'T_trim', -200,400, 300,440.0, -80,120); tb = wc.bRepBodies.itemByName('T_trim')
W['combine'](wc, W2, [tb], W['INTER'], keep=False)
W['box'](wc,'Rib440', -200,400, 438.8,440.0, -80,120); rb = wc.bRepBodies.itemByName('Rib440')
W['combine'](wc, rb, [OML], W['INTER'], keep=True); W['combine'](wc, W2, [rb], W['JOIN'], keep=False)
out.append(('W2', round(W2.volume,2), W2.lumps.count))
# 2) delete old fin winglet
old = wc.bRepBodies.itemByName('Winglet_R'); old.deleteMe()
# 3) blended winglet loft; verify plane normals
secs=[]; checks=[]
for i,(s,c,le,tw,t) in enumerate(W['bw_stations']()):
    sk, pts = W['bw_sketch'](wc, s, c, le, tw, t, f'BW_{i}')
    y0,z0,th = W['bw_path_point'](s)
    n = sk.referencePlane.geometry.normal
    checks.append(round(abs(n.y*math.cos(th)+n.z*math.sin(th)),4))
    secs.append(sk)
out.append(('plane|dot tangent|', checks))
out.append(('profiles', [s.profiles.count for s in secs]))
bw = W['loft'](wc, secs, W['NEW'], 'Loft_BlendedWinglet').bodies.item(0); bw.name='WingletBlend_R'
bb=bw.boundingBox
out.append(('BW', round(bw.volume,2), bw.lumps.count, [round(v*10,1) for v in (bb.minPoint.y,bb.maxPoint.y,bb.minPoint.z,bb.maxPoint.z)]))
out

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
LIB='./revc.py'
W={'adsk':adsk,'math':math,'design':design,'__file__':LIB}; exec(open(LIB).read(), W)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
out=[(b.name, round(b.volume,2)) for b in wc.bRepBodies]
for s in list(wc.sketches):
    if s.name.startswith('BW_'):
        try: s.deleteMe()
        except: pass
secs=[]; checks=[]
for i,(s,c,le,tw,t) in enumerate(W['bw_stations']()):
    sk, pts = W['bw_sketch'](wc, s, c, le, tw, t, f'BW_{i}')
    y0,z0,th = W['bw_path_point'](s)
    o,xa,ya,za = sk.transform.getAsCoordinateSystem()
    checks.append(round(abs(za.y*math.cos(th)+za.z*math.sin(th)),4))
    secs.append(sk)
out.append(('normal·tangent', checks)); out.append(('profiles',[s.profiles.count for s in secs]))
bw = W['loft'](wc, secs, W['NEW'], 'Loft_BlendedWinglet').bodies.item(0); bw.name='WingletBlend_R'
bb=bw.boundingBox
out.append(('BW', round(bw.volume,2), bw.lumps.count, [round(v*10,1) for v in (bb.minPoint.y,bb.maxPoint.y,bb.minPoint.z,bb.maxPoint.z)]))
out

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
LIB='./revc.py'
W={'adsk':adsk,'math':math,'design':design,'__file__':LIB}; exec(open(LIB).read(), W)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
for s in list(wc.sketches):
    if s.name.startswith('BW_'):
        try: s.deleteMe()
        except: pass
for p in list(wc.constructionPlanes):
    if p.name.startswith('PL_BW_'):
        try: p.deleteMe()
        except: pass
secs=[]; res=[]
for i,(s,c,le,tw,t) in enumerate(W['bw_stations']()):
    sk, pts = W['bw_sketch'](wc, s, c, le, tw, t, f'BW_{i}')
    y0,z0,th = W['bw_path_point'](s)
    o,xa,ya,za = sk.transform.getAsCoordinateSystem()
    res.append((i, round(za.y*math.cos(th)+za.z*math.sin(th),4), sk.profiles.count)); secs.append(sk)
bw = W['loft'](wc, secs, W['NEW'], 'Loft_BlendedWinglet').bodies.item(0); bw.name='WingletBlend_R'
bb=bw.boundingBox
res.append(('BW', round(bw.volume,2), bw.lumps.count, [round(v*10,1) for v in (bb.minPoint.x,bb.maxPoint.x,bb.minPoint.y,bb.maxPoint.y,bb.minPoint.z,bb.maxPoint.z)]))
res

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
LIB='./revc.py'
W={'adsk':adsk,'math':math,'design':design,'__file__':LIB}; exec(open(LIB).read(), W)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
bw = wc.bRepBodies.itemByName('WingletBlend_R'); W2 = wc.bRepBodies.itemByName('W2_R')
st = W['bw_stations'](); L = W['bw_len']()
st_in = [(1.2,)+st[0][1:]] + st[1:-1] + [(L-2.5,)+st[-1][1:]]
secs=[]
for i,(s,c,le,tw,t) in enumerate(st_in):
    sk,_ = W['bw_sketch'](wc, s, c, le, tw, t, f'BWi_{i}', inset=0.6)
    secs.append(sk)
cav = W['loft'](wc, secs, W['NEW'], 'Loft_BWcav').bodies.item(0)
W['combine'](wc, bw, [cav], W['CUT'], keep=False)
# joint at y=440: spar sleeve through the straight part + bore; two dowels parallel to the spar
t = math.tan(math.radians(20)); ZS=2.0
W['rod'](wc,'SparSleeve_BW', (441.0*t,441.0,ZS), (466.0*t,466.0,ZS), 4.3)
W['combine'](wc, bw, [wc.bRepBodies.itemByName('SparSleeve_BW')], W['JOIN'], keep=False)
W['rod'](wc,'SparBore_BW', (436*t,436,ZS), (467*t,467,ZS), 3.1, op=W['CUT'], bodies=[bw, W2])
y0=440.0; c=W['w_chord'](y0); le=W['w_le'](y0)
for tag,xc in (('F',0.14),('R',0.58)):
    x0 = le + xc*c; z0 = 1.2
    W['rod'](wc, f'DS_W2_{tag}', (x0-12*t, y0-12, z0), (x0-0.2*t, y0-0.2, z0), 2.4)
    W['combine'](wc, W2, [wc.bRepBodies.itemByName(f'DS_W2_{tag}')], W['JOIN'], keep=False)
    W['rod'](wc, f'DS_BW_{tag}', (x0+0.2*t, y0+0.2, z0), (x0+12*t, y0+12, z0), 2.4)
    W['combine'](wc, bw, [wc.bRepBodies.itemByName(f'DS_BW_{tag}')], W['JOIN'], keep=False)
    W['rod'](wc, f'DB440_{tag}', (x0-13*t, y0-13, z0), (x0+13*t, y0+13, z0), 1.6, op=W['CUT'], bodies=[W2, bw])
[(n, round(wc.bRepBodies.itemByName(n).volume,2), wc.bRepBodies.itemByName(n).lumps.count) for n in ('W2_R','WingletBlend_R')]

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
LIB='./revc.py'
W={'adsk':adsk,'math':math,'design':design,'__file__':LIB}; exec(open(LIB).read(), W)
wc = design.rootComponent.occurrences.itemByName('WingC:1').component
for s in list(wc.sketches):
    if s.name.startswith('BWi_'):
        try: s.deleteMe()
        except: pass
bw = wc.bRepBodies.itemByName('WingletBlend_R'); W2 = wc.bRepBodies.itemByName('W2_R')
st = W['bw_stations'](); L = W['bw_len']()
st_in = [(1.2,)+st[0][1:]] + st[1:-1] + [(L-2.5,)+st[-1][1:]]
secs=[W['bw_sketch'](wc, s, c, le, tw, t, f'BWi_{i}', inset=0.6)[0] for i,(s,c,le,tw,t) in enumerate(st_in)]
cav = W['loft'](wc, secs, W['NEW'], 'Loft_BWcav').bodies.item(0)
W['combine'](wc, bw, [cav], W['CUT'], keep=False)
t = math.tan(math.radians(20)); ZS=2.0
W['rod'](wc,'SparSleeve_BW', (441.0*t,441.0,ZS), (466.0*t,466.0,ZS), 4.3)
W['combine'](wc, bw, [wc.bRepBodies.itemByName('SparSleeve_BW')], W['JOIN'], keep=False)
W['rod'](wc,'SparBore_BW', (436*t,436,ZS), (467*t,467,ZS), 3.1, op=W['CUT'], bodies=[bw, W2])
y0=440.0; c=W['w_chord'](y0); le=W['w_le'](y0)
for tag,xc in (('F',0.14),('R',0.58)):
    x0 = le + xc*c; z0 = 1.2
    W['rod'](wc, f'DS_W2_{tag}', (x0-12*t, y0-12, z0), (x0-0.2*t, y0-0.2, z0), 2.4)
    W['combine'](wc, W2, [wc.bRepBodies.itemByName(f'DS_W2_{tag}')], W['JOIN'], keep=False)
    W['rod'](wc, f'DS_BW_{tag}', (x0+0.2*t, y0+0.2, z0), (x0+12*t, y0+12, z0), 2.4)
    W['combine'](wc, bw, [wc.bRepBodies.itemByName(f'DS_BW_{tag}')], W['JOIN'], keep=False)
    W['rod'](wc, f'DB440_{tag}', (x0-13*t, y0-13, z0), (x0+13*t, y0+13, z0), 1.6, op=W['CUT'], bodies=[W2, bw])
[(n, round(wc.bRepBodies.itemByName(n).volume,2), wc.bRepBodies.itemByName(n).lumps.count) for n in ('W2_R','WingletBlend_R')]

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
root = design.rootComponent
vp = app.activeViewport
for o in root.occurrences:
    o.isLightBulbOn = (o.component.name in ('WingC','Centerbody'))
wc = root.occurrences.itemByName('WingC:1').component
for b in wc.bRepBodies: b.isLightBulbOn = b.name in ('W1_R','W2_R','Elevon1_R','Elevon2_R','WingletBlend_R')
cb = root.occurrences.itemByName('Centerbody:1').component
for b in cb.bRepBodies: b.isLightBulbOn = b.name in ('Centerbody','Hatch')
for s in wc.sketches: s.isVisible=False
for p in wc.constructionPlanes: p.isLightBulbOn=False
SP='./'
def shot(name, eye, tgt, up=(0,0,1)):
    cam=vp.camera; cam.target=adsk.core.Point3D.create(*tgt); cam.eye=adsk.core.Point3D.create(*eye); cam.upVector=adsk.core.Vector3D.create(*up)
    cam.isSmoothTransition=False; vp.camera=cam; return vp.saveAsImageFile(SP+name,1600,1000)
cam=vp.camera; cam.isFitView=False
r=[shot('c_tip.png',(-2,20,14),(19,49,2)), shot('c_tip_front.png',(-40,48,4),(18,48,3))]
r

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
root = design.rootComponent
wc = root.occurrences.itemByName('WingC:1').component
tbm = adsk.fusion.TemporaryBRepManager.get()
m = adsk.core.Matrix3D.create(); m.setCell(1,1,-1)
out=[]
for n in ('W1_R','W2_R','Elevon1_R','Elevon2_R','WingletBlend_R'):
    src = wc.bRepBodies.itemByName(n)
    tb = tbm.copy(src); tbm.transform(tb, m)
    nb = wc.bRepBodies.add(tb); nb.name = n.replace('_R','_L')
    out.append((nb.name, round(nb.volume,2), nb.lumps.count))
# hide helper bodies
for b in wc.bRepBodies:
    if not any(b.name.startswith(k) for k in ('W1_','W2_','Elevon','WingletBlend')): b.isLightBulbOn=False
    else: b.isLightBulbOn=True
root.occurrences.itemByName('Wings:1').isLightBulbOn=False
out

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
LIB='./revc.py'
W={'adsk':adsk,'math':math,'design':design,'__file__':LIB}; exec(open(LIB).read(), W)
root = design.rootComponent
wc = root.occurrences.itemByName('WingC:1').component
hc = root.occurrences.itemByName('Hardware:1').component
tbm = adsk.fusion.TemporaryBRepManager.get()
out=[]
for side in ('R','L'):
    s = 1 if side=='R' else -1
    horn = tbm.copy(hc.bRepBodies.itemByName(f'Horn_{side}'))
    e1 = wc.bRepBodies.itemByName(f'Elevon1_{side}')
    hb = wc.bRepBodies.add(horn); hb.name=f'HornP_{side}'
    W['combine'](wc, e1, [hb], W['JOIN'], keep=False)
    # horn pushrod hole 1.6 mm (Z-bend)
    xh = W['w_le'](202.4)+0.75*W['w_chord'](202.4)
    W['rod'](wc, f'HornHole_{side}', (xh+3.0, s*199.0, -11.05), (xh+3.0, s*206.0, -11.05), 0.8, op=W['CUT'], bodies=[e1])
    # conformal servo cover: OML ∩ box, minus OML shifted +0.8 z
    oml = tbm.copy(wc.bRepBodies.itemByName('WingOML_R'))
    if side=='L':
        m = adsk.core.Matrix3D.create(); m.setCell(1,1,-1); tbm.transform(oml, m)
    y0,y1 = (172.6,204.4) if side=='R' else (-204.4,-172.6)
    c = adsk.core.Point3D.create((86.2+120.8)/20, (y0+y1)/20, -2.05)
    bx = tbm.createBox(adsk.core.OrientedBoundingBox3D.create(c, adsk.core.Vector3D.create(1,0,0), adsk.core.Vector3D.create(0,1,0), 3.46, (y1-y0)/10, 3.9))
    cov = tbm.copy(oml); tbm.booleanOperation(cov, bx, adsk.fusion.BooleanTypes.IntersectionBooleanType)
    up = tbm.copy(oml); mv = adsk.core.Matrix3D.create(); mv.translation = adsk.core.Vector3D.create(0,0,0.08); tbm.transform(up, mv)
    tbm.booleanOperation(cov, up, adsk.fusion.BooleanTypes.DifferenceBooleanType)
    cb_ = wc.bRepBodies.add(cov); cb_.name=f'ServoCover_{side}'
    out.append((side, round(e1.volume,2), round(cb_.volume,2), cb_.lumps.count))
out

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
root = design.rootComponent
cb = root.occurrences.itemByName('Centerbody:1').component
body = cb.bRepBodies.itemByName('Centerbody')
tbm = adsk.fusion.TemporaryBRepManager.get()
def boxT(x0,x1,y0,y1,z0,z1):
    c = adsk.core.Point3D.create((x0+x1)/20,(y0+y1)/20,(z0+z1)/20)
    return tbm.createBox(adsk.core.OrientedBoundingBox3D.create(c, adsk.core.Vector3D.create(1,0,0), adsk.core.Vector3D.create(0,1,0), (x1-x0)/10,(y1-y0)/10,(z1-z0)/10))
parts = {'CB_FrontRight':(-200,95,0,200), 'CB_FrontLeft':(-200,95,-200,0), 'CB_RearRight':(95,400,0,200), 'CB_RearLeft':(95,400,-200,0)}
out=[]
for n,(x0,x1,y0,y1) in parts.items():
    t = tbm.copy(body); tbm.booleanOperation(t, boxT(x0,x1,y0,y1,-100,150), adsk.fusion.BooleanTypes.IntersectionBooleanType)
    nb = cb.bRepBodies.add(t); nb.name = n
    bb = nb.boundingBox
    out.append((n, round(nb.volume,2), nb.lumps.count, [round((bb.maxPoint.x-bb.minPoint.x)*10,1), round((bb.maxPoint.y-bb.minPoint.y)*10,1), round((bb.maxPoint.z-bb.minPoint.z)*10,1)]))
body.isLightBulbOn = False
app.activeDocument.save('Rev C: printed wing (blended winglet), centerbody split 4 + bolted lugs')
out

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
root = design.rootComponent
col = adsk.core.ObjectCollection.create()
cbo = root.occurrences.itemByName('Centerbody:1'); wco = root.occurrences.itemByName('WingC:1')
for n in ('CB_FrontRight','CB_FrontLeft','CB_RearRight','CB_RearLeft','Hatch'):
    col.add(cbo.component.bRepBodies.itemByName(n).createForAssemblyContext(cbo))
for n in ('W1_R','W1_L','ServoCover_R','ServoCover_L'):
    col.add(wco.component.bRepBodies.itemByName(n).createForAssemblyContext(wco))
for o in root.occurrences:
    if o.name.startswith(('RP-004882','rpi-cam','Emax','Open CASCADE')): col.add(o)
ii = design.createInterferenceInput(col); ii.areCoincidentFacesIncluded=False
r = design.analyzeInterference(ii)
rows=[]
for i in range(r.count):
    it=r.item(i)
    n1 = it.entityOne.name if hasattr(it.entityOne,'name') else '?'; n2 = it.entityTwo.name if hasattr(it.entityTwo,'name') else '?'
    try: p1 = it.entityOne.assemblyContext.name[:14] if it.entityOne.assemblyContext else ''
    except: p1=''
    try: p2 = it.entityTwo.assemblyContext.name[:14] if it.entityTwo.assemblyContext else ''
    except: p2=''
    rows.append((p1+'/'+n1[:18], p2+'/'+n2[:18], round(it.interferenceBody.volume*1000,2)))
sorted(rows, key=lambda x:-x[2])[:25]

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
root = design.rootComponent
cbo = root.occurrences.itemByName('Centerbody:1')
col = adsk.core.ObjectCollection.create()
for n in ('CB_FrontRight','CB_FrontLeft','CB_RearRight','CB_RearLeft','Hatch'):
    col.add(cbo.component.bRepBodies.itemByName(n).createForAssemblyContext(cbo))
for o in root.occurrences:
    if o.name.startswith(('RP-004882','rpi-cam')): col.add(o)
ii = design.createInterferenceInput(col); ii.areCoincidentFacesIncluded=False
r = design.analyzeInterference(ii)
rows=[]
for i in range(r.count):
    it=r.item(i)
    def nm(e):
        try: ctx = e.assemblyContext.name[:12] if e.assemblyContext else ''
        except: ctx=''
        return ctx+'/'+(e.name[:16] if hasattr(e,'name') else '?')
    rows.append((nm(it.entityOne), nm(it.entityTwo), round(it.interferenceBody.volume*1000,2)))
(r.count, sorted(rows, key=lambda x:-x[2])[:15])

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
root = design.rootComponent
alib = app.materialLibraries.itemByName('Fusion Appearance Library')
def find(*keys):
    for i in range(alib.appearances.count):
        a = alib.appearances.item(i)
        if all(k.lower() in a.name.lower() for k in keys): return a
A = {'white': find('Plastic','Matte','White'), 'grey': find('Plastic','Matte','Grey') or find('Plastic','Glossy','Grey'),
     'accent': find('Plastic','Glossy','Red'), 'black': find('Plastic','Matte','Black'), 'metal': find('Aluminum','Anodized','Grey'),
     'carbon': find('Carbon Fiber'), 'green': find('Plastic','Glossy','Green'), 'blue': find('Plastic','Glossy','Blue')}
for n in ('Wings:1','CFD_OML:1'):
    o = root.occurrences.itemByName(n)
    if o: o.isLightBulbOn = False
for o in root.occurrences:
    for s in o.component.sketches: s.isVisible = False
    for p in o.component.constructionPlanes: p.isLightBulbOn = False
cb = root.occurrences.itemByName('Centerbody:1').component
for b in cb.bRepBodies:
    b.isLightBulbOn = b.name.startswith('CB_') and b.name != 'CB_OML_ref' or b.name == 'Hatch'
    if b.isLightBulbOn: b.appearance = A['white']
wc = root.occurrences.itemByName('WingC:1').component
for b in wc.bRepBodies:
    vis = b.name.startswith(('W1_','W2_','Elevon','WingletBlend','ServoCover'))
    b.isLightBulbOn = vis
    if vis: b.appearance = A['accent'] if b.name.startswith('Elevon') else (A['grey'] if b.name.startswith('ServoCover') else A['white'])
hc = root.occurrences.itemByName('Hardware:1').component
for b in hc.bRepBodies:
    n = b.name
    b.appearance = A['carbon'] if ('Spar' in n or 'Pin' in n) else A['metal'] if n.startswith(('Motor','Pitot')) else A['black'] if n.startswith(('Prop','Spinner','ServoArm','Pushrod')) else A['green']
app.activeDocument.save('Rev C: vendor CAD (Pi 5, CM3 x2, ES08A x2, 21700 x6), detailed propulsion')
vp = app.activeViewport
SP='./'
def shot(name, eye, tgt=(8,0,0), up=(0,0,1), fit=True):
    cam=vp.camera; cam.target=adsk.core.Point3D.create(*tgt); cam.eye=adsk.core.Point3D.create(*eye); cam.upVector=adsk.core.Vector3D.create(*up)
    cam.isSmoothTransition=False; vp.camera=cam
    if fit: vp.fit()
    return vp.saveAsImageFile(SP+name,1800,1100)
r=[shot('c_hero.png',(-55,-75,38))]
cb.bRepBodies.itemByName('Hatch').isLightBulbOn=False; cb.bRepBodies.itemByName('CB_FrontRight').isLightBulbOn=False; cb.bRepBodies.itemByName('CB_RearRight').isLightBulbOn=False
r.append(shot('c_internals.png',(-8,34,22),(4,0,0), fit=False))
cb.bRepBodies.itemByName('Hatch').isLightBulbOn=True; cb.bRepBodies.itemByName('CB_FrontRight').isLightBulbOn=True; cb.bRepBodies.itemByName('CB_RearRight').isLightBulbOn=True
r.append(shot('c_rear.png',(60,-40,25),(10,0,2)))
r

#==========
design = adsk.fusion.Design.cast(app.activeProduct)
root = design.rootComponent
P = lambda x,y,z: adsk.core.Point3D.create(x/10,y/10,z/10)
Vv = lambda x,y,z: adsk.core.Vector3D.create(x,y,z)
ys = (-53.5,-32.1,-10.7,10.7,32.1,53.5)
cells = sorted([o for o in root.occurrences if o.name.startswith('Open CASCADE')], key=lambda o: o.name)
for o,y in zip(cells, ys):
    m = adsk.core.Matrix3D.create(); m.setWithCoordinateSystem(P(-17.1,y,1.21), Vv(1,0,0), Vv(0,1,0), Vv(0,0,1)); o.transform2 = m
root.occurrences.itemByName('Hardware:1').isLightBulbOn = True
out=[[round(v*10,1) for v in (o.boundingBox.minPoint.x,o.boundingBox.maxPoint.x,o.boundingBox.minPoint.y,o.boundingBox.maxPoint.y,o.boundingBox.minPoint.z,o.boundingBox.maxPoint.z)] for o in cells]
app.activeDocument.save('Rev C: vendor parts placed correctly')
vp = app.activeViewport
SP='./'
def shot(name, eye, tgt=(8,0,0), up=(0,0,1), fit=True):
    cam=vp.camera; cam.target=adsk.core.Point3D.create(*tgt); cam.eye=adsk.core.Point3D.create(*eye); cam.upVector=adsk.core.Vector3D.create(*up)
    cam.isSmoothTransition=False; vp.camera=cam
    if fit: vp.fit()
    return vp.saveAsImageFile(SP+name,1800,1100)
r=[shot('c_hero.png',(-55,-75,38)), shot('c_rear.png',(70,-45,25),(10,0,2))]
cb = root.occurrences.itemByName('Centerbody:1').component
for n in ('Hatch','CB_FrontRight','CB_RearRight'): cb.bRepBodies.itemByName(n).isLightBulbOn=False
r.append(shot('c_internals.png',(-8,34,22),(4,0,0), fit=False))
for n in ('Hatch','CB_FrontRight','CB_RearRight'): cb.bRepBodies.itemByName(n).isLightBulbOn=True
(out, r)

#==========
design = adsk.fusion.Design.cast(app.activeProduct); root = design.rootComponent
tbm = adsk.fusion.TemporaryBRepManager.get(); BO = adsk.fusion.BooleanTypes
C = {o.component.name: o.component for o in root.occurrences}
def voids(b):
    bx = b.boundingBox; pad = 0.2
    ob = adsk.core.OrientedBoundingBox3D.create(adsk.core.Point3D.create((bx.minPoint.x+bx.maxPoint.x)/2, (bx.minPoint.y+bx.maxPoint.y)/2, (bx.minPoint.z+bx.maxPoint.z)/2),
        adsk.core.Vector3D.create(1,0,0), adsk.core.Vector3D.create(0,1,0), bx.maxPoint.x-bx.minPoint.x+2*pad, bx.maxPoint.y-bx.minPoint.y+2*pad, bx.maxPoint.z-bx.minPoint.z+2*pad)
    box = tbm.createBox(ob); tbm.booleanOperation(box, tbm.copy(b), BO.DifferenceBooleanType)
    out = []
    for l in box.lumps:
        lb = l.boundingBox
        closed = (lb.minPoint.x > bx.minPoint.x - pad/2 and lb.maxPoint.x < bx.maxPoint.x + pad/2 and lb.minPoint.y > bx.minPoint.y - pad/2 and lb.maxPoint.y < bx.maxPoint.y + pad/2 and lb.minPoint.z > bx.minPoint.z - pad/2 and lb.maxPoint.z < bx.maxPoint.z + pad/2)
        if closed: out.append(round(l.volume, 2))
    return out
res = {}
for c, n in (('WingC','W1_R'), ('WingC','W2_R'), ('WingC','WingletBlend_R'), ('WingC','Elevon1_R'), ('WingC','Elevon2_R'), ('Centerbody','CB_FrontRight'), ('Centerbody','CB_RearRight'), ('Centerbody','Hatch')):
    b = C[c].bRepBodies.itemByName(n)
    res[n] = (round(b.volume,2), [s.isVoid for l in b.lumps for s in l.shells], sorted(voids(b), reverse=True)[:10])
res