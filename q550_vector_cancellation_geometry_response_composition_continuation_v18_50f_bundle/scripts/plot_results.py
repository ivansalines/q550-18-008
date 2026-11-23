"""Rebuild all v18.50f figures from the auditable output CSVs."""
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plot(rows,endpoints,out):
  d=[x for x in rows if x['kind']=='original' and x['mode']=='same_seed' and abs(float(x['ramp_xi'])-.24)<1e-8 and x['shape']=='beta:2:2']
  d.sort(key=lambda x:x['horizon_xi']);h=[x['horizon_xi'] for x in d]
  fig,ax=plt.subplots(figsize=(8.5,5.1))
  for key,label in [('local_norm','Local L'),('transported_norm','Transported T'),('resultant_norm','Resultant L + T')]:
    ax.plot(h,[x[key] for x in d],marker='o',label=label)
  ax.set(xlabel='Common evolution horizon Δξ',ylabel='4D direction-response norm',title='How the endpoint response is composed (r=0.24, original κ₀)')
  ax.legend();fig.tight_layout();fig.savefig(out/'reference_response_composition.png',dpi=155);plt.close(fig)
  fig,axs=plt.subplots(1,2,figsize=(11,4.7))
  for r in sorted(set(float(x['ramp_xi']) for x in rows)):
    x=sorted([z for z in rows if z['kind']=='original' and z['mode']=='same_seed' and abs(float(z['ramp_xi'])-r)<1e-8 and z['shape']=='beta:2:2'],key=lambda z:z['horizon_xi'])
    axs[0].plot([z['horizon_xi'] for z in x[1:]],[float(z['alignment_cos']) for z in x[1:]],marker='o',label=f'r={r:g}')
    axs[1].plot([z['horizon_xi'] for z in x],[float(z['cancellation_fraction']) for z in x],marker='o',label=f'r={r:g}')
  axs[0].set(xlabel='Δξ',ylabel='cosine(L,T)',title='Opposition grows')
  axs[1].set(xlabel='Δξ',ylabel='Fraction of sum of norms cancelled',title='Relative cancellation can shrink')
  for a in axs:a.legend(fontsize=8)
  fig.tight_layout();fig.savefig(out/'opposition_vs_cancellation.png',dpi=155);plt.close(fig)
  fig,ax=plt.subplots(figsize=(8.5,5.1))
  for mode in ['natural_turn','same_seed']:
    x=sorted([v for v in endpoints if v['mode']==mode and v['kind']=='original' and v['shape']=='beta:2:2'],key=lambda v:v['ramp_xi'])
    ax.plot([v['ramp_xi'] for v in x],[v['cancellation_fraction'] for v in x],marker='o',label=mode)
  ax.set(xlabel='Ramp duration r',ylabel='Endpoint cancellation fraction',title='Two starting-state protocols, identical horizon Δξ=0.05')
  ax.legend();fig.tight_layout();fig.savefig(out/'natural_vs_common_seed_cancellation.png',dpi=155);plt.close(fig)
  fig,ax=plt.subplots(figsize=(8.5,5.1))
  for kind in ['original','autonomous']:
    x=sorted([v for v in endpoints if v['mode']=='same_seed' and v['kind']==kind and v['shape']=='beta:2:2'],key=lambda v:v['ramp_xi'])
    ax.plot([v['ramp_xi'] for v in x],[v['alignment_angle_deg'] for v in x],marker='o',label=f'{kind} κ₀')
  ax.set(xlabel='Ramp duration r',ylabel='Angle(L,T) [deg]',title='Response-sector orientation vs ramp duration')
  ax.legend();fig.tight_layout();fig.savefig(out/'orientation_vs_duration.png',dpi=155);plt.close(fig)
