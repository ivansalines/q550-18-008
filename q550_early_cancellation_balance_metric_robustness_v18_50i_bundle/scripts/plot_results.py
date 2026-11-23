"""Source plots for v18.50i. All figures are regenerated from source CSV."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def plots(rows,peaks,out):
    fig,ax=plt.subplots(figsize=(9,5.2))
    for kind in ['original','autonomous']:
        a=[r for r in rows if r['kind']==kind and r['metric']=='common_parent_c' and r['epsilon']==.0001 and 0<r['horizon_xi']<=.004]
        ax.plot([r['horizon_xi'] for r in a],[100*r['cancellation'] for r in a],label=kind)
        p=next(q for q in peaks if q['kind']==kind and q['metric']=='common_parent_c' and q['epsilon']==.0001)
        ax.scatter([p['peak_xi']],[100*p['peak_cancellation']],s=22)
    ax.set(xlabel='Elapsed evolution Δξ (model coordinate)',ylabel='Cancellation C (%)',title='v18.50i — early cancellation, two κ₀ families')
    ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'both_kappa_early_cancellation.png',dpi=180);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4.3),sharey=False)
    for idx,kind in enumerate(['original','autonomous']):
        ax=axes[idx]
        for metric in ['common_parent_c','raw_coordinate','angles_weighted_2x','rates_weighted_2x']:
            a=[r for r in rows if r['kind']==kind and r['metric']==metric and r['epsilon']==.0001 and 0<r['horizon_xi']<=.004]
            ax.plot([r['horizon_xi'] for r in a],[100*r['cancellation'] for r in a],label=metric.replace('_',' '))
        ax.set(xlabel='Δξ',ylabel='Cancellation (%)',title=kind);ax.grid(alpha=.2)
    axes[-1].legend(fontsize=7);fig.suptitle('Metric-chart dependence of sampled early cancellation');fig.tight_layout();fig.savefig(out/'metric_chart_early_cancellation.png',dpi=170);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4.3))
    for idx,kind in enumerate(['original','autonomous']):
        ax=axes[idx]
        a=[r for r in rows if r['kind']==kind and r['metric']=='common_parent_c' and r['epsilon']==.0001 and 0<r['horizon_xi']<=.004]
        ax.plot([r['horizon_xi'] for r in a],[r['T_over_L'] for r in a],label='||T|| / ||L||')
        ax.axhline(1,linestyle='--',alpha=.6)
        ax.set(xlabel='Δξ',ylabel='Transport / local norm',title=kind);ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'balance_ratio_early_window.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4.8))
    for kind in ['original','autonomous']:
        for eps in [1e-5,1e-4,1e-3]:
            a=[r for r in rows if r['kind']==kind and r['metric']=='common_parent_c' and r['epsilon']==eps and 0<r['horizon_xi']<=.004]
            ax.plot([r['horizon_xi'] for r in a],[100*r['cancellation'] for r in a],label=f'{kind} ε={eps:g}',alpha=.8)
    ax.set(xlabel='Δξ',ylabel='Cancellation (%)',title='Kick-amplitude stability of the declared vector ledger')
    ax.legend(fontsize=8);ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'amplitude_stability.png',dpi=180);plt.close(fig)
