"""Noncausal, direct visualization of measured v18.49u duration/section metrics."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'results'
with (out/'duration_continuation.csv').open() as f:rows=list(csv.DictReader(f))
fig,ax=plt.subplots(figsize=(9,5.3))
for k in sorted({r['kappa_kind'] for r in rows}):
 s=sorted((float(r['ramp_xi']),float(r['min_joint_full_state'])) for r in rows if r['kappa_kind']==k)
 ax.plot([x[0] for x in s],[x[1] for x in s],'.-',label=k)
ax.set(xlabel='Return ramp duration r',ylabel='Minimum full reversed-state gap',
 title='Q550 v18.49u — Dynamical return closure search')
ax.grid(alpha=.3);ax.legend();fig.tight_layout();fig.savefig(out/'continuation_joint_gap.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5.3))
for k in sorted({r['kappa_kind'] for r in rows}):
 s=sorted((float(r['ramp_xi']),float(r['min_config']),float(r['min_velocity'])) for r in rows if r['kappa_kind']==k)
 ax.plot([x[0] for x in s],[x[1] for x in s],'.-',label=k+' (min config)')
 ax.plot([x[0] for x in s],[x[2] for x in s],'.--',label=k+' (min reversed velocity)')
ax.set(xlabel='Return ramp duration r',ylabel='Separately optimized coordinate gap',
 title='Q550 v18.49u — Location and orientation-velocity gates')
ax.grid(alpha=.3);ax.legend();fig.tight_layout();fig.savefig(out/'separate_closure_gates.png',dpi=160)
