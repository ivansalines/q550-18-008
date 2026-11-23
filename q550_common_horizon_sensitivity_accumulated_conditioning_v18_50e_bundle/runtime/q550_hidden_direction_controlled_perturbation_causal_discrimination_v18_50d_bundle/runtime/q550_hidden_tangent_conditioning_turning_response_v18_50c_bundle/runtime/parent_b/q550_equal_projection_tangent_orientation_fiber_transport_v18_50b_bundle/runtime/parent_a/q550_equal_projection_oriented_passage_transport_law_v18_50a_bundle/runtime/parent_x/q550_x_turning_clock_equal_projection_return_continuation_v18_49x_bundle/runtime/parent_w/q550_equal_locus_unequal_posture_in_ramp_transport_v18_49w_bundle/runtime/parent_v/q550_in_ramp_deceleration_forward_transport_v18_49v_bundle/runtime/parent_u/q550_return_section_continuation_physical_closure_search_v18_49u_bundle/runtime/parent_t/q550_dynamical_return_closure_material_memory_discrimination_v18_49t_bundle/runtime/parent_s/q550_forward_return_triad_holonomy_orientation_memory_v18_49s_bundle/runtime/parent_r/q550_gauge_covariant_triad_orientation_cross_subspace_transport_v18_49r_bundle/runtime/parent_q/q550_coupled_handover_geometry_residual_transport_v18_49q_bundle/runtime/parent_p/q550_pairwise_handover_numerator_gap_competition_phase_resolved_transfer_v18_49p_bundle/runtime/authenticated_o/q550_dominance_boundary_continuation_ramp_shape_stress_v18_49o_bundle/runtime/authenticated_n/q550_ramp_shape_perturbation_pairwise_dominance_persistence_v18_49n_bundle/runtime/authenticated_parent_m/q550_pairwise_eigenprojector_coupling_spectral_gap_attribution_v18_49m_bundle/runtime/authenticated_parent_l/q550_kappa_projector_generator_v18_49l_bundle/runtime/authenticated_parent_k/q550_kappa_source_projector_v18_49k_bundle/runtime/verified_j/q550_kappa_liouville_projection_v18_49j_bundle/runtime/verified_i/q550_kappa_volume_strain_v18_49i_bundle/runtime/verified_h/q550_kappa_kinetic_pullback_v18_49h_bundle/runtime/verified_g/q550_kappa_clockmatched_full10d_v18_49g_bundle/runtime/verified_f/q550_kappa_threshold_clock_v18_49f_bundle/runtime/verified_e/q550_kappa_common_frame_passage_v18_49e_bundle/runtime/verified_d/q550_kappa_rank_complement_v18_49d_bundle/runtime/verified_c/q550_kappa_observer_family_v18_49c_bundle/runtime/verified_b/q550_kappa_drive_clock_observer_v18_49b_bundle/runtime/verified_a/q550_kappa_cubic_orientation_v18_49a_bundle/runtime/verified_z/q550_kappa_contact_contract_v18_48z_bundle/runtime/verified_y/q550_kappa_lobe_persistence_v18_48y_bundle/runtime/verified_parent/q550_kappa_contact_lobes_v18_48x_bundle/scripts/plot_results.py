#!/usr/bin/env python3
"""Plot ONLY computed Q550 v18.48x numerical data (no generated geometry)."""
from __future__ import annotations
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
def rows(name):
    with (OUT/name).open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
P=rows('focus_lobe_profiles.csv')
B=rows('extended_lobe_intervals.csv')
C=rows('critical_barrier_refinement.csv')
G=rows('phase_lobe_summary.csv')
fig,axs=plt.subplots(1,2,figsize=(13,5),sharex=True,sharey=True,constrained_layout=True)
for ax,kind in zip(axs,['original','autonomous']):
    these=[p for p in P if p['kappa_kind']==kind]
    ramps=sorted({float(p['ramp_duration_xi']) for p in these})
    qs=sorted({float(p['common_phase_q']) for p in these})
    mat=np.array([[float(p['geometric_gap_3D']) for p in these if float(p['ramp_duration_xi'])==r] for r in ramps])
    q=np.array(qs);r=np.array(ramps)
    edges=np.r_[r[0]-(r[1]-r[0])/2,(r[:-1]+r[1:])/2,r[-1]+(r[-1]-r[-2])/2]
    qe=np.r_[q[0]-(q[1]-q[0])/2,(q[:-1]+q[1:])/2,q[-1]+(q[-1]-q[-2])/2]
    img=ax.pcolormesh(qe,edges,mat,norm=LogNorm(vmin=.0002,vmax=.10),shading='flat',rasterized=True)
    ax.contour(q,r,mat,levels=[.01],linewidths=1.3,colors=['white'])
    ax.set_xlim(.35,.63);ax.set_ylim(.289,.303)
    ax.set_title(('Original κ₀ = 1/6' if kind=='original' else 'Autonomous κ₀'))
    ax.set_xlabel('Matched return phase q')
    ax.grid(alpha=.12)
axs[0].set_ylabel('Command slowdown duration ξ')
fig.colorbar(img,ax=axs,label='Computed reduced-shape distance d₃ (logarithmic scale)',shrink=.86)
fig.suptitle('Q550 v18.48x — subthreshold lobe merger (white contour d₃ = 0.01)')
fig.savefig(OUT/'phase_ramp_contact_lobe_map.png',dpi=190);plt.close(fig)

fig,axs=plt.subplots(1,2,figsize=(13,5),sharex=True,sharey=True,constrained_layout=True)
selections=[.295,.296,.2965,.29675,.297,.300]
for ax,kind in zip(axs,['original','autonomous']):
    for r in selections:
        subset=[p for p in P if p['kappa_kind']==kind and abs(float(p['ramp_duration_xi'])-r)<1e-9]
        ax.plot([float(p['common_phase_q']) for p in subset],
                [float(p['geometric_gap_3D']) for p in subset],label=f'{r:.5f} ξ',lw=1.4)
    ax.axhline(.01,linestyle='--',linewidth=1,label='d₃ = 0.01')
    ax.set_xlim(.38,.59);ax.set_ylim(0,.029);ax.set_xlabel('Matched phase q')
    ax.set_title(kind);ax.grid(alpha=.2);ax.legend(fontsize=8,ncol=2)
axs[0].set_ylabel('Numerical reduced-shape distance d₃')
fig.suptitle('Inter-lobe barrier descends through the chosen contact threshold')
fig.savefig(OUT/'lobe_barrier_profile.png',dpi=190);plt.close(fig)

fig,ax=plt.subplots(figsize=(9,5),constrained_layout=True)
for kind in ['original','autonomous']:
    cc=sorted([p for p in C if p['kappa_kind']==kind and p.get('is_final_bracket')!='1'],key=lambda z:float(z['ramp_duration_xi']))
    ax.plot([float(z['ramp_duration_xi']) for z in cc],
            [float(z['barrier_minus_threshold']) for z in cc],marker='.',label=kind)
ax.axhline(0,linestyle='--',linewidth=1)
ax.set_xlabel('Slowdown duration ξ');ax.set_ylabel('Inter-lobe barrier distance − 0.01')
ax.set_title('Sign-bracketed numerical merger for two κ₀ choices')
ax.legend();ax.grid(alpha=.25)
fig.savefig(OUT/'critical_barrier_zero_brackets.png',dpi=190);plt.close(fig)

# Boundary audit: draw old/new phase intervals for remaining original-kappa controls.
fig,ax=plt.subplots(figsize=(11,5),constrained_layout=True)
control=[z for z in G if z['kappa_kind']=='original' and
         not (z['family_short']=='phaseblind' and int(z['branch'])==0)]
control.sort(key=lambda z:(z['family_short'],int(z['branch'])))
for i,z in enumerate(control):
    old=json.loads(z['intervals_parent_json']);new=json.loads(z['intervals_extended_json'])
    for l,h in new:ax.plot([l,h],[i+.1,i+.1],lw=5)
    for l,h in old:ax.plot([l,h],[i-.1,i-.1],lw=2,linestyle='--')
ax.axvline(.312500001,linewidth=1,linestyle=':');ax.axvline(.719999999,linewidth=1,linestyle=':')
ax.set_yticks(range(len(control)),[f"{z['family_short']} {z['branch']}" for z in control]);ax.set_xlim(.1,.9)
ax.set_xlabel('Common phase q');ax.set_title('Extended lobe interval (thick) vs old window (dashed), d₃ < 0.01')
ax.grid(alpha=.2)
fig.savefig(OUT/'phase_boundary_control_other_branches.png',dpi=190);plt.close(fig)
print('Generated four verified-data numerical figures')
