#!/usr/bin/env python3
"""v18.49c: SHA-authenticated material observer-family envelope and separation.

Replays historical 11D driven IVPs and integrates 5 authentic seeded 10D
material cotangent directions on each new return. Computes analytic
whole-subspace amplitude under two EXPLICIT tangent metrics. Not a
material metric theorem, gauge-independent handedness or finite-IVP duality.
"""
from __future__ import annotations
import argparse,csv,json,math,platform,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from verify_parent import verify,dynamic
from family_math import envelope,local_lift,transform_chart
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'reference'))
RAMPS=(.285,.292,.296333,.300,.305,.309)
def read_csv(path):
 with Path(path).open(newline='') as f:return list(csv.DictReader(f))
def write_csv(path,rows):
 if not rows:raise RuntimeError('Missing results for '+str(path))
 cols=list(dict.fromkeys(k for x in rows for k in x))
 with Path(path).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)
def run(args):
 b,a,z,y,j,pin=verify()
 phys=dynamic(ROOT/'reference/physical_math.py','c_auth_physical')
 ramp=dynamic(ROOT/'reference/parent_ramp_math.py','c_auth_ramp')
 yr=dynamic(ROOT/'reference/y_original_run_audit.py','c_auth_integrator')
 jet=dynamic(ROOT/'reference/structural_jet.py','c_auth_structural_J')
 observer=dynamic(ROOT/'reference/parent_observer_math.py','c_auth_cotangent')
 candidates=list(z.rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
 if len(candidates)!=1:raise RuntimeError('Missing authentic source field')
 support=dynamic(candidates[0],'c_auth_support')
 audit=dynamic(candidates[0].parent/'test_support_mobius_monodromy_audit.py','c_auth_audit')
 h=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
 conf=json.loads((j/'runtime/report_v18_48h.json').read_text())
 ks={'original':float(conf['kappa_original']),'autonomous':float(conf['kappa_autonomous'])}
 omega=float(h['clock_speed']);slope=omega/(2*np.pi)
 params=audit.ModelParameters(gamma_rho=.3)
 byfam=defaultdict(list)
 for i in range(len(h['y'])):
  byfam[(str(h['families'][i]),int(h['seed_branches'][i]),str(h['kappa_kind'][i]))].append(i)
 roots={(row['kappa_kind'],round(float(row['ramp_duration_xi']),8),float(row['delta_B_minus_threshold'])):row for row in read_csv(a/'results/continuous_11D_root_validation.csv')}
 parent={(row['kappa_kind'],round(float(row['ramp_duration_xi']),8),float(row['delta']),row['root_position'],int(row['observer_channel'])):row for row in read_csv(b/'results/observer_probe_at_physical_roots.csv')}
 out=ROOT/'results';out.mkdir(exist_ok=True)
 figures=[];checks=[];duality=[];summary=[];max_replay=0.;max_root=0.;max_parent=0.;max_chart=0.;max_basis=0.;max_bound=0.;max_dual=0.;max_ledger=0.
 nphys=0;ntransport=0
 scale=np.array([1.2,.8,1.15,1.1,.95,1.3,.7,1.1,.8,1.25])
 metrics={'euclidean':np.eye(10),'declared_weighted':np.diag(scale*scale)}
 chart_transforms={
  'mild_scaling':np.diag([1.3,.8,1.15,.9,1.1,1.25,.7,1.4,.95,1.2]),
  'mild_shear':np.eye(10)+.21*np.eye(10,k=1)-.11*np.eye(10,k=-1)}
 # The same mixing must not change the family column span.
 mixing=np.array([[1.0,.3],[-.2,1.1]])
 for kind in (('original',) if args.smoke else ('original','autonomous')):
  ids=sorted(next(v for k,v in byfam.items() if k[0].startswith('phaseblind') and k[1]==0 and k[2]==kind),key=lambda ii:float(h['xi'][ii]))
  yy=np.asarray(h['y'][ids[0]],float);kap=ks[kind]
  fwd,ledger=yr.integrate(phys,ramp,support,audit,kap,params,slope,omega,yy,args)
  nphys+=1;max_ledger=max(max_ledger,ledger)
  max_replay=max(max_replay,max(float(np.linalg.norm(fwd(t)[:11]-h['y'][ii])) for t,ii in zip(np.linspace(0,1,41),ids)))
  turn=fwd(1.)[:11].copy();turn[[1,3,5,7,9]]*=-1
  seeds=np.asarray(h['covectors'][ids[-1],:,:10],float).copy()
  if seeds.shape!=(5,10):raise RuntimeError('Expected 5 original historical covectors')
  seeds/=np.linalg.norm(seeds,axis=1,keepdims=True)
  for duration in ((.296333,) if args.smoke else RAMPS):
   design=ramp.Design('v18_49c','smoothstep',duration)
   back,ledger=yr.integrate(phys,ramp,support,audit,kap,params,slope,omega,turn,args,design=design)
   nphys+=1;max_ledger=max(max_ledger,ledger)
   def jac(state,k,p,sl):return jet.structural_jet(state,k,p,sl)[1]
   propagated,sol=observer.integrate_dual(back,design,kap,params,slope,omega,jac,seeds,seeds[0],1.+duration,
              rtol=args.adjoint_rtol,atol=args.adjoint_atol,max_step=args.adjoint_max_step)
   ntransport+=1
   seed_dual=seeds@seeds[0]
   for t in np.linspace(0,1+duration,25):
    gs,v=propagated(t)
    dif=gs@v-seed_dual
    max_dual=max(max_dual,float(np.max(np.abs(dif)/np.maximum(1.,np.abs(seed_dual)))))
    duality.append({'kappa_kind':kind,'ramp_xi':duration,'elapsed_xi':float(t),
          'max_seed_pairing_relative_residual':float(np.max(np.abs(dif)/np.maximum(1.,np.abs(seed_dual))))})
   for dlev in (1e-5,3e-5,1e-4,3e-4):
    row=roots[(kind,round(duration,8),dlev)]
    vals=[('left',float(row['dense_IVP_left_root_q'])),('barrier',float(row['barrier_phase'])),('right',float(row['dense_IVP_right_root_q']))]
    for position,q in vals:
     yb=back(duration+q)[:11];yf=fwd(1-q)[:11]
     g,_=propagated(duration+q)
     delta=local_lift(yb,yf)
     # Compare against direct authenticated material physical root/gauge.
     target=float(row['barrier_height']) if position=='barrier' else float(row['threshold_d3'])
     _,geomdist=observer.shape_gradient(yb,yf)
     max_root=max(max_root,abs(geomdist-target))
     energydiff=float(phys.energy(yb,kap,params)-phys.energy(yf,kap,params))
     for idx in (0,1):
      prev=parent[(kind,round(duration,8),dlev,position,idx)]
      p=float(g[idx]@delta)
      max_parent=max(max_parent,abs(p-float(prev['genuinely_transported_probe'])))
     for name,m in metrics.items():
      for count in (2,5):
       group=g[:count]
       diag=envelope(group,delta,m,args.family_rank_tol)
       # Check actual readings against analytic whole-family envelope.
       matnorms=np.sqrt(np.einsum('ai,ij,aj->a',group,np.linalg.inv(m),group))
       selected=np.max(np.abs(group@delta)/matnorms)
       bound=max(0.,float(selected)-diag['amplitude'])
       max_bound=max(max_bound,bound)
       # Non-unit coordinate changes WITH metric/covector transformations.
       for chart,S in chart_transforms.items():
        gg,dd,mm=transform_chart(group,delta,m,S)
        rec=envelope(gg,dd,mm,args.family_rank_tol)
        diff=abs(diag['amplitude']-rec['amplitude'])/max(1.,diag['amplitude'])
        max_chart=max(max_chart,diff)
       if count==2:
        remixed=mixing@group
        moved=envelope(remixed,delta,m,args.family_rank_tol)
        max_basis=max(max_basis,abs(diag['amplitude']-moved['amplitude'])/max(1.,diag['amplitude']))
       data={'kappa_kind':kind,'ramp_xi':duration,'delta_B_minus_threshold':dlev,
         'root_position':position,'phase_q':q,'external_clock_angle':float(yb[10]),
         'clock_gap_rad':float((yb[10]-yf[10]+np.pi)%(2*np.pi)-np.pi),
         'metric':name,'family_size':count,'numerical_rank':diag['rank'],
         'smallest_over_largest_sv':diag['relative_singular_floor'],
         'envelope_abs_max':diag['amplitude'],'envelope_min':-diag['amplitude'],
         'envelope_max':diag['amplitude'],'material_distance_metric':diag['material_distance'],
         'orthogonal_material_residual':diag['orthogonal_residual'],
         'fraction_explained':diag['fraction'],'shape_3D_distance':geomdist,
         'mechanical_energy_difference':energydiff,
         'single_observer_max_within_envelope':float(selected),
         'first_frozen_readout':float(seeds[0]@delta),'first_transported_readout':float(g[0]@delta)}
       figures.append(data)
    print('v18.49c',kind,'ramp',duration,'material-cotangent 5 seeded vectors; steps',len(sol.t),flush=True)
 write_csv(out/'observer_family_envelopes.csv',figures)
 write_csv(out/'transported_family_duality.csv',duality)
 tolmax={'relative_chart':max_chart,'relative_family_basis':max_basis,'bound_violation':max_bound,'parent_readout':max_parent,'root_distance':max_root,'duality_relative':max_dual}
 centers=[x for x in figures if x['root_position']=='barrier' and x['delta_B_minus_threshold']==1e-5]
 # Preserve independent count: each barrier is repeated per four threshold levels.
 report={'version':'v18.49c','status':'AUTHENTIC_11D_REPLAY_AND_TRANSPORTED_FINITE_COVECTOR_FAMILY',
         'physical_11D_integrations':nphys,'new_10D_five_covector_transport_IVPs':ntransport,
         'n_csv_rows':len(figures),'unique_barrier_states':ntransport,
         'metrics':list(metrics),'observer_family_sizes':[2,5],
         'max_11D_historical_forward_regression':max_replay,
         'max_energy_ledger_relative_residual':max_ledger,
         'max_relative_chart_covariance_residual':max_chart,
         'max_relative_basis_mixing_residual':max_basis,
         'max_observer_readout_envelope_violation':max_bound,
         'max_parent_B_probe_regression':max_parent,
         'max_parent_A_root_distance_regression':max_root,
         'max_tangent_cotangent_duality_residual':max_dual,
         'observations':{'euclidean_2':{'range_fraction': [min(x['fraction_explained'] for x in centers if x['metric']=='euclidean' and x['family_size']==2),max(x['fraction_explained'] for x in centers if x['metric']=='euclidean' and x['family_size']==2)]},
             'euclidean_5':{'range_fraction':[min(x['fraction_explained'] for x in centers if x['metric']=='euclidean' and x['family_size']==5),max(x['fraction_explained'] for x in centers if x['metric']=='euclidean' and x['family_size']==5)]}},
         'genealogy':pin,'boundary':'Invariant under equivalent column basis and joint chart+metric+covector transformation, NOT invariant under observer FAMILY or METRIC choice. Phaseblind branch0 only. Cotangent is 10D with externally prescribed Theta. Finite displacement need not satisfy linearized pairing conservation.'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 (out/'environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__},indent=2)+'\n')
 print(json.dumps(report,indent=2),flush=True)
 if max_replay>1e-7 or max_ledger>args.maximum_ledger_error or max_root>2e-7 or max_parent>args.maximum_parent_error or max_dual>args.maximum_duality_error or max_chart>1e-7 or max_basis>1e-7 or max_bound>1e-8:
  raise RuntimeError('Scientific regression gate failed')
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--smoke',action='store_true')
 ap.add_argument('--rtol',type=float,default=3e-12)
 ap.add_argument('--atol',type=float,default=3e-13)
 ap.add_argument('--max-step',type=float,default=.025)
 ap.add_argument('--maximum-ledger-error',type=float,default=1e-8)
 ap.add_argument('--adjoint-rtol',type=float,default=2e-10)
 ap.add_argument('--adjoint-atol',type=float,default=2e-12)
 ap.add_argument('--adjoint-max-step',type=float,default=.0125)
 ap.add_argument('--family-rank-tol',type=float,default=1e-10)
 ap.add_argument('--maximum-parent-error',type=float,default=1e-7)
 ap.add_argument('--maximum-duality-error',type=float,default=1e-7)
 run(ap.parse_args())
