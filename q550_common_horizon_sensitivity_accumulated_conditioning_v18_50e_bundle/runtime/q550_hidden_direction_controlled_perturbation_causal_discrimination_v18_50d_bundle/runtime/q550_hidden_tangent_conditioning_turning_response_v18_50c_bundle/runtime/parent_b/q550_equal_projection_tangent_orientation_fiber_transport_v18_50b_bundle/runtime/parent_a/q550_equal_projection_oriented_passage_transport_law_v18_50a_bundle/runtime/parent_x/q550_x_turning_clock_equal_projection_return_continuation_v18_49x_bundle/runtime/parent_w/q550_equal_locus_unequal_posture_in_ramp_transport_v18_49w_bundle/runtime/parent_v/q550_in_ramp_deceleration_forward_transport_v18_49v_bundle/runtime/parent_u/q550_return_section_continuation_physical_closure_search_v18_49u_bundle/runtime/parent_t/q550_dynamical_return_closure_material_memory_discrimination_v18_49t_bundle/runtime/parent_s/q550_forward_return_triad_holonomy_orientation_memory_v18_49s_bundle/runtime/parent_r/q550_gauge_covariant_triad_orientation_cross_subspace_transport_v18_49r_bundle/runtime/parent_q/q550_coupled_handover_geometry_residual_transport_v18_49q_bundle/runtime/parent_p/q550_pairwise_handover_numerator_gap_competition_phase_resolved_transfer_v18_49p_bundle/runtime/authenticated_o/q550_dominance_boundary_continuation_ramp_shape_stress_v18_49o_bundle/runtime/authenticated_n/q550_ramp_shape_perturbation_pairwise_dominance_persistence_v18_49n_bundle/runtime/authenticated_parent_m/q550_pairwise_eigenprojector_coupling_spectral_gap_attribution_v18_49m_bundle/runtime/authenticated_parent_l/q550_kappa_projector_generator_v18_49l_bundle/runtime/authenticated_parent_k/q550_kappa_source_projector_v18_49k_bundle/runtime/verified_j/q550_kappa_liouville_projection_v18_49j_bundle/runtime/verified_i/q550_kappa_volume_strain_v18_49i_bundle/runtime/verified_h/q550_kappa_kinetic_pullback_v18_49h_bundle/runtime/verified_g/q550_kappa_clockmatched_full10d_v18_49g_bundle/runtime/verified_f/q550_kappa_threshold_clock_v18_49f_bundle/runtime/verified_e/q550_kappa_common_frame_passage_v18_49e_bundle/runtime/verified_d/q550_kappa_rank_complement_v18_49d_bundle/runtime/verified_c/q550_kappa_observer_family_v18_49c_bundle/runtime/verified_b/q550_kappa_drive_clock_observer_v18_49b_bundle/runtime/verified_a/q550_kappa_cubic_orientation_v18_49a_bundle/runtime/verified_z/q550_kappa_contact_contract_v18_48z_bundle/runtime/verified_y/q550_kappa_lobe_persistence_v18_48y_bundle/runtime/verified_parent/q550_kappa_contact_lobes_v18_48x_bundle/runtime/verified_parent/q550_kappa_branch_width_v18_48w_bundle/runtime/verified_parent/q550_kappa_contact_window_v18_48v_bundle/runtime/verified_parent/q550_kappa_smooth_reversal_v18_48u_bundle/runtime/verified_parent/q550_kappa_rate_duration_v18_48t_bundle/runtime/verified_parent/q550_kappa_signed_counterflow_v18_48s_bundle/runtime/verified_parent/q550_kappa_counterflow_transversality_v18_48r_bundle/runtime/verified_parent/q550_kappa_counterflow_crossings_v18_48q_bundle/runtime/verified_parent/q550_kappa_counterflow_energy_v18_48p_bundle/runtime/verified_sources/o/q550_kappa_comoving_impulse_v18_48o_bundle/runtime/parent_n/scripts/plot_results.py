#!/usr/bin/env python3
"""Plot only measurements written by run_audit.py (no simulated data)."""
import csv,math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results'
def rows(name):
 with (OUT/name).open() as f:return list(csv.DictReader(f))

def keyrows(allrows,family,branch,kappa,cutoff):
 return sorted([r for r in allrows if r['family'].startswith(family) and int(r['branch'])==branch
        and r['kappa']==kappa and float(r['source_cutoff'])==cutoff],key=lambda a:float(a.get('xi',a.get('xi_a',0))))

def figmake(family,branch,cutoff):
 s=rows('rhythm_states.csv');d=rows('rhythm_steps.csv');fig,ax=plt.subplots(3,1,figsize=(10,11),sharex=True,constrained_layout=True)
 for kap in ('original','autonomous'):
  r=keyrows(s,family,branch,kap,cutoff);q=keyrows(d,family,branch,kap,cutoff)
  xi=np.array([float(z['xi']) for z in r]);xd=np.array([(float(z['xi_a'])+float(z['xi_b']))/2 for z in q]);
  col=None if kap=='original' else 'tab:orange'
  ax[0].plot(xi,[float(z['historical_logR']) for z in r],label=kap,color=col)
  ax[1].plot(xd,[float(z['projector_speed_per_xi']) for z in q],label=kap,color=col)
  ax[2].plot(xd,[float(z['historical_observer_speed_deg_per_xi']) for z in q],label=kap,color=col)
 ax[0].set_ylabel('log historical cancellation R')
 ax[1].set_ylabel('projector pace  ||dP||F / dξ')
 ax[2].set_ylabel('historical observer pace [deg / ξ]')
 ax[2].set_xlabel('ξ, inherited true 11D trajectory sections')
 for a in ax:a.grid(alpha=.22);a.legend(loc='best')
 fig.suptitle(f'Q550 v18.48n — {family}, branch {branch} | source cutoff {cutoff:g}\nModel phase clock: dΘ/dξ = 0.8443579154 rad/ξ')
 f=OUT/f'{family}_branch{branch}_rhythm_{str(cutoff).replace("-", "m")}.png'
 fig.savefig(f,dpi=180);plt.close(fig)

def figlag(family,branch,cutoff):
 src=rows('lag_correlations.csv');fig,ax=plt.subplots(figsize=(10,6.2),constrained_layout=True)
 for kap in ('original','autonomous'):
  r=[z for z in src if z['family'].startswith(family) and int(z['branch'])==branch
      and z['kappa']==kap and float(z['source_cutoff'])==cutoff
      and z['signal_pair']=='projector_vs_historical_logR_change']
  if not r:continue
  r.sort(key=lambda z:int(z['lag_steps']))
  ax.plot([float(z['lag_xi']) for z in r],[float(z['correlation']) for z in r],marker='o',label=kap)
 ax.axvline(0,linestyle='--',color='gray',linewidth=1)
 ax.set_xlabel('shift Δξ (positive: logR response later than projector change)')
 ax.set_ylabel('Pearson correlation of local pace signals')
 ax.set_title(f'Q550 v18.48n — short-history exploratory cross-lag\n{family} branch {branch}, cutoff {cutoff:g}')
 ax.grid(alpha=.2);ax.legend()
 fig.savefig(OUT/f'{family}_branch{branch}_lag.png',dpi=180);plt.close(fig)
if __name__=='__main__':
 for family in ('phaseblind','phasecov'):
  for branch in (0,1):figmake(family,branch,1e-6)
  figlag(family,0,1e-6)
