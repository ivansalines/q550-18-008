#!/usr/bin/env python3
"""Generate visualizations strictly from CSVs produced by run_audit.py."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'results'
def read(name):
 with (O/name).open() as f:return list(csv.DictReader(f))
def family_filter(rows,fam,branch,kappa,cutoff):
 return [r for r in rows if r['family'].startswith(fam) and int(r['branch'])==branch and r['kappa']==kappa and float(r['source_cutoff'])==cutoff]
def main():
 steps=read('phase_steps.csv');lag=read('lag_scans_full.csv');events=read('impulse_stability.csv')
 for family in ('phaseblind','phasecov'):
  fig,ax=plt.subplots(3,1,figsize=(11,10),sharex=True,constrained_layout=True)
  for kind in ('original','autonomous'):
   ss=family_filter(steps,family,0,kind,1e-6);x=np.array([float(s['xi_mid']) for s in ss]);
   ax[0].plot(x,[float(s['raw_projector']) for s in ss],label=f'{kind} fixed')
   ax[0].plot(x,[float(s['comoving_projector']) for s in ss],linestyle='--',label=f'{kind} co-moving')
   ax[1].plot(x,[float(s['signed_logR_rate']) for s in ss],label=kind)
   ax[2].plot(x,[float(s['abs_logR_rate']) for s in ss],label=kind)
  ax[0].set_ylabel('Projector step pace [1/xi]');ax[1].set_ylabel('Signed d logR/dxi');ax[2].set_ylabel('|d logR/dxi|')
  ax[2].set_xlabel('xi, authentic forward Q550 IVP')
  for a in ax:a.legend(fontsize=8);a.grid(alpha=.2)
  fig.suptitle('v18.48o '+family+' branch 0, source cutoff 1e-6\nFixed chart vs discrete projective co-moving frame')
  fig.savefig(O/f'{family}_branch0_comoving_rhythm.png',dpi=160);plt.close(fig)
  fig,ax=plt.subplots(figsize=(10,6),constrained_layout=True)
  for driver in ('raw_projector','comoving_projector'):
   z=[r for r in family_filter(lag,family,0,'original',1e-6) if r['driver']==driver and r['response']=='abs_logR_rate']
   z.sort(key=lambda r:int(r['lag_steps']))
   ax.plot([float(r['lag_xi']) for r in z],[float(r['correlation']) for r in z],marker='o',label=driver)
  ax.axvline(0,color='gray',ls='--',lw=.9);ax.set_xlabel('lag xi; positive means response later')
  ax.set_ylabel('Correlation of unsigned response');ax.set_title(f'v18.48o {family}: co-moving vs fixed-frame lag');ax.grid(alpha=.2);ax.legend()
  fig.savefig(O/f'{family}_branch0_lag_compare.png',dpi=160);plt.close(fig)
 fig,ax=plt.subplots(figsize=(10,5.8),constrained_layout=True)
 filtered=[r for r in family_filter(events,'phasecov',0,'original',1e-6) if r['response']=='abs_logR_rate']
 names=[r['driver'] for r in filtered];scores=[float(r['unchanged_fraction']) for r in filtered]
 ax.bar(names,scores);ax.set_ylim(0,1);ax.set_ylabel('Unchanged best lag after leave-one-pulse-out / total')
 ax.set_title('v18.48o phasecov branch 0: lag stability, original kappa, cutoff 1e-6')
 ax.tick_params(axis='x',rotation=16);fig.savefig(O/'phasecov_impulse_stability.png',dpi=160);plt.close(fig)
if __name__=='__main__':main()
