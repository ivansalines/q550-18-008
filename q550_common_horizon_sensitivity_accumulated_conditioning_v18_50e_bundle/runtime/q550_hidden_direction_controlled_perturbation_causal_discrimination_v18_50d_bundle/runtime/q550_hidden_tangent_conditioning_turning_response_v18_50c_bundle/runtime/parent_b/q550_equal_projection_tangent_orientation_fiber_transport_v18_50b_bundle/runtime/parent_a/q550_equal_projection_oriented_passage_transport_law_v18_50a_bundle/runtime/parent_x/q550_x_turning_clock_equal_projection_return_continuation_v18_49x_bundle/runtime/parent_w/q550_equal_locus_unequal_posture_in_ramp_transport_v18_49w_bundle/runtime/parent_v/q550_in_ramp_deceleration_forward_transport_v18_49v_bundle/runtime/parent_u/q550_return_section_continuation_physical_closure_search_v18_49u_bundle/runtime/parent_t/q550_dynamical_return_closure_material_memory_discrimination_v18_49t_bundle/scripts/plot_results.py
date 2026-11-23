from pathlib import Path
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[1];p=R/'results/dynamic_matched_sections.csv'
if p.exists():
 with p.open() as f:rows=list(csv.DictReader(f))
 if rows:
  fig,ax=plt.subplots(figsize=(8.5,5))
  for kind,r in sorted({(x['kappa_kind'],x['ramp_xi']) for x in rows}):
   z=sorted([x for x in rows if x['kappa_kind']==kind and x['ramp_xi']==r],key=lambda x:float(x['forward_anchor_time']))
   ax.plot([float(x['forward_anchor_time']) for x in z], [float(x['configuration_distance']) for x in z],'-o',label=f'{kind}, ramp {r}')
  ax.set_title('v18.49t — closest physical return section (not forced closure)')
  ax.set_xlabel('Forward anchor time');ax.set_ylabel('Configuration distance (declared coordinate norm)');ax.grid(alpha=.25);ax.legend(fontsize=8)
  fig.tight_layout();fig.savefig(R/'results/dynamic_return_configuration_gaps.png',dpi=170);plt.close(fig)
  fig,ax=plt.subplots(figsize=(8.5,5))
  for kind,r in sorted({(x['kappa_kind'],x['ramp_xi']) for x in rows}):
   z=sorted([x for x in rows if x['kappa_kind']==kind and x['ramp_xi']==r],key=lambda x:float(x['forward_anchor_time']))
   ax.plot([float(x['forward_anchor_time']) for x in z],[float(x['energy_difference']) for x in z],'-o',label=f'{kind}, ramp {r}')
  ax.axhline(0,ls='--',lw=1);ax.grid(alpha=.25);ax.legend(fontsize=8)
  ax.set_title('v18.49t — energy differences at best-matched geometry (not closed states)');ax.set_xlabel('Forward anchor time');ax.set_ylabel('Return minus forward mechanical energy')
  fig.tight_layout();fig.savefig(R/'results/dynamic_return_energy_differences.png',dpi=170);plt.close(fig)
