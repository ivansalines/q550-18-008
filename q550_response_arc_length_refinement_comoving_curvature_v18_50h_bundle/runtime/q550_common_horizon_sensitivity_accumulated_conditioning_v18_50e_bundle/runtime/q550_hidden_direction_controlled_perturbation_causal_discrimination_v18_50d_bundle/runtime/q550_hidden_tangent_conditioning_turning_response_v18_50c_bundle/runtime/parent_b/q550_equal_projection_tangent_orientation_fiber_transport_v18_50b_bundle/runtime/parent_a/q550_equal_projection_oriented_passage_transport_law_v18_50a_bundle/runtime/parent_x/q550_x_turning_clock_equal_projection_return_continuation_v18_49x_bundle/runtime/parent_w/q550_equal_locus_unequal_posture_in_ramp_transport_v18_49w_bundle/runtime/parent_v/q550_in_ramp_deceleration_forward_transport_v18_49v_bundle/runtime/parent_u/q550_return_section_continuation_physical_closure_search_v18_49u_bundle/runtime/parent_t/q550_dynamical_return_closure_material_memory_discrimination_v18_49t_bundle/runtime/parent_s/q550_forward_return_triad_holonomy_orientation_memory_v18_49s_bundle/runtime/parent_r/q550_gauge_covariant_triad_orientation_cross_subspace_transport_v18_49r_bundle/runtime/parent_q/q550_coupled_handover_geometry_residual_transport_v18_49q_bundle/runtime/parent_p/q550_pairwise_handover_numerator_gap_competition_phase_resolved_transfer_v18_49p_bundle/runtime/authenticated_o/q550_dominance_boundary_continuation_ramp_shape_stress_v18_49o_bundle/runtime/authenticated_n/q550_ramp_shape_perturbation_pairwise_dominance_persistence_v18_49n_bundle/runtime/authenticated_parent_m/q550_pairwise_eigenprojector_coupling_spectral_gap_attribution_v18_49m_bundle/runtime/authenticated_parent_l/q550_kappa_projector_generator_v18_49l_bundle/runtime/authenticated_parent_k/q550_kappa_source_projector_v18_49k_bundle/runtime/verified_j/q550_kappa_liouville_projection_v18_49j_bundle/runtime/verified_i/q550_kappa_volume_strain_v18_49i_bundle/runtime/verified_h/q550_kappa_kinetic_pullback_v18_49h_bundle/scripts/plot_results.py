#!/usr/bin/env python3
"""Matplotlib figures generated exclusively from authenticated h-audit CSV."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]

def load(name):
 with (ROOT/'results'/name).open() as f:return list(csv.DictReader(f))
def save(fig,name):
 fig.tight_layout();fig.savefig(ROOT/'results'/name,dpi=175);plt.close(fig)

def plot():
 deformation=load('kinetic_deformation_eigenvalues.csv');curves=load('kinetic_sphere_curvature.csv');comp=load('metric_comparison_with_G.csv');profile=load('kinetic_orientation_profiles.csv')
 fig,ax=plt.subplots(figsize=(8,5.2))
 for k in ('original','autonomous'):
  rs=sorted([r for r in deformation if r['kappa_kind']==k and float(r['tau_ref'])==1 and float(r['phase_q'])==.50],key=lambda r:float(r['ramp_xi']))
  ax.plot([float(r['ramp_xi']) for r in rs],[float(r['strain_max_stretch']) for r in rs],marker='o',label=f'{k}  max stretch')
  ax.plot([float(r['ramp_xi']) for r in rs],[float(r['strain_min_stretch']) for r in rs],linestyle='--',marker='s',label=f'{k}  min stretch')
 ax.set(xlabel='Reversal ramp duration [xi]',ylabel='Kinetic-metric material stretch (q=0.50)',title='Q550 v18.49h — generalized Cauchy–Green stretches')
 ax.grid(alpha=.25);ax.legend(fontsize=8);save(fig,'kinetic_cauchy_green_stretches.png')
 fig,ax=plt.subplots(figsize=(8,5.2))
 for k in ('original','autonomous'):
  for tau in (.5,1.,2.):
   rs=sorted([r for r in curves if r['kappa_kind']==k and float(r['tau_ref'])==tau],key=lambda r:float(r['ramp_xi']))
   ax.plot([float(r['ramp_xi']) for r in rs],[float(r['curvature_at_q050']) for r in rs],marker='o' if k=='original' else 'x',label=f'{k}, tau={tau:g}')
 ax.set(xlabel='Reversal ramp duration [xi]',ylabel='Geodesic curvature at q=0.50',title='Metric choice matters: S9 curvature of kinetic pullback')
 ax.grid(alpha=.25);ax.legend(fontsize=8,ncol=2);save(fig,'curvature_scale_sensitivity.png')
 fig,ax=plt.subplots(figsize=(8,5.2))
 for k in ('original','autonomous'):
  rs=sorted([r for r in comp if r['kappa_kind']==k],key=lambda r:float(r['ramp_xi']))
  x=np.array([float(r['ramp_xi']) for r in rs]);z=np.array([float(r['excess_parent_G_euclidean_chart_deg']) for r in rs]);w=np.array([float(r['excess_kinetic_cartesian_deg']) for r in rs]);
  ax.plot(x,z,marker='o',label=f'{k} G: hidden-chart excess');ax.plot(x,w,marker='s',label=f'{k} H: full kinetic metric excess')
 ax.set(xlabel='Reversal ramp duration [xi]',ylabel='Arc minus endpoint [degrees]',title='Different observable and metric: excess is not a universal scalar')
 ax.legend(fontsize=8);ax.grid(alpha=.25);save(fig,'metric_vs_previous_G_excess.png')
 fig,ax=plt.subplots(figsize=(8,5.2))
 for k in ('original','autonomous'):
  rs=sorted([r for r in profile if r['kappa_kind']==k and abs(float(r['ramp_xi'])-.300)<1e-10],key=lambda r:float(r['phase_q']))
  ax.plot([float(r['phase_q']) for r in rs],[float(r['curvature']) for r in rs],label=k)
 ax.set(xlabel='Common drive-clock phase q',ylabel='Geodesic curvature on S9',title='Full-material curvature history, 0.300 xi reversal, tau=1')
 ax.legend();ax.grid(alpha=.25);save(fig,'covariant_direction_curvature_profile.png')
if __name__=='__main__':plot()
