#!/usr/bin/env python3
"""Plot actual numerical v18.48r output, not illustrative/synthetic trajectories."""
from pathlib import Path
import csv,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];D=ROOT/'results'
def data(filename):
    with (D/filename).open() as f:return list(csv.DictReader(f))
def main():
    a=data('crossing_transversality.csv');b=data('projection_crossings_2d.csv')
    n=np.load(D/'phasecov_selected_trajectories.npz')
    from sys import path
    path.insert(0,str(ROOT/'scripts'))
    from transversality_math import shape
    f=shape(n['forward']);r=shape(n['reverse'])
    fig=plt.figure(figsize=(10,7));ax=fig.add_subplot(111,projection='3d')
    ax.plot(*f.T,label='Forward 11D projected into 3D',linewidth=2)
    ax.plot(*r.T,label='Counterflow with reversed velocities',linewidth=2)
    u=float(n['free_u']);s=float(n['free_s']);v=n['grid']
    rf=np.array([np.interp(u,v,r[:,j]) for j in range(3)])
    ff=np.array([np.interp(s,v,f[:,j]) for j in range(3)])
    ax.plot(*np.stack((rf,ff)).T,linestyle='--',linewidth=2,label='Closest q asynchronous pair')
    ax.scatter(*rf,marker='o',s=48);ax.scatter(*ff,marker='x',s=48)
    ax.set(xlabel='log rho1',ylabel='log rho2',zlabel='x',title='Q550 v18.48r: near-pass in reduced shape (phasecov 0)')
    ax.legend(fontsize=8,loc='best');fig.tight_layout()
    fig.savefig(D/'phasecov_reduced_nearpass.png',dpi=160);plt.close(fig)

    free=[v for v in a if v['comparison']=='q_asynchronous_min_reintegrated' and v['interior_minimum']=='True']
    phase=[v for v in a if v['comparison']=='phase_conditioned_min']
    fig,ax=plt.subplots(figsize=(9,5.6))
    ax.scatter([float(v['shape_distance']) for v in free],
               [float(v['full11D_delta_L2']) for v in free],s=70,label='q interior 3D near-passes')
    ax.scatter([float(v['shape_distance']) for v in phase],
               [float(v['full11D_delta_L2']) for v in phase],s=18,alpha=.45,label='Externally phase-conditioned')
    ax.set(xscale='log',xlabel='3D reduced shape separation',ylabel='Complete 11D chart separation',
           title='Apparent near-crossings versus full-state separation')
    ax.grid(alpha=.25);ax.legend();fig.tight_layout()
    fig.savefig(D/'shape_vs_full11d_separation.png',dpi=160);plt.close(fig)

    fig,ax=plt.subplots(figsize=(9,5.6))
    if b:
        for axes in sorted(set(r['projection_axes'] for r in b)):
            s=[r for r in b if r['projection_axes']==axes and float(r['projection_root_residual'])<1e-8]
            if s:ax.scatter([float(v['shape_distance']) for v in s],
                         [abs(float(v['Theta_delta_rad'])) for v in s],alpha=.65,s=20,label=f'axes {axes}')
    ax.set(xscale='log',xlabel='3D gap at exact 2D-projection crossings',
           ylabel='|External drive phase mismatch| [rad]',
           title='A 2D line crossing need not be a 3D or phase recurrence')
    ax.legend();ax.grid(alpha=.3);fig.tight_layout()
    fig.savefig(D/'projection_crossings_phase_mismatch.png',dpi=160);plt.close(fig)
    print('v18.48r: wrote three diagnostic plots')
if __name__=='__main__':main()
