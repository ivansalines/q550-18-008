#!/usr/bin/env python3
"""Reproducible plots from actual Y and Z numerical datasets only."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results';Y=ROOT/'inputs'

def save(name):
    plt.tight_layout()
    plt.savefig(R/name,dpi=190,facecolor='white')
    plt.close()

p=pd.read_csv(R/'continuous_11D_root_validation.csv')
fig,ax=plt.subplots(figsize=(9,5.5))
for (kind,ramp),g in p.groupby(['kappa_kind','ramp_duration_xi']):
    g=g.sort_values('delta_B_minus_threshold')
    ax.plot(g.delta_B_minus_threshold,g.ratio_I_dense_IVP,marker='.',alpha=.65,
            linewidth=1.1,label=f'{kind} {ramp:.3f}')
ax.axhline(1,ls='--',lw=1,color='black',alpha=.6)
ax.set_xlabel('Barrier excess  B - epsilon')
ax.set_ylabel('Contract ratio  |C| G^2 / (8 (B - epsilon))')
ax.set_title('Q550 v18.48z: direct dense-11D contract-ratio convergence')
ax.grid(alpha=.2)
ax.legend(fontsize=7,ncol=3)
save('contract_ratio_direct_11d.png')

fig,ax=plt.subplots(figsize=(9,5.5))
for col,label in [('quadratic_relative_gap_error','Quadratic Taylor'),
                  ('quartic_relative_gap_error','Quartic polynomial'),
                  ('sextic_relative_gap_error','Sixth-order polynomial')]:
    g=p.groupby('delta_B_minus_threshold')[col].agg(['median','max']).sort_index()
    ax.loglog(g.index,g['median'],marker='o',label=f'{label}: median')
    ax.loglog(g.index,g['max'],marker='.',ls=':',label=f'{label}: max')
ax.set_xlabel('Barrier excess B - epsilon')
ax.set_ylabel('Relative width prediction error')
ax.set_title('Q550 v18.48z: independent continuous-root validation')
ax.grid(alpha=.25,which='both');ax.legend(fontsize=8)
save('normal_form_error_orders.png')

fig,ax=plt.subplots(figsize=(8.5,6))
for kind,g in p.groupby('kappa_kind'):
    ax.scatter(g.true_dense_IVP_gap_q,g.quartic_jet_gap_q,s=22,label=kind,alpha=.7)
lo=min(p.true_dense_IVP_gap_q.min(),p.quartic_jet_gap_q.min());hi=max(p.true_dense_IVP_gap_q.max(),p.quartic_jet_gap_q.max())
ax.plot([lo,hi],[lo,hi],color='black',ls='--',lw=1,label='Exact equality')
ax.set_xlabel('Observed gap from 11D dense-IVP roots (q)')
ax.set_ylabel('Predicted gap from local quartic jet (q)')
ax.set_title('Contact-contract: independently measured vs predicted')
ax.grid(alpha=.2);ax.legend()
save('quartic_predicted_vs_true_gap.png')

fig,ax=plt.subplots(figsize=(9,5.5))
cr=pd.read_csv(Y/'v18_48y_critical_threshold_curve.csv')
for kind,g in cr.groupby('kappa_kind'):
    g=g.sort_values('threshold')
    ax.plot(g['secant_interpolated_ramp'],g['threshold'],marker='o',label=kind)
ax.set_xlabel('Critical ramp  r (xi)')
ax.set_ylabel('Contact threshold epsilon')
ax.set_title('Authenticated parent Y: phaseblind branch0 level-set bridge')
ax.grid(alpha=.25);ax.legend()
save('parent_y_critical_threshold_curve.png')

fig,ax=plt.subplots(figsize=(9,5.5))
jet=pd.read_csv(R/'normal_form_jets.csv')
for kind,g in jet[(jet.degree==4) & (jet.window_q==.012)].groupby('kappa_kind'):
    g=g.sort_values('ramp_duration_xi')
    ax.plot(g.ramp_duration_xi,g.fitted_cubic,marker='o',label=f'{kind}  third derivative')
ax.axhline(0,color='black',ls='--',lw=1)
ax.set_xlabel('Ramp duration (xi)')
ax.set_ylabel('Local cubic derivative  d^3(d3) / dq^3')
ax.set_title('Fitted cubic asymmetry is not an invariant constant')
ax.grid(alpha=.2);ax.legend()
save('barrier_cubic_asymmetry_vs_ramp.png')
print('Generated five authentic Y/Z numerical charts.')
