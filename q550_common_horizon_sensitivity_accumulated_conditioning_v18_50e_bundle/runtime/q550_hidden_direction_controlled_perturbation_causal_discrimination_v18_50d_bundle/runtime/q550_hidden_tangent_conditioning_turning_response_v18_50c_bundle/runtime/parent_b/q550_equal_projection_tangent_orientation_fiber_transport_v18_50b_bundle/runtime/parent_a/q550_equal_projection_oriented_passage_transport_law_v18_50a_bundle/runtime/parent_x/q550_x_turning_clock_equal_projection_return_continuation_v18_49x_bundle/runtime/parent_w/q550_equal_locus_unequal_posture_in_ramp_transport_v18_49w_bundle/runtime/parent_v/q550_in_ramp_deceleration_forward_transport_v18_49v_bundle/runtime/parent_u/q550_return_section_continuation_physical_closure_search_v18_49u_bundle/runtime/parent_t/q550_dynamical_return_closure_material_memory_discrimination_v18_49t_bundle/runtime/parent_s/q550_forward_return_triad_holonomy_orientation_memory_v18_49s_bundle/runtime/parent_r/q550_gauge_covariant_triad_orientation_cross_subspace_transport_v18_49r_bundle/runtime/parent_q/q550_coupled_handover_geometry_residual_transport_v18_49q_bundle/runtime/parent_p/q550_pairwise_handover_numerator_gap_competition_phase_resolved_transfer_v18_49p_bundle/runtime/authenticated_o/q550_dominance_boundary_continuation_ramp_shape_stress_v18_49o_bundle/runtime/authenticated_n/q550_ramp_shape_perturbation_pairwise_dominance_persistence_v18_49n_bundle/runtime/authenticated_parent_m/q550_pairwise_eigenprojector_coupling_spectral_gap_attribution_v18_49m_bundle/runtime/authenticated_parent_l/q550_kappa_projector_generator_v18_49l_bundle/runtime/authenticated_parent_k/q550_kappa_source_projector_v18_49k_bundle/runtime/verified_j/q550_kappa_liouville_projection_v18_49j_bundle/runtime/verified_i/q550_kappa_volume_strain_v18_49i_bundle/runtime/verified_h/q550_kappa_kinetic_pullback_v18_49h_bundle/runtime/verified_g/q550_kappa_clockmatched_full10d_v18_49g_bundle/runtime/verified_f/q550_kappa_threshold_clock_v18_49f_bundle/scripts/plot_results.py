#!/usr/bin/env python3
"""Diagnostic plots rendered solely from v18.49f numeric CSV outputs."""
from pathlib import Path
import csv,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1]/'results'
def rows(name):
 with (R/name).open(newline='') as f:return list(csv.DictReader(f))
summary=rows('threshold_contact_summary.csv')
passages=rows('threshold_passage_orientation.csv')
profiles=rows('clock_registered_orientation_profiles.csv')
extrema=rows('threshold_extrema.csv')
colors={'original':'tab:blue','autonomous':'tab:orange'}
# 1: phase threshold map
fig,ax=plt.subplots(1,2,figsize=(12,4.6),sharex=True,sharey=True)
for axis,kind in zip(ax,('original','autonomous')):
 sub=[r for r in summary if r['kappa_kind']==kind]
 ramps=sorted(set(float(r['ramp_xi']) for r in sub))
 thresholds=sorted(set(float(r['threshold']) for r in sub))
 arr=np.array([[int(next(r['connected_contact_components'] for r in sub if float(r['ramp_xi'])==rv and float(r['threshold'])==ep)) for ep in thresholds] for rv in ramps])
 im=axis.imshow(arr,aspect='auto',origin='lower',vmin=.5,vmax=2.5,cmap='viridis',extent=[thresholds[0]-.0005,thresholds[-1]+.0005,ramps[0]-.003,ramps[-1]+.003])
 for i,rv in enumerate(ramps):
  for j,eps in enumerate(thresholds):axis.text(eps,rv,str(arr[i,j]),color='white',ha='center',va='center',fontsize=9)
 axis.set_title(f'{kind} κ₀');axis.set_xlabel('Geometric contact threshold ε');axis.set_yticks(ramps)
ax[0].set_ylabel('Drive ramp duration [ξ]')
fig.suptitle('Q550 v18.49f — number of subthreshold contact intervals')
fig.tight_layout();fig.savefig(R/'threshold_persistence_map.png',dpi=170);plt.close(fig)
# 2: angle and off-plane residual with threshold contact passages
fig,ax=plt.subplots(2,1,figsize=(11,8),sharex=True)
for kind in ('original','autonomous'):
 seg=sorted((r for r in profiles if r['kappa_kind']==kind and abs(float(r['ramp_xi'])-.3)<1e-10),key=lambda r:float(r['phase_q']))
 x=np.array([float(r['phase_q']) for r in seg]);ang=np.array([float(r['signed_orientation_in_reference_plane_deg']) for r in seg]);leak=np.array([float(r['off_reference_plane_fraction']) for r in seg]);
 ax[0].plot(x,ang,label=f'{kind} κ₀',lw=2);ax[1].plot(x,leak,label=f'{kind} κ₀',lw=2)
for eps,trans in ((.008,.13),(.01,.07)):
 subset=[r for r in passages if r['kappa_kind']=='original' and abs(float(r['ramp_xi'])-.3)<1e-10 and abs(float(r['threshold'])-eps)<1e-12]
 for i,row in enumerate(subset):
  ax[0].axvspan(float(row['entry_q']),float(row['exit_q']),alpha=trans,color='grey',label=f'ε={eps:g} passages' if i==0 else None)
ax[0].axvline(.35,ls='--',color='grey',lw=.8,label='fixed frame anchor q=0.35')
ax[0].set_ylabel('Signed projected orientation [deg]');ax[0].legend(fontsize=9)
ax[1].set_ylabel('Fraction outside reference 2-plane');ax[1].set_xlabel('Common drive phase q (increases opposite Θ)');ax[1].legend()
fig.suptitle('Q550 v18.49f — the same material orientation, different contact thresholds')
fig.tight_layout();fig.savefig(R/'clock_orientation_and_plane_leakage.png',dpi=180);plt.close(fig)
# 3: rate of change of projected angle over physical phase
fig,axis=plt.subplots(figsize=(10.5,4.5))
for kind in ('original','autonomous'):
 seg=sorted((r for r in profiles if r['kappa_kind']==kind and abs(float(r['ramp_xi'])-.3)<1e-10),key=lambda r:float(r['phase_q']))
 q=np.array([float(r['phase_q']) for r in seg]);rate=np.array([float(r['signed_rate_deg_per_xi']) for r in seg]);
 axis.plot(q,rate,lw=2,label=f'{kind} κ₀')
axis.axhline(0,color='grey',lw=1,ls='--');axis.axvline(.35,color='grey',ls=':',lw=.7)
axis.set_xlabel('Common drive phase q');axis.set_ylabel('d(projected angle)/dq [deg / ξ]');axis.set_title('Clock-registered orientation rate: a sign reversal in the 2-plane projection');axis.legend();fig.tight_layout();fig.savefig(R/'clock_registered_angular_rate.png',dpi=170);plt.close(fig)
# 4: orientation angle and out-of-plane vs duration on passage
fig,axis=plt.subplots(figsize=(10,5))
for kind,marker in (('original','o'),('autonomous','s')):
 for eps,c in ((.008,'tab:green'),(.01,'tab:blue')):
  sub=[r for r in passages if r['kappa_kind']==kind and abs(float(r['threshold'])-eps)<1e-12]
  if sub:
   axis.scatter([float(r['entry_exit_angle_deg']) for r in sub],[float(r['path_total_turn_deg']) for r in sub],
       s=35,marker=marker,color=c,label=f'{kind}, ε={eps:g}',alpha=.8)
axis.plot([0,20],[0,20],color='grey',lw=.8,ls='--',label='straight shortest-angle path')
axis.set_xlim(0,18);axis.set_ylim(0,20);axis.set_xlabel('Entry-to-exit angular separation [deg]');axis.set_ylabel('Total 10D direction turning along passage [deg]');axis.set_title('Total bending vs endpoint angle (same 10D common frame)');axis.legend(fontsize=8);fig.tight_layout();fig.savefig(R/'passage_turn_vs_endpoint_angle.png',dpi=180);plt.close(fig)
# 5: threshold-independent geometric extrema
fig,axis=plt.subplots(figsize=(11,4.5))
for kind in ('original','autonomous'):
 ss=sorted(set(float(r['ramp_xi']) for r in extrema if r['kappa_kind']==kind))
 peak=[]
 for rr in ss:peak.append(max(float(r['shape_distance_3d']) for r in extrema if r['kappa_kind']==kind and float(r['ramp_xi'])==rr and r['kind']=='max'))
 axis.plot(ss,peak,marker='o',label=f'{kind} κ₀')
for eps in (.006,.008,.01,.012,.014):axis.axhline(eps,color='grey',alpha=.45,lw=.8)
axis.set_xlabel('Drive ramp duration [ξ]');axis.set_ylabel('Central barrier height of d₃D');axis.set_title('Threshold-independent barrier maximum and level-dependent merger');axis.legend();fig.tight_layout();fig.savefig(R/'barrier_vs_thresholds.png',dpi=170);plt.close(fig)
print('v18.49f plots written:', len(list(R.glob('*.png'))))
