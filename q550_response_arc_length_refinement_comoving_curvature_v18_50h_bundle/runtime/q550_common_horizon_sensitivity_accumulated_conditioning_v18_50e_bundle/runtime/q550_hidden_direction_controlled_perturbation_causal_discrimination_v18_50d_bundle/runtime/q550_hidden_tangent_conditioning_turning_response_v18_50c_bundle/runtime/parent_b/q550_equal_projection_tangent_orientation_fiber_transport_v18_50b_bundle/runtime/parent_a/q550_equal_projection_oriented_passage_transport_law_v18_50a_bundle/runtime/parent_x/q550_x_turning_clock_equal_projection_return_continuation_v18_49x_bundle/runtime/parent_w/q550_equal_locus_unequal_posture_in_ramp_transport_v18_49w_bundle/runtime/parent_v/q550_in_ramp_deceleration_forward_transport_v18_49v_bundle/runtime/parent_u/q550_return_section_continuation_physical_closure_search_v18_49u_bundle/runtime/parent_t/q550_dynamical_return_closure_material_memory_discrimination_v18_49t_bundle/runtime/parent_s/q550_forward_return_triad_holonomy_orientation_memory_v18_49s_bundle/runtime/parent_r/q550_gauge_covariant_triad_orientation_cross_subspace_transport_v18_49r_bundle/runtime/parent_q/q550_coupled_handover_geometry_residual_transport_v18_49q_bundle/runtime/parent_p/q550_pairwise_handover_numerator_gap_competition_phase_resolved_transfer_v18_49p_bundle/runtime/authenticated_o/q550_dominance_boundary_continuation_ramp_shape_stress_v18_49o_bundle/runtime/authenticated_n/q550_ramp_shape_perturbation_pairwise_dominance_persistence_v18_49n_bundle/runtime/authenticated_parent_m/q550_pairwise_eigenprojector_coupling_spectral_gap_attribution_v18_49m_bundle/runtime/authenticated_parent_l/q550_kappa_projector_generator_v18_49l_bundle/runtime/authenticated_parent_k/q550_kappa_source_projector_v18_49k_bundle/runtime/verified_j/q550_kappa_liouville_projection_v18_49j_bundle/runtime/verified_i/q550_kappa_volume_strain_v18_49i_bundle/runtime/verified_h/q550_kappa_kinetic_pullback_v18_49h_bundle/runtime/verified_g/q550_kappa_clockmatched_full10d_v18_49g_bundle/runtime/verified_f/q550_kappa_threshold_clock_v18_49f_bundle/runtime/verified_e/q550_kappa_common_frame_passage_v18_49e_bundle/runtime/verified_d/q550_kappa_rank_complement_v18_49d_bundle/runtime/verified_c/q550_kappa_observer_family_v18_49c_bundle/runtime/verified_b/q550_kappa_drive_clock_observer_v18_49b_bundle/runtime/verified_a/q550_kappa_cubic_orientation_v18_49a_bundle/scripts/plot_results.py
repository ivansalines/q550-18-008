#!/usr/bin/env python3
"""Plots from authentic physical Y/Z profile samples and exact chart transforms."""
from pathlib import Path
import csv
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
R=Path(__file__).resolve().parents[1]/'results'
def data(name):
    with (R/name).open() as f:return list(csv.DictReader(f))
def cv(row,key):return float(row[key])

gauges=data('independent_chart_jet_refits.csv')
fig,ax=plt.subplots(figsize=(9,5.4))
for kind in ('original','autonomous'):
    rows=[x for x in gauges if x['kappa_kind']==kind and x['gauge']=='physical_q']
    rows.sort(key=lambda x:cv(x,'ramp_duration_xi'))
    ax.plot([cv(x,'ramp_duration_xi') for x in rows],[cv(x,'chain_rule_cubic_from_authentic_Z_jet') for x in rows],marker='o',label=kind+' · drive-calibrated q')
ax.axhline(0,color='grey',linewidth=.7)
ax.set(xlabel='Smooth-reversal ramp duration [xi]',ylabel='Cubic Taylor coefficient [phase q^-3]',title='Q550 · phase-calibrated barrier skew across drive histories')
ax.grid(alpha=.25);ax.legend();fig.tight_layout()
fig.savefig(R/'physical_cubic_vs_ramp.png',dpi=180);plt.close(fig)

fig,ax=plt.subplots(figsize=(9,5.4))
rows=[x for x in gauges if x['kappa_kind']=='original' and abs(cv(x,'ramp_duration_xi')-.296333)<1e-8]
names=['reversed_chart','monotone_skew_flip','locally_cubic_free','physical_q','monotone_skew_boost']
for name in names:
    x=next(t for t in rows if t['gauge']==name)
    ax.plot([name],[cv(x,'chain_rule_cubic_from_authentic_Z_jet')],marker='o',markersize=9)
ax.axhline(0,color='grey',linewidth=.8)
ax.set(ylabel='Cubic coefficient in chosen chart',title='The raw cubic changes sign or vanishes without changing the 11D IVP')
ax.tick_params(axis='x',rotation=22);ax.grid(axis='y',alpha=.25);fig.tight_layout()
fig.savefig(R/'cubic_skew_coordinate_counterfactual.png',dpi=180);plt.close(fig)

chart=data('chart_counterfactuals.csv')
fig,ax=plt.subplots(figsize=(9,5.4))
for kind in ('original','autonomous'):
    for chart_name in ('physical_q','monotone_skew_flip','locally_cubic_free'):
        rows=[x for x in chart if x['kappa_kind']==kind and abs(cv(x,'ramp_duration_xi')-.296333)<1e-8 and x['gauge']==chart_name]
        rows.sort(key=lambda x:cv(x,'delta'))
        ax.plot([cv(x,'delta') for x in rows],[cv(x,'charted_midpoint_shift') for x in rows],marker='o',label=f'{kind} / {chart_name}')
ax.axhline(0,color='grey',linewidth=.7)
ax.set(xlabel='Barrier height minus threshold [delta]',ylabel='Raw midpoint offset in chosen phase chart',title='Same authentic 11D roots, different chart midpoint asymmetries')
ax.grid(alpha=.25);ax.legend(fontsize=8,ncol=2);fig.tight_layout()
fig.savefig(R/'root_midpoint_gauge_dependence.png',dpi=180);plt.close(fig)

fig,ax=plt.subplots(figsize=(9,5.4))
xx=[];yy=[]
for row in gauges:
    xx.append(cv(row,'chain_rule_cubic_from_authentic_Z_jet'));yy.append(cv(row,'fitted_cubic_from_authentic_11D_Y_profile'))
low=min(xx+yy);high=max(xx+yy)
ax.scatter(xx,yy,alpha=.6,s=24)
ax.plot([low,high],[low,high],'k--',linewidth=1)
ax.set(xlabel='Predicted cubic by coordinate chain rule',ylabel='Fitted cubic from independent 11D phase profiles',title='Direct chart refits check the analytic transformation law')
ax.grid(alpha=.25);fig.tight_layout()
fig.savefig(R/'chart_chainrule_independent_fit.png',dpi=180);plt.close(fig)
print('Plotted four authenticated Q550 v18.49a figures')
