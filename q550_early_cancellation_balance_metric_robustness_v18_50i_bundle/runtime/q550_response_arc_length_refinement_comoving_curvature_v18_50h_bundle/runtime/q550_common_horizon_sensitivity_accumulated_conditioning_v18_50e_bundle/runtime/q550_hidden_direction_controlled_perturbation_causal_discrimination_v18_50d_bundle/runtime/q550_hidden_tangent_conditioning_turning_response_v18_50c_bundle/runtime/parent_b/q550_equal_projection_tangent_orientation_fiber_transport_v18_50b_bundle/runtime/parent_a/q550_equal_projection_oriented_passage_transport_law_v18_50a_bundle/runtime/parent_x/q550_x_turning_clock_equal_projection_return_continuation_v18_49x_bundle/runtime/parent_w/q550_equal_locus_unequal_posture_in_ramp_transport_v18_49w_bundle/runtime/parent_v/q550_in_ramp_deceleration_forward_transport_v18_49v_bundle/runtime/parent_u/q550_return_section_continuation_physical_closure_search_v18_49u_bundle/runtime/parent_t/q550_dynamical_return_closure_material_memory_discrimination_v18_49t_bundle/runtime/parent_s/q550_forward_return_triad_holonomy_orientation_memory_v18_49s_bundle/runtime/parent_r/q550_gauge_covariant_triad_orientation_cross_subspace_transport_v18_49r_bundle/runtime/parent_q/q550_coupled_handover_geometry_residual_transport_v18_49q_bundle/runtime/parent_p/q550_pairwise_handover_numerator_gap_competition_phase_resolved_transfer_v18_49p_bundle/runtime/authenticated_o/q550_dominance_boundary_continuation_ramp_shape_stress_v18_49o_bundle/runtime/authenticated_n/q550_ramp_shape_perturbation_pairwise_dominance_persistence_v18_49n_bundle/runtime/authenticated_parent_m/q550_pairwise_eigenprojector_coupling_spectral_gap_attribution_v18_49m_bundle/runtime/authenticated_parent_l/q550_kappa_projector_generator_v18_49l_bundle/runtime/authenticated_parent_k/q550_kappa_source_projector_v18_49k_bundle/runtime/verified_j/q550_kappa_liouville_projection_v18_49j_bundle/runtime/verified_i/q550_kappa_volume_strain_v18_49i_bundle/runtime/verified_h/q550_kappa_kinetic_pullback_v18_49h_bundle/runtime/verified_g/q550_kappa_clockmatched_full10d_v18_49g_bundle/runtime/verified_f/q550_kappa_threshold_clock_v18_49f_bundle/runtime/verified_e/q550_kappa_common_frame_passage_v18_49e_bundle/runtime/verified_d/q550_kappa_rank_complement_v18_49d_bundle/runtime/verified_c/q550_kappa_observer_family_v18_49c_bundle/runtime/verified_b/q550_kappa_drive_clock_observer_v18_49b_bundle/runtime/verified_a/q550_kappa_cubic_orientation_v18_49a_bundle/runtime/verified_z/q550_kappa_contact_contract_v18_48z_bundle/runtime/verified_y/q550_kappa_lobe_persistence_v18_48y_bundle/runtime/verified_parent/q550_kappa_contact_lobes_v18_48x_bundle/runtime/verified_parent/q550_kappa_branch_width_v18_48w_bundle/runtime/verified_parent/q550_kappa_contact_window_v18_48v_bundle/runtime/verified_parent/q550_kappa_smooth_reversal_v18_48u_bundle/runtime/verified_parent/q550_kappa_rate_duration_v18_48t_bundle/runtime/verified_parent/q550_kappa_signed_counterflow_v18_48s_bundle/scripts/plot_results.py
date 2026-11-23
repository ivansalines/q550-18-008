#!/usr/bin/env python3
"""Plot only computed v18.48s numerical data (no synthetic Q550 curves)."""
from __future__ import annotations
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
def rows(filename):
    with (OUT/filename).open(newline='') as f:return list(csv.DictReader(f))
def values(rows,key):return np.array([float(r[key]) for r in rows])
def main():
    contacts=rows('signed_contacts.csv');lock=[r for r in contacts if r['contact_kind']=='phase_locked_min']
    free=[r for r in contacts if r['contact_kind']=='async_free_min']
    cross=rows('signed_projected_crossings.csv')
    fig,ax=plt.subplots(figsize=(8.6,6.2))
    for lab,d in [('Equal phase',lock),('Independent instants',free)]:
        ax.scatter(values(d,'chronological_angle_deg'),values(d,'shape_distance'),s=22,alpha=.7,label=lab)
    ax.set(xlabel='Chronological 3D tangent angle [deg]',ylabel='3D geometric separation (declared chart)',title='Oriented geometry: matching phase vs independent time')
    ax.set_yscale('log');ax.grid(alpha=.2);ax.legend();fig.tight_layout()
    fig.savefig(OUT/'signed_tangent_vs_contact.png',dpi=180);plt.close(fig)

    fig,ax=plt.subplots(figsize=(8.6,6.2))
    sc=ax.scatter(values(lock,'drive_power_forward_per_xi'),values(lock,'drive_power_return_per_xi'),
                  c=values(lock,'energy_difference'),s=35,alpha=.85)
    ax.axhline(0,ls='--',lw=.7);ax.axvline(0,ls='--',lw=.7)
    ax.set(xlabel='Signed forward drive power dE/dxi term',ylabel='Signed return drive power dE/dxi term',title='Signed drive work rates at phase-matched near-contacts')
    ax.grid(alpha=.2);fig.colorbar(sc,ax=ax,label='Energy difference E_return - E_forward');fig.tight_layout()
    fig.savefig(OUT/'signed_drive_power_phase_locked.png',dpi=180);plt.close(fig)

    if cross:
        fig,ax=plt.subplots(figsize=(8.6,6.2))
        sc=ax.scatter(values(cross,'Theta_delta_rad'),values(cross,'shape_distance'),
                c=values(cross,'projected_2D_chirality_signed'),s=28,alpha=.8)
        ax.axvline(0,ls='--',lw=.8)
        ax.set(xlabel='Return-forward external phase mismatch [rad]',
               ylabel='Residual 3D separation',title='Projected 2D crossings: orientation and phase mismatch')
        ax.set_yscale('log');ax.grid(alpha=.2)
        fig.colorbar(sc,ax=ax,label='Signed 2D tangent determinant (ordered axes)')
        fig.tight_layout();fig.savefig(OUT/'projected_crossings_signed_chirality.png',dpi=180);plt.close(fig)

    data=np.load(OUT/'phasecov_phase_locked_paths.npz')
    from sys import path
    path.insert(0,str(ROOT/'reference'))
    from transversality_math import shape
    u=data['progress']; fshape=shape(data['synchronous_forward_state']);rshape=shape(data['return_state'])
    fwork=data['synchronous_forward_work'];rwork=data['return_work'];
    # This is a component-ledger trajectory difference, not a material work cycle.
    diffdrive=rwork[:,0]+data['forward_work'][-1,0]-fwork[:,0]
    diffdamping=(rwork[:,1]+rwork[:,2]+data['forward_work'][-1,1]+data['forward_work'][-1,2]
                 -fwork[:,1]-fwork[:,2])
    fig,(a,b,c)=plt.subplots(3,1,figsize=(10.2,8.9),sharex=True,constrained_layout=True)
    gaps=rshape-fshape
    a.plot(u,np.linalg.norm(gaps,axis=1),label='3D shape gap')
    a.set_yscale('log');a.set_ylabel('Shape distance');a.legend();a.grid(alpha=.18)
    for i,lab in enumerate(('delta log rho1','delta log rho2','delta x')):b.plot(u,gaps[:,i],label=lab)
    b.set_ylabel('Signed geometric gaps');b.legend(ncol=3,fontsize=8);b.grid(alpha=.18)
    c.plot(u,diffdrive,label='drive-work differential')
    c.plot(u,diffdamping,label='dissipative-work differential')
    c.set(xlabel='Return progress u; forward evaluated at s=1-u',ylabel='Cumulative signed work difference')
    c.legend(fontsize=8);c.grid(alpha=.18)
    fig.suptitle('phasecov branch 0: equal-drive-phase counterflow vs forward history')
    fig.savefig(OUT/'phasecov_signed_phase_locked_dance.png',dpi=180);plt.close(fig)
if __name__=='__main__':main()
