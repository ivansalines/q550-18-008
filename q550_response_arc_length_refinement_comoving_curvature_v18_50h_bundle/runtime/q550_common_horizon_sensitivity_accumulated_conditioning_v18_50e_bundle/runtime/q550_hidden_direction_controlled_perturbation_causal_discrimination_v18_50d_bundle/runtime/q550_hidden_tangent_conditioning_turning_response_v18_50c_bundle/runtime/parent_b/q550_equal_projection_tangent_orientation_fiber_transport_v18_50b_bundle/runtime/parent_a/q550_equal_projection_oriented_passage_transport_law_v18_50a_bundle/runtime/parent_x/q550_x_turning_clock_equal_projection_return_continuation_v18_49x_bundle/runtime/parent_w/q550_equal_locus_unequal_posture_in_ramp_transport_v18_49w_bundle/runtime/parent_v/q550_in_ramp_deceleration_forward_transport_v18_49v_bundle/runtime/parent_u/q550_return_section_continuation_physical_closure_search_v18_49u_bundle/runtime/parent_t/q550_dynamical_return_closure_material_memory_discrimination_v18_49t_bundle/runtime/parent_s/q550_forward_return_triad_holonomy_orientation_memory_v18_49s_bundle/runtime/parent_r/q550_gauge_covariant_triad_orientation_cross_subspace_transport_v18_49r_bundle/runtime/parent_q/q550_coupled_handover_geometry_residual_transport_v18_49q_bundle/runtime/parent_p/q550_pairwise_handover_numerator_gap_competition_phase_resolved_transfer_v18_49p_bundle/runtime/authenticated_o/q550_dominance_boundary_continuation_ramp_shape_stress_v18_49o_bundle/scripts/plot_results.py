#!/usr/bin/env python3
"""Plot only measured Q550 solver output; no smoothed/imaginary boundary curves."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];p=R/'results'
with (p/'case_surveys.csv').open() as f:rows=list(csv.DictReader(f))
fig,ax=plt.subplots(figsize=(9,5))
for kind in sorted({x['kappa_kind'] for x in rows}):
    rr=sorted([x for x in rows if x['shape']=='beta:2:2' and x['stage']=='duration_survey' and x['kappa_kind']==kind],key=lambda x:float(x['ramp_xi']))
    if rr:ax.plot([float(x['ramp_xi']) for x in rr],[float(x['margin_at_q065']) for x in rr],'.-',label=kind)
ax.axhline(0,color='gray',linestyle='--',linewidth=1)
ax.axvline(.3,color='gray',linestyle=':',linewidth=1)
ax.set(xlabel='Physical ramp duration r',ylabel='6–7 margin over strongest other pair at q=0.65',title='Q550 v18.49o — sampled duration-boundary scout')
ax.legend();fig.tight_layout();fig.savefig(p/'duration_boundary_scout.png',dpi=155);plt.close(fig)
fig,ax=plt.subplots(figsize=(11,5))
rr=[x for x in rows if x['stage']=='shape_stress' and x['kappa_kind']=='original' and abs(float(x['ramp_xi'])-.3)<1e-12]
if rr:
    ax.bar(range(len(rr)),[float(x['margin_at_q065']) for x in rr]);ax.set_xticks(range(len(rr)),[x['shape'] for x in rr],rotation=55,ha='right')
ax.axhline(0,color='gray',linestyle='--',linewidth=1)
ax.set(ylabel='6–7 margin at q=0.65',title='Q550 v18.49o — fixed-duration equal-phase-area shape stress')
fig.tight_layout();fig.savefig(p/'shape_stress_endpoint_margin.png',dpi=155);plt.close(fig)
print('Wrote 2 measured v18.49o figures')
