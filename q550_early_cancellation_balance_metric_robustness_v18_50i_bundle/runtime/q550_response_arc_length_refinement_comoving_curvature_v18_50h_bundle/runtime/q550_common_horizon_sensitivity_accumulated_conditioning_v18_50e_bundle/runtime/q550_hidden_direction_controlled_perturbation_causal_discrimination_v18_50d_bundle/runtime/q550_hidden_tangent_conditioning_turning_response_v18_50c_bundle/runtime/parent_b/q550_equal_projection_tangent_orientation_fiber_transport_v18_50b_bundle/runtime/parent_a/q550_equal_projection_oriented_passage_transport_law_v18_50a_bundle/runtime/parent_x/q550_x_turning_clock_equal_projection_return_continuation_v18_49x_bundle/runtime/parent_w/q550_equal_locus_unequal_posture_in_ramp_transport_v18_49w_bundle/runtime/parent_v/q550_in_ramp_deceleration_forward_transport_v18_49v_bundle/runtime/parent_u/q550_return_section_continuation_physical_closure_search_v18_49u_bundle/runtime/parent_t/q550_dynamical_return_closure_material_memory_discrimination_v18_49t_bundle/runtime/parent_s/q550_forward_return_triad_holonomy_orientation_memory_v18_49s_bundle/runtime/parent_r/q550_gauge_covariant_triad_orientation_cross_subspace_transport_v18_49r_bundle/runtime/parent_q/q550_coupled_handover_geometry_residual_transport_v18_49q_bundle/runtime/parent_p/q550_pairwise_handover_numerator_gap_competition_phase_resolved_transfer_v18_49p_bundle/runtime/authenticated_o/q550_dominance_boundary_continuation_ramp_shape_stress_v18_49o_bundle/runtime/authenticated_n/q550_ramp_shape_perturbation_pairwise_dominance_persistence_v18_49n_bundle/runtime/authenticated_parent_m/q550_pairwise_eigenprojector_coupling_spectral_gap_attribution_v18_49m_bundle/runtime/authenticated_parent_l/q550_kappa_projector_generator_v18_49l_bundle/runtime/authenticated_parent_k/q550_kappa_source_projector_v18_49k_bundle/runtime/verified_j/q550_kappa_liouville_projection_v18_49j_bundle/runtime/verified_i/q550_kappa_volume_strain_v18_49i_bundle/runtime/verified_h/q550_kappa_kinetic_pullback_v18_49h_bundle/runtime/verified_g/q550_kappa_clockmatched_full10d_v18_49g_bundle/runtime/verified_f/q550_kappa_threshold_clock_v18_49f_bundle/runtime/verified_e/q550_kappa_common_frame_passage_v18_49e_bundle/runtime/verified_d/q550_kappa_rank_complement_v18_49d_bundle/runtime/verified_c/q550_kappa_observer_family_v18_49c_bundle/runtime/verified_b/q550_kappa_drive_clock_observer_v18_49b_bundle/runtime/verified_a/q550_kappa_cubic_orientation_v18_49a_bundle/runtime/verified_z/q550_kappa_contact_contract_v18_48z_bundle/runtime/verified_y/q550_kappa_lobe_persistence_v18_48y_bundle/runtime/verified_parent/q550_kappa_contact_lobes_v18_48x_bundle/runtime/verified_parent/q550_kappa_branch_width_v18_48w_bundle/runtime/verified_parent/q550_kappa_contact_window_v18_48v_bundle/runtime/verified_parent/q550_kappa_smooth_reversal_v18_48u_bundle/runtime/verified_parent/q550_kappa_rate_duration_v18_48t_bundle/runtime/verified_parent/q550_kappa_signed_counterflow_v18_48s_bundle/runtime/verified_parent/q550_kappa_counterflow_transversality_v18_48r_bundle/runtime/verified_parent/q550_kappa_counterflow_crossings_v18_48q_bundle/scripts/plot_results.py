#!/usr/bin/env python3
"""Reconstruct genuine v18.48q plots from machine-readable Q550 outputs."""
from __future__ import annotations
import csv,json,pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
def read(name):
    with (OUT/name).open(newline='') as f:return list(csv.DictReader(f))
def main():
    cases=read('near_crossing_pairs.csv')
    summary=read('sweep_summary.csv')
    matches=[x for x in cases if x['family'].startswith('phasecov') and x['branch']=='0'
             and x['kappa_kind']=='original' and x['protocol']=='phase_closed_rate1_flip1']
    if len(matches)!=2:raise RuntimeError('Missing unique case for plot')
    data=np.load(OUT/'selected_case_dense_samples.npz',allow_pickle=False)
    f=data['forward_state'];r=data['reverse_state'];u=data['fraction']
    def xval(z):return 1/(1+np.exp(-z[...,8]))
    fig=plt.figure(figsize=(10,8));ax=fig.add_subplot(111,projection='3d')
    ax.plot(f[:,0],f[:,4],xval(f),lw=2.2,label='Forward reference',color='#3184a3')
    ax.plot(r[:,0],r[:,4],xval(r),lw=2.2,label='Reverse drive + velocity flip',color='#a34c82')
    ax.scatter([f[-1,0]],[f[-1,4]],[xval(f[-1])],s=45,c='#353535',label='Turnaround')
    ax.set_xlabel('log rho1');ax.set_ylabel('log rho2');ax.set_zlabel('x')
    ax.legend(loc='upper right',fontsize=8);ax.set_title('Q550: distinct histories in 3D shape projection')
    fig.tight_layout();fig.savefig(OUT/'phasecov_counterflow_nearcrossings_3d.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(3,1,figsize=(11,9),sharex=True,layout='constrained')
    sample=[x for x in read('matched_progress_samples.csv') if x['family'].startswith('phasecov')
            and x['branch']=='0' and x['kappa_kind']=='original'
            and x['protocol']=='phase_closed_rate1_flip1']
    u=np.array([float(x['return_progress']) for x in sample])
    axes[0].plot(u,[float(x['shape_distance']) for x in sample]);axes[0].set_ylabel('3D shape gap')
    axes[1].plot(u,[float(x['velocity_delta_L2']) for x in sample],label='Tau-velocity gap')
    axes[1].plot(u,[abs(float(x['Theta_delta_rad'])) for x in sample],label='Clock phase gap')
    axes[1].legend();axes[1].set_ylabel('State mismatch (different units)')
    axes[2].plot(u,[float(x['energy_delta']) for x in sample]);axes[2].axhline(0,ls='--',lw=.7)
    axes[2].set_ylabel('Energy difference');axes[2].set_xlabel('Normalized return progress u')
    fig.suptitle('Q550 v18.48q: progress-matched spatial vs phase/velocity/energy mismatch')
    fig.savefig(OUT/'phasecov_phase_energy_separation.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(2,1,figsize=(11,8),layout='constrained')
    for flip,marker in [(0,'o'),(1,'s')]:
        sub=[x for x in summary if x['design']=='phase_closed' and int(x['flip_tau_velocities'])==flip]
        rates=sorted(set(float(x['reverse_clock_rate_multiplier']) for x in sub))
        shape_med=[float(np.median([float(x['endpoint_shape_distance']) for x in sub if float(x['reverse_clock_rate_multiplier'])==rate])) for rate in rates]
        en_med=[float(np.median([float(x['delta_E']) for x in sub if float(x['reverse_clock_rate_multiplier'])==rate])) for rate in rates]
        axes[0].plot(rates,shape_med,marker=marker,label=f'Flip tau velocities={flip}')
        axes[1].plot(rates,en_med,marker=marker,label=f'Flip tau velocities={flip}')
    axes[0].set_ylabel('Median endpoint 3D shape gap')
    axes[1].set_ylabel('Median reverse-leg delta E');axes[1].set_xlabel('Reverse phase-clock speed multiplier')
    for a in axes:a.legend();a.grid(alpha=.2)
    axes[0].set_title('Phase-closed protocol (duration=1/rate) — rate and duration coupled')
    fig.savefig(OUT/'phaseclosed_rate_duration_sweep.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10.5,5),layout='constrained')
    for design in ('phase_closed','fixed_duration'):
        sub=[x for x in summary if x['design']==design and not int(x['flip_tau_velocities'])]
        rates=sorted(set(float(x['reverse_clock_rate_multiplier']) for x in sub))
        gap=[float(np.median([float(x['endpoint_shape_distance']) for x in sub if float(x['reverse_clock_rate_multiplier'])==rr])) for rr in rates]
        ax.plot(rates,gap,marker='o',label=design)
    ax.set_xlabel('Reverse phase-clock speed multiplier');ax.set_ylabel('Median terminal shape mismatch')
    ax.grid(alpha=.2);ax.legend();ax.set_title('Phase closed vs fixed duration (no initial velocity flip)')
    fig.savefig(OUT/'phaseclosed_vs_fixedtime.png',dpi=180);plt.close(fig)
    print('Generated 4 diagnostic plots.')
if __name__=='__main__':main()
