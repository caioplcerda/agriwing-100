#!/bin/sh
# alpha sweep on the converged mesh; each alpha gets its own copy of the decomposed case
cd "${0%/*}" || exit 1
for A in 1 7 10; do
  D=case_a$A; rm -rf $D; mkdir $D
  cp -r case/system case/constant case/0.orig $D/
  for p in case/processor*; do mkdir -p $D/$(basename $p); cp -r $p/constant $D/$(basename $p)/; done
  python3 - "$A" "$D" <<'PY'
import sys, math, re, os
a=math.radians(float(sys.argv[1])); D=sys.argv[2]; U=15.0
ux, uz = U*math.cos(a), U*math.sin(a)
for f in ('U',):
    p=os.path.join(D,'0.orig',f); s=open(p).read()
    s=re.sub(r'\(14\.947 0 1\.255\)', f'({ux:.5f} 0 {uz:.5f})', s); open(p,'w').write(s)
p=os.path.join(D,'system','controlDict'); s=open(p).read()
s=s.replace('liftDir (-0.08368 0 0.99649)', f'liftDir ({-math.sin(a):.5f} 0 {math.cos(a):.5f})').replace('dragDir (0.99649 0 0.08368)', f'dragDir ({math.cos(a):.5f} 0 {math.sin(a):.5f})')
s=s.replace('writeInterval 400','writeInterval 2000'); open(p,'w').write(s)
PY
  (cd $D && for d in processor*; do cp -r 0.orig $d/0; done && mpirun -np 10 potentialFoam -parallel > log.potentialFoam 2>&1 && mpirun -np 10 simpleFoam -parallel > log.simpleFoam 2>&1) || echo "alpha $A failed"
done
echo SWEEP_DONE
