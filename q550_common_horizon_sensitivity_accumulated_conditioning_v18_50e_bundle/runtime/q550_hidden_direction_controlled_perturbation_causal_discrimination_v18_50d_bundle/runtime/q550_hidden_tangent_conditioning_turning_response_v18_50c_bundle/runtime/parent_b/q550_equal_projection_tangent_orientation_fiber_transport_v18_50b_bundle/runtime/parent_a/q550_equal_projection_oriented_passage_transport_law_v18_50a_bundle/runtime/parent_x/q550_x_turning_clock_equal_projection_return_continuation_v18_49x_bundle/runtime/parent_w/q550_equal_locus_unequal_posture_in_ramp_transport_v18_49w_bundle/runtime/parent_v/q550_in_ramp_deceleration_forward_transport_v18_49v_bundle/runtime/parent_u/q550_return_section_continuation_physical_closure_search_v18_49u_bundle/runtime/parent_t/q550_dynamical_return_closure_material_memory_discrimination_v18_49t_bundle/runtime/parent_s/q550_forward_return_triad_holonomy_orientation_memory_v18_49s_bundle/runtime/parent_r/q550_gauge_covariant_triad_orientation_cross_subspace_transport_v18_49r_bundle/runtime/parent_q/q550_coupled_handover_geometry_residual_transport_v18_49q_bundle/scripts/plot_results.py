#!/usr/bin/env python3
"""Original figures for Q550 v18.49q, regenerated from numerical CSV/JSON."""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'results/phase_resolved_geometric_ledger.csv').open(newline='') as f: data=list(csv.DictReader(f))
rep=json.loads((ROOT/'results/report.json').read_text())
kind='original';r=.327375
rows=[x for x in data if x['kappa_kind']==kind and abs(float(x['ramp_xi'])-r)<1e-9]
if not rows:raise RuntimeError('Need original r=.327375 trace for figures')
q=np.array([float(x['q']) for x in rows]);a=lambda key:np.array([float(x[key]) for x in rows])
fig,ax=plt.subplots(figsize=(9,5))
ax.plot(q,100*a('share_67'),lw=2,label='Pair 6–7')
ax.plot(q,100*a('share_78'),lw=2,label='Pair 7–8')
ax.plot(q,100*a('share_68'),lw=1.8,label='Observed pair 6–8')
ax.plot(q,100*a('share_43_other_pairs'),lw=2,label='Remaining 43 (including 6–8)')
event=next(x for x in rep['handover_events'] if x['kappa_kind']==kind and abs(x['ramp_xi']-r)<1e-9)
ax.axvline(event['q_root'],ls=':',color='0.5',label=f"Handover q={event['q_root']:.7f}")
ax.set(xlabel='Registered phase q',ylabel='Contribution to ||K||² [%]',title='v18.49q — Instantaneous handover and the other 43 pair channels')
ax.legend(loc='best');ax.grid(alpha=.2);fig.tight_layout()
fig.savefig(ROOT/'results/phase_pairwise_residual_shares.png',dpi=170);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5))
ax.plot(q,a('comm_norm_67_78'),label='||[K67, K78]||  (phase rate squared)',lw=2)
ax.plot(q,a('comm_68_coefficient'),label='Oriented bracket coefficient in 6–8 plane',lw=2)
ax.set(xlabel='Registered phase q',ylabel='Commutator scale [phase⁻²]',title='v18.49q — Shared rank-7 Lie bracket in the 6–8 plane')
ax.grid(alpha=.2);ax.legend();fig.tight_layout()
fig.savefig(ROOT/'results/coupled_bracket_68.png',dpi=170);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5))
ax.plot(q,a('observed_K68_norm'),label='Measured ||K68|| [phase⁻¹]',lw=2)
ax.plot(q,a('subspace_678_leakage_norm'),label='||[Kother,P678]|| [phase⁻¹]',lw=2)
ax.set(xlabel='Registered phase q',ylabel='Generator rate magnitude [phase⁻¹]',title='v18.49q — Measured 6–8 channel versus outward subspace leakage')
ax.grid(alpha=.2);ax.legend();fig.tight_layout()
fig.savefig(ROOT/'results/measured_68_and_subspace_leakage.png',dpi=170);plt.close(fig)
labels=[('O ' if x['kappa_kind']=='original' else 'A ')+f"{x['ramp_xi']:.6f}" for x in rep['cases']]
x=np.arange(len(labels));w=.24
fig,ax=plt.subplots(figsize=(9,5))
ax.bar(x-w,[c['full_projector_transport_max_error'] for c in rep['cases']],width=w,label='All 45 pairs')
ax.bar(x,[c['pair_plus_68_projector_transport_max_error'] for c in rep['cases']],width=w,label='6–7,7–8,6–8 only')
ax.bar(x+w,[c['pair_only_projector_transport_max_error'] for c in rep['cases']],width=w,label='6–7,7–8 only')
ax.set_yscale('log');ax.set_xticks(x,labels);ax.set(xlabel='κ₀ kind / ramp duration',ylabel='Maximum projector transport error (Frobenius)',title='v18.49q — Full transport compared to truncated generators')
ax.grid(alpha=.2,axis='y');ax.legend();fig.tight_layout()
fig.savefig(ROOT/'results/full_vs_truncated_transport.png',dpi=170);plt.close(fig)
print('four audited figures generated')
