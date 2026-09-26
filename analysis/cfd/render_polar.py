import json, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
BG, INK = '#12151a', '#e8ecf1'
plt.rcParams.update({'font.size':10,'text.color':INK,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'axes.edgecolor':'#3a414c','figure.facecolor':BG,'axes.facecolor':BG,'savefig.facecolor':BG})
s = json.load(open('cfd_summary.json')); a = np.array(s['alpha']); cl = np.array(s['CL']); cd = np.array(s['CD']); cm = np.array(s['Cm_x54'])
cm68 = cm + cl*(68-54)/220.9
fig, ax = plt.subplots(1, 3, figsize=(14, 4.4), constrained_layout=True)
ax[0].plot(a, cl, 'o-', color='#59b8ff'); ax[0].set_xlabel('α [deg]'); ax[0].set_ylabel('CL'); ax[0].set_title('Lift  (CLα = %.3f /deg)' % s['CLa_perdeg'])
ax[0].axhline(0.38, color='#ffb347', ls='--', lw=1); ax[0].text(1, 0.40, 'CL needed, 1.1 kg @ 15 m/s', color='#ffb347', fontsize=9)
ax[1].plot(cd, cl, 'o-', color='#7bd88f'); ax[1].set_xlabel('CD'); ax[1].set_ylabel('CL'); ax[1].set_title('Drag polar')
for A, D, L in zip(a, cd, cl): ax[1].annotate(f'{A:g}°  L/D {L/D:.1f}' if L > 0.05 else f'{A:g}°', (D, L), textcoords='offset points', xytext=(6, -3), fontsize=8, color=INK)
ax[2].plot(a, cm, 'o-', color='#c792ea', label='CG 54 mm'); ax[2].plot(a, cm68, 'o-', color='#ff7a59', label='CG 68 mm (chosen)')
ax[2].axhline(0, color='#888', lw=0.8); ax[2].set_xlabel('α [deg]'); ax[2].set_ylabel('Cm'); ax[2].legend(frameon=False)
ax[2].set_title('Pitch stability  (NP = %.0f mm)' % s['x_np_mm'])
for x in ax: x.grid(alpha=0.15)
fig.suptitle('OpenFOAM α sweep · 15 m/s · half model, 0.8 M cells', color=INK, fontsize=12)
fig.savefig('img_polars.png', dpi=140); print('polar ok')
