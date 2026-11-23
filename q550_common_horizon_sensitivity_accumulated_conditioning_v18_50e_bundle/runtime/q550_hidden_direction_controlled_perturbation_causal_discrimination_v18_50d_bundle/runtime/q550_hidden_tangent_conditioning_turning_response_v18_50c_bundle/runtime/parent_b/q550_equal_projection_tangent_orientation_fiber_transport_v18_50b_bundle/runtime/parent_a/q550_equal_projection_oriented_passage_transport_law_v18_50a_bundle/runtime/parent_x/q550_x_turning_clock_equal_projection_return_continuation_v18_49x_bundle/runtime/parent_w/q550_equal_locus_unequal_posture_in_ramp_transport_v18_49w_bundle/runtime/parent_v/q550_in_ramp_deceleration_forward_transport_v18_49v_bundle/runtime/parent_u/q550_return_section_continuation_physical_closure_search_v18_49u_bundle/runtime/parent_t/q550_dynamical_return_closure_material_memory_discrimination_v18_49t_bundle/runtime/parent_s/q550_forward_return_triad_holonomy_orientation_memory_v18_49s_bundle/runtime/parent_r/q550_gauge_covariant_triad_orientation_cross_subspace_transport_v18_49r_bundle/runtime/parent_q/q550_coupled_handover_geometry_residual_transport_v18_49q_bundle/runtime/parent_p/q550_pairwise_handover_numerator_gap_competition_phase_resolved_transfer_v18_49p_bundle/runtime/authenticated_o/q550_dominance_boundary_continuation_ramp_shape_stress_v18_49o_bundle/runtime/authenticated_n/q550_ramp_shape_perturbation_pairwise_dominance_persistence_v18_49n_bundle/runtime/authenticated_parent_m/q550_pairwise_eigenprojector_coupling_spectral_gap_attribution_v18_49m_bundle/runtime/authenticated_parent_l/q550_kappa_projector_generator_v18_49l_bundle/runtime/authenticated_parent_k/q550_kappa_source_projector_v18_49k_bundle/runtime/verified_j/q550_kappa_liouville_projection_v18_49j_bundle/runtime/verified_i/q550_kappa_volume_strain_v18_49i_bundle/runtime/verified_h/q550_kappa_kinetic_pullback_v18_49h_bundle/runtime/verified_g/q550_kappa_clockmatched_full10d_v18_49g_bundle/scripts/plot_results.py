#!/usr/bin/env python3
"""Plots generated only from authenticated/reintegrated v18.49g CSV outputs."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/'results'

def draw():
 e=pd.read_csv(RESULT/'threshold_free_extrema_orientation.csv')
 p=pd.read_csv(RESULT/'clock_matched_threshold_passages.csv')
 s=pd.read_csv(RESULT/'full10d_clock_profiles.csv')
 for kind,g in e.groupby('kappa_kind'):
  pass
 fig,ax=plt.subplots(figsize=(10,5.8))
 for kind,g in e.groupby('kappa_kind'):
  g=g.sort_values('ramp_xi')
  ax.plot(g.ramp_xi,g.full10d_extrema_path_turn_deg,marker='o',label=f'{kind}: full 10D path')
  ax.plot(g.ramp_xi,g.full10d_extrema_endpoint_angle_deg,marker='s',ls='--',label=f'{kind}: endpoint angle')
 ax.set(xlabel='Smooth reversal ramp [xi]',ylabel='Angular measure [degrees]',title='Q550 v18.49g | Full-10D path vs endpoint angle (extrema markers)')
 ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(RESULT/'full10d_path_vs_endpoint.png',dpi=180);plt.close(fig)
 fig,ax=plt.subplots(figsize=(10,5.8))
 for threshold,g in p.groupby('threshold'):
  ax.scatter([threshold]*len(g),g.span_over_kappa0,marker='o',s=30,alpha=.75)
 ax.axhline(1.2,ls='--',color='black',label='6/5 = 1.2')
 ax.set(xlabel='Contact threshold epsilon',ylabel='Passage span / kappa0',title='Q550 v18.49g | Threshold-selected passages vs 6/5')
 ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(RESULT/'threshold_scaling_vs_six_fifths.png',dpi=180);plt.close(fig)
 fig,ax=plt.subplots(figsize=(10,5.8))
 for kind,g in e.groupby('kappa_kind'):
  g=g.sort_values('ramp_xi');ax.plot(g.ramp_xi,g.extrema_span_over_kappa0,marker='o',label=f'{kind}: min-to-min span / kappa0')
 ax.axhline(1.2,ls='--',color='black',label='6/5')
 ax.set(xlabel='Smooth reversal ramp [xi]',ylabel='Extrema span / kappa0',title='Q550 v18.49g | Threshold-independent (not metric-independent) markers')
 ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(RESULT/'extrema_span_not_six_fifths.png',dpi=180);plt.close(fig)
 fig,ax=plt.subplots(figsize=(10,5.8))
 for kind,g in e.groupby('kappa_kind'):
  g=g.sort_values('ramp_xi')
  ax.plot(g.ramp_xi,g.projected_2d_angle_max_q,marker='o',label=f'{kind}: 2D projected peak')
  ax.plot(g.ramp_xi,g.barrier_max_q,marker='^',ls='--',label=f'{kind}: central barrier')
 ax.axhline(.75,ls=':',color='black',label='Full 10D max in observed window: q=0.75 (boundary)')
 ax.set(xlabel='Smooth reversal ramp [xi]',ylabel='Clock-registered phase q',title='Q550 v18.49g | Projected 2D turn vs full-10D nonreturn')
 ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(RESULT/'clock_registered_2d_vs_10d.png',dpi=180);plt.close(fig)
 fig,ax=plt.subplots(figsize=(10,5.8))
 for kind in sorted(s.kappa_kind.unique()):
  a=s[(s.kappa_kind==kind) & (np.isclose(s.ramp_xi,.300))].sort_values('phase_q')
  if a.empty:continue
  ax.plot(a.phase_q,a.angle_to_q035_full10d_deg,label=f'{kind}: 10D angle from q=0.35')
 ax.axvline(.54,ls=':',color='black',label='Approximate 2D projected peak q≈0.54')
 ax.set(xlabel='Physical-clock registered phase q',ylabel='Full 10D angle from q=0.35 [degrees]',title='Q550 v18.49g | Full-10D direction keeps departing after the 2D peak')
 ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(RESULT/'full10d_clock_orientation_profile.png',dpi=180);plt.close(fig)
 print('v18.49g plots written: 5')
if __name__=='__main__':draw()
