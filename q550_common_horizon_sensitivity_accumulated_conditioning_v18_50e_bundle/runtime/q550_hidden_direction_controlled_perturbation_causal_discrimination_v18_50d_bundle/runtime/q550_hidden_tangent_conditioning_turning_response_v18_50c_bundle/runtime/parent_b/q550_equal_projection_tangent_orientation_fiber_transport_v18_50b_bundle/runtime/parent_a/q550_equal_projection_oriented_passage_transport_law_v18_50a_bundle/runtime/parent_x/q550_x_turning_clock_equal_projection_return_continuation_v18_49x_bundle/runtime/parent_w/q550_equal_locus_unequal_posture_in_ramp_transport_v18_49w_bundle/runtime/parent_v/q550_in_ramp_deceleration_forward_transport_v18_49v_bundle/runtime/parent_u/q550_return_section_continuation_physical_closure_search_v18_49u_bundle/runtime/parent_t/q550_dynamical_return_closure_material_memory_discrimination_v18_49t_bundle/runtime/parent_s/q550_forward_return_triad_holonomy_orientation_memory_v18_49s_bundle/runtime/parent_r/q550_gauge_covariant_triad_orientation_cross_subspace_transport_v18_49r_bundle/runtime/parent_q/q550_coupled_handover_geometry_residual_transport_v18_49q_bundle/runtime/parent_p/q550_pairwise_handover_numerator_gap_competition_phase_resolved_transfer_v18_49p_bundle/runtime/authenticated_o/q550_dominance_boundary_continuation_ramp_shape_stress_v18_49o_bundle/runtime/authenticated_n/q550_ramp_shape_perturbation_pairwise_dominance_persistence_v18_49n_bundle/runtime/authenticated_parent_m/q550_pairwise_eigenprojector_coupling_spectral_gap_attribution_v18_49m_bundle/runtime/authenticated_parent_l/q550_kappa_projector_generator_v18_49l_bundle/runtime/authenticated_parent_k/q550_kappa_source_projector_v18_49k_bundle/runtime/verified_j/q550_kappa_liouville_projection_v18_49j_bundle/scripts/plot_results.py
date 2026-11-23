#!/usr/bin/env python3
"""Reproduce v18.49j figures from authenticated numerical CSV results."""
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
RES=ROOT/'results'
def load(name):return pd.read_csv(RES/name)
def run():
    pair=load('clockmatched_kappa_cancellation.csv')
    fig,ax=plt.subplots(figsize=(9,5.5))
    x=pair['ramp_xi'].to_numpy();scale=1000
    ax.plot(x,scale*pair['delta_integrated_trace'],marker='o',label='Delta integrated solver divergence')
    ax.plot(x,scale*pair['delta_kinetic_density'],marker='s',label='Delta kinetic density endpoints')
    ax.plot(x,scale*pair['delta_log_volume'],marker='^',label='Delta physical log-volume')
    ax.axhline(0,lw=.7,color='gray');ax.set(xlabel='Reversal ramp [xi]',ylabel='Difference × 1000',title='v18.49j — Kappa contrast: integrated source cancellation')
    ax.legend();ax.grid(alpha=.25);fig.tight_layout();fig.savefig(RES/'kappa_integrated_source_cancellation.png',dpi=165);plt.close(fig)
    ins=load('instantaneous_volume_sources.csv')
    fig,axs=plt.subplots(2,1,figsize=(9,8),sharex=True)
    u=ins[(ins.kappa_kind=='autonomous')&(np.isclose(ins.ramp_xi,.3))].sort_values('phase_q')
    o=ins[(ins.kappa_kind=='original')&(np.isclose(ins.ramp_xi,.3))].sort_values('phase_q')
    q=u.phase_q.to_numpy()
    for column,label in [('div_solver_trace','Delta solver divergence'),('kinetic_density_derivative','Delta kinetic density rate'),('physical_volume_source','Delta total source')]:
        delta=u[column].to_numpy()-o[column].to_numpy()
        axs[0].plot(q,delta*1e3,label=label)
        axs[1].plot(q,delta*1e6,label=label)
    axs[0].set_ylabel('Local source delta × 1000')
    axs[1].set_ylabel('Local source delta × 10^6');axs[1].set_xlabel('Clock-matched phase q')
    axs[0].legend(loc='upper right',fontsize=8);axs[1].legend(loc='lower left',fontsize=8)
    for ax in axs:ax.grid(alpha=.25)
    fig.suptitle('v18.49j — Pointwise cancellation is not only an endpoint effect')
    fig.tight_layout();fig.savefig(RES/'instantaneous_kappa_source_cancellation.png',dpi=165);plt.close(fig)
    occupation=load('ten_axis_occupation_and_split.csv')
    s=occupation[(occupation.kappa_kind=='original')&(np.isclose(occupation.ramp_xi,.3))]
    fig,axs=plt.subplots(2,1,figsize=(9,8),sharex=False)
    for rank in [1,3,8,10]:
        r=s[s.axis_rank==rank].sort_values('phase_q')
        axs[0].plot(r.phase_q,r.occupation*100,label=f'Axis {rank}')
    at=s[np.isclose(s.phase_q,.50)].sort_values('axis_rank')
    ranks=at.axis_rank.to_numpy()
    w=.36
    axs[1].bar(ranks-w/2,at.directional_rate,width=w,label='Moving material direction')
    axs[1].bar(ranks+w/2,at.axis_rotation_rate,width=w,label='Moving eigenprojector')
    axs[0].set_ylabel('Squared direction occupation [%]');axs[0].set_xlabel('Clock-matched phase q');axs[0].legend(ncol=4)
    axs[1].set(xlabel='Principal strain axis rank',ylabel='Contribution to occupation rate / q')
    axs[1].set_xticks(ranks);axs[1].legend()
    for ax in axs:ax.grid(alpha=.2)
    fig.suptitle('v18.49j — What changes when a strain-axis occupation changes?')
    fig.tight_layout();fig.savefig(RES/'direction_vs_eigenprojector_occupation.png',dpi=165);plt.close(fig)
    counter=load('counterfactual_volume_forms.csv')
    fig,ax=plt.subplots(figsize=(9,5.5))
    for rv in [.285,.3,.309]:
        s=counter[np.isclose(counter.ramp_xi,rv)].pivot(index='alpha',columns='kappa_kind',values='log_volume_alternate')
        d=s['autonomous']-s['original']
        ax.plot(d.index,d*1e6,marker='o',label=f'Ramp {rv:.3f}')
    ax.axhline(0,color='gray',lw=.7)
    ax.set(xlabel='Additional volume density weight alpha',ylabel='Delta log-volume between kappa values [×10⁻⁶]',
           title='v18.49j — Near-cancellation depends on the declared volume form')
    ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(RES/'volume_form_counterfactual.png',dpi=165);plt.close(fig)
if __name__=='__main__':run()
