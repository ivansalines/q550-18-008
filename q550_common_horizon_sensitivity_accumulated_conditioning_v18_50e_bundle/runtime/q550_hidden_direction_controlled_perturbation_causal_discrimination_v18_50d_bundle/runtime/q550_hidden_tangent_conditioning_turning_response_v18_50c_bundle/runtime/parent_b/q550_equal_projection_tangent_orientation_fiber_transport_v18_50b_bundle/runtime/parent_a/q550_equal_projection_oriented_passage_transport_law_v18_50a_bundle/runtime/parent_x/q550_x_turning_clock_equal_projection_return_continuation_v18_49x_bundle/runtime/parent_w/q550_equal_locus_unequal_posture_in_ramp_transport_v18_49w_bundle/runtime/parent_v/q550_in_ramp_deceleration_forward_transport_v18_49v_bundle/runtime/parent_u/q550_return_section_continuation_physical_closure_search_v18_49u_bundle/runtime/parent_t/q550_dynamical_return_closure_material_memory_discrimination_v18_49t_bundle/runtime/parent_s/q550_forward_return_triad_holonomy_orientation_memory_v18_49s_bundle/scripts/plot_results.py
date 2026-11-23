#!/usr/bin/env python3
"""Plot actual measured v18.49s loops and null roundtrip controls."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]; d=ROOT/'results'
def read(n):
    p=d/n
    with p.open(newline='') as f:return list(csv.DictReader(f))
rows=read('two_path_canonical_connector_holonomy.csv')
fig,ax=plt.subplots(figsize=(10,5.2))
selected=[r for r in rows if r['window']=='full']
labels=[r['leg_b'].replace('original:','orig r=').replace('autonomous:','auto r=') for r in selected]
ax.bar(range(len(selected)),[float(r['loop_holonomy_angle_deg']) for r in selected])
ax.set_xticks(range(len(selected)),labels,rotation=18,ha='right')
ax.set_ylabel('Canonical two-path SO(3) angle [degrees]')
ax.set_title('Q550 v18.49s — Geometric two-path holonomy\n(closure-dependent; not material memory)')
ax.grid(axis='y',alpha=.25);fig.tight_layout();fig.savefig(d/'two_path_holonomy_angles.png',dpi=165);plt.close(fig)
fig,ax=plt.subplots(figsize=(8.5,5))
for name in sorted({r['leg_b'] for r in rows}):
    xs=[];ys=[]
    for r in rows:
        if r['leg_b']==name:
            xs.append({'early':0,'late':1,'full':2}[r['window']]);ys.append(float(r['loop_holonomy_angle_deg']))
    ax.plot(xs,ys,'o-',label=name)
ax.set_xticks([0,1,2],['Early .630–.645','Late .635–.650','Full .630–.650'])
ax.set_ylabel('Closed-loop angle [degrees]');ax.set_title('Window dependence of two-path holonomy')
ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(d/'phase_window_holonomy.png',dpi=165);plt.close(fig)
ctrl=read('forward_reverse_null_controls.csv')
fig,ax=plt.subplots(figsize=(8,4.8))
ax.bar(range(len(ctrl)),[float(x['self_reversed_10D_norm_error']) for x in ctrl])
ax.set_xticks(range(len(ctrl)),[x['kappa_kind']+' '+x['ramp_xi'] for x in ctrl],rotation=30,ha='right')
ax.set_ylabel('||U_reverse U_forward - I||_F')
ax.set_title('Null control: exact same-path reversal');ax.set_yscale('symlog',linthresh=1e-16)
ax.grid(axis='y',alpha=.25);fig.tight_layout();fig.savefig(d/'same_path_reverse_null_control.png',dpi=165);plt.close(fig)
