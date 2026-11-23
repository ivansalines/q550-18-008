"""Render actual 33-point Q550 response and nested arc refinements."""
from collections import defaultdict
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plot(records,points,summary,out):
    by=defaultdict(list)
    for p in points:
        if p['mode']=='same_seed' and p['kind']=='original' and p['shape']=='beta:2:2':
            by[float(p['ramp_xi'])].append(p)
    fig,ax=plt.subplots(figsize=(9,5.2))
    for ramp,ps in sorted(by.items()):
        ps.sort(key=lambda z:z['horizon_xi'])
        ax.plot([p['horizon_xi'] for p in ps],[p['cancellation']*100 for p in ps],label=f'r={ramp:g}')
        pk=max(ps,key=lambda p:p['cancellation'])
        ax.scatter([pk['horizon_xi']],[pk['cancellation']*100],s=25)
    ax.set(xlabel='Common elapsed evolution Δξ',ylabel='Relative vector cancellation (%)',title='Q550 v18.50h — densely sampled cancellation')
    ax.legend();ax.grid(alpha=.25);fig.tight_layout();fig.savefig(out/'dense_cancellation_growth.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.5,5))
    rr=[r for r in records if r['mode']=='same_seed' and r['kind']=='original' and abs(float(r['ramp_xi'])-.24)<1e-9 and r['shape']=='beta:2:2']
    rr.sort(key=lambda r:r['samples'])
    ax.plot([r['samples'] for r in rr],[r['arc_lower_bound'] for r in rr],'-o')
    ax.set(xlabel='Actual integrated response samples',ylabel='Sampled 4D response arc (lower bound)',title='Nested resolution: 5 / 9 / 17 / 33')
    ax.grid(alpha=.25);fig.tight_layout();fig.savefig(out/'arc_refinement_reference.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,5))
    pp=sorted(by.get(.24,[]),key=lambda z:z['horizon_xi'])
    if pp:
        ax.plot([p['arc33_partial'] for p in pp],[100*p['cancellation'] for p in pp],'-o',markersize=2.4)
    ax.set(xlabel='Cumulative sampled response arc (4D)',ylabel='Relative vector cancellation (%)',title='Co-moving cancellation: 33 measured horizons')
    ax.grid(alpha=.25);fig.tight_layout();fig.savefig(out/'cancellation_vs_dense_arc.png',dpi=170);plt.close(fig)

if __name__=='__main__':
    import csv
    root=Path(__file__).resolve().parents[1]/'results'
    def rows(file):
        with (root/file).open() as f:return [{k:(float(v) if k in ('horizon_xi','ramp_xi','arc33_partial','cancellation','samples','arc_lower_bound') else v) for k,v in row.items()} for row in csv.DictReader(f)]
    plot(rows('arc_grid_refinement.csv'),rows('dense_cancellation_trace.csv'),rows('case_summary.csv'),root)
