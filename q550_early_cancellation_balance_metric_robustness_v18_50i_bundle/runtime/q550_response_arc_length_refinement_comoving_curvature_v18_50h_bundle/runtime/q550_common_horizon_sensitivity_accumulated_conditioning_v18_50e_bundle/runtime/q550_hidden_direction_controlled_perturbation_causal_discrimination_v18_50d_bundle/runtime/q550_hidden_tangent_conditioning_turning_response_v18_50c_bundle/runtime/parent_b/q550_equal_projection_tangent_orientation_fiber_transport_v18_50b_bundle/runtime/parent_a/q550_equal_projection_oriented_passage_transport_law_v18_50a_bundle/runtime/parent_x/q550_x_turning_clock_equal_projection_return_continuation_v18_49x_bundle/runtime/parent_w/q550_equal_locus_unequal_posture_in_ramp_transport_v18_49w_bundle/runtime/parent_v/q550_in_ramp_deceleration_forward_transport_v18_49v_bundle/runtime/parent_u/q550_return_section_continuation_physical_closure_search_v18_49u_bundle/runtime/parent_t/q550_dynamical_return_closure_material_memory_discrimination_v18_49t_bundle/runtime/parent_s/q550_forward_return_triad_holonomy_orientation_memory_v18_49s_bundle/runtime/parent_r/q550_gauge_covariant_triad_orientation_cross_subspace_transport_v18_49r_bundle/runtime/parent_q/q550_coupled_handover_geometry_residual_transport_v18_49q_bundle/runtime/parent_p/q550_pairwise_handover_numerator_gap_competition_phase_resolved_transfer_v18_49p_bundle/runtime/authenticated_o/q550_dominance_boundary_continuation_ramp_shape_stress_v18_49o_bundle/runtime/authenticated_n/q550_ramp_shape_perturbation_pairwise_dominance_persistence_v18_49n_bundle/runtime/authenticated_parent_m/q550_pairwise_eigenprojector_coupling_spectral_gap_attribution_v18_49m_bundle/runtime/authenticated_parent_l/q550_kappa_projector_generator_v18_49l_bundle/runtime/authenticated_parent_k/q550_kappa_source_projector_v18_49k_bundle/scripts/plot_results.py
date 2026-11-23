#!/usr/bin/env python3
"""Generate figures from authentic numeric results; no hard-coded measurements."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'results'
def rows(n):
    with (RES/n).open(newline='') as f:return list(csv.DictReader(f))
def take(ramps,rs,kind,rank):
    return np.array([float(next(r['half_turn_clock_q'] for r in rs if r['kappa_kind']==kind and float(r['ramp_xi'])==x and int(r['axis_rank'])==rank)) for x in ramps])

def plot():
    zz=rows('source_zero_counterfactual_roots.csv');mm=rows('principal_projector_halfturn_markers.csv')
    q=sorted(set(float(r['ramp_xi']) for r in zz))
    zx=np.array([float(next(r['clock_source_zero_q'] for r in zz if float(r['ramp_xi'])==v and float(r['alpha'])==0)) for v in q])
    fig,ax=plt.subplots(figsize=(10.3,6))
    ax.plot(q,zx,'o-',lw=2.0,label='Kinetic source-difference zero (alpha=0)')
    for rank,style in ((1,'s-'),(8,'^-'),(10,'d-'),(0,'o--')):
        ax.plot(q,take(q,mm,'original',rank),style,lw=1.8,label=('All 10 projector half-turn' if rank==0 else f'Axis {rank} projector half-turn'))
    ax.set(xlabel='Ramp duration xi',ylabel='Return phase q',title='Clock-matched source zero and principal projector half-turns')
    ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(RES/'source_zero_vs_projector_clock.png',dpi=160);plt.close(fig)

    fig,ax=plt.subplots(figsize=(9.4,5.7))
    for alpha,style in ((-.001,'o-'),(0.,'s-'),(.001,'x--')):
        vals=[next(r for r in zz if float(r['ramp_xi'])==rv and float(r['alpha'])==alpha) for rv in q]
        ys=[float(v['clock_source_zero_q']) for v in vals]
        if np.any(np.isfinite(ys)):ax.plot(q,ys,style,label=f'alpha={alpha:g}')
        else:ax.plot([],[],style,label=f'alpha={alpha:g}: no root in window')
    ax.set(xlabel='Ramp duration xi',ylabel='Source-zero phase q',ylim=(.35,.65),title='Volume-form counterfactual: zero is not an intrinsic event')
    ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(RES/'volume_form_shifts_or_erases_zero.png',dpi=160);plt.close(fig)

    pp=rows('principal_projector_transport.csv');phys=rows('physical_sources_clockmatched.csv')
    rv=.3;kind='original'
    fig,axs=plt.subplots(2,1,figsize=(10.3,8),sharex=True)
    for rank in (1,3,8,10):
        ar=[r for r in pp if r['kappa_kind']==kind and float(r['ramp_xi'])==rv and int(r['axis_rank'])==rank]
        axs[0].plot([float(r['phase_q']) for r in ar],[float(r['projector_line_speed_rad_per_q']) for r in ar],label=f'Axis {rank}')
    axs[0].set(ylabel='Projector angular speed [rad / q]',title='Kinetic-frame principal eigenprojector transport — original kappa, ramp 0.300')
    axs[0].grid(alpha=.25);axs[0].legend()
    for rank in (3,8,10):
        ar=[r for r in pp if r['kappa_kind']==kind and float(r['ramp_xi'])==rv and int(r['axis_rank'])==rank]
        axs[1].plot([float(r['phase_q']) for r in ar],[100*float(r['occupation']) for r in ar],label=f'Axis {rank}')
    axs[1].set(xlabel='Registered return phase q',ylabel='Gap occupation [%]')
    axs[1].grid(alpha=.25);axs[1].legend();fig.tight_layout();fig.savefig(RES/'principal_projector_rates_and_occupation.png',dpi=160);plt.close(fig)

    lag=rows('clock_lag_and_volume_form_controls.csv');fig,ax=plt.subplots(figsize=(10,5.6))
    for rank in (1,8,10,0):
        series=[r for r in lag if float(r['alpha'])==0 and r['kappa_kind']=='original' and int(r['axis_rank'])==rank]
        series=sorted(series,key=lambda r:float(r['ramp_xi']))
        ax.plot([float(r['ramp_xi']) for r in series],[float(r['lag_projector_minus_source_q']) for r in series],'.-',lw=2,label=f'Axis {rank}' if rank else 'All projectors')
    ax.set(xlabel='Ramp duration xi',ylabel='Half-turn clock minus source-zero clock [q]',title='Event lag is nonzero and changes with ramp')
    ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(RES/'lag_evolution_across_ramps.png',dpi=160);plt.close(fig)
    print('Generated four numerical figures')
if __name__=='__main__':plot()
