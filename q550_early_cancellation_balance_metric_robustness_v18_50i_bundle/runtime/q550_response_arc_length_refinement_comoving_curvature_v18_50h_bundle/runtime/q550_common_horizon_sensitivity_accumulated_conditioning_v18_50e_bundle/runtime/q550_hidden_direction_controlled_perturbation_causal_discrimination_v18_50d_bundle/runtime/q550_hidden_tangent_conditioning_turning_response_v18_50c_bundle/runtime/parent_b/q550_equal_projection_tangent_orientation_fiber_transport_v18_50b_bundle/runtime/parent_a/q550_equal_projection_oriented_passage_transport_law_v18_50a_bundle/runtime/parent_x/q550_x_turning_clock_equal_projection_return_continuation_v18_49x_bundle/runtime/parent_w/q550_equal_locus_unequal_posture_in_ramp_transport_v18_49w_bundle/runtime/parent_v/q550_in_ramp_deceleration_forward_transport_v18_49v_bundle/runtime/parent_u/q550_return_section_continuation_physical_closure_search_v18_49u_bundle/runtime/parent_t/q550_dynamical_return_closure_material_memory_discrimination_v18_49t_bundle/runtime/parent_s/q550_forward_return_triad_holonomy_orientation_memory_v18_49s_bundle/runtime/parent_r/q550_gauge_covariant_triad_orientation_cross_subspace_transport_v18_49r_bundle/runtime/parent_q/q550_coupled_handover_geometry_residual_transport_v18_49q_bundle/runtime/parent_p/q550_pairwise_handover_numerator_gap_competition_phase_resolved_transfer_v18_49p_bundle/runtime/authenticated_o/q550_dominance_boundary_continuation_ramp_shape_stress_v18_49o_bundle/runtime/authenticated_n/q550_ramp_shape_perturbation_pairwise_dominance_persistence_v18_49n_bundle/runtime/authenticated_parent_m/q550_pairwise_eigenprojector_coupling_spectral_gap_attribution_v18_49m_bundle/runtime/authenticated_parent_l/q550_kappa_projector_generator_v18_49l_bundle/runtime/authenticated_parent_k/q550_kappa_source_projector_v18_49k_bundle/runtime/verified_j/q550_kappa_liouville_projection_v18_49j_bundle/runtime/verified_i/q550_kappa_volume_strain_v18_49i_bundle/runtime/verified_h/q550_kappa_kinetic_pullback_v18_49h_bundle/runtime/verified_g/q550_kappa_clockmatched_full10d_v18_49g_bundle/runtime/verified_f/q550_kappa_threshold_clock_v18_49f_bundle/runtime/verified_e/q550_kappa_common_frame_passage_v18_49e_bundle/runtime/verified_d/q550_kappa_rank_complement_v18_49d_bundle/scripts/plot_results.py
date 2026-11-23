"""Visualizations from numerical CSV outputs only; no synthetic data."""
from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results'
def read(name):
 with (R/name).open() as f:return list(csv.DictReader(f))
rows=read('rank_and_hidden_complement.csv')
phases=sorted(set(float(x['phase_q']) for x in rows))
fig,ax=plt.subplots(figsize=(9,5.5))
for tol in [1e-4,1e-6,1e-8,1e-10,1e-12]:
 subset=sorted([r for r in rows if r['kappa_kind']=='original' and abs(float(r['ramp_xi'])-.296333)<1e-7 and r['metric']=='euclidean' and int(r['family_size'])==5 and abs(float(r['rank_tolerance'])-tol)<tol*1e-5],key=lambda r:float(r['phase_q']))
 ax.plot([float(r['phase_q']) for r in subset],[float(r['hidden_complement_norm']) for r in subset],label=f'tol={tol:g}',marker='.',lw=1)
ax.set(xlabel='Common drive phase q',ylabel='Metric-orthogonal hidden residual (10D)',title='v18.49d: Rank-threshold dependence of the five-observer complement')
ax.grid(alpha=.2);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(R/'threshold_hidden_complement.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5.5))
for n in [2,5,6,8,10]:
 sub=sorted([r for r in rows if r['kappa_kind']=='original' and abs(float(r['ramp_xi'])-.296333)<1e-7 and r['metric']=='euclidean' and int(r['family_size'])==n and float(r['rank_tolerance'])==1e-10],key=lambda r:float(r['phase_q']))
 ax.plot([float(r['phase_q']) for r in sub],[float(r['fraction_explained']) for r in sub],label=f'{n} covectors',lw=1.6)
ax.set(xlabel='Common drive phase q',ylabel='Observed fraction A/D',ylim=(0,1.04),title='v18.49d: Nested historical + explicitly synthetic observer families')
ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(R/'family_extension_fraction.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5.5))
data=read('within_return_projector_transport.csv')
for tol in [1e-6,1e-10,1e-12]:
 sub=sorted([r for r in data if r['kappa_kind']=='original' and abs(float(r['ramp_xi'])-.296333)<1e-7 and r['metric']=='euclidean' and int(r['family_size'])==5 and float(r['rank_tolerance'])==tol],key=lambda r:float(r['phase_q1']))
 ax.plot([float(r['phase_q1']) for r in sub],[float(r['projector_frobenius_gap']) for r in sub],label=f'tol={tol:g}',marker='.',lw=1.1)
ax.set(xlabel='Phase q (end of comparison)',ylabel='Consecutive metric projector Frobenius gap',title='v18.49d: Local observer-space transport (chart-fixed diagnostics)')
ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(R/'projector_transport_rank_threshold.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(8.5,5))
rows4=read('kappa_scale_return_tests.csv')
for k in ['original','autonomous']:
 for span in ['kappa_length','literal_0p2_xi']:
  sub=[r for r in rows4 if r['kappa_kind']==k and r['metric']=='euclidean' and r['span_kind']==span]
  if not sub:continue
  ax.scatter([float(r['span_over_kappa']) for r in sub],[float(r['projector_frobenius_gap']) for r in sub],label=k+' / '+span,alpha=.75)
ax.set(xlabel='Compared span / kappa0',ylabel='Projector gap (not a physical cycle marker)',title='v18.49d: Exploratory 0.2 vs kappa-scale subspace recurrence check')
ax.grid(alpha=.2);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(R/'kappa_scale_recurrence_probe.png',dpi=180);plt.close(fig)
print('v18.49d: 4 CSV-backed plots created')
