#!/usr/bin/env python3
"""Generate figures from numerical CSV records, without surrogate curves."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
R=ROOT/'results'
def rows(name):
    with (R/name).open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
c=rows('combined_branch_contacts.csv');fixed=rows('combined_branch_fixed_phase_energy.csv')
base=[x for x in c if x['kappa_kind']=='original']
fig,ax=plt.subplots(figsize=(10,6.5))
for fam in ('phaseblind','phasecov'):
    for b in (0,1):
        rr=sorted([x for x in base if x['family'].startswith(fam) and int(x['branch'])==b],key=lambda x:float(x['ramp_duration_xi']))
        x=np.array([float(z['ramp_duration_xi']) for z in rr]);v=np.array([float(z['minimum_3D_gap']) for z in rr])
        ax.plot(x,v,marker='.',label=f'{fam} / branch {b}')
        i=np.argmin(v);ax.scatter([x[i]],[v[i]],marker='x',s=70,zorder=10)
ax.set(yscale='log',xlabel='Cubic drive-braking duration [xi]',ylabel='Minimum equal-phase 3D shape gap',title='Q550 v18.48w | Branch-specific favorable contact ramps')
ax.grid(alpha=.25);ax.legend(fontsize=9);fig.tight_layout();fig.savefig(R/'branch_contact_refinement.png',dpi=190);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,6.5))
for fam in ('phaseblind','phasecov'):
    for b in (0,1):
        rr=sorted([x for x in base if x['family'].startswith(fam) and int(x['branch'])==b],key=lambda x:float(x['ramp_duration_xi']))
        x=np.array([float(z['ramp_duration_xi']) for z in rr]);v=np.array([float(z['contact_total_q_0p01']) for z in rr])
        ax.plot(x,v,marker='.',label=f'{fam} / branch {b}')
ax.set(xlabel='Cubic drive-braking duration [xi]',ylabel='Total phase interval with shape gap < 0.01 [q]',title='Q550 v18.48w | Contact persistence, same geometric threshold')
ax.grid(alpha=.25);ax.legend(fontsize=9);fig.tight_layout();fig.savefig(R/'branch_contact_width_continuation.png',dpi=190);plt.close(fig)
fig,ax=plt.subplots(figsize=(10,6.5))
for fam in ('phaseblind','phasecov'):
    for b in (0,1):
        rr=sorted([x for x in fixed if x['kappa_kind']=='original' and x['family'].startswith(fam) and int(x['branch'])==b and float(x['common_phase_q'])==.5],key=lambda x:float(x['ramp_duration_xi']))
        x=np.array([float(z['ramp_duration_xi']) for z in rr]);v=np.array([float(z['return_cumulative_drive_work']) for z in rr])
        ax.plot(x,v,marker='.',label=f'{fam} / branch {b}')
ax.axhline(0,color='black',linewidth=.8)
ax.set(xlabel='Cubic drive-braking duration [xi]',ylabel='Cumulative signed drive work at q = 0.50',title='Q550 v18.48w | Individual work signs are not the ensemble median')
ax.grid(alpha=.25);ax.legend(fontsize=9);fig.tight_layout();fig.savefig(R/'branch_work_sign_q050.png',dpi=190);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,6.5))
for fam in ('phaseblind','phasecov'):
    for b in (0,1):
        rr=[x for x in base if x['family'].startswith(fam) and int(x['branch'])==b]
        dist=np.array([float(z['minimum_3D_gap']) for z in rr]);width=np.array([float(z['contact_total_q_0p01']) for z in rr])
        ax.scatter(dist,width,s=28,alpha=.7,label=f'{fam} / branch {b}')
ax.set(xscale='log',xlabel='Minimum shape gap (3D)',ylabel='Total contact width in phase q, threshold = 0.01',title='Q550 v18.48w | Depth and width are different contact objectives')
ax.grid(alpha=.25);ax.legend(fontsize=9);fig.tight_layout();fig.savefig(R/'branch_contact_depth_width_tradeoff.png',dpi=190);plt.close(fig)
print('Saved four figures from verified physical data')
