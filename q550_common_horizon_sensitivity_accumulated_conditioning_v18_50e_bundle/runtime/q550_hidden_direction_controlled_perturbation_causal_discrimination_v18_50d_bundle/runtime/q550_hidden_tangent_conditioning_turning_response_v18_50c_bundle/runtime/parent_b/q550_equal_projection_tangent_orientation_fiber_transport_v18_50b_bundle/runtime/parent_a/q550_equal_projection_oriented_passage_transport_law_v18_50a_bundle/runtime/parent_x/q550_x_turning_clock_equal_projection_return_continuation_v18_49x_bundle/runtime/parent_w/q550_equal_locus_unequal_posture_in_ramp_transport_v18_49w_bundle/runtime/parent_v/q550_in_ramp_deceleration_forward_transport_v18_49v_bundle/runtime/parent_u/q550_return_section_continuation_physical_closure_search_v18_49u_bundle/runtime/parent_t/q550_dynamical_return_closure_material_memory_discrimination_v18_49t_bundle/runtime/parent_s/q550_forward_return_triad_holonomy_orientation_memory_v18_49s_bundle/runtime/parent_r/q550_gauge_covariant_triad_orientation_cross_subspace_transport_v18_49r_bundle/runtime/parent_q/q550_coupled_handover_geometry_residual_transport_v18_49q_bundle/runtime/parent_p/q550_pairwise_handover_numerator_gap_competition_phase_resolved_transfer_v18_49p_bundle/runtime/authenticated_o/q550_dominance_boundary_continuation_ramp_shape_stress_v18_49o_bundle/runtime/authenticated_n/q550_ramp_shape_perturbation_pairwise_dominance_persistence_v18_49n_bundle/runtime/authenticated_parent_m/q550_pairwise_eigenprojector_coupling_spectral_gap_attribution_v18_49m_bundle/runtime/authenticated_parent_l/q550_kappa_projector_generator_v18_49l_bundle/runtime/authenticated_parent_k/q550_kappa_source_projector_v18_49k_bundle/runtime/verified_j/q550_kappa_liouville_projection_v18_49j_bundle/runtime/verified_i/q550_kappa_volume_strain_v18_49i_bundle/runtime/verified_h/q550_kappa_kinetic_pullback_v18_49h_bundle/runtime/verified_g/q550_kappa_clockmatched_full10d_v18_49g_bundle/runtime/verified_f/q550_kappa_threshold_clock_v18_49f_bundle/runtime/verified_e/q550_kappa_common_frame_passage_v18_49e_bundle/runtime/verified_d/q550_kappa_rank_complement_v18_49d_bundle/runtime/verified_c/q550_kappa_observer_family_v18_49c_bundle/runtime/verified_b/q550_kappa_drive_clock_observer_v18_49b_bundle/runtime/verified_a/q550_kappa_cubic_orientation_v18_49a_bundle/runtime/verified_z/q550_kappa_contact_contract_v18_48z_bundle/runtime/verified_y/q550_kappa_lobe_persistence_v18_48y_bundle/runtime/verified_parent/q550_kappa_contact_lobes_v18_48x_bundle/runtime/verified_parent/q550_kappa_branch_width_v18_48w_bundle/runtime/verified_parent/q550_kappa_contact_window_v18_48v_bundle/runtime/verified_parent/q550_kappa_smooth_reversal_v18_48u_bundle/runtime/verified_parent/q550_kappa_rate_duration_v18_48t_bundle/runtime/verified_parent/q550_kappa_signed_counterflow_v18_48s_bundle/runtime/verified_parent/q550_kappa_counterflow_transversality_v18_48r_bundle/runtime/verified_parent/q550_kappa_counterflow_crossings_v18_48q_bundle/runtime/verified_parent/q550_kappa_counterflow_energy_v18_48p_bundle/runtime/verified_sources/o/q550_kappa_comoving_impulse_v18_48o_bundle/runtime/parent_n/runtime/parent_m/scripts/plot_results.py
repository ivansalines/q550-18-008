#!/usr/bin/env python3
"""Read numerical ledgers; draw subspace transport and 2D projection controls."""
from pathlib import Path
import csv,matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
def read(name):
    with (ROOT/'results'/name).open() as f:return list(csv.DictReader(f))
def main():
    rows=read('adjacent_principal_angles.csv')
    family='phaseblind_d2_lam-1.00_mod+0.00'; fig,ax=plt.subplots(figsize=(10.5,5.8))
    for cutoff in (1e-6,1e-10):
        arr=[r for r in rows if r['family']==family and r['branch']=='0' and r['kappa']=='original' and float(r['source_cutoff'])==cutoff and float(r['cancel_cutoff'])==1e-2]
        arr.sort(key=lambda x:float(x['xi_b']))
        xx=[float(r['xi_b']) for r in arr]; yy=[float(r['near_projector_spectral']) for r in arr]
        ax.plot(xx,yy,marker='o',ms=2.5,label=f'source cutoff {cutoff:g}')
    ax.set(xlabel='xi (common physical section)',ylabel='spectral projector gap',title='phaseblind branch 0: cancellation subspace transport')
    ax.set_ylim(bottom=0);ax.grid(alpha=.25);ax.legend();fig.tight_layout()
    fig.savefig(ROOT/'results'/'phaseblind_projector_transport.png',dpi=175);plt.close(fig)
    arr=[r for r in rows if r['family']==family and r['branch']=='0' and r['kappa']=='original' and float(r['source_cutoff'])==1e-6 and float(r['cancel_cutoff'])==1e-2]
    arr.sort(key=lambda x:float(x['xi_b']))
    fig,ax=plt.subplots(figsize=(10.5,5.8))
    x=[float(r['xi_b']) for r in arr]
    ax.plot(x,[int(r['source_rank_b']) for r in arr],label='source active dimension',lw=1.9)
    ax.plot(x,[int(r['cancellation_rank_b']) for r in arr],label='near-cancellation dimension',lw=1.9)
    ax.set(xlabel='xi',ylabel='numerical dimension',title='Cutoff-dependent ranks along phaseblind branch 0')
    ax.grid(alpha=.3);ax.legend();fig.tight_layout()
    fig.savefig(ROOT/'results'/'phaseblind_rank_changes.png',dpi=175);plt.close(fig)
    arr=read('projection_false_crossings.csv')
    good=[r for r in arr if r['family']==family and r['branch']=='0' and r['kappa']=='original' and float(r['source_cutoff'])==1e-6 and float(r['cancel_cutoff'])==1e-2]
    fig,ax=plt.subplots(figsize=(6.8,6))
    ax.scatter([float(z['full_10D_angle_deg']) for z in good],[float(z['projection_angle_deg']) for z in good],s=10,alpha=.45)
    ax.axhline(1,color='0.5',ls='--',lw=1);ax.axvline(10,color='0.5',ls='--',lw=1)
    ax.set(xlabel='full 10D angle (degrees)',ylabel='projected 2D angle (degrees)',title='Projection cannot certify a shared 10D direction')
    ax.grid(alpha=.2);fig.tight_layout();fig.savefig(ROOT/'results'/'projection_vs_full_angle.png',dpi=175);plt.close(fig)
if __name__=='__main__':main()
