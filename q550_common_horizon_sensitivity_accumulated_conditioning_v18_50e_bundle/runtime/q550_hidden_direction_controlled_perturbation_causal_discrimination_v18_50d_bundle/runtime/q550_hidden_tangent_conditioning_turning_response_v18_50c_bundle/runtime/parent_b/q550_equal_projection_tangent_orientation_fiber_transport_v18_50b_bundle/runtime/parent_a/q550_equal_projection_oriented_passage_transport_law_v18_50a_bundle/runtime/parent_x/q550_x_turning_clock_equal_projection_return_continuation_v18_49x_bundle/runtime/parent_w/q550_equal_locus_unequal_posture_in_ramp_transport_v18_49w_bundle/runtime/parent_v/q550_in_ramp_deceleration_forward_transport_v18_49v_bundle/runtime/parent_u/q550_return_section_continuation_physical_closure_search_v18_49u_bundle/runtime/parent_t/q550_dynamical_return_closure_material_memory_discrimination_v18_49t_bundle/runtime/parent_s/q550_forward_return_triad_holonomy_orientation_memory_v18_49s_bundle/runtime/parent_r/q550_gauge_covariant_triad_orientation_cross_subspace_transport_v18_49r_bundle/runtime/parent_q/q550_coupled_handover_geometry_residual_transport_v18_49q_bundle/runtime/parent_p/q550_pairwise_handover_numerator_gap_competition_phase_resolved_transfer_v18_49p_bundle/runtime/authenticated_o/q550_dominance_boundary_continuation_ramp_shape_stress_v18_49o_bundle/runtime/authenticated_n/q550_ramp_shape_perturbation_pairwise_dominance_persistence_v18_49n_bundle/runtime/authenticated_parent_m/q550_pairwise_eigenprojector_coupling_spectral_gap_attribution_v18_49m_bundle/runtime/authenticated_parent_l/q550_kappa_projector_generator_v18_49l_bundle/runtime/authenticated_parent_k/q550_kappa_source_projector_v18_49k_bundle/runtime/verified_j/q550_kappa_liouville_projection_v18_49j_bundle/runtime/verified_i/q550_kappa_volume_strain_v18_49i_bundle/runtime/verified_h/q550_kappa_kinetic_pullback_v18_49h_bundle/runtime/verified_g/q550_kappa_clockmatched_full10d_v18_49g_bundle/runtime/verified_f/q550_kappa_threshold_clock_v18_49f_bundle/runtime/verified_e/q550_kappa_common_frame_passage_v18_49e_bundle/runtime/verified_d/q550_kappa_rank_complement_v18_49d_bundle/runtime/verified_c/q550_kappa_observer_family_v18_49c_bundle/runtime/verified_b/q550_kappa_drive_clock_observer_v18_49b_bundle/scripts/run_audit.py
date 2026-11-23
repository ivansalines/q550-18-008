#!/usr/bin/env python3
"""v18.49b: real 10D material cotangent transport along 11D Q550 counterflows.

Theta(t) is prescribed by the original drive clock; material Jacobian is
analytic and derived from the authenticated 11D source. Historical v18.48j
covectors provide ONLY initial data at the genuine turning point, not a
pretend historical propagation along newly driven return trajectories.
"""
from __future__ import annotations
import argparse,csv,json,math,platform,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from verify_parent import verify,dynamic
from observer_math import integrate_dual,diagonal_covariance,shape_gradient,projective_angle
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'reference'))
RAMPS=(.285,.292,.296333,.300,.305,.309)
VELOCITY=(1,3,5,7,9)

def rows(path):
 with Path(path).open(newline='') as f:return list(csv.DictReader(f))
def output(path,data):
 if not data:raise ValueError('Empty output '+str(path))
 cols=list(dict.fromkeys(k for row in data for k in row))
 with Path(path).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(data)

def run(args):
 aroot,zroot,yroot,jroot,pins=verify()
 phys=dynamic(ROOT/'reference/physical_math.py','b_auth_phys')
 ramp=dynamic(ROOT/'reference/parent_ramp_math.py','b_auth_ramp')
 yr=dynamic(ROOT/'reference/y_original_run_audit.py','b_auth_ivp')
 jet=dynamic(ROOT/'reference/structural_jet.py','b_auth_analytic_J')
 support_candidates=list(zroot.rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
 if len(support_candidates)!=1:raise RuntimeError('Nonunique historical Q550 support source')
 support=dynamic(support_candidates[0],'b_auth_original_support')
 audit=dynamic(support_candidates[0].parent/'test_support_mobius_monodromy_audit.py','b_auth_original_audit')
 history=np.load(jroot/'runtime/physical_paths.npz',allow_pickle=False)
 hist=json.loads((jroot/'runtime/report_v18_48h.json').read_text())
 kvalues={'original':float(hist['kappa_original']),'autonomous':float(hist['kappa_autonomous'])}
 omega=float(history['clock_speed']);slope=omega/(2*np.pi)
 params=audit.ModelParameters(gamma_rho=.3)
 byfamily=defaultdict(list)
 for i in range(len(history['y'])):
  byfamily[(str(history['families'][i]),int(history['seed_branches'][i]),str(history['kappa_kind'][i]))].append(i)
 ar=rows(aroot/'results/continuous_11D_root_validation.csv')
 barrier=rows(zroot/'results/continuous_11D_root_validation.csv')
 assert len(ar)==48 and len(barrier)==48
 source={(x['kappa_kind'],round(float(x['ramp_duration_xi']),8),float(x['delta_B_minus_threshold'])):x for x in ar}
 use_kinds=('original',) if args.smoke else ('original','autonomous')
 use_ramps=(.296333,) if args.smoke else RAMPS
 out=ROOT/'results';out.mkdir(exist_ok=True)
 measurements=[];dual=[];samples=[];checks=[]
 num_integrations=0;max_replay=0.;max_ledger=0.;max_jac=0.;max_root=0.;max_coord=0.
 for kind in use_kinds:
  key=next(key for key in byfamily if key[0].startswith('phaseblind') and key[1]==0 and key[2]==kind)
  ix=sorted(byfamily[key],key=lambda i:float(history['xi'][i]))
  kappa=kvalues[kind]
  start=np.asarray(history['y'][ix[0]],float)
  forward,er=yr.integrate(phys,ramp,support,audit,kappa,params,slope,omega,start,args)
  num_integrations+=1;max_ledger=max(max_ledger,er)
  replay=max(float(np.linalg.norm(forward(t)[:11]-history['y'][index])) for t,index in zip(np.linspace(0,1,41),ix))
  max_replay=max(max_replay,replay)
  if replay>1e-7:raise RuntimeError('Physical forward history mismatch')
  turn=forward(1.)[:11].copy();turn[list(VELOCITY)]*=-1.
  historical=np.asarray(history['covectors'][ix[-1]],float)
  g0=historical[[0,1],:10].copy()
  norms=np.linalg.norm(g0,axis=1)
  if np.any(norms<1e-12):raise RuntimeError('Degenerate historical observer condition')
  g0/=norms[:,None]
  v0=g0[0].copy()
  for rv in use_ramps:
   design=ramp.Design('v18_49b_'+str(rv),'smoothstep',rv)
   back,eb=yr.integrate(phys,ramp,support,audit,kappa,params,slope,omega,turn,args,design=design)
   num_integrations+=1;max_ledger=max(max_ledger,eb)
   for t in [0.,rv*.35,rv,rv+.25,rv+.485,rv+.80]:
    state=back(t)[:11];f,J,_=jet.structural_jet(state,kappa,params,slope)
    fr=phys.rhs_from_original(state,kappa,params,slope,ramp.cubic_clock_sign(t,design),support,audit)
    jr=np.zeros((10,10))
    for col in [0,2,4,8]:
     h=2e-6;hi=state.copy();lo=state.copy();hi[col]+=h;lo[col]-=h
     jr[:,col]=(phys.rhs_from_original(hi,kappa,params,slope,0,support,audit)[:10]-phys.rhs_from_original(lo,kappa,params,slope,0,support,audit)[:10])/(2*h)
    errf=float(np.linalg.norm(f[:10]-fr[:10])/max(1.,np.linalg.norm(fr[:10])))
    errjac=float(np.linalg.norm(jr[:,[0,2,4,8]]-J[:10][:,[0,2,4,8]])/max(1.,np.linalg.norm(J[:10][:,[0,2,4,8]])))
    max_jac=max(max_jac,errf,errjac)
    checks.append({'kind':kind,'ramp':rv,'time':t,'analytic_rhs_relative_residual':errf,'analytic_jacobian_directional_fd_relative_residual':errjac})
   def jacobian(y,k,p,s):return jet.structural_jet(y,k,p,s)[1]
   transported,sol=integrate_dual(back,design,kappa,params,slope,omega,jacobian,g0,v0,1.+rv,
              rtol=args.adjoint_rtol,atol=args.adjoint_atol,max_step=args.adjoint_max_step)
   for t in np.linspace(0.,1.+rv,47):
    g,v=transported(t);base=g0@v0;current=g@v
    for channel in range(2):
     err=abs(current[channel]-base[channel])/max(1.,abs(base[channel]),abs(current[channel]))
     dual.append({'kappa_kind':kind,'ramp_duration_xi':rv,'elapsed_xi':t,'channel':channel,
       'frozen_seed_pairing':float(g0[channel]@v),'transported_dual_pairing':float(current[channel]),
       'initial_pairing':float(base[channel]),'relative_transport_pairing_residual':err,
       'observer_projective_angle_deg':projective_angle(g[channel],g0[channel]),
       'observer_norm_ratio':float(np.linalg.norm(g[channel])/np.linalg.norm(g0[channel]))})
   for delta in (1e-5,3e-5,1e-4,3e-4):
    keyroot=(kind,round(rv,8),delta)
    if keyroot not in source:raise RuntimeError('Authentic continuous root missing '+str(keyroot))
    r=source[keyroot]
    qleft=float(r['dense_IVP_left_root_q']);qright=float(r['dense_IVP_right_root_q'])
    qb=float(r['barrier_phase']);qlist=(('left',qleft),('barrier',qb),('right',qright))
    for name,q in qlist:
     yback=back(rv+q)[:11];yfwd=forward(1.-q)[:11]
     g,v=transported(rv+q)
     grad,d=shape_gradient(yback,yfwd)
     if name!='barrier':
      target=float(r['threshold_d3'])
     else:target=float(r['barrier_height'])
     max_root=max(max_root,abs(d-target))
     offset=(yback-yfwd)[:10].copy()
     for coord in [2,6]:offset[coord]=(offset[coord]+math.pi)%(2*math.pi)-math.pi
     scales=np.array([1.2,.8,1.15,1.1,.95,1.3,.7,1.1,.8,1.25])
     for channel in range(2):
      fixed=float(g0[channel]@offset)
      moved=float(g[channel]@offset)
      max_coord=max(max_coord,abs(diagonal_covariance(g[channel],offset,scales)))
      measurements.append({'kappa_kind':kind,'ramp_duration_xi':rv,'delta':delta,
       'root_position':name,'phase_q':q,'drive_clock_angle':float(yback[10]),
       'original_physical_clock_gap_rad':float((yback[10]-yfwd[10]+math.pi)%(2*math.pi)-math.pi),
       'geometric_distance_3D':d,'original_11D_separation':float(r['barrier_full_11D_distance']) if name=='barrier' else '',
       'energy_difference':phys.energy(yback,kappa,params)-phys.energy(yfwd,kappa,params),
       'observer_channel':channel,'historical_at_turn_fixed_probe':fixed,
       'genuinely_transported_probe':moved,'observer_gradient_overlap':float(g[channel]@grad/(np.linalg.norm(g[channel])*max(np.linalg.norm(grad),1e-300))),
       'fixed_gradient_overlap':float(g0[channel]@grad/(np.linalg.norm(g0[channel])*max(np.linalg.norm(grad),1e-300))),
       'observer_projective_angle_deg':projective_angle(g[channel],g0[channel]),
       'gauge_pairing_diagonal_residual':abs(diagonal_covariance(g[channel],offset,scales))})
   print('v18.49b',kind,'ramp',rv,'adjoint steps',len(sol.t),'roots 4 levels',flush=True)
 output(out/'transport_duality.csv',dual)
 output(out/'observer_probe_at_physical_roots.csv',measurements)
 output(out/'analytic_jacobian_checks.csv',checks)
 # Second covariance layer: recover original physical-clock skew from every
 # authenticated A chart counterfactual. These are NOT new 11D integrations.
 gauge_rows=rows(aroot/'results/chart_counterfactuals.csv')
 physical_skew={(r['kappa_kind'],round(float(r['ramp_duration_xi']),8),float(r['delta'])):r
                 for r in rows(aroot/'results/physical_phase_skew.csv')}
 gauge_checks=[]
 for row in gauge_rows:
  key=(row['kappa_kind'],round(float(row['ramp_duration_xi']),8),float(row['delta']))
  physrow=physical_skew[key]
  e1=abs(float(row['recovered_physical_midpoint_shift'])-float(physrow['signed_midpoint_shift_physical_q']))
  e2=abs(float(row['recovered_physical_cubic'])-float(physrow['physical_phase_local_fitted_cubic']))
  gauge_checks.append({'kappa_kind':row['kappa_kind'],'ramp_duration_xi':row['ramp_duration_xi'],
    'gauge':row['gauge'],'orientation':row['orientation'],
    'phase_midpoint_recovery_abs_error':e1,'physical_cubic_recovery_abs_error':e2,
    'physical_midpoint_shift':physrow['signed_midpoint_shift_physical_q'],
    'charted_midpoint_shift':row['charted_midpoint_shift']})
 if len(gauge_checks)!=240:raise RuntimeError('Original chart counterfactual genealogy incomplete')
 output(out/'physical_clock_chart_recovery.csv',gauge_checks)
 all_dual=[float(x['relative_transport_pairing_residual']) for x in dual]
 report={'version':'v18.49b','status':'AUTHENTIC_11D_DRIVEN_IVP_WITH_NEW_MATERIAL_COTANGENT_TRANSPORT',
 'parent_A_sha256':pins['parent_A_sha256'],'ancestry_verified_to_J':pins['ancestry_verified_to_J'],
 'physical_11D_integrations':num_integrations,'genuine_new_10D_cotangent_IVPs':len(use_kinds)*len(use_ramps),
 'historical_covectors_used_as_turning_point_seeds':2,
 'independent_model_control':'Theta(t) prescribed; only 10D material Jacobian and adjoint integrated',
 'physical_root_and_observer_rows':len(measurements),'sampled_duality_checks':len(dual),
 'maximum_duality_relative_residual':max(all_dual),
 'maximum_11D_parent_replay_error':max_replay,'maximum_energy_ledger_relative_error':max_ledger,
 'maximum_directional_Jacobian_FD_residual':max_jac,'maximum_original_root_distance_regression':max_root,
 'maximum_diagonal_chart_pairing_residual':max_coord,
 'rechecked_historical_phase_chart_counterfactuals':len(gauge_checks),
 'max_physical_clock_root_midpoint_recovery_error':max(x['phase_midpoint_recovery_abs_error'] for x in gauge_checks),
 'max_physical_clock_cubic_recovery_error':max(x['physical_cubic_recovery_abs_error'] for x in gauge_checks),
 'physical_root_clocks_unchanged':True,
 'scope':'Phaseblind branch0, two κ kinds, six ramps, four continuous-IVP root levels; material cotangent along each counterflow, not 11D full control adjoint.',
 'scientific_boundary':'Observer transport changes readout, not the physical geometric root locations. Dual pairing is linearized and must not be equated to finite-separation/energy conservation.'}
 (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
 (out/'runtime_environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__},indent=2)+'\n')
 print(json.dumps(report,indent=2),flush=True)
 if max_replay>1e-7 or max_root>2e-7 or max_jac>args.maximum_jacobian_residual or max_coord>1e-10 or max(all_dual)>args.maximum_duality_residual or max(x['physical_cubic_recovery_abs_error'] for x in gauge_checks)>1e-10:
  raise RuntimeError('One or more physical/transport verification gates did not pass')
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
 ap.add_argument('--maximum-jacobian-residual',type=float,default=1e-5)
 ap.add_argument('--maximum-duality-residual',type=float,default=1e-5)
 run(ap.parse_args())
