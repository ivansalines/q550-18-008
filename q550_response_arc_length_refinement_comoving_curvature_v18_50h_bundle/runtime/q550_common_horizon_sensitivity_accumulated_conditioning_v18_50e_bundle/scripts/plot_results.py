#!/usr/bin/env python3
"""Plots from actually integrated v18.50e response CSV; no synthetic interpolation."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'results/common_horizon_direction_responses.csv').open() as f: rows=list(csv.DictReader(f))
for r in rows:
    for k in ('ramp_xi','horizon_xi','gain','frozen_endpoint_x_gain','transported_component_gain','relative_residual_linearized_vs_IVP'):
        r[k]=float(r[k])

fig,ax=plt.subplots(figsize=(9,5.5),layout='constrained')
for kind in ('original','autonomous'):
  for mode in ('natural_turn','same_seed'):
    q=sorted((r for r in rows if r['kind']==kind and r['mode']==mode and r['shape']=='beta:2:2' and abs(r['horizon_xi']-.05)<1e-12),key=lambda x:x['ramp_xi'])
    ax.plot([r['ramp_xi'] for r in q],[r['gain'] for r in q],marker='o',label=f'{kind} · {mode.replace("_"," ")}')
ax.set(xlabel='Ramp duration r (xi)',ylabel='Final hidden-direction sensitivity gain',title='Same elapsed horizon: natural turning vs same physical seed')
ax.grid(alpha=.3);ax.legend(fontsize=9)
fig.savefig(ROOT/'results/common_horizon_gain_comparison.png',dpi=170);plt.close(fig)

fig,ax=plt.subplots(figsize=(9,5.5),layout='constrained')
for r in [0.18,0.24,0.327375,0.5]:
    q=sorted((v for v in rows if v['kind']=='original' and v['mode']=='same_seed' and v['shape']=='beta:2:2' and abs(v['ramp_xi']-r)<1e-9),key=lambda x:x['horizon_xi'])
    ax.plot([v['horizon_xi'] for v in q],[v['gain'] for v in q],marker='o',label=f'r = {r}')
ax.set(xlabel='Elapsed evolution after intervention Δξ',ylabel='Gain ∥∂ε ûh∥',title='Accumulation along a common horizon from one shared Q550 seed')
ax.grid(alpha=.3);ax.legend()
fig.savefig(ROOT/'results/accumulation_over_common_horizon.png',dpi=170);plt.close(fig)

fig,ax=plt.subplots(figsize=(9,5.5),layout='constrained')
q=sorted((v for v in rows if v['kind']=='original' and v['mode']=='same_seed' and v['shape']=='beta:2:2' and abs(v['ramp_xi']-.24)<1e-9),key=lambda x:x['horizon_xi'])
ax.plot([v['horizon_xi'] for v in q],[v['gain'] for v in q],'-o',label='Total response after dynamics')
ax.plot([v['horizon_xi'] for v in q],[v['frozen_endpoint_x_gain'] for v in q],'-o',label='Frozen-endpoint direct-x component')
ax.plot([v['horizon_xi'] for v in q],[v['transported_component_gain'] for v in q],'-o',label='Transported component magnitude')
ax.set(xlabel='Elapsed evolution Δξ',ylabel='Norm in fixed normalized hidden-direction chart',title='Linear-response ledger — magnitudes do not add (vectors partly cancel)')
ax.grid(alpha=.3);ax.legend()
fig.savefig(ROOT/'results/local_vs_transported_direction_response.png',dpi=170);plt.close(fig)

fig,ax=plt.subplots(figsize=(9,5.5),layout='constrained')
for mode in ('natural_turn','same_seed'):
  q=sorted((v for v in rows if v['kind']=='original' and v['mode']==mode and abs(v['ramp_xi']-.24)<1e-9 and abs(v['horizon_xi']-.05)<1e-9),key=lambda x:x['shape'])
  ax.bar([f'{mode.replace("_"," ")}\n{v["shape"]}' for v in q],[v['gain'] for v in q],alpha=.75)
ax.set(ylabel='Final directional gain',title='Cubic vs quintic: effect of controlling the turning seed')
ax.grid(axis='y',alpha=.3)
fig.savefig(ROOT/'results/ramp_shape_same_seed_control.png',dpi=170);plt.close(fig)
print('plots generated')
