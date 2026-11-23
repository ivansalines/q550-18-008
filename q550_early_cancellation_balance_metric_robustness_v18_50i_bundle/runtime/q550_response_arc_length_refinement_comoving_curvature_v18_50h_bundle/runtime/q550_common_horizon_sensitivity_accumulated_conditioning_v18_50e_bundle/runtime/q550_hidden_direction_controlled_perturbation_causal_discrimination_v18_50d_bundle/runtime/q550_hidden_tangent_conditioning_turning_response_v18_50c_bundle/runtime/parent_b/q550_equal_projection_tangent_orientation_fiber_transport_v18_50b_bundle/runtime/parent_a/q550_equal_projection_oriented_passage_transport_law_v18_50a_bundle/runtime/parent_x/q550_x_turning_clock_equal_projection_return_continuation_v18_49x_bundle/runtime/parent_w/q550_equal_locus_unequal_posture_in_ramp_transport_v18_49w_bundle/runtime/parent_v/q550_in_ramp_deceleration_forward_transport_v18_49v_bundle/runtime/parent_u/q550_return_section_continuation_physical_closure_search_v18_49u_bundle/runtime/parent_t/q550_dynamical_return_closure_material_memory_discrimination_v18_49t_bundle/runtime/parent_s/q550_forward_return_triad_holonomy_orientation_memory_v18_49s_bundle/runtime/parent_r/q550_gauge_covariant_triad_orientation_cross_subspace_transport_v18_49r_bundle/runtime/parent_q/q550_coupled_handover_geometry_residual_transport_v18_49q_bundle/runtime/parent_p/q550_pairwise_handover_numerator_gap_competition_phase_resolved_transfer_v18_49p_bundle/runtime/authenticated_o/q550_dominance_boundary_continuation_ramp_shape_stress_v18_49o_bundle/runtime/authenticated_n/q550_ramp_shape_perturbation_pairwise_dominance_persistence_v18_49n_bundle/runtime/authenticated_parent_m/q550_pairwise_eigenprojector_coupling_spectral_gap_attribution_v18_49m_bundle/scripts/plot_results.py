"""Figures generated only from authentic 11D/10D replay data."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1]/'results'
def read(file):
 with (P/file).open(newline='') as f:return list(csv.DictReader(f))
rows=read('pairwise_generator_phase_profiles.csv')
select=[r for r in rows if r['kappa_kind']=='original' and float(r['ramp_xi'])==.3]
by_pair={}
for x in select:
 p=(int(x['axis_rank_a']),int(x['axis_rank_b']))
 by_pair.setdefault(p,[]).append(x)
weights={k:float(v[-1]['generator_fraction_sq']) for k,v in by_pair.items()}
top=sorted(weights,key=weights.get,reverse=True)[:8]
fig,axs=plt.subplots(2,1,figsize=(10,8),sharex=True)
for a,b in top:
 pts=by_pair[a,b];q=[float(x['phase_q']) for x in pts]
 axs[0].plot(q,[float(x['omega_abs']) for x in pts],label=f'{a}-{b}')
 axs[1].plot(q,[float(x['generator_fraction_sq']) for x in pts],label=f'{a}-{b}')
axs[0].set_ylabel('|Omega_ij| per q');axs[1].set_ylabel('Fraction of ||K||²')
axs[1].set_xlabel('Registered return phase q')
for ax in axs:ax.legend(ncol=4,fontsize=8);ax.grid(alpha=.22)
fig.suptitle('Original kappa, 0.300 ramp: dominant 10D eigenprojector pairs')
fig.tight_layout();fig.savefig(P/'dominant_pairwise_couplings.png',dpi=170);plt.close(fig)
rows=read('pairwise_shapley_comparison.csv')
rr=[r for r in rows if r['kappa_kind']=='original' and float(r['ramp_xi'])==.3]
rr=sorted(rr,key=lambda r:abs(float(r['delta_pair_generator_norm_sq'])),reverse=True)[:12]
labels=[f"{r['axis_rank_a']}-{r['axis_rank_b']}" for r in rr]
x=np.arange(len(rr));fig,ax=plt.subplots(figsize=(11,5))
ax.bar(x-.2,[float(r['numerator_attribution_norm_sq']) for r in rr],width=.4,label='Numerator (symmetric attribution)')
ax.bar(x+.2,[float(r['gap_attribution_norm_sq']) for r in rr],width=.4,label='Inverse-gap (symmetric attribution)')
ax.set_xticks(x,labels);ax.axhline(0,color='gray',lw=.6);ax.legend();ax.grid(alpha=.2,axis='y')
ax.set_ylabel('Contribution to Δ||K||², q .50 -> .65')
ax.set_title('Pairwise algebraic attribution: signed contributions, not forces')
fig.tight_layout();fig.savefig(P/'numerator_vs_gap_pairwise_attribution.png',dpi=170);plt.close(fig)
rows=read('pairwise_case_summary.csv')
fig,axs=plt.subplots(2,1,figsize=(9,7),sharex=True)
for kind in ('original','autonomous'):
 case=sorted((r for r in rows if r['kappa_kind']==kind),key=lambda r:float(r['ramp_xi']))
 rv=[float(r['ramp_xi']) for r in case]
 axs[0].plot(rv,[float(r['numerator_attribution_norm_sq']) for r in case],'-o',label=f'{kind} numerator')
 axs[0].plot(rv,[float(r['gap_attribution_norm_sq']) for r in case],'--o',label=f'{kind} gap')
 axs[1].plot(rv,[float(r['top5_final_pair_share']) for r in case],'-o',label=kind)
axs[0].set_ylabel('Contribution to Δ||K||²');axs[1].set_ylabel('Top 5 pair share at q=.65')
axs[1].set_xlabel('Ramp duration ξ')
for ax in axs:ax.legend(fontsize=9,ncol=2);ax.grid(alpha=.2)
fig.suptitle('12 authenticated Q550 cases: numerator and inverse-gap roles')
fig.tight_layout();fig.savefig(P/'ramp_kappa_attribution.png',dpi=170);plt.close(fig)
print('v18.49m generated three data-backed plots')
