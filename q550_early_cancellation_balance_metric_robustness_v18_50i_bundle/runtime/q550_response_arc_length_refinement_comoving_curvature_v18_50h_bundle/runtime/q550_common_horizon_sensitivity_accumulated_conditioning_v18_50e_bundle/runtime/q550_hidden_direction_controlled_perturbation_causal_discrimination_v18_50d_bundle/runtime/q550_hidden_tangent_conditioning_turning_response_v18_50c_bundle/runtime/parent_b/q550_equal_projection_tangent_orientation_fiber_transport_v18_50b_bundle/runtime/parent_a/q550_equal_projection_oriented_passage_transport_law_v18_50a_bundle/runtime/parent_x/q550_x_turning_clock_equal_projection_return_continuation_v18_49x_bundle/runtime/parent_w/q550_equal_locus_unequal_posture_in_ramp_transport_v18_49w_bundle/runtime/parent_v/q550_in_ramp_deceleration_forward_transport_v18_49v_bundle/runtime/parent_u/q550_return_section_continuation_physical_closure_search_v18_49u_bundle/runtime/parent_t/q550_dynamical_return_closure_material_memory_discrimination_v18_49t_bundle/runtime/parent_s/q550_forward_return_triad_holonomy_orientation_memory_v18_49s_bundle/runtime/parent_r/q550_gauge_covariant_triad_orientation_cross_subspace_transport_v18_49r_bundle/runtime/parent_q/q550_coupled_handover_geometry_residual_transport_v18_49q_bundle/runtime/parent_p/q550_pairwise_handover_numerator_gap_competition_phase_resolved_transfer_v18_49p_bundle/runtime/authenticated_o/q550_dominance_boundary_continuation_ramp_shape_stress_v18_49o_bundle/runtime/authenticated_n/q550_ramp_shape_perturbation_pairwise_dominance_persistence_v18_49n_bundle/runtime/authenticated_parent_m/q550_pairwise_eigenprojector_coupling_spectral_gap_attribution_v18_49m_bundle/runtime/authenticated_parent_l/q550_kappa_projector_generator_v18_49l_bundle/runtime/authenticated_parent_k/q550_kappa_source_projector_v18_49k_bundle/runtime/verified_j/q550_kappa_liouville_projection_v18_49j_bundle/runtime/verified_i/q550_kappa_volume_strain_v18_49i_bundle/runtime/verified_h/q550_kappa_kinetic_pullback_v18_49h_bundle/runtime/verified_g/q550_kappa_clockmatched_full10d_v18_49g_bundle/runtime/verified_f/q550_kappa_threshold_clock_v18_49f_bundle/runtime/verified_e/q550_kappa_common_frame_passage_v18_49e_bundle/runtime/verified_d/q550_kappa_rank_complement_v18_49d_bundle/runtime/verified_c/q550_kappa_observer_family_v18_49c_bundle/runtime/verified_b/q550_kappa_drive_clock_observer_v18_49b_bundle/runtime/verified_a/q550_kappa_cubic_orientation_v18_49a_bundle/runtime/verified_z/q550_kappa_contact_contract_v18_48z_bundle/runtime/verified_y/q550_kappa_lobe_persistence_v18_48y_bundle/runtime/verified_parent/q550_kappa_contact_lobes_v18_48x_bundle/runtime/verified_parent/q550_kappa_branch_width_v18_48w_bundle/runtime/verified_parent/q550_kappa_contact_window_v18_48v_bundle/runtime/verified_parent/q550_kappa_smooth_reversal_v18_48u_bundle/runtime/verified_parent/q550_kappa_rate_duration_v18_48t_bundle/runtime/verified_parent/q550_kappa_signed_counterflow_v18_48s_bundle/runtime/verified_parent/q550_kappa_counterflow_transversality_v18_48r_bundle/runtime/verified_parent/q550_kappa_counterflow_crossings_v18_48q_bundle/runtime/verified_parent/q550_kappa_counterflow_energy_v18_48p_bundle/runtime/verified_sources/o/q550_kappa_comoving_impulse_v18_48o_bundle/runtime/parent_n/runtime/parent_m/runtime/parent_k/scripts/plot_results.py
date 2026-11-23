#!/usr/bin/env python3
"""Render actual v18.48k observer-space numerical profiles, not illustrations."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results'
with (OUT/'observer_direction_profiles.csv').open(newline='',encoding='utf8') as f:rows=list(csv.DictReader(f))
for family in ('phaseblind','phasecov'):
    fig,ax=plt.subplots(figsize=(10,5))
    for kind in ('original','autonomous'):
        label=f'{family}_xi'+('3.575' if family=='phaseblind' else '4.25')+'_'+kind
        a=[z for z in rows if z['crest']==label]
        if not a:raise ValueError('Missing focal profile '+label)
        xx=[float(z['angle_deg']) for z in a]; yy=[float(z['ratio']) for z in a]
        ax.plot(xx,yy,label=kind,linewidth=2)
    ax.set_yscale('log')
    ax.set_xlabel('Signed observer-covector angle (degrees, original frozen chart)')
    ax.set_ylabel('Hessian cancellation ratio R (log scale)')
    ax.set_title(f'Q550 {family}: historical crest, steepest local observer direction')
    ax.grid(True,alpha=.22)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT/f'{family}_observer_crest_width.png',dpi=180)
    plt.close(fig)

with (OUT/'observer_random_sphere.csv').open(newline='',encoding='utf8') as f:rr=list(csv.DictReader(f))
fig,ax=plt.subplots(figsize=(10,5))
for crest in sorted({z['crest'] for z in rr}):
    a=[z for z in rr if z['crest']==crest]
    ax.plot([float(z['angle_deg']) for z in a], [float(z['median_R']) for z in a],marker='o',label=crest)
ax.set_xscale('log');ax.set_yscale('log')
ax.set_xlabel('Angular radius on historical covector sphere (degrees)')
ax.set_ylabel('Median R among sampled random tangent directions')
ax.set_title('Observer directional perturbation: sampled medians, not certified sphere measure')
ax.grid(True,alpha=.22);ax.legend(fontsize=8)
fig.tight_layout();fig.savefig(OUT/'observer_random_direction_medians.png',dpi=180)
plt.close(fig)
print('PLOTS_WRITTEN 3')
