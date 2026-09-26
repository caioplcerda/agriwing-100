"""Build the AgriWing-100 Rev D report (agw_site/index.html) from the analysis JSON files."""
import json, html, os
E = lambda s: html.escape(str(s))
S = json.load(open('agw_struct.json')); M = json.load(open('mass_d.json')); MF = json.load(open('agw_mfg.json'))
CFD = json.load(open('cfd/cfd_summary.json')); PC = json.load(open('perf_c.json'))
style = open('report_style.html').read()
pass
kW = M['auw'] / 1152.0; kP = kW ** 1.5
perf = dict(P_cfd=PC['P_cfd'] * kP, P_cons=PC['P_cons'] * kP, t_cfd=PC['t_cfd'] / kP, t_cons=PC['t_cons'] / kP, vs=PC['vs'] * kW ** 0.5, vc=15.0 * kW ** 0.5)
def pill(sf):
    if sf is None: return ''
    c = 'ok' if sf >= 2 else ('warn' if sf >= 1.5 else 'fail'); return f'<span class="pill {c}">SF {sf:g}</span>'
def tbl_struct():
    r = []
    for x in S['rows']:
        r.append(f'<tr><th scope="row">{E(x["item"])}</th><td>Rev {x["rev"]}</td><td class="num">{x["load"]:g}</td><td class="num">{x["cap"]:g}</td><td>{E(x["unit"])}</td><td>{pill(x["sf"])}</td><td>{E(x["note"])}</td></tr>')
    return '\n'.join(r)
def tbl_mass():
    r = [f'<tr><th scope="row">{E(n)}</th><td class="num">{m:.1f}</td><td class="num">{x:.1f}</td><td class="num">{c}</td></tr>' for n, m, x, c in M['items']]
    r.append(f'<tr class="tot"><th scope="row">Total</th><td class="num">{M["auw"]}</td><td class="num">{M["cg"]}</td><td class="num">{M["cost"]}</td></tr>')
    return '\n'.join(r)
ORDER = ['CB_FrontRight', 'CB_FrontLeft', 'CB_RearRight', 'CB_RearLeft', 'Hatch', 'W1_R', 'W1_L', 'W2_R', 'W2_L', 'WingletBlend_R', 'WingletBlend_L', 'Elevon1_R', 'Elevon1_L', 'Elevon2_R', 'Elevon2_L', 'ServoCover_R', 'ServoCover_L']
SUP = {'Hatch': 'brim', 'WingletBlend_R': 'brim', 'WingletBlend_L': 'brim', 'ServoCover_R': '2-layer raft', 'ServoCover_L': '2-layer raft'}
def tbl_print():
    P = {p['part']: p for p in MF['parts']}; r = []
    for n in ORDER:
        p = P[n]
        r.append(f'<tr><th scope="row"><code>{n}</code></th><td>{E(p["note"])}</td><td class="num">{p["height"]}</td><td class="num">{p["footprint"]}</td><td>{SUP.get(n, "none")}</td><td class="num">{p["mass_g"]:.0f}</td><td class="num">{p["hours"]:.1f}</td></tr>')
    t = MF['total']; r.append(f'<tr class="tot"><th scope="row">Total, {t["parts"]} parts</th><td colspan="4">LW-ASA, Bambu 256 mm bed</td><td class="num">{t["mass"]}</td><td class="num">{t["hours"]}</td></tr>')
    return '\n'.join(r)
def tbl_polar():
    r = []
    for a, cl, cd, cm in zip(CFD['alpha'], CFD['CL'], CFD['CD'], CFD['Cm_x54']):
        r.append(f'<tr><th scope="row">{a:g}°</th><td class="num">{cl:.3f}</td><td class="num">{cd:.4f}</td><td class="num">{(cl / cd if cl > 0.05 else 0):.1f}</td><td class="num">{cm:+.4f}</td></tr>')
    return '\n'.join(r)
def fig(src, alt, cap, w=1400, h=856):
    return f'<figure><img src="img/{src}.webp" alt="{E(alt)}" width="{w}" height="{h}" loading="lazy"><figcaption class="cap">{cap}</figcaption></figure>'
T = open('agw_report_body.html').read()
rep = {'{{AUW}}': str(M['auw']), '{{CG}}': str(M['cg']), '{{SM}}': str(M['sm']), '{{PRINTED}}': str(M['printed']), '{{COST}}': str(M['cost']),
       '{{HOURS}}': str(MF['total']['hours']), '{{PARTS}}': str(MF['total']['parts']), '{{M0}}': f"{S['M0']:.1f}", '{{M130}}': f"{S['M130']:.1f}",
       '{{P_CFD}}': f"{perf['P_cfd']:.0f}", '{{P_CONS}}': f"{perf['P_cons']:.0f}", '{{T_CFD}}': f"{perf['t_cfd']:.0f}", '{{T_CONS}}': f"{perf['t_cons']:.0f}",
       '{{VS}}': f"{perf['vs']:.1f}", '{{VC}}': f"{perf['vc']:.1f}", '{{LD}}': f"{PC['LD_cfd']}", '{{NP}}': f"{CFD['x_np_mm']:.1f}",
       '{{TBL_STRUCT}}': tbl_struct(), '{{TBL_MASS}}': tbl_mass(), '{{TBL_PRINT}}': tbl_print(), '{{TBL_POLAR}}': tbl_polar(),
       '{{XBATT}}': str(M['x_batt'])}
for k, v in rep.items(): T = T.replace(k, v)
import re
T = re.sub(r'\{\{FIG ([a-z0-9_]+) \| ([^|]+) \| ([^}]+)\}\}', lambda m: fig(m.group(1), m.group(2).strip(), m.group(3).strip()), T)
out = '<title>AgriWing-100 Rev D</title>\n' + style + '<div class="wrap">\n' + T + '\n</div>\n'
assert '{{' not in out, re.findall(r'\{\{[^}]*\}\}', out)[:5]
os.makedirs('site', exist_ok=True); open('site/index.html', 'w').write(out); print('ok', len(out) // 1024, 'KB')
