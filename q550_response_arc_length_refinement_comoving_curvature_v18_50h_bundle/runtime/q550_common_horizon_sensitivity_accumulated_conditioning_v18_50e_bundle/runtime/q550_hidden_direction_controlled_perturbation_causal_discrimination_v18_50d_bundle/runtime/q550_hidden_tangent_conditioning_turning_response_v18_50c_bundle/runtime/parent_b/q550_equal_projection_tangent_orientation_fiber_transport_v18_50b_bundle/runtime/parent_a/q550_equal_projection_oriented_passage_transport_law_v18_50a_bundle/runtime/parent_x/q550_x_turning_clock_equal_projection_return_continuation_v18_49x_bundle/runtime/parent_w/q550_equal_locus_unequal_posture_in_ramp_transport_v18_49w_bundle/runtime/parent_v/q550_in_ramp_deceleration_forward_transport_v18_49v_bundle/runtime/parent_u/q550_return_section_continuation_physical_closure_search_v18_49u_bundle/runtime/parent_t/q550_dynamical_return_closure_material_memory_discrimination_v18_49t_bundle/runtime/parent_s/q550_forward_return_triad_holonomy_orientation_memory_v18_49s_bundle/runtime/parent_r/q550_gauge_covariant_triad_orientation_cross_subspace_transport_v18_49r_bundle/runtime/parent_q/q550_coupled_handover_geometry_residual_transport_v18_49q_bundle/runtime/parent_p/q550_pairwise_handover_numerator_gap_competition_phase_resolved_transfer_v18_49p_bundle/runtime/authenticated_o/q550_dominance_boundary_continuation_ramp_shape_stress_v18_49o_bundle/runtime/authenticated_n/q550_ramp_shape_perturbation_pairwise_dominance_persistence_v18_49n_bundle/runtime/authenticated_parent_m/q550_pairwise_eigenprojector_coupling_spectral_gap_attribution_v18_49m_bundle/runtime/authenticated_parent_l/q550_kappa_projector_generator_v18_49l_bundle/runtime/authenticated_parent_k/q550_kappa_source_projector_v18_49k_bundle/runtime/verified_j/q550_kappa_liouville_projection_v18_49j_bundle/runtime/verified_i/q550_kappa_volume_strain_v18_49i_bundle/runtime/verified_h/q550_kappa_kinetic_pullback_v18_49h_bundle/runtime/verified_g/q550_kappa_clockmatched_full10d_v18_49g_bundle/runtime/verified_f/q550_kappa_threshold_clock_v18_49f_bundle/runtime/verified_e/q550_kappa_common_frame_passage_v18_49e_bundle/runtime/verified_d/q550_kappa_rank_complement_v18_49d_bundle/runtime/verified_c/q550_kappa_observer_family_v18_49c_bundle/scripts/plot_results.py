#!/usr/bin/env python3
"""Make figures only from computed v18.49c CSV, never synthetic data."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'results'
with (R/'observer_family_envelopes.csv').open(newline='') as f:rows=list(csv.DictReader(f))
main=[r for r in rows if r['root_position']=='barrier' and float(r['delta_B_minus_threshold'])==1e-5]
fig,ax=plt.subplots(figsize=(9.3,5.5))
for kind in ('original','autonomous'):
 for sz in (2,5):
  r=sorted([a for a in main if a['kappa_kind']==kind and a['metric']=='euclidean' and int(a['family_size'])==sz],key=lambda z:float(z['ramp_xi']))
  ax.plot([float(x['ramp_xi']) for x in r],[100*float(x['fraction_explained']) for x in r],marker='o',label=f'{kind} / {sz} observers')
ax.set(xlabel='Smooth reversal duration [xi]',ylabel='Envelope / material 10D distance [%]',title='Q550 v18.49c: observer-family captured fraction (declared Euclidean chart metric)')
ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(R/'observer_family_fraction.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(9.2,5.2))
for sz in (2,5):
 r=sorted([a for a in main if a['kappa_kind']=='original' and a['metric']=='euclidean' and int(a['family_size'])==sz],key=lambda z:float(z['ramp_xi']))
 ax.plot([float(x['ramp_xi']) for x in r],[float(x['envelope_abs_max']) for x in r],marker='o',label=f'{sz}D family envelope')
r=sorted([a for a in main if a['kappa_kind']=='original' and a['metric']=='euclidean' and int(a['family_size'])==5],key=lambda z:float(z['ramp_xi']))
ax.plot([float(x['ramp_xi']) for x in r],[float(x['material_distance_metric']) for x in r],ls='--',label='Full 10D material distance')
ax.plot([float(x['ramp_xi']) for x in r],[float(x['orthogonal_material_residual']) for x in r],ls=':',label='Undetected residual (5D family)')
ax.set(xlabel='Smooth reversal duration [xi]',ylabel='Metric amplitude [declared chart units]',title='Q550: family envelope versus full finite material-state displacement')
ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(R/'envelope_and_material_residual.png',dpi=180);plt.close(fig)
with (R/'transported_family_duality.csv').open(newline='') as f:dual=list(csv.DictReader(f))
fig,ax=plt.subplots(figsize=(9.2,4.7))
for kind in ('original','autonomous'):
 rr=[x for x in dual if x['kappa_kind']==kind]
 times=sorted({float(x['elapsed_xi']) for x in rr})
 maxres=[max(float(x['max_seed_pairing_relative_residual']) for x in rr if abs(float(x['elapsed_xi'])-t)<1e-12) for t in times]
 ax.semilogy(times,np.maximum(maxres,1e-18),marker='.',label=kind)
ax.set(xlabel='Time after velocity reversal [xi]',ylabel='Normalized adjoint-tangent duality residual',title='Five-covector transported-family duality regression')
ax.legend();ax.grid(alpha=.3);fig.tight_layout();fig.savefig(R/'family_duality_residual.png',dpi=180);plt.close(fig)
print('Generated three data-derived figures')
