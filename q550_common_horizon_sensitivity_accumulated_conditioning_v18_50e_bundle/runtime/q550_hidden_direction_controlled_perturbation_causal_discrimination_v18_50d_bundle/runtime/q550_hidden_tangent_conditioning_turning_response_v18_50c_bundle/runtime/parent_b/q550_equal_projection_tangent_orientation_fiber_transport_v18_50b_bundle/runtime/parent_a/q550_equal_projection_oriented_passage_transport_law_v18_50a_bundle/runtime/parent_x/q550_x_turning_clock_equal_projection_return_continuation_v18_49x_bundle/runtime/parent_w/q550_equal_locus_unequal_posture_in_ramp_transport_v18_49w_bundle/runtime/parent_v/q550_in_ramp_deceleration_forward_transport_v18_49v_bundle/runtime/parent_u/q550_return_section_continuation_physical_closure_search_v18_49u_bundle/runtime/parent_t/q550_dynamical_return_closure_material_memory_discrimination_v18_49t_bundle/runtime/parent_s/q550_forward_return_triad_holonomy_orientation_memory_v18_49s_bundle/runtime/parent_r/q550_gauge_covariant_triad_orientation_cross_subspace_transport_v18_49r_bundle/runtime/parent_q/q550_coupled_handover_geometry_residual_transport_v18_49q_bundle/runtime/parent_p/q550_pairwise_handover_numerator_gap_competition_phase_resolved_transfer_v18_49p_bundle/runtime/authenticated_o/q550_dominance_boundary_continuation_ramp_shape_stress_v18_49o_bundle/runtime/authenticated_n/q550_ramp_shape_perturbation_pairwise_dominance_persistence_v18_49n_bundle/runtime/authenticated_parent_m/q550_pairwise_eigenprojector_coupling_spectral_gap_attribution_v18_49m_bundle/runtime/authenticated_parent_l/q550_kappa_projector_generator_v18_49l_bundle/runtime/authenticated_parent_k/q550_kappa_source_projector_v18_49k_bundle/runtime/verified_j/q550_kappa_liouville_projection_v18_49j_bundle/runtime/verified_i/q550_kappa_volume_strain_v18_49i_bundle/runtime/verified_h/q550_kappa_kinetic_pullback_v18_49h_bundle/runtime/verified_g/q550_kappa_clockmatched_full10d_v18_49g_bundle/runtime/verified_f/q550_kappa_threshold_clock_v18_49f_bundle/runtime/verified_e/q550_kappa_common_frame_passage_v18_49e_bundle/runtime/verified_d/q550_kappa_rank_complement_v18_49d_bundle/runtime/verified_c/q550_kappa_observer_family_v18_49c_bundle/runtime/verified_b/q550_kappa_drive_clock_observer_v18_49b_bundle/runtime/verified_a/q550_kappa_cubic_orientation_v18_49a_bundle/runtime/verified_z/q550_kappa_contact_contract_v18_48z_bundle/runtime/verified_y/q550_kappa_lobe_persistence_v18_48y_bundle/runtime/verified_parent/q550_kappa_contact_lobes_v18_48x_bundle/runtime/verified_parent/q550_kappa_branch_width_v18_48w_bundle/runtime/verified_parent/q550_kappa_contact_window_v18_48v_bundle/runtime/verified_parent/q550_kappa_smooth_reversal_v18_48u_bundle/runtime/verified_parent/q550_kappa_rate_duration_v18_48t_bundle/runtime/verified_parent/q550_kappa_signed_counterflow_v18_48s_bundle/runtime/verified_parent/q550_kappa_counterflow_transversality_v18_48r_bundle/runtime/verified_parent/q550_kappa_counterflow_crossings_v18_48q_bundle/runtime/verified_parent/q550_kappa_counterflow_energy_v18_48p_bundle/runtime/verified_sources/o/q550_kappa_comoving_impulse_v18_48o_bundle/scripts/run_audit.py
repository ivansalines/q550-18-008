#!/usr/bin/env python3
"""v18.48o: discrete projective observer-frame / phase lag / impulse robustness.

ONLY authentic forward Q550 11D states and historically integrated observer
covectors from the nested v18.48h lineage are used. No reverse-time trajectory,
physical energy, or causality is inferred from cross-lag correlations.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,platform,sys
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_parent import verify
from phase_transport import (unit,comoving_frames,projector_gap,lag_pairs,best_lag,
                             impulse_masks,cycling_control)

def save_csv(path,records):
 if not records:raise ValueError('Empty CSV: '+str(path))
 names=list(records[0]);
 if any(set(row)!=set(names) for row in records):raise ValueError('Inconsistent row keys '+str(path))
 with path.open('w',encoding='utf-8',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=names);writer.writeheader();writer.writerows(records)

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--source-cutoffs',default='1e-6,1e-10')
 parser.add_argument('--cancel-cutoff',type=float,default=1e-2)
 parser.add_argument('--max-lag-steps',type=int,default=6)
 parser.add_argument('--pulse-radius',type=int,default=1)
 parser.add_argument('--max-events',type=int,default=4)
 parser.add_argument('--output-dir',type=Path,default=ROOT/'results')
 opts=parser.parse_args()
 cuts=[float(q) for q in opts.source_cutoffs.split(',')]
 if not cuts or any(not 0<c<1 for c in cuts):raise ValueError('Invalid source cutoff')
 if opts.cancel_cutoff<=0 or opts.cancel_cutoff>=1:raise ValueError('Invalid cancellation threshold')
 if not 0<=opts.max_lag_steps<=10 or not 0<=opts.pulse_radius<=4 or not 1<=opts.max_events<=8:
  raise ValueError('Unsafe lag or event configuration')
 out=opts.output_dir;out.mkdir(parents=True,exist_ok=True)
 provenance=verify()
 parent=ROOT/'runtime/parent_n';m=parent/'runtime/parent_m'
 sys.path.insert(0,str(parent/'scripts'));sys.path.insert(0,str(m/'scripts'));sys.path.insert(0,str(m/'reference'))
 from principal_geometry import source_active_subspaces
 from structural_jet import structural_jet,coupling_jet
 from observer_geometry_v18_48k import matrices
 from test_support_mobius_monodromy_audit import ModelParameters
 from rhythm_math import cancellation_signals
 physical=m/'runtime/parent_k/runtime/parent_j/runtime/physical_paths.npz'
 data=np.load(physical,allow_pickle=False)
 hist=json.loads((m/'runtime/parent_k/runtime/parent_j/runtime/report_v18_48h.json').read_text())
 kappa={'original':float(hist['kappa_original']),'autonomous':float(hist['kappa_autonomous'])}
 clock=float(data['clock_speed']);slope=clock/(2*math.pi)
 scale=np.asarray(data['chart_scale'],float);params=ModelParameters(gamma_rho=.3)
 groups=defaultdict(list)
 for idx in range(len(data['xi'])):
  key=(str(data['families'][idx]),int(data['seed_branches'][idx]),str(data['kappa_kind'][idx]))
  y=np.asarray(data['y'][idx],float);kind=key[2];xi=float(data['xi'][idx]);g=unit(data['covectors'][idx,0,:10])
  f,_,_=structural_jet(y,kappa[kind],params,slope)
  HB=structural_jet(y,0.,params,slope)[2]
  HC=slope*kappa[kind]*coupling_jet(y,params)[2]
  B,C=matrices(HB,HC,f,scale)
  groups[key].append({'xi':xi,'index':idx,'g':g,'B':B,'C':C})
 if len(groups)!=8 or any(len(rows)!=41 for rows in groups.values()):raise RuntimeError('Lost authentic Q550 sections')
 state_out=[];step_out=[];lag_out=[];lag_full=[];event_out=[];quality=[]
 main_pair=('comoving_projector','abs_logR_rate')
 for key,rows in sorted(groups.items()):
  fam,branch,kind=key;rows.sort(key=lambda r:r['xi'])
  xi=np.array([r['xi'] for r in rows]);assert np.allclose(np.diff(xi),.025,rtol=0,atol=2e-13)
  frames,q=comoving_frames([r['g'] for r in rows]);quality.append(dict(family=fam,branch=branch,kappa=kind,**q))
  for cutoff in cuts:
   states=[]
   for i,r in enumerate(rows):
    sub=source_active_subspaces(r['B'],r['C'],cutoff,opts.cancel_cutoff)
    U=sub['near'];P=U@U.T
    # Conjugation to the frame which parallelizes the historical projective line.
    Pc=frames[i].T@P@frames[i]
    g=r['g'];g0=rows[0]['g']
    stat=cancellation_signals(r['B'],r['C'],g)
    anchor_overlap=float(g@P@g)
    pulled_overlap=float(g0@Pc@g0)
    if abs(anchor_overlap-pulled_overlap)>5e-12:raise RuntimeError('Comoving overlap identity violated')
    states.append(dict(**r,P=P,Pc=Pc,near_rank=int(sub['near_rank']),
                       source_rank=int(sub['source_rank']),log_R=stat['log_R'],
                       R=stat['R'],opposition=stat['opposition_cosine'],
                       source_imbalance=stat['source_imbalance'],overlap=anchor_overlap))
    state_out.append(dict(family=fam,branch=branch,kappa=kind,source_cutoff=cutoff,
             xi=r['xi'],theta_rel_rad=clock*(r['xi']-3.5),near_rank=sub['near_rank'],
             source_rank=sub['source_rank'],historical_logR=stat['log_R'],historical_R=stat['R'],
             opposition_cosine=stat['opposition_cosine'],source_imbalance=stat['source_imbalance'],
             near_plane_overlap=anchor_overlap,comoving_near_plane_overlap=pulled_overlap,
             comoving_frame_tracking_max=q['max_line_tracking_error']))
   steps=[]
   for i,(a,b) in enumerate(zip(states[:-1],states[1:])):
    dt=b['xi']-a['xi']
    raw=projector_gap(a['P'],b['P'])/dt
    com=projector_gap(a['Pc'],b['Pc'])/dt
    signed=(b['log_R']-a['log_R'])/dt
    val=dict(family=fam,branch=branch,kappa=kind,source_cutoff=cutoff,
             step=i,xi_a=a['xi'],xi_b=b['xi'],xi_mid=(a['xi']+b['xi'])/2,
             theta_mid_rad=clock*((a['xi']+b['xi'])/2-3.5),
             raw_projector=raw,comoving_projector=com,
             comoving_minus_raw=com-raw,raw_over_comoving=raw/max(com,1e-300),
             observer_line_speed_deg_per_xi=math.degrees(math.acos(min(1.,abs(a['g']@b['g']))))/dt,
             abs_logR_rate=abs(signed),signed_logR_rate=signed,
             signed_source_imbalance_rate=(b['source_imbalance']-a['source_imbalance'])/dt,
             signed_plane_overlap_rate=(b['overlap']-a['overlap'])/dt,
             rank_a=a['near_rank'],rank_b=b['near_rank'],same_rank=a['near_rank']==b['near_rank'])
    steps.append(val);step_out.append(val)
   features=['raw_projector','comoving_projector','observer_line_speed_deg_per_xi']
   responses=['abs_logR_rate','signed_logR_rate','signed_source_imbalance_rate']
   for driver in features:
    for response in responses:
     xs=np.array([s[driver] if s['same_rank'] else float('nan') for s in steps]);ys=np.array([s[response] for s in steps]);
     cases=impulse_masks(xs,ys,opts.max_events,opts.pulse_radius)
     bests=[]
     for case,mask,center in cases:
      scan=lag_pairs(xs,ys,opts.max_lag_steps,mask=mask)
      b=best_lag(scan)
      if b is None:continue
      # Expensive cyclic controls only on full and both fixed interiors.
      null,num_shifts=cycling_control(xs,ys,mask,opts.max_lag_steps) if case in ('full','interior_80','interior_60') else (float('nan'),0)
      rec=dict(family=fam,branch=branch,kappa=kind,source_cutoff=cutoff,
        driver=driver,response=response,case=case,excluded_center=center,
        retained_steps=int(mask.sum()),best_lag_steps=b['lag_steps'],best_lag_xi=.025*b['lag_steps'],
        best_lag_phase_rad=.025*clock*b['lag_steps'],best_correlation=b['correlation'],
        compared_pairs=b['pairs'],cyclic_shift_exceedance=null,cyclic_controls=num_shifts)
      lag_out.append(rec);bests.append(rec)
      if case=='full':
       for pt in scan:
        lag_full.append(dict(family=fam,branch=branch,kappa=kind,source_cutoff=cutoff,
         driver=driver,response=response,lag_steps=pt['lag_steps'],lag_xi=.025*pt['lag_steps'],
         correlation=pt['correlation'],pairs=pt['pairs']))
     full=next((b for b in bests if b['case']=='full'),None)
     event_cases=[b for b in bests if b['case'].startswith('leave_')]
     if full:
      count=sum(b['best_lag_steps']==full['best_lag_steps'] for b in event_cases)
      same_sign=sum(np.sign(b['best_correlation'])==np.sign(full['best_correlation']) for b in event_cases)
      event_out.append(dict(family=fam,branch=branch,kappa=kind,source_cutoff=cutoff,
       driver=driver,response=response,full_lag_steps=full['best_lag_steps'],
       full_lag_xi=full['best_lag_xi'],full_correlation=full['best_correlation'],
       full_cyclic_shift_exceedance=full['cyclic_shift_exceedance'],
       eligible_leave_one_events=len(event_cases),unchanged_lag_after_leave_one=count,
       unchanged_fraction=count/max(1,len(event_cases)),unchanged_correlation_sign=int(same_sign),
       retained_event_lags=';'.join(str(b['best_lag_steps']) for b in event_cases),
       interior80_lag=next((b['best_lag_steps'] for b in bests if b['case']=='interior_80'),''),
       interior60_lag=next((b['best_lag_steps'] for b in bests if b['case']=='interior_60'),'')))
   print('v18.48o',fam,'branch',branch,kind,'source',cutoff,
         'raw/comoving median pace',f'{np.median([x["raw_projector"] for x in steps]):.6g}',
         f'{np.median([x["comoving_projector"] for x in steps]):.6g}',flush=True)
 # Authentic numerical regression to signed original v18.48n history
 n_states={}
 with (parent/'results/rhythm_states.csv').open() as f:
  for x in csv.DictReader(f):n_states[(x['family'],int(x['branch']),x['kappa'],float(x['source_cutoff']),float(x['xi']))]=x
 max_err=0.
 for s in state_out:
  key=(s['family'],s['branch'],s['kappa'],s['source_cutoff'],s['xi'])
  if key not in n_states:raise RuntimeError('Missing n history row')
  n=n_states[key]
  if int(n['near_rank'])!=s['near_rank']:raise RuntimeError('Parent rank mismatch')
  err=abs(s['historical_R']-float(n['historical_R']))/max(abs(float(n['historical_R'])),1e-300)
  max_err=max(max_err,err)
 if max_err>1e-10:raise RuntimeError('Parent n historical R mismatch')
 n_steps={}
 with (parent/'results/rhythm_steps.csv').open() as f:
  for x in csv.DictReader(f):
   n_steps[(x['family'],int(x['branch']),x['kappa'],float(x['source_cutoff']),float(x['xi_a']))]=x
 max_step_err=0.
 for row in step_out:
  key=(row['family'],row['branch'],row['kappa'],row['source_cutoff'],row['xi_a'])
  if key not in n_steps:raise RuntimeError('Missing n step')
  old=n_steps[key]
  for newkey,oldkey in [('raw_projector','projector_speed_per_xi'),('signed_logR_rate','signed_logR_change_speed')]:
   diff=abs(row[newkey]-float(old[oldkey]))/max(1.,abs(float(old[oldkey])))
   max_step_err=max(max_step_err,diff)
 if max_step_err>1e-6:raise RuntimeError('Parent n step regression exceeded (ill-conditioned 1e-10 source subspace)')
 save_csv(out/'phase_states.csv',state_out)
 save_csv(out/'phase_steps.csv',step_out)
 save_csv(out/'lag_cases.csv',lag_out)
 save_csv(out/'lag_scans_full.csv',lag_full)
 save_csv(out/'impulse_stability.csv',event_out)
 save_csv(out/'comoving_frame_quality.csv',quality)
 focus=[r for r in event_out if r['family'].startswith('phasecov') and r['branch']==0 and r['kappa']=='original' and r['source_cutoff']==1e-6]
 reference=[r for r in focus if (r['driver'],r['response'])==('comoving_projector','abs_logR_rate')]
 ref=reference[0] if reference else None
 rawfocus=[r for r in focus if (r['driver'],r['response'])==('raw_projector','abs_logR_rate')]
 refraw=rawfocus[0] if rawfocus else None
 report=dict(version='v18.48o',title='Co-Moving Phase Delay & Impulse-Robust Transport Audit',
  classification='AUTHENTICATED_DISCRETE_CO_MOVING_GAUGE_AND_IMPULSE_SENSITIVITY_DIAGNOSTIC',
  original_11D_states=328,original_forward_11D_paths=8,new_11D_integrations=0,
  states_by_cutoffs=len(state_out),steps_by_cutoffs=len(step_out),lag_case_records=len(lag_out),
  lag_full_records=len(lag_full),impulse_stability_groups=len(event_out),
  source_cutoffs=cuts,cancellation_cutoff=opts.cancel_cutoff,max_lag_steps=opts.max_lag_steps,
  pulse_radius_intervals=opts.pulse_radius,events_per_signal=opts.max_events,
  xi_step=.025,phase_clock_rad_per_xi=clock,
  source_physical_paths_sha256=hashlib.sha256(physical.read_bytes()).hexdigest(),
  provenance=provenance,regression_max_relative_original_v18_48n_historical_R=max_err,
  regression_max_relative_original_v18_48n_steps=max_step_err,
  coframe_quality={k:max(float(v[k]) for v in quality) for k in ('max_step_line_error','max_orthogonality_error','max_line_tracking_error')},
  reference_phasecov_branch0_original_cutoff_1em6_comoving_abs_logR=ref,
  reference_phasecov_branch0_original_cutoff_1em6_raw_abs_logR=refraw,
  scientific_limits=[
   'The discrete minimal-turn observer frame is a chosen Euclidean chart gauge, NOT the full physical 11D variational or adjoint propagator.',
   'Historical observed covectors were authentically integrated forward in v18.48h; they are projected to the frozen 10D chart.',
   'Phase-lag statistics are conditional correlations of a short deterministic signal; they are not a causal response delay.',
   'The signed logR derivative records increase/decrease of a mathematical cancellation ratio, not physical energy direction.',
   'Driver and response are evaluated on the same 40 fixed intervals; impulse masks preserve timeline indices.',
   'Cancellation subspaces depend on source and cancellation thresholds; coframe is nonunique beyond its observer-line parallelism.',
   'No reverse physical trajectory, energetic balance, dissipation theorem, or invariant material phase-lag is established.'])
 (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False,default=lambda x: x.item() if isinstance(x,np.generic) else (_ for _ in ()).throw(TypeError(str(type(x)))))+'\n')
 print(json.dumps({k:report[k] for k in ('version','states_by_cutoffs','steps_by_cutoffs','lag_case_records','impulse_stability_groups','coframe_quality','reference_phasecov_branch0_original_cutoff_1em6_comoving_abs_logR')},indent=2))
if __name__=='__main__':main()
