#!/usr/bin/env python3
"""Visualize measured coordinate-dependent tangents without implying spatial rotation."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]/'results'
def rd(name):
    p=R/name
    return list(csv.DictReader(p.open())) if p.exists() else []
P=rd('equal_projection_tangent_pairs.csv'); T=rd('tangent_trace_selected.csv')
if not P:raise RuntimeError('No measured pairs')
# Metric sensitivity: same physical events, very different chart-angle definitions.
fig,ax=plt.subplots(figsize=(8,5))
x=np.asarray([float(r['sigma_out'])-float(r['sigma_in']) for r in P]);order=np.argsort(x)
for col,label in [('angle_5d_deg_native','5D native'),('angle_5d_deg_span','5D span-scaled'),('angle_10d_deg_native','10D native'),('angle_10d_deg_span','10D span-scaled')]:
    y=np.asarray([float(r[col]) for r in P]);ax.plot(x[order],y[order],'.-',alpha=.65,label=label)
ax.set(xlabel='Normalized time separation Δσ',ylabel='Angle between endpoint tangents (degrees)',title='Same passages, different declared chart metrics')
ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(R/'tangent_metric_sensitivity.png',dpi=160);plt.close(fig)
# The outgoing x direction opposes the incoming one even if full 5D directions are oblique.
fig,ax=plt.subplots(figsize=(8,5))
for kind,marker in [('original','o'),('autonomous','x')]:
    rows=[r for r in P if r['kappa_kind']==kind]
    ax.scatter([float(r['sigma_in']) for r in rows],[float(r['angle_5d_deg_span']) for r in rows],label=kind,marker=marker,alpha=.78)
ax.set(xlabel='Entry phase σ',ylabel='Full 5D endpoint-tangent angle (degrees)',title='Equal-x return: x reverses, hidden-state tangents do not need to')
ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(R/'equal_x_tangent_orientation.png',dpi=160);plt.close(fig)
# Selected same-x projected arc with tangents oriented at the endpoints.
rows=[r for r in T if r['kappa_kind']=='original' and abs(float(r['ramp_xi'])-.24)<1e-9 and r['shape']=='beta:2:2']
if rows:
    xs=np.array([float(r['x']) for r in rows]);ys=np.array([float(r['theta1']) for r in rows]);
    fig,ax=plt.subplots(figsize=(7,5));ax.plot(xs,ys,'-',label='Dynamical projected passage')
    xspan=max(np.ptp(xs),1e-12);yspan=max(np.ptp(ys),1e-12)
    for i,n in [(2,'entry'),(-3,'return')]:
        vx=float(rows[i]['dx_dxi']);vy=float(rows[i]['dtheta1_dxi'])
        v=np.array([vx/xspan,vy/yspan]);v=v/np.linalg.norm(v)
        ax.annotate('',xy=(xs[i]+xspan*.065*v[0],ys[i]+yspan*.065*v[1]),
                    xytext=(xs[i]-xspan*.065*v[0],ys[i]-yspan*.065*v[1]),
                    arrowprops={'arrowstyle':'->','lw':2})
        ax.annotate(n,(xs[i],ys[i]),xytext=(5,9),textcoords='offset points')
    ax.set(xlabel='x (projected locus)',ylabel='θ₁ (radians)',title='Same x, distinct posture and crossing direction')
    ax.grid(alpha=.2);fig.tight_layout();fig.savefig(R/'selected_equal_projection_crossing.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.8))
    ss=np.array([float(r['sigma']) for r in rows]);fs=np.array([float(r['fiber_share_span']) for r in rows]);
    ax.plot(ss,fs,label='Hidden-component fraction, span-scaled 5D')
    ax.plot(ss,np.abs(np.array([float(r['dx_dxi']) for r in rows])),label='|dx/dξ| (raw units)')
    ax.set(xlabel='Ramped phase σ',ylabel='Fraction / native rate (distinct units)',title='Internal tangent persists through projected turning')
    ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(R/'hidden_tangent_during_passage.png',dpi=160);plt.close(fig)
print('v18.50b PLOTS_DONE',len(P))
