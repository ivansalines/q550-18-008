"""Recreate four CSV-driven figures; no fabricated or smoothed trajectories."""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];R=ROOT/'results'
def read(name):
 with (R/name).open(newline='') as f:return list(csv.DictReader(f))
def val(rows,key):return np.array([float(a[key]) for a in rows])
profiles=read('common_frame_profiles.csv');passages=read('subthreshold_passage_pairs.csv')
events=read('oriented_passage_events.csv');scale=read('kappa0_marker_scale_tests.csv')
# Geometric lobe markers from genuine IVP root solves; envelope only.
fig,ax=plt.subplots(figsize=(9.5,5.6),constrained_layout=True)
for kind,color,yofs in [('original','tab:blue',0.),('autonomous','tab:orange',.003)]:
 for ramp in sorted(set(float(a['ramp_xi']) for a in events if a['kappa_kind']==kind)):
  rr=[a for a in passages if a.get('kappa_kind')==kind and abs(float(a['ramp_xi'])-ramp)<1e-10]
  for a in rr:
   ax.plot([float(a['entry_q']),float(a['exit_q'])],[ramp+yofs]*2,
      color=color,lw=5,solid_capstyle='round')
 ax.plot([],[],label=kind,color=color,lw=5)
ax.set_xlabel('Common drive-clock phase coordinate q  (post-turn xi)')
ax.set_ylabel('Reversal ramp duration [xi]  (autonomous displaced +0.003 for visibility)')
ax.set_title('Q550: oriented sub-threshold contact intervals, d3 < 0.01')
ax.grid(alpha=.18);ax.legend();fig.savefig(R/'oriented_contact_passages.png',dpi=165);plt.close(fig)
# Common frame and instantaneous norm are DIFFERENT METRICS; label clearly.
fig,ax=plt.subplots(figsize=(9.8,5.7),constrained_layout=True)
for rv,color in [(.285,'tab:blue'),(.296333,'tab:orange'),(.309,'tab:green')]:
 rows=sorted((a for a in profiles if a['kappa_kind']=='original' and abs(float(a['ramp_xi'])-rv)<1e-9),key=lambda a:float(a['phase_q']))
 ax.plot(val(rows,'phase_q'),val(rows,'common_hidden'),'-o',ms=2.6,lw=1.5,color=color,label=f'common frame, ramp {rv}')
 ax.plot(val(rows,'phase_q'),val(rows,'instantaneous_hidden'),'--',lw=1.25,color=color,label=f'fixed chart, ramp {rv}')
ax.set_xlabel('Common drive-clock coordinate q')
ax.set_ylabel('Hidden residual norm (metric and reference explicitly DIFFER)')
ax.set_title('Observer complement: transported common frame versus instantaneous chart')
ax.grid(alpha=.18);ax.legend(ncol=2,fontsize=8);fig.savefig(R/'common_frame_vs_chart_residual.png',dpi=165);plt.close(fig)
# Exactly same transported frame comparison for both time-span probes.
fig,ax=plt.subplots(figsize=(9,5.4),constrained_layout=True)
for kind in ['original','autonomous']:
 for span,style in [('kappa0_interval','-o'),('0p2_interval','--s')]:
  rr=[a for a in scale if a['kappa_kind']==kind and a['span_kind']==span and abs(float(a['q_entry'])-.35)<1e-10]
  rr=sorted(rr,key=lambda a:float(a['ramp_xi']))
  ax.plot(val(rr,'ramp_xi'),val(rr,'hidden_cosine_common_frame'),style,ms=4,
         label=f'{kind} · {span}',lw=1.2)
ax.set_ylim(0,1.04);ax.set_xlabel('Reversal ramp duration [xi]')
ax.set_ylabel('Signed cosine: hidden directions in SAME pulled-back frame')
ax.set_title('Kappa0 and 0.2 xi probes: no closure assumed')
ax.legend(fontsize=8);ax.grid(alpha=.18);fig.savefig(R/'kappa_common_frame_orientation.png',dpi=165);plt.close(fig)
# Check transported frame against physical dual pairing.
fig,ax=plt.subplots(figsize=(9.2,5.4),constrained_layout=True)
for kind in ['original','autonomous']:
 a=[x for x in profiles if x['kappa_kind']==kind]
 if not a:continue
 ax.scatter(val(a,'phase_q'),np.maximum(val(a,'frame_pullback_identity_error'),1e-18),s=12,
  alpha=.70,label=f'{kind}: g(t) Phi(t) - g(0)')
ax.set_yscale('log');ax.set_xlabel('Common clock phase q');ax.set_ylabel('Relative common-frame duality residual')
ax.set_title('Physical tangent/cotangent transport — numerical consistency')
ax.grid(alpha=.18);ax.legend();fig.savefig(R/'common_frame_duality_consistency.png',dpi=165);plt.close(fig)
print('v18.49e: four genuine CSV-derived PNG files generated')
