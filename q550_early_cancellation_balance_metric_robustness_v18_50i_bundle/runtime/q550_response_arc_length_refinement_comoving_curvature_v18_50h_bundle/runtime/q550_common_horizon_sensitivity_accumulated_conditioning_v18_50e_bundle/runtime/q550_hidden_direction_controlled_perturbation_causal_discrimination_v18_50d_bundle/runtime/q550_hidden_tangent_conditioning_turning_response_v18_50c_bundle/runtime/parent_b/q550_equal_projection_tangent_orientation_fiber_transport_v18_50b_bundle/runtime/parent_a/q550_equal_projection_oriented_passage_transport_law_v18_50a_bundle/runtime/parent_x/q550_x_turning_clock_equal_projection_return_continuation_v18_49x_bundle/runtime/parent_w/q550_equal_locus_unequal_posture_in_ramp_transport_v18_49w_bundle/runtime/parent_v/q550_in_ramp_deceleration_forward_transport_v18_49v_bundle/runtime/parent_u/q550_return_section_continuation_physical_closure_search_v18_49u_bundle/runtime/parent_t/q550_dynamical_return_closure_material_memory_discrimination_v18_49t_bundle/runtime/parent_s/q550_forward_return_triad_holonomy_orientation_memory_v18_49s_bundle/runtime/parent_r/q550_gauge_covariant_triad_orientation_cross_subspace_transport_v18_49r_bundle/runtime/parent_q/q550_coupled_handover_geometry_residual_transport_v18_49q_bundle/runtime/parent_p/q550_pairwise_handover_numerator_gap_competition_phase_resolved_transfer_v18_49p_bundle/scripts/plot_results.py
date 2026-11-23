#!/usr/bin/env python3
"""Generate reproducible plots from v18.49p measured CSVs and report."""
from pathlib import Path
import csv,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]
read=lambda p:list(csv.DictReader((R/'results'/p).open(newline='')))
rows=read('phase_resolved_pair_67_vs_78.csv');pairs=read('numerator_gap_pair_traces.csv')
rep=json.loads((R/'results/report.json').read_text())
for kind in rep['kappa_kinds']:
    chosen=[r for r in rows if r['kappa_kind']==kind and abs(float(r['ramp_xi'])-.327375)<1e-10]
    if not chosen:continue
    q=np.array([float(x['phase_q']) for x in chosen]);s67=np.array([float(x['share_67']) for x in chosen]);s78=np.array([float(x['share_78']) for x in chosen])
    fig,ax=plt.subplots(figsize=(9.0,5.0))
    ax.plot(q,s67,label='6–7 pair share',lw=2)
    ax.plot(q,s78,label='7–8 pair share',lw=2)
    ev=[e for e in rep['phase_crossing_events'] if e['kappa_kind']==kind and abs(e['ramp_xi']-.327375)<1e-10]
    for e in ev:ax.axvline(e['phase_q_root'],ls='--',alpha=.6,label=f"Leading-pair equality q={e['phase_q_root']:.9f}")
    ax.set(xlabel='Registered return phase q',ylabel='Share of total squared projector generator',title=f'Q550 v18.49p — 6–7 → 7–8 handover ({kind}, r=0.327375)')
    ax.grid(alpha=.2);ax.legend();fig.tight_layout()
    fig.savefig(R/'results'/f'handover_pair_shares_{kind}.png',dpi=175)
    plt.close(fig)

    chosen=[r for r in rows if r['kappa_kind']==kind and abs(float(r['ramp_xi'])-.327375)<1e-10]
    q=np.array([float(x['phase_q']) for x in chosen]);N=np.array([float(x['log_numerator_ratio_term']) for x in chosen]);G=np.array([float(x['log_inverse_gap_ratio_term']) for x in chosen]);T=np.array([float(x['log_power_ratio_78_over_67']) for x in chosen])
    fig,ax=plt.subplots(figsize=(9.0,5.0))
    ax.plot(q,T,label='log(A78/A67) = numerator + inverse-gap terms',lw=2)
    ax.plot(q,N,label='2 log(N78/N67)',lw=1.7)
    ax.plot(q,G,label='−2 log(g78/g67)',lw=1.7)
    ax.axhline(0,ls=':',color='gray')
    ax.set(xlabel='Registered return phase q',ylabel='Log ratio / log component',title=f'Q550 v18.49p — instantaneous algebraic balance ({kind})')
    ax.grid(alpha=.2);ax.legend();fig.tight_layout()
    fig.savefig(R/'results'/f'numerator_vs_gap_log_ledger_{kind}.png',dpi=175)
    plt.close(fig)

fig,ax=plt.subplots(figsize=(9,5))
for kind in rep['kappa_kinds']:
    ev=sorted([e for e in rep['phase_crossing_events'] if e['kappa_kind']==kind],key=lambda e:e['ramp_xi'])
    if ev:ax.plot([e['ramp_xi'] for e in ev],[e['phase_q_root'] for e in ev],'o-',label=kind)
ax.set(xlabel='Ramp duration r',ylabel='Numerical handover phase q',title='Q550 v18.49p — handover location along the ramp continuation')
ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(R/'results/handover_phase_vs_duration.png',dpi=175);plt.close(fig)
print('Wrote v18.49p measured plots')
