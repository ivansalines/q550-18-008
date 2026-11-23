"""Static data-driven plots for v18.50g."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plot(points, segments, cases, out):
    pick=lambda mode,kind,r,shape,met: sorted((x for x in points if x['mode']==mode and x['kind']==kind and abs(x['ramp_xi']-r)<1e-8 and x['shape']==shape and x['metric']==met),key=lambda x:x['tau'])
    ref=pick('same_seed','original',.24,'beta:2:2','parent_whitened')
    fig,ax=plt.subplots(figsize=(7.8,4.6))
    ax.plot([x['tau'] for x in ref],[x['response_gain'] for x in ref],marker='o',label='Response gain vs evolution coordinate')
    ax.set_xlabel('Evolution horizon Δξ');ax.set_ylabel('||R|| in declared 4D chart');ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'response_gain_over_horizon.png',dpi=165);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.8,4.6))
    for r in (.18,.24,.327375,.5):
        p=pick('same_seed','original',r,'beta:2:2','parent_whitened')
        ax.plot([x['normalized_arc'] for x in p],[100*x['cancellation'] for x in p],marker='o',label='Ramp '+str(r))
    ax.set(xlabel='Normalized accumulated sampled response arc s',ylabel='Endpoint cancellation (%)',title='Cancellation versus co-moving response progress')
    ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'cancellation_vs_response_arc.png',dpi=165);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.8,4.6))
    q=[x for x in segments if x['mode']=='same_seed' and x['kind']=='original' and abs(x['ramp_xi']-.24)<1e-9 and x['shape']=='beta:2:2' and x['metric']=='parent_whitened']
    q.sort(key=lambda x:x['mid_tau'])
    xs=[x['normalized_mid_arc'] for x in q]
    ax.plot(xs,[x['local_signed_advance'] for x in q],marker='o',label='Local signed advance')
    ax.plot(xs,[x['transported_signed_advance'] for x in q],marker='s',label='Transported signed advance')
    ax.plot(xs,[x['segment_length'] for x in q],marker='^',label='Resultant segment chord')
    ax.set(xlabel='Normalized sampled response arc s',ylabel='Signed advance in co-moving chord frame',title='Segmentwise response composition')
    ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'comoving_signed_increment_ledger.png',dpi=165);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.8,4.6))
    cc=[c for c in cases if c['metric']=='parent_whitened' and c['mode']=='same_seed' and c['kind']=='original' and c['shape']=='beta:2:2'];cc.sort(key=lambda x:x['ramp_xi'])
    ax.plot([x['ramp_xi'] for x in cc],[x['arc5'] for x in cc],marker='o',label='5 point arc lower bound')
    ax.plot([x['ramp_xi'] for x in cc],[x['arc3'] for x in cc],marker='o',label='3 point lower bound')
    ax.plot([x['ramp_xi'] for x in cc],[x['arc2'] for x in cc],marker='o',label='Endpoint chord')
    ax.set(xlabel='Ramp duration r',ylabel='Sampled length in 4D response chart',title='Sampling changes measured path length')
    ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'sampling_resolution_lower_bound.png',dpi=165);plt.close(fig)
    fig,ax=plt.subplots(figsize=(7.8,4.6))
    w=[x for x in cases if x['mode']=='same_seed' and x['kind']=='original' and x['shape']=='beta:2:2'];
    for metric in ('parent_whitened','declared_diagonal_stress'):
        cc=sorted((x for x in w if x['metric']==metric),key=lambda x:x['ramp_xi'])
        ax.plot([x['ramp_xi'] for x in cc],[x['arc5'] for x in cc],marker='o',label=metric)
    ax.set(xlabel='Ramp duration r',ylabel='Sampled arc length in selected chart',title='Explicit sensitivity to metric choice')
    ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(out/'metric_arc_length_control.png',dpi=165);plt.close(fig)
