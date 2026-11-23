#!/usr/bin/env python3
"""Real Q550 data visualizations for v18.49n. No simulated traces."""
import csv,json
from pathlib import Path
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results'
def rows(file):
    with (R/file).open(newline='') as f:return list(csv.DictReader(f))

def main():
    command=rows('ramp_command_shapes.csv');phase=rows('pairwise_dominance_phase_profiles.csv')
    envelope=rows('cross_case_dominance_envelope.csv')
    by=defaultdict(list)
    for p in command:by[p['shape']].append(p)
    fig,ax=plt.subplots(figsize=(10,5.3))
    for k,rr in by.items():ax.plot([float(x['normalized_ramp_time']) for x in rr],
        [float(x['signed_clock_rate']) for x in rr],label=k,lw=2)
    ax.set(xlabel='Normalized brake time s',ylabel='Signed phase-clock rate',
        title='Q550 v18.49n — equal duration, equal accumulated phase')
    ax.axhline(0,lw=.5);ax.legend(ncol=3);ax.grid(alpha=.25);fig.tight_layout()
    fig.savefig(R/'ramp_shape_controls.png',dpi=155);plt.close(fig)
    by=defaultdict(list)
    for p in phase:
        if p['kappa_kind']=='original' and abs(float(p['ramp_xi'])-.3)<1e-8:
            by[p['shape']].append(p)
    fig,ax=plt.subplots(figsize=(10,5.3))
    for k,rr in by.items():
        ax.plot([float(x['phase_q']) for x in rr],
            [float(x['pair_67_share']) for x in rr],label=k,lw=2)
    ax.axhline(.5,ls='--',lw=1,label='majority 50%')
    ax.set(xlabel='Return phase q',ylabel='6–7 share of squared generator',
       title='Q550 v18.49n — 6–7 response to brake shape, ramp=0.300')
    ax.grid(alpha=.25);ax.legend(ncol=3);fig.tight_layout()
    fig.savefig(R/'pair_67_dominance_under_shapes.png',dpi=155);plt.close(fig)
    q=np.array([float(p['phase_q']) for p in envelope]);lo=np.array([float(p['pair_67_min_share']) for p in envelope]);hi=np.array([float(p['pair_67_max_share']) for p in envelope]);
    m=np.array([float(p['pair_67_min_margin']) for p in envelope]);
    fig,ax=plt.subplots(figsize=(10,5.3))
    ax.fill_between(q,lo,hi,alpha=.28,label='min–max across measured cases')
    ax.plot(q,lo,lw=1.6,label='worst-case 6–7 share')
    ax.plot(q,hi,lw=1,label='best-case 6–7 share')
    ax.axhline(.5,ls='--',lw=1,label='majority threshold')
    ax.axvline(.55,ls=':',lw=1,label='persistence test starts q=.55')
    ax.set(xlabel='Return phase q',ylabel='6–7 share',
           title='Q550 v18.49n — observed cross-case domain envelope')
    ax.legend();ax.grid(alpha=.25);fig.tight_layout()
    fig.savefig(R/'cross_case_pair_67_share_envelope.png',dpi=155);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4.6))
    ax.plot(q,m,label='minimum over all tested cases')
    ax.axhline(0,ls='--',lw=1,label='6–7 ties the strongest rival')
    ax.axvline(.55,ls=':',lw=1)
    ax.set(xlabel='Return phase q',ylabel='Share margin vs strongest rival',
           title='Q550 v18.49n — worst-case dominance margin')
    ax.legend();ax.grid(alpha=.25);fig.tight_layout();fig.savefig(R/'worst_case_dominance_margin.png',dpi=155);plt.close(fig)
    print('Wrote four authentic data-driven Q550 figures')
if __name__=='__main__':main()
