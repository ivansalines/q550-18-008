#!/usr/bin/env python3
"""Scientific figures drawn only from completed v18.49i CSV measurements."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 with (ROOT/'results'/name).open() as f:return list(csv.DictReader(f))
def plot():
 profiles=load('strain_axes_phase_profiles.csv');volume=load('liouville_volume_identity.csv');curves=load('strain_axis_vs_material_curvature.csv')
 fig,axes=plt.subplots(2,1,figsize=(8,8),sharex=True)
 for kind in ('original','autonomous'):
  data=sorted([r for r in volume if r['kappa_kind']==kind],key=lambda r:float(r['ramp_xi']))
  x=np.array([float(r['ramp_xi']) for r in data]);v=np.array([float(r['volume_factor']) for r in data]);
  axes[0].plot(x,v,marker='o',label=kind)
  axes[1].plot(x,[-float(r['liouville_abs_error']) for r in data],marker='o',label=kind)
 axes[0].set_ylabel('Kinetic volume Jacobian at q=0.50');axes[0].legend()
 axes[1].set_ylabel('Negative absolute Liouville residual');axes[1].set_xlabel('Reversal ramp [xi]')
 for a in axes:a.grid(alpha=.25)
 fig.suptitle('v18.49i — invariant kinetic volume density and Liouville check');fig.tight_layout();fig.savefig(ROOT/'results/volume_and_liouville.png',dpi=170);plt.close(fig)
 fig,axes=plt.subplots(2,1,figsize=(8,8),sharex=True)
 for kind in ('original','autonomous'):
  rows=sorted([r for r in profiles if r['kappa_kind']==kind and abs(float(r['ramp_xi'])-.300)<1e-9],key=lambda r:float(r['phase_q']))
  axes[0].plot([float(r['phase_q']) for r in rows],[float(r['max_stretch']) for r in rows],marker='o',label=f'{kind} maximum')
  axes[0].plot([float(r['phase_q']) for r in rows],[float(r['min_stretch']) for r in rows],marker='x',label=f'{kind} minimum')
  axes[1].plot([float(r['phase_q']) for r in rows],[float(r['top_axis_to_material_gap_deg']) for r in rows],marker='o',label=kind)
 axes[0].set_ylabel('Principal material stretch');axes[0].legend(fontsize=8,ncol=2)
 axes[1].set_ylabel('Top axis vs finite-gap direction [deg]');axes[1].set_xlabel('Common drive-clock phase q');axes[1].legend()
 for a in axes:a.grid(alpha=.25)
 fig.suptitle('v18.49i — strain axes in common initial kinetic frame');fig.tight_layout();fig.savefig(ROOT/'results/principal_strain_and_gap.png',dpi=170);plt.close(fig)
 fig,axes=plt.subplots(2,1,figsize=(8,8),sharex=True)
 for kind in ('original','autonomous'):
  rows=sorted([r for r in profiles if r['kappa_kind']==kind and abs(float(r['ramp_xi'])-.300)<1e-9],key=lambda r:float(r['phase_q']))
  axes[0].plot([float(r['phase_q']) for r in rows],[float(r['top1_axis_angle_prev_deg']) for r in rows],marker='o',label=kind)
  axes[1].plot([float(r['phase_q']) for r in rows],[float(r['top_stretch_gap_relative']) for r in rows],marker='o',label=kind)
 axes[0].set_ylabel('Top line turn between q samples [deg]');axes[1].set_ylabel('Spectral top gap / max stretch');axes[1].set_xlabel('Common drive-clock phase q')
 for a in axes:a.grid(alpha=.25);a.legend()
 fig.suptitle('v18.49i — sign-free principal-axis transport and spectral gaps');fig.tight_layout();fig.savefig(ROOT/'results/principal_axis_rotation.png',dpi=170);plt.close(fig)
 fig,ax=plt.subplots(figsize=(8,5))
 for kind in ('original','autonomous'):
  rows=sorted([r for r in curves if r['kappa_kind']==kind and abs(float(r['ramp_xi'])-.300)<1e-9],key=lambda r:float(r['phase_q']))
  ax.plot([float(r['phase_q']) for r in rows],[float(r['principal_axis_to_direction_tangent_deg']) for r in rows],marker='o',label=kind)
 ax.set(xlabel='Common drive-clock phase q',ylabel='Principal stretch axis / direction-path tangent [deg]',title='v18.49i — deformation axis vs material direction transport')
 ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(ROOT/'results/strain_axis_vs_direction_tangent.png',dpi=170);plt.close(fig)
if __name__=='__main__':plot()
