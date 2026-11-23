#!/usr/bin/env python3
"""Render truthful sampled rate/duration/alpha persistence from generated CSVs."""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
def read(file):
    with (OUT/file).open(newline='') as f:return list(csv.DictReader(f))
def main():
    cs=read('protocol_contacts.csv');pp=read('common_phase_profiles.csv');report=json.loads((OUT/'report.json').read_text())
    family=next((x for x in sorted(set(r['family'] for r in cs)) if 'phasecov' in x),cs[0]['family'])
    branch=min(int(r['branch']) for r in cs if r['family']==family)
    kind='original' if any(r['kappa_kind']=='original' for r in cs if r['family']==family and int(r['branch'])==branch) else cs[0]['kappa_kind']
    sub=[r for r in cs if r['family']==family and int(r['branch'])==branch and r['kappa_kind']==kind]
    if not sub:sub=cs
    by_design={d:sorted((r for r in sub if r['design']==d),key=lambda r:float(r['alpha'])) for d in sorted(set(r['design'] for r in sub))}
    fig,ax=plt.subplots(figsize=(10,6))
    for d in ('phaseclosed_slow','phaseclosed_reference','phaseclosed_fast','durationfixed_slow','durationfixed_fast','ratefixed_short','ratefixed_long'):
        rr=by_design.get(d,[])
        if rr:ax.plot([float(r['alpha']) for r in rr],[float(r['phase_locked_min_distance']) for r in rr],marker='o',label=d)
    ax.set_yscale('log');ax.set_xlabel('Partial material velocity reversal alpha')
    ax.set_ylabel('Best same-external-phase 3D shape gap')
    ax.set_title('Q550 v18.48t — sampled protocol sensitivity ('+family+' / '+kind+')')
    ax.legend(fontsize=8,ncol=2);ax.grid(alpha=.25);fig.tight_layout()
    fig.savefig(OUT/'alpha_rate_duration_contact.png',dpi=180);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,6))
    for d,rr in by_design.items():
        ax.plot([float(r['alpha']) for r in rr],[float(r['shape_below_0p005_fraction']) for r in rr],marker='o',label=d)
    ax.set_xlabel('Partial velocity reversal alpha');ax.set_ylabel('Fraction of shared phase grid with shape gap <= 0.005')
    ax.set_ylim(-.03,1.03);ax.set_title('Persistence across the SAME external-phase interval')
    ax.legend(fontsize=8,ncol=2);ax.grid(alpha=.25);fig.tight_layout()
    fig.savefig(OUT/'common_phase_contact_persistence.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(12,5))
    for d,rr in by_design.items():
        al=[float(r['alpha']) for r in rr]
        axes[0].plot(al,[float(r['preparation_energy_jump']) for r in rr],marker='o',label=d)
        axes[1].plot(al,[float(r['min_energy_difference']) for r in rr],marker='o',label=d)
    axes[0].set_title('Energy jump at return preparation')
    axes[1].set_title('Energy gap at same-phase near-contact')
    for ax in axes:ax.set_xlabel('alpha');ax.set_ylabel('Mechanical energy (model units)');ax.grid(alpha=.3)
    axes[1].legend(fontsize=7,ncol=2);fig.tight_layout()
    fig.savefig(OUT/'preparation_jump_vs_return_energy.png',dpi=180);plt.close(fig)
    # One example common-clock sweep, without re-minimizing for each protocol.
    fig,ax=plt.subplots(figsize=(10,6))
    curves=[r for r in pp if r['family']==family and int(r['branch'])==branch and r['kappa_kind']==kind and float(r['alpha'])==1]
    for name in sorted(set(r['design'] for r in curves)):
        rr=sorted((r for r in curves if r['design']==name),key=lambda x:float(x['common_phase_q']))
        ax.plot([float(r['common_phase_q']) for r in rr],[float(r['shape_distance']) for r in rr],label=name)
    ax.set_yscale('log');ax.set_xlabel('Shared external-phase travel q = rate × duration × u')
    ax.set_ylabel('3D shape gap');ax.set_title('Same phase, different counterflow protocol (alpha=1)')
    ax.legend(fontsize=8,ncol=2);ax.grid(alpha=.25);fig.tight_layout()
    fig.savefig(OUT/'shared_phase_profiles_alpha1.png',dpi=180);plt.close(fig)
    print('PLOTS: four v18.48t original-data figures')
if __name__=='__main__':main()
