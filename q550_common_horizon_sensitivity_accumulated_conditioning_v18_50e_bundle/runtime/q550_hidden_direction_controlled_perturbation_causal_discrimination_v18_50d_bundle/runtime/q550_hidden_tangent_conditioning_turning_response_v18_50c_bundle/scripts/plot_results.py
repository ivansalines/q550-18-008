#!/usr/bin/env python3
"""Reproducible v18.50c figures from CSV measurements; no new dynamical integration."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
def rows(name):
 with (OUT/name).open() as f:return list(csv.DictReader(f))

def main():
 data=rows('hidden_tangent_phase_trace.csv');stats=rows('turning_clock_hidden_response.csv');pairs=rows('equal_x_pair_hidden_orientation.csv')
 fig,ax=plt.subplots(figsize=(9.2,5.3))
 for r in sorted({float(v['ramp_xi']) for v in data if v['kind']=='original' and v['shape']=='beta:2:2'}):
  vs=[z for z in data if z['kind']=='original' and z['shape']=='beta:2:2' and abs(float(z['ramp_xi'])-r)<1e-9]
  vs=sorted(vs,key=lambda x:float(x['xi']))
  line,=ax.plot([float(v['xi']) for v in vs],[float(v['hidden_dir_turn_rate']) for v in vs],label=f'Ramp r={r:g}')
  turn=float(vs[0]['turn_xi']);rate=float(np.interp(turn,[float(v['xi']) for v in vs],[float(v['hidden_dir_turn_rate']) for v in vs]))
  ax.plot(turn,rate,'o',color=line.get_color(),ms=6)
 ax.set(xlabel=r'Evolution coordinate $\xi$',ylabel=r'Hidden-direction turning rate $\|d\hat h\prime/d\xi\|$',
        title='Direction continues to bend across the x-turn')
 ax.grid(alpha=.25);ax.legend(fontsize=9)
 fig.tight_layout();fig.savefig(OUT/'hidden_direction_turning_rate.png',dpi=180);plt.close(fig)

 fig,ax=plt.subplots(figsize=(9,5.2))
 for (kind,shape) in sorted(set((v['kind'],v['shape']) for v in stats)):
  if any(v['metric']!='common' for v in stats): pass
  vs=sorted([v for v in stats if v['kind']==kind and v['shape']==shape and v['metric']=='common'],key=lambda v:float(v['ramp_xi']))
  if not vs:continue
  ax.plot([float(v['ramp_xi']) for v in vs],[float(v['hidden_direction_change_across_turn_deg']) for v in vs],'-o',label=f'{kind}, {shape}')
 ax.set(xlabel='Ramp duration r',ylabel='Hidden direction deflection across measured turning (degrees)',
        title='Event-centered directional change in a shared metric')
 ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout()
 fig.savefig(OUT/'turning_deflection_by_ramp.png',dpi=180);plt.close(fig)

 fig,ax=plt.subplots(figsize=(9.2,5.2))
 a=[z for z in stats if z['kind']=='original' and z['metric']=='common']
 for v in a:
  x=float(v['turn_xi']);y=float(v['peak_minus_x_turn_xi']);edge=v['local_peak_boundary_flag']=='True'
  ax.scatter(x,y,s=80,marker='x' if edge else 'o',label=f"r={float(v['ramp_xi']):g}, {v['shape']}")
 ax.axhline(0,color='gray',lw=1,ls='--')
 ax.set(xlabel=r'Measured x-turn coordinate $\xi_*$',ylabel=r'Windowed peak lag $\xi_{peak}-\xi_*$',
        title='Peak lag is not a universal turning clock (x = window-boundary result)')
 ax.grid(alpha=.25);ax.legend(fontsize=8,loc='best');fig.tight_layout()
 fig.savefig(OUT/'peak_lag_window_boundary.png',dpi=180);plt.close(fig)

 fig,ax=plt.subplots(figsize=(8.7,5.1))
 for kind in ('original','autonomous'):
  v=[p for p in pairs if p['kind']==kind]
  ax.scatter([float(p['delta_xi']) for p in v],[float(p['hidden_angle_deg_common']) for p in v],label=kind,alpha=.8)
 ax.set(xlabel=r'Time separation of equal-x passages, $\Delta\xi$',ylabel='Hidden 4D tangent angle (degrees)',
        title='Equal projection, distinct hidden tangent directions')
 ax.grid(alpha=.25);ax.legend();fig.tight_layout()
 fig.savefig(OUT/'equal_x_hidden_orientation_common_metric.png',dpi=180);plt.close(fig)

 fig,ax=plt.subplots(figsize=(8.8,5.2))
 for m in ('common','native','theta_half','theta_double'):
  v=[s for s in stats if s['kind']=='original' and s['shape']=='beta:2:2' and s['metric']==m]
  ax.plot([float(s['ramp_xi']) for s in v],[float(s['hidden_direction_change_across_turn_deg']) for s in v],'-o',label=m)
 ax.set(xlabel='Ramp duration r',ylabel='Event-centered deflection (degrees)',
        title='Absolute angles depend on the declared state-space metric')
 ax.grid(alpha=.25);ax.legend();fig.tight_layout()
 fig.savefig(OUT/'direction_metric_sensitivity.png',dpi=180);plt.close(fig)
 print('Generated 5 figures.')
if __name__=='__main__':main()
