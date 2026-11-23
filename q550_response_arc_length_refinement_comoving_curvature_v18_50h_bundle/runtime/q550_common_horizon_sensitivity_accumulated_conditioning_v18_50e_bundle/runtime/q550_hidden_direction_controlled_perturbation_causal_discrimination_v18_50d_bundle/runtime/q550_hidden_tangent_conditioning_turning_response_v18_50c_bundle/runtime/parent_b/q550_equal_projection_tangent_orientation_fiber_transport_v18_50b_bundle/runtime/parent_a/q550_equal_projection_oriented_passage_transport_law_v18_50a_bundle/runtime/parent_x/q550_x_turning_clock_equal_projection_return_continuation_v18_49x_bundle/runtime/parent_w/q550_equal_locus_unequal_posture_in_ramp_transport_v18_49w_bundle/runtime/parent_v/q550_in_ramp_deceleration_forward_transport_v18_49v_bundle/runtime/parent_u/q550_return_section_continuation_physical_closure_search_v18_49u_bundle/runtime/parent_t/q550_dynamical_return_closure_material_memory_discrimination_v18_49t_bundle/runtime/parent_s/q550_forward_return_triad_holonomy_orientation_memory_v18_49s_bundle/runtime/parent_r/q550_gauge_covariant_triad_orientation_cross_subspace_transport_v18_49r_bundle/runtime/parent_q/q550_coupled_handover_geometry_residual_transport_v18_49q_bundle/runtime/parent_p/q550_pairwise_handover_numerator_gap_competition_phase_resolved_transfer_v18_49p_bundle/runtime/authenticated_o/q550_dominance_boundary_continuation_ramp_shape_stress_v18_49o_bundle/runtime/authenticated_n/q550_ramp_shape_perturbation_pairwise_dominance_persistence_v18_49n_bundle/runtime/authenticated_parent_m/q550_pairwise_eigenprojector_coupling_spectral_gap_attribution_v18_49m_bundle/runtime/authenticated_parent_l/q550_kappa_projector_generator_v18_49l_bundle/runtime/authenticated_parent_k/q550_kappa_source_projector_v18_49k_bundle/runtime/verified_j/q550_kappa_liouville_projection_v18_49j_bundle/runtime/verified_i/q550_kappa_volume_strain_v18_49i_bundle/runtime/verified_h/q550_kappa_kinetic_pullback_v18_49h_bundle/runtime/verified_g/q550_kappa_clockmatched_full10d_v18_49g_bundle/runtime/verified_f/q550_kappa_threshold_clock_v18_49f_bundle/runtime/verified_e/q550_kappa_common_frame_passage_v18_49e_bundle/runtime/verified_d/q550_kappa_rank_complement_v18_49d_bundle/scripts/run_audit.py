#!/usr/bin/env python3
"""v18.49d: SHA-authenticated rank, hidden complement and transport audit.

Genuine 11D reference/return trajectories and 10D cotangent IVPs, with five
historical seeds and five explicitly synthetic extensions. The chosen finite
metric and observer family are not intrinsic physical structures.
"""
from __future__ import annotations
import argparse,csv,json,platform,sys,math
from collections import defaultdict
from pathlib import Path
import numpy as np
from verify_parent import verify,dynamic
from subspace_math import subspace,compare,complement_alignment,independent_extension
ROOT=Path(__file__).resolve().parents[1]
RAMPS=(.285,.292,.296333,.300,.305,.309)
TOLS=(1e-4,1e-6,1e-8,1e-10,1e-12)
SIZES=(2,5,6,8,10)
PHASES=tuple(np.linspace(.20,.80,13))

def rows(path):
 with Path(path).open(newline='') as f:return list(csv.DictReader(f))
def save_csv(path,data):
 if not data:
  Path(path).write_text('kappa_kind,ramp_xi0,ramp_xi1,phase_q,projector_frobenius_gap\n')
  return
 keys=list(dict.fromkeys(k for row in data for k in row))
 with Path(path).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(data)

def run(args):
 c,b,a,z,y,j,pin=verify()
 sys.path.insert(0,str(c/'reference'))
 sys.path.insert(0,str(c/'scripts'))
 phys=dynamic(c/'reference/physical_math.py','d_orig_phys')
 ramp=dynamic(c/'reference/parent_ramp_math.py','d_orig_ramp')
 yr=dynamic(c/'reference/y_original_run_audit.py','d_orig_11d_ivp')
 jet=dynamic(c/'reference/structural_jet.py','d_orig_jacobian')
 observer=dynamic(c/'reference/parent_observer_math.py','d_orig_cotangent')
 family=dynamic(c/'scripts/family_math.py','d_orig_family_math')
 candidates=list(z.rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
 if len(candidates)!=1:raise RuntimeError('Missing authenticated source ODE')
 support=dynamic(candidates[0],'d_orig_support')
 audit=dynamic(candidates[0].parent/'test_support_mobius_monodromy_audit.py','d_orig_model')
 h=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
 conf=json.loads((j/'runtime/report_v18_48h.json').read_text())
 kappas={'original':float(conf['kappa_original']),'autonomous':float(conf['kappa_autonomous'])}
 omega=float(h['clock_speed']);slope=omega/(2*np.pi)
 params=audit.ModelParameters(gamma_rho=.3)
 byfam=defaultdict(list)
 for i in range(len(h['y'])):
  byfam[(str(h['families'][i]),int(h['seed_branches'][i]),str(h['kappa_kind'][i]))].append(i)
 parent={(row['kappa_kind'],round(float(row['ramp_xi']),8),row['metric'],int(row['family_size'])):row
         for row in rows(c/'results/observer_family_envelopes.csv')
         if row['root_position']=='barrier' and abs(float(row['delta_B_minus_threshold'])-1e-5)<1e-12}
 out=ROOT/'results';out.mkdir(exist_ok=True)
 metrics={'euclidean':np.eye(10),'declared_weighted':np.diag(np.array([1.2,.8,1.15,1.1,.95,1.3,.7,1.1,.8,1.25])**2)}
 records=[];transport=[];scale=[];cross=[];dualities=[];snapshots={}
 nphysical=0;ntransport=0;max_history=0.;max_ledger=0.;max_parent=0.;max_cov=0.;max_identity=0.;max_duality=0.
 for kind in (('original',) if args.smoke else ('original','autonomous')):
  ids=sorted(next(v for k,v in byfam.items() if k[0].startswith('phaseblind') and k[1]==0 and k[2]==kind),key=lambda ii:float(h['xi'][ii]))
  yy=np.asarray(h['y'][ids[0]],float);kap=kappas[kind]
  fwd,led=yr.integrate(phys,ramp,support,audit,kap,params,slope,omega,yy,args)
  nphysical+=1;max_ledger=max(max_ledger,led)
  max_history=max(max_history,max(float(np.linalg.norm(fwd(t)[:11]-h['y'][ii])) for t,ii in zip(np.linspace(0,1,41),ids)))
  turn=fwd(1.)[:11].copy();turn[[1,3,5,7,9]]*=-1
  historical=np.asarray(h['covectors'][ids[-1],:,:10],float).copy()
  historical/=np.linalg.norm(historical,axis=1,keepdims=True)
  full_seeds=independent_extension(historical)
  for duration in ((.296333,) if args.smoke else RAMPS):
   design=ramp.Design('v18_49d','smoothstep',duration)
   back,led=yr.integrate(phys,ramp,support,audit,kap,params,slope,omega,turn,args,design=design)
   nphysical+=1;max_ledger=max(max_ledger,led)
   def jac(state,k,p,sl):return jet.structural_jet(state,k,p,sl)[1]
   propagated,sol=observer.integrate_dual(back,design,kap,params,slope,omega,jac,full_seeds,historical[0],1.+duration,
      rtol=args.adjoint_rtol,atol=args.adjoint_atol,max_step=args.adjoint_max_step)
   ntransport+=1
   for ti in np.linspace(0,1.+duration,17):
    gs,v=propagated(ti)
    target=full_seeds@historical[0]
    max_duality=max(max_duality,float(np.max(np.abs(gs@v-target)/np.maximum(1.,np.abs(target)))))
    dualities.append({'kind':kind,'ramp_xi':duration,'time_xi':ti,
      'relative_pairing_error':float(np.max(np.abs(gs@v-target)/np.maximum(1.,np.abs(target))))})
   parentrow=parent[(kind,round(duration,8),'euclidean',5)]
   qbar=float(parentrow['phase_q'])
   phases=sorted(set([round(float(q),12) for q in PHASES]+[round(qbar,12),.35,.55,round(.35+kap,12),.55]))
   local={}
   for q in phases:
    yi=back(duration+q)[:11]
    yf=fwd(1.-q)[:11]
    g,_=propagated(duration+q)
    delta=family.local_lift(yi,yf)
    local[q]=(g,delta)
    if abs(q-qbar)<1e-10:
     for metricname,metric in metrics.items():
      for size in (2,5):
       base=subspace(g[:size],delta,metric,1e-10)
       row=parent[(kind,round(duration,8),metricname,size)]
       max_parent=max(max_parent,abs(base['fraction']-float(row['fraction_explained'])),
          abs(base['amplitude']-float(row['envelope_abs_max'])))
    for metricname,metric in metrics.items():
     for size in SIZES:
      for tol in TOLS:
       obj=subspace(g[:size],delta,metric,tol)
       max_identity=max(max_identity,obj['identity_error'])
       rec={'kappa_kind':kind,'ramp_xi':duration,'phase_q':q,'metric':metricname,
           'family_size':size,'source_kind':'historical' if size<=5 else 'historical_plus_synthetic',
           'rank_tolerance':tol,'effective_rank':obj['rank'],
           'smallest_relative_sv':float(obj['s'][-1]/obj['s'][0]),
           'full_metric_distance':obj['distance'],'observable_envelope':obj['amplitude'],
           'hidden_complement_norm':obj['residual'],'fraction_explained':obj['fraction'],
           'algebraic_identity_error':obj['identity_error'],
           'mechanical_energy_difference':float(phys.energy(yi,kap,params)-phys.energy(yf,kap,params))}
       records.append(rec)
       if metricname=='euclidean' and size==5 and tol==1e-10:
        if q not in snapshots:snapshots[q]={}
        snapshots[q][(kind,duration)]=(obj,delta)
       if q==round(qbar,12) and metricname=='euclidean' and size==5 and tol==1e-10:
        # Change the chart+metric together; the scalar envelope must be preserved.
        chart=np.eye(10)+.13*np.eye(10,k=1)
        change=np.linalg.inv(chart)
        test=subspace(g[:size]@change,chart@delta,change.T@metric@change,tol)
        max_cov=max(max_cov,abs(test['amplitude']-obj['amplitude'])/max(1.,obj['amplitude']))
   for metricname,metric in metrics.items():
    for size in (2,5,6,10):
     for tol in TOLS:
      last=None;last_q=None
      for q in phases:
       gg,dd=local[q]
       obj=subspace(gg[:size],dd,metric,tol)
       if last is not None:
        d=compare(last,obj)
        transport.append({'kappa_kind':kind,'ramp_xi':duration,'metric':metricname,
         'family_size':size,'rank_tolerance':tol,'phase_q0':last_q,'phase_q1':q,
         'delta_q':q-last_q,**d,'hidden_residual_alignment':complement_alignment(last,obj),
         'hidden_residual_growth':obj['residual']-last['residual']})
       last=obj;last_q=q
   for phase0 in (.35,.55):
    for span,label in ((kap,'kappa_length'),(.2,'literal_0p2_xi')):
     q1=round(phase0+span,12)
     if q1 not in local:local[q1]=(propagated(duration+q1)[0],family.local_lift(back(duration+q1)[:11],fwd(1-q1)[:11]))
     for metricname,metric in metrics.items():
      g0,d0=local[phase0];g1,d1=local[q1]
      a0=subspace(g0[:5],d0,metric,1e-10);a1=subspace(g1[:5],d1,metric,1e-10)
      comp=compare(a0,a1)
      scale.append({'kappa_kind':kind,'ramp_xi':duration,'metric':metricname,'phase0':phase0,'phase1':q1,
       'span_kind':label,'span_xi':span,'span_over_kappa':span/kap,
       **comp,'residual_ratio_end_over_start':a1['residual']/a0['residual'],
       'hidden_cosine':complement_alignment(a0,a1)})
   print(f'v18.49d {kind}, ramp={duration:.6f}: 11D + ten covectors; adjoint steps={len(sol.t)}',flush=True)
 # Cross-ramp family transport at same physical common phase q=0.5, not a single time trajectory.
 for kind in ('original','autonomous'):
  vals=[]
  for ramp_duration in RAMPS:
   item=snapshots.get(.5,{}).get((kind,ramp_duration))
   if item is not None:vals.append((ramp_duration,item[0]))
  for (t1,s1),(t2,s2) in zip(vals,vals[1:]):
   d=compare(s1,s2)
   cross.append({'kappa_kind':kind,'ramp_xi0':t1,'ramp_xi1':t2,'phase_q':.5,
       'basis':'historical_five','rank_tol':1e-10,**d,
       'hidden_norm_change':s2['residual']-s1['residual'],
       'hidden_cosine':complement_alignment(s1,s2)})
 save_csv(out/'rank_and_hidden_complement.csv',records)
 save_csv(out/'within_return_projector_transport.csv',transport)
 save_csv(out/'across_ramps_fixed_phase.csv',cross)
 save_csv(out/'kappa_scale_return_tests.csv',scale)
 save_csv(out/'tangent_cotangent_pairing.csv',dualities)
 active=[r for r in records if r['metric']=='euclidean' and r['family_size']==5 and r['rank_tolerance']==1e-10 and abs(r['phase_q']-.5)<1e-10]
 report={'version':'v18.49d','status':'AUTHENTIC_11D_10D_COTANGENT_OBSERVER_SUBSPACE_DIAGNOSTIC',
  'physical_integrations':nphysical,'cotangent_integrations':ntransport,'full_ten_covector_transport':True,
  'new_synthetic_observer_rows_per_path':5,'data_rows':len(records),'within_return_comparisons':len(transport),
  'across_ramp_comparisons':len(cross),'kappa_length_comparisons':len(scale),
  'rank_tolerances':list(TOLS),'family_sizes':list(SIZES),'metrics':list(metrics),
  'max_parent_C_regression':max_parent,'max_forward_history_regression':max_history,
  'max_energy_ledger_residual':max_ledger,'max_metric_chart_covariance_error':max_cov,
  'max_metric_pythagorean_error':max_identity,'max_tangent_cotangent_duality_residual':max_duality,
  'at_common_phase_q050':{'five_observer_fraction_range':[min(r['fraction_explained'] for r in active),max(r['fraction_explained'] for r in active)],
    'five_observer_hidden_norm_range':[min(r['hidden_complement_norm'] for r in active),max(r['hidden_complement_norm'] for r in active)],
    'five_observer_rank_distribution':{str(k):sum(r['effective_rank']==k for r in active) for k in range(1,6)}},
  'genealogy':pin,
  'limitations':'Phaseblind branch0 only. Metric-dependent complement and rank-dependent SVD. Five new directions are synthetic mathematical observers, NOT historical or discovered physical modes. Within-trajectory projector changes in a fixed material chart are not gauge-covariant holonomy. Delta xi=0.2 / kappa is a numerical scale comparison, not an established full-cycle/return marker. No 11D physical cycle or hidden-information law established.'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 (out/'environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__},indent=2)+'\n')
 print(json.dumps(report,indent=2),flush=True)
 if max_parent>args.maximum_regression or max_history>args.maximum_regression or max_ledger>args.maximum_ledger_error or max_duality>args.maximum_duality_error or max_cov>1e-7 or max_identity>1e-8:
  raise RuntimeError('Scientific gates failed')

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--smoke',action='store_true')
 p.add_argument('--rtol',type=float,default=3e-12)
 p.add_argument('--atol',type=float,default=3e-13)
 p.add_argument('--max-step',type=float,default=.025)
 p.add_argument('--adjoint-rtol',type=float,default=2e-10)
 p.add_argument('--adjoint-atol',type=float,default=2e-12)
 p.add_argument('--adjoint-max-step',type=float,default=.0125)
 p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
 p.add_argument('--maximum-regression',type=float,default=1e-7)
 p.add_argument('--maximum-duality-error',type=float,default=1e-7)
 run(p.parse_args())
