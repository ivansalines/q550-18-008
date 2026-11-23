#!/usr/bin/env python3
import csv
from collections import defaultdict
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
with (ROOT/'results/in_ramp_phase_resolved.csv').open() as f:data=list(csv.DictReader(f))
group=defaultdict(list)
for row in data:group[(row['kappa_kind'],float(row['ramp_xi']))].append(row)
for kind in ('original','autonomous'):
 selected=[(r,rs) for (k,r),rs in group.items() if k==kind]
 if not selected:continue
 fig,ax=plt.subplots(figsize=(9,5));
 for r,rs in selected:
  ax.plot([float(v['sigma']) for v in rs],[float(v['material_10d_rate_norm']) for v in rs],label=f'r={r:g}')
 ax.axvline(.5,ls='--',lw=1,color='gray',label='drive zero')
 ax.set(xlabel='Normalized in-ramp time σ',ylabel='Original material 10D rate norm (coordinates / ξ)',title='Q550 in-ramp intrinsic transport — '+kind)
 ax.legend();fig.tight_layout();fig.savefig(ROOT/'results'/f'in_ramp_material_rate_{kind}.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5))
for (k,r),rs in group.items():
 if k!='original':continue
 ax.plot([float(v['sigma']) for v in rs],[float(v['material_10d_coordinate_path']) for v in rs],label=f'path r={r:g}')
ax.axvline(.5,ls='--',lw=1,color='gray')
ax.set(xlabel='Normalized in-ramp time σ',ylabel='Accumulated original 10D coordinate path',title='Motion continues during command reversal')
ax.legend();fig.tight_layout();fig.savefig(ROOT/'results/in_ramp_accumulated_path.png',dpi=160);plt.close(fig)
fig,ax=plt.subplots(figsize=(9,5))
for (k,r),rs in group.items():
 if abs(r-.327375)>1e-10:continue
 z=[v for v in rs if v['triad_defined']=='1' and v['triad_rotation_from_first_valid_deg']]
 if z:ax.plot([float(v['sigma']) for v in z],[float(v['triad_rotation_from_first_valid_deg']) for v in z],label=k)
ax.set(xlabel='Normalized in-ramp time σ',ylabel='Approx. relative 6-7-8 triad angle (deg)',title='Spectral triad motion during ramp — valid sections only')
ax.legend();fig.tight_layout();fig.savefig(ROOT/'results/in_ramp_triad_orientation.png',dpi=160);plt.close(fig)
