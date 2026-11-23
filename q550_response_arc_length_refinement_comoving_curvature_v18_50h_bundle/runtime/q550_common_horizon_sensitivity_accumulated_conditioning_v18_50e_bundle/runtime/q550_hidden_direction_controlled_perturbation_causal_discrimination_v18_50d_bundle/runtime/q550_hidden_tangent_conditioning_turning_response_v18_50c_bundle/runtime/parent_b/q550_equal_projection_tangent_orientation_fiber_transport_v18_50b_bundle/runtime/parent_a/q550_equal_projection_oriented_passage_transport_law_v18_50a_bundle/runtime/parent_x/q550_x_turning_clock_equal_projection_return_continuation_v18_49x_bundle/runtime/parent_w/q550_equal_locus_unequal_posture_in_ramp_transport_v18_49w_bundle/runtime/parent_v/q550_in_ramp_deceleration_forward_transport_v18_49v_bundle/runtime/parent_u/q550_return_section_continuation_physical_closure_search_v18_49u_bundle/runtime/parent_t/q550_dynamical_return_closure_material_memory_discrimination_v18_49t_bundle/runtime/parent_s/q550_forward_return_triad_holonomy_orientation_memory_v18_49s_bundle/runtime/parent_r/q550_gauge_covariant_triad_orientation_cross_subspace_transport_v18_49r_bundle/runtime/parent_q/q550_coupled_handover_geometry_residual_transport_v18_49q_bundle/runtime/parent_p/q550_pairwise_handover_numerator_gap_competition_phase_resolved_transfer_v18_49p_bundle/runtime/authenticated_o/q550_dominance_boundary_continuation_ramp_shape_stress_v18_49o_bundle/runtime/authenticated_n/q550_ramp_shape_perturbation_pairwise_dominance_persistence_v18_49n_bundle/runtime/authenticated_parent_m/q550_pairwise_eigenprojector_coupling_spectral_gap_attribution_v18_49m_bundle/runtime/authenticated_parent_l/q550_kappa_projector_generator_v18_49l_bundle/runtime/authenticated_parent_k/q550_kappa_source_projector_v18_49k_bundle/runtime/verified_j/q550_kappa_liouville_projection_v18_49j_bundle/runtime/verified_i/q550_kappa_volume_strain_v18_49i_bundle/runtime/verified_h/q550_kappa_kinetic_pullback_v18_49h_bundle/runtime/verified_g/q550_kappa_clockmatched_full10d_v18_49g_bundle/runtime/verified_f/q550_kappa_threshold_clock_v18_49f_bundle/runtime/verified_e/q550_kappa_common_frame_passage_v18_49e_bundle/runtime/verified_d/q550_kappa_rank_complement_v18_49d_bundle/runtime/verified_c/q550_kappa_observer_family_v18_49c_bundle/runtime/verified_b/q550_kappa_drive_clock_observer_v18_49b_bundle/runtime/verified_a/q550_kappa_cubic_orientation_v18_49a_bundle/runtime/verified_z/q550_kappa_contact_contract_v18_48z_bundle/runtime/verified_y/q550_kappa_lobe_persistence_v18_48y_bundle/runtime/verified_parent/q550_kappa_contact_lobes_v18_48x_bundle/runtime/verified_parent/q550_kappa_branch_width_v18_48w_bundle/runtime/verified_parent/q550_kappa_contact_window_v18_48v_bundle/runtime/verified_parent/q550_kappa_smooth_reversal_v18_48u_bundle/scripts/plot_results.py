#!/usr/bin/env python3
"""Publication-style diagnostics drawn from genuine Q550 outputs."""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
def read(name):
    with (OUT/name).open(newline='') as f:return list(csv.DictReader(f))
def main():
    a=read('phase_locked_contacts.csv');b=read('common_phase_profiles.csv')
    names=['instant','smooth_short','smooth_medium','smooth_long','smoother_medium','stop_dwell']
    fig,ax=plt.subplots(figsize=(11,6))
    for alpha in sorted({float(x['alpha']) for x in a}):
        vals=[]
        for name in names:
            z=[float(x['phase_matched_min_distance_3D']) for x in a if x['drive_design']==name and float(x['alpha'])==alpha]
            vals.append(float(np.median(z)))
        ax.plot(range(len(names)),vals,marker='o',label=f'alpha={alpha:g}')
    ax.set_yscale('symlog',linthresh=.001)
    ax.set_xticks(range(len(names)),names,rotation=20,ha='right')
    ax.set_ylabel('Median best matched-phase 3D distance')
    ax.set_title('Q550 v18.48u | dependence on prescribed clock history')
    ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(OUT/'ramp_contact_comparison.png',dpi=180);plt.close(fig)
    group=[x for x in b if x['family'].startswith('phasecov') and int(x['branch'])==0 and x['kappa_kind']=='original' and float(x['alpha'])==1.]
    fig,ax=plt.subplots(2,1,figsize=(11,8),sharex=True)
    for name in names:
        rows=[x for x in group if x['drive_design']==name]
        if not rows:continue
        q=[float(x['common_phase_q']) for x in rows]
        ax[0].plot(q,[float(x['shape_distance_3D']) for x in rows],label=name)
        ax[1].plot(q,[float(x['energy_difference']) for x in rows],label=name)
    ax[0].set_ylabel('3D geometry gap');ax[1].set_ylabel('Return minus forward mechanical energy')
    ax[1].set_xlabel('Common external phase excursion q')
    ax[0].legend(ncol=3,fontsize=8)
    for aa in ax:aa.grid(alpha=.2)
    fig.suptitle('Q550 | phasecov branch0 original kappa | alpha=1 | equal external phase')
    fig.tight_layout();fig.savefig(OUT/'phasecov_smooth_drive_comparison.png',dpi=180);plt.close(fig)
    print('PLOTS generated: two authentic data figures')
if __name__=='__main__':main()
