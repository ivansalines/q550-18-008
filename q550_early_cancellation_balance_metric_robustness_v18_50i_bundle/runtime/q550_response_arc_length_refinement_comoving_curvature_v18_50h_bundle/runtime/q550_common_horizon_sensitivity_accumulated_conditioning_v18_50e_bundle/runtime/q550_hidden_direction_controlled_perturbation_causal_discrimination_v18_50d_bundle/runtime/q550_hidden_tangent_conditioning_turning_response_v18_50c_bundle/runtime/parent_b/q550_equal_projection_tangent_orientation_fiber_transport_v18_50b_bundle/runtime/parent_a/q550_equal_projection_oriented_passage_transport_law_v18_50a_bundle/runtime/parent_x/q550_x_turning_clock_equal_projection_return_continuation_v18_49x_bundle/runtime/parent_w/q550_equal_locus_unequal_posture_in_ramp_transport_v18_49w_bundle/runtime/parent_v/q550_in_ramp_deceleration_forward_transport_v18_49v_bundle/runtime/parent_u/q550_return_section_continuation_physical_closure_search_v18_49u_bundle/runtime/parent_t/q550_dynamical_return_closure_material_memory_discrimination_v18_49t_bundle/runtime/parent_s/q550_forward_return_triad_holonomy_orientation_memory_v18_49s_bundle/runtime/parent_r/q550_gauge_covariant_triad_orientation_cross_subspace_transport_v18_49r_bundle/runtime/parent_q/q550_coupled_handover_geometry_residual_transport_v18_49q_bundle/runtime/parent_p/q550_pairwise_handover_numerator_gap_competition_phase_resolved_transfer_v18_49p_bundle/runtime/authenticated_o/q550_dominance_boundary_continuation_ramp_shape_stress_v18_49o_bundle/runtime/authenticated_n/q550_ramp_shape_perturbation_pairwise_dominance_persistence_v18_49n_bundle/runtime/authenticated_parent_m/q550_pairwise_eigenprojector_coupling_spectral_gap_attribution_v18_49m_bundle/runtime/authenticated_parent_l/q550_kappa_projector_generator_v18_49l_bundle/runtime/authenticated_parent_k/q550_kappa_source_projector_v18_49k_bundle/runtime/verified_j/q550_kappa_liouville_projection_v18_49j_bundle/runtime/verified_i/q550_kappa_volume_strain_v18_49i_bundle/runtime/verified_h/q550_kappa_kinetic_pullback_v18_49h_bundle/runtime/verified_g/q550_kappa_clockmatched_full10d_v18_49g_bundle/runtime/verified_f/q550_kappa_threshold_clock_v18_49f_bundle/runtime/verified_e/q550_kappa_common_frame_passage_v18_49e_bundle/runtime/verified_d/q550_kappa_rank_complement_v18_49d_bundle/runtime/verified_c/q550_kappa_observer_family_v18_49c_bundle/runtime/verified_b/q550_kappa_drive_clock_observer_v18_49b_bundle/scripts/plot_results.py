#!/usr/bin/env python3
"""Render actual v18.49b transported-observer calculations, not synthetic curves."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
def load(file):
 with (OUT/file).open(newline='') as f:return list(csv.DictReader(f))
def main():
 points=load('observer_probe_at_physical_roots.csv')
 select=[r for r in points if r['root_position']=='barrier' and float(r['delta'])==1e-5 and int(r['observer_channel'])==0]
 fig,ax=plt.subplots(figsize=(9.5,5.2))
 for kind in ('original','autonomous'):
  rows=sorted((r for r in select if r['kappa_kind']==kind),key=lambda r:float(r['ramp_duration_xi']))
  x=[float(r['ramp_duration_xi']) for r in rows]
  ax.plot(x,[float(r['historical_at_turn_fixed_probe']) for r in rows],marker='o',label=f'{kind}: frozen covector')
  ax.plot(x,[float(r['genuinely_transported_probe']) for r in rows],marker='s',label=f'{kind}: transported covector')
 ax.axhline(0,lw=.8,color='grey');ax.set(xlabel='Ramp duration [xi]',ylabel='Signed covector pairing with finite state displacement',title='Q550 v18.49b: fixed versus genuinely transported observer')
 ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(OUT/'frozen_vs_transported_readout.png',dpi=175);plt.close(fig)
 fig,ax=plt.subplots(figsize=(9.2,4.7))
 for kind in ('original','autonomous'):
  rows=sorted((r for r in select if r['kappa_kind']==kind),key=lambda r:float(r['ramp_duration_xi']))
  ax.plot([float(r['ramp_duration_xi']) for r in rows],[float(r['observer_projective_angle_deg']) for r in rows],marker='o',label=kind)
 ax.set(xlabel='Ramp duration [xi]',ylabel='Projective angle between observer and its initial line [deg]',title='Observer rotation in the fixed material chart (not physical torsion)')
 ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(OUT/'observer_projective_rotation.png',dpi=175);plt.close(fig)
 dual=load('transport_duality.csv');fig,ax=plt.subplots(figsize=(9.2,4.7))
 for kind in ('original','autonomous'):
  rows=[r for r in dual if r['kappa_kind']==kind and int(r['channel'])==0]
  xs=sorted({float(r['elapsed_xi']) for r in rows})
  v=[max(float(r['relative_transport_pairing_residual']) for r in rows if abs(float(r['elapsed_xi'])-x)<1e-12) for x in xs]
  ax.semilogy(xs,np.maximum(v,1e-18),label=kind)
 ax.set(xlabel='Elapsed time along return [xi]',ylabel='Max sampled normalized duality residual',title='Tangential–cotangential pairing regression')
 ax.legend();ax.grid(alpha=.25);fig.tight_layout();fig.savefig(OUT/'tangent_cotangent_duality_check.png',dpi=175);plt.close(fig)
 print('Saved 3 authentic plots')
if __name__=='__main__':main()
