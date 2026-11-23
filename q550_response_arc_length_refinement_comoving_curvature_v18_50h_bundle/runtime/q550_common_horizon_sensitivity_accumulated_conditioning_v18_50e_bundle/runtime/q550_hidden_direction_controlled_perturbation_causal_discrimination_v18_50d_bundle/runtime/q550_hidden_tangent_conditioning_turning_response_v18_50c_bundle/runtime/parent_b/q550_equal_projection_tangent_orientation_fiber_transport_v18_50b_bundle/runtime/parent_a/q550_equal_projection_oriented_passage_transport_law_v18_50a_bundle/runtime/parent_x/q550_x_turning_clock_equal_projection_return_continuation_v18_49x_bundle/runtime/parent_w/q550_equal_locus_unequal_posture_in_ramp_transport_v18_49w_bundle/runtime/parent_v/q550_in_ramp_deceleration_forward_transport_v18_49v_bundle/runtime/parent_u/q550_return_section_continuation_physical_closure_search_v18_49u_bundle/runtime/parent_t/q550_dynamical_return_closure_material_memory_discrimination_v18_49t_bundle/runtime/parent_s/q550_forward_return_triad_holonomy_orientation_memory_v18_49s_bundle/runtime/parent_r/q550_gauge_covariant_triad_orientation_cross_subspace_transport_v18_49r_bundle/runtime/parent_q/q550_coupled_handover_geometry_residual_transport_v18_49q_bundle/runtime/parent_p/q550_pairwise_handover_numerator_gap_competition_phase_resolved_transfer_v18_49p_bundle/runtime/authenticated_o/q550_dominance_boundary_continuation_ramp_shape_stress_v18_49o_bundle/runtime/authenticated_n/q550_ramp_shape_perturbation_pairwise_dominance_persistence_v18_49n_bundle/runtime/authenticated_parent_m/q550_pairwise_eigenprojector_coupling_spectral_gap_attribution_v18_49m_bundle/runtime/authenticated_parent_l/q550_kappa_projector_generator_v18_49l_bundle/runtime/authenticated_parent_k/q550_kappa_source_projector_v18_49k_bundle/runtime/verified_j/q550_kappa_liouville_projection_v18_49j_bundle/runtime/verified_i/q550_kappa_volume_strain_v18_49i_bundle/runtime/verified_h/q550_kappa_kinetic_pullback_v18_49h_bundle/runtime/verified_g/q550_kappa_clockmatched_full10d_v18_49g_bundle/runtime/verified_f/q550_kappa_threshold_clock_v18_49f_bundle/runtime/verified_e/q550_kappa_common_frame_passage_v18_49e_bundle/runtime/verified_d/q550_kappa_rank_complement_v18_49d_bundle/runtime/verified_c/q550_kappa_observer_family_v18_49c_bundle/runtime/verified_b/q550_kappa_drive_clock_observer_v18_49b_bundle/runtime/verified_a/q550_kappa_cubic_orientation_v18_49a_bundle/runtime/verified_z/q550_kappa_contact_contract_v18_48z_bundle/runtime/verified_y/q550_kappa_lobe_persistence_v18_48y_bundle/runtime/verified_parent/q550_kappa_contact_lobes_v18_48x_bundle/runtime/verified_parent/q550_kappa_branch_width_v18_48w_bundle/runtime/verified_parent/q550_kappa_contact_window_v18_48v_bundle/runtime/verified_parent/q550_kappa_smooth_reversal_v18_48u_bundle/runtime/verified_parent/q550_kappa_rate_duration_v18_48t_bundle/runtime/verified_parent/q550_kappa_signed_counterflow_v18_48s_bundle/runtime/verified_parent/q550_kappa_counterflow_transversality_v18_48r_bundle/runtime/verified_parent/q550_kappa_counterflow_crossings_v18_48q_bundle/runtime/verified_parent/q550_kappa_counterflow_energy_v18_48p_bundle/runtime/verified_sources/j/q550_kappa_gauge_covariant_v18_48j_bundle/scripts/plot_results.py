"""Generate deterministic observational plots (not generative illustrations)."""
from __future__ import annotations
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'results'
def read(n):
 with (out/n).open() as f:return list(csv.DictReader(f))
rows=read('gauge_invariance.csv')
for stem,xi in [('phaseblind',3.575),('phasecov',4.25)]:
 sub=[r for r in rows if r['family'].startswith(stem) and int(r['seed_branch'])==0 and r['kappa_kind']=='original' and r['observer']=='historical_transport' and abs(float(r['xi'])-xi)<1e-8]
 if len(sub)!=4:raise RuntimeError('missing gauge crest '+stem)
 order=['identity','fixed_rotation','comoving_rotation','anisotropic_shear']
 exact=[float(next(r['cancellation_metric_covariant'] for r in sub if r['gauge']==g)) for g in order]
 naive=[float(next(r['cancellation_naive_new_euclidean'] for r in sub if r['gauge']==g)) for g in order]
 fig,ax=plt.subplots(figsize=(8,4.6))
 x=range(len(order));ax.plot(x,exact,'o-',label='Covariant cometric norm');ax.plot(x,naive,'s--',label='Naive Euclidean norm')
 ax.set_xticks(list(x),['identity','fixed rotation','co-moving','anisotropic shear'],rotation=12)
 ax.set_ylabel('Projected cancellation ratio')
 ax.set_title(f'Q550 {stem} branch 0, xi={xi:g} — original kappa')
 ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(out/f'{stem}_gauge_vs_naive.png',dpi=160);plt.close(fig)
rows=read('observer_change_negative_control.csv')
for stem in ('phaseblind','phasecov'):
 sub=[r for r in rows if r['family'].startswith(stem) and r['kappa_kind']=='original' and int(r['seed_branch'])==0 and ((stem=='phaseblind' and abs(float(r['xi'])-3.575)<1e-9) or (stem=='phasecov' and abs(float(r['xi'])-4.25)<1e-9))]
 if sub:
  x=sub[0];print(stem,'crest',x['original_ratio'],'physical observer perturbation',x['changed_physical_observer_ratio'])
