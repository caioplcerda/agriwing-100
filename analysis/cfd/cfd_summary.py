import json, numpy as np
A=np.array([1.0,4.8,7.0,10.0]); CD=np.array([0.02239,0.02708,0.03534,0.05545]); CL=np.array([0.00210,0.27690,0.43522,0.63706]); CM=np.array([0.01882,-0.01552,-0.03649,-0.06559])
MAC=220.9; XREF=54.0; S=0.2061
cla=np.polyfit(A,CL,1)[0]; cma=np.polyfit(A,CM,1)[0]
xnp = XREF - cma/cla*MAC
res={"alpha":A.tolist(),"CL":CL.tolist(),"CD":CD.tolist(),"Cm_x54":CM.tolist(),"CLa_perdeg":cla,"Cma_perdeg":cma,"x_np_mm":xnp}
for m in (1.05,1.10,1.15):
    for xcg in (62.0,66.0,70.0):
        clr=m*9.81/(0.5*1.225*15**2*S); a=np.interp(clr,CL,A); cd=np.interp(a,A,CD)
        cm=np.interp(a,A,CM)+clr*(xcg-XREF)/MAC
        res[f"m{m}_x{int(xcg)}"]={"alpha":round(float(a),2),"CL":round(float(clr),3),"CD":round(float(cd),4),"L/D":round(float(clr/cd),1),"Cm_untrimmed":round(float(cm),4),"SM_pct":round(float((xnp-xcg)/MAC*100),1)}
json.dump(res,open('cfd_summary.json','w'),indent=1)
print(f"CLa {cla:.4f}/deg  Cma {cma:.5f}/deg  x_np {xnp:.1f} mm")
for k,v in res.items():
    if k.startswith('m1.1'): print(k,v)
