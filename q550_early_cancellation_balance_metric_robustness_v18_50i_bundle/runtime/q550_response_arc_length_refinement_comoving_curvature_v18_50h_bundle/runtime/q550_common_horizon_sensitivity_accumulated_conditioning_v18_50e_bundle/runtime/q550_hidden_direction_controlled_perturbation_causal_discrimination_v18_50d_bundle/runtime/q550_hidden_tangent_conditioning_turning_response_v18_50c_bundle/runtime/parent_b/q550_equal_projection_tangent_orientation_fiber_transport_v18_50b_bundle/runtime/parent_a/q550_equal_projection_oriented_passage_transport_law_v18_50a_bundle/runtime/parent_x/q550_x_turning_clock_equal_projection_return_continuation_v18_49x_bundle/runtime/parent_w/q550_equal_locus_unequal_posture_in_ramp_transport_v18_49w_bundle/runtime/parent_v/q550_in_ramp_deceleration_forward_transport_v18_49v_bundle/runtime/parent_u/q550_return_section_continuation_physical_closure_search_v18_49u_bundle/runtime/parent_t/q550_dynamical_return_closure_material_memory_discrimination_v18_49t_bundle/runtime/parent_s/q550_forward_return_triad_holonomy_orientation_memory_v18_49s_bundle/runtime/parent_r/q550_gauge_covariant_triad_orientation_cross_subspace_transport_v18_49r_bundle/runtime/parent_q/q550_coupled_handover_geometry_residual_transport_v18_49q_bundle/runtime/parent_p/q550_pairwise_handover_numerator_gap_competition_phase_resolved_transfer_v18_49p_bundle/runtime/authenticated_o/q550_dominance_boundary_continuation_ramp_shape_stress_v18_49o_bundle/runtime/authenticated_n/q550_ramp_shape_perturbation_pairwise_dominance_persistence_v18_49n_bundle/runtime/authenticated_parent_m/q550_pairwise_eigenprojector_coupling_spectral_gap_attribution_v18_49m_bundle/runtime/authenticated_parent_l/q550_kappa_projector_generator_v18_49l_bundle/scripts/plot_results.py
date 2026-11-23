"""Plots computed from the actual 11D/10D outputs, never illustrative data."""
import csv
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1]/'results'
def load(name):
 with (P/name).open() as f:return list(csv.DictReader(f))
rows=load('covariant_generator_phase_profiles.csv')
cases=[r for r in rows if float(r['ramp_xi'])==.3]
fig,axs=plt.subplots(2,1,figsize=(9,7),sharex=True)
for kind in ('original','autonomous'):
 r=[x for x in cases if x['kappa_kind']==kind]
 q=[float(x['phase_q']) for x in r]
 axs[0].plot(q,[float(x['projector_generator_norm']) for x in r],label=f'{kind} kappa')
 axs[1].plot(q,[float(x['offdiagonal_Cdot_fraction']) for x in r],label=f'{kind} kappa')
axs[0].set_ylabel('Generator Frobenius norm / q');axs[1].set_ylabel('Off-diagonal Cdot fraction')
axs[1].set_xlabel('Common return phase q')
for ax in axs:ax.grid(alpha=.2);ax.legend()
fig.suptitle('Authentic Q550 v18.49l: material projector generator')
fig.tight_layout();fig.savefig(P/'generator_and_strain_profile.png',dpi=175);plt.close(fig)
rows=load('principal_strain_projector_phase_profiles.csv')
fig,axs=plt.subplots(2,1,figsize=(9,7),sharex=True)
for rank in (1,3,8,10):
 r=[x for x in rows if x['kappa_kind']=='original' and float(x['ramp_xi'])==.3 and int(x['axis_rank'])==rank]
 q=[float(x['phase_q']) for x in r]
 axs[0].plot(q,[float(x['instantaneous_projector_speed']) for x in r],label=f'axis {rank}')
 axs[1].plot(q,[float(x['stretch_log_derivative']) for x in r],label=f'axis {rank}')
axs[0].set_ylabel('Projector angular speed / q');axs[1].set_ylabel('Principal log-stretch rate / q')
axs[1].set_xlabel('Common return phase q')
for ax in axs:ax.grid(alpha=.2);ax.legend(ncol=2)
fig.suptitle('Projector rotation vs principal stretch rate (original kappa, ramp 0.300)')
fig.tight_layout();fig.savefig(P/'projector_rotation_vs_strain_rate.png',dpi=175);plt.close(fig)
rows=load('ramp_kappa_summary.csv')
fig,axs=plt.subplots(2,1,figsize=(9,7),sharex=True)
for kind in ('original','autonomous'):
 r=[x for x in rows if x['kappa_kind']==kind];rr=np.array([float(x['ramp_xi']) for x in r])
 axs[0].plot(rr,[float(x['generator_norm_at_q050']) for x in r],'o-',label=kind)
 axs[1].plot(rr,[float(x['strain_lograte_norm_at_q050']) for x in r],'o-',label=kind)
axs[0].set_ylabel('Generator norm at q=0.50');axs[1].set_ylabel('Log-strain-rate norm at q=0.50')
axs[1].set_xlabel('Ramp duration (xi)')
for ax in axs:ax.grid(alpha=.2);ax.legend()
fig.suptitle('Independent ramp and kappa comparison; correlation is not causation')
fig.tight_layout();fig.savefig(P/'generator_vs_strain_across_ramps.png',dpi=175);plt.close(fig)
print('v18.49l created 3 numerical figures')
