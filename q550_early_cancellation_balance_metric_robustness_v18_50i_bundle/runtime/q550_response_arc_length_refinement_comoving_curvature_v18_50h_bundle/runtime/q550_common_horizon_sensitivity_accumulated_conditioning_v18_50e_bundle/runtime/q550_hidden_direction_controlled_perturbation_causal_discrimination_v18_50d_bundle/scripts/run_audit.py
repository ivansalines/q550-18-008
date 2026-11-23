#!/usr/bin/env python3
"""v18.50d — Hidden-Direction Controlled Perturbation & Causal Discrimination Audit.

Controlled in-model interventions at AUTHENTIC x-turning states: logit-x kick,
angular-state kick, or a zero-net-phase external clock pulse. Evaluate
finite-difference response of the hidden 4D direction under a fixed metric.
These identify responses in THIS ODE, not a physical causal mechanism.
"""
from pathlib import Path
from collections import defaultdict
import argparse,csv,json,platform,sys,traceback
import numpy as np
from scipy.integrate import solve_ivp
from verify_parent_c import verify
from perturbation_math import unit,centered,direction_angle,pulse
ROOT=Path(__file__).resolve().parents[1]

def csv_out(name,rows):
    if not rows:return
    p=ROOT/'results'/name;p.parent.mkdir(parents=True,exist_ok=True)
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with p.open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader();wr.writerows(rows)

def run(args):
    croot,creport,lineage=verify()
    from parent_o_experiment import Experiment
    ex=Experiment(args)
    origins={}
    for c in creport['cases']:
        if c['metric']=='common':origins[(c['kind'],round(float(c['ramp_xi']),9),c['shape'])]=float(c['turn_xi'])
    scale=np.asarray(creport['common_scale_4d'],float)
    if len(origins)!=10:raise RuntimeError('Unexpected source case count')
    cases=sorted(origins)
    if args.smoke:cases=[('original',.24,'beta:2:2')]
    elif args.kind!='both':cases=[c for c in cases if c[0]==args.kind]
    if args.ramps:cases=[c for c in cases if any(abs(c[1]-r)<1e-9 for r in args.ramps)]
    if not cases:raise RuntimeError('No case selected')
    source_rows=[];responses=[];case_summary=[];failures=[];linear=[];run_count=0
    amplitudes=tuple(float(v) for v in args.amplitudes)
    for kind,r,shape in cases:
      print('v18.50d controlled case',kind,r,shape,flush=True)
      try:
        design=ex.original_ramp.Design('50d_'+kind,shape,r)
        back,ledger=ex.original.integrate(ex.physical,ex.clock,ex.support,ex.audit,
            ex.ks[kind],ex.params,ex.slope,ex.omega,ex.turning[kind],args,design=design)
        event=origins[(kind,r,shape)]
        if not 0<event<r:raise RuntimeError('Invalid event')
        horizon=min(args.horizon,r-event-args.end_guard)
        if horizon<=0:raise RuntimeError('Event leaves no probe interval')
        probe=event+horizon
        seed=np.asarray(back(event)[:11],float)
        refstate=np.asarray(back(probe)[:11],float)
        theta_start=float(ex.turning[kind][10]);kappa=ex.ks[kind]
        def reference_theta(t,drive_amp=0.):
            dp,_=pulse(t,event,probe,drive_amp)
            return theta_start-ex.omega*(ex.clock.cubic_phase_excursion(t,design)+dp)
        def sign(t,drive_amp=0.):
            _,rate=pulse(t,event,probe,drive_amp)
            return ex.clock.cubic_clock_sign(t,design)+rate
        def structural_velocity(y):
            f,J,_=ex.jet.structural_jet(y,kappa,ex.params,ex.slope)
            acc=J@f
            return np.asarray([f[2],f[6],acc[2],acc[6]],float)
        def endpoint_velocity(y):
            return unit(structural_velocity(y),scale)
        base_dir=endpoint_velocity(refstate)
        src_y=seed.copy()
        sf,Jac,_=ex.jet.structural_jet(src_y,kappa,ex.params,ex.slope)
        dx_struct=Jac[[2,6,3,7],8]
        check_eps=1e-5
        aplus=src_y.copy();aminus=src_y.copy();aplus[8]+=check_eps;aminus[8]-=check_eps
        field_plus=ex.physical.rhs_from_original(aplus,kappa,ex.params,ex.slope,sign(event),ex.support,ex.audit)
        field_minus=ex.physical.rhs_from_original(aminus,kappa,ex.params,ex.slope,sign(event),ex.support,ex.audit)
        dx_finite=((field_plus-field_minus)/(2*check_eps))[[2,6,3,7]]
        direct_jac_error=float(np.linalg.norm(dx_finite-dx_struct)/max(1.,np.linalg.norm(dx_struct)))
        if direct_jac_error>args.direct_jac_tolerance:raise RuntimeError('Structural Jacobian / physical RHS cross derivative disagree')
        # Analytic coupling proxy; first two entries may be zero by coordinate structure.
        src={'kind':kind,'ramp_xi':r,'shape':shape,'turn_xi':event,
             'horizon_xi':horizon,'probe_xi':probe,'source_x':float(1/(1+np.exp(-seed[8]))),
             'source_hidden_field_x_jac_norm':float(np.linalg.norm(dx_struct)),
             'source_hidden_field_x_jac':json.dumps(dx_struct.tolist()),
             'source_x_jacobian_physical_finite_difference_relative_error':direct_jac_error,
             'baseline_mechanical_ledger':float(ledger)}
        source_rows.append(src)
        for intervention in ('x_logit_kick','theta1_kick','compensated_drive_pulse'):
          entries=[]
          for eps in amplitudes:
            ends={}
            for sgn in (-1,1):
              strength=sgn*eps
              initial=seed.copy();drive_amp=0.
              if intervention=='x_logit_kick':initial[8]+=strength
              elif intervention=='theta1_kick':initial[2]+=strength
              else:drive_amp=strength
              def ode(t,z):
                  y=np.r_[z,reference_theta(t,drive_amp)]
                  return ex.physical.rhs_from_original(y,kappa,ex.params,ex.slope,sign(t,drive_amp),ex.support,ex.audit)[:10]
              sol=solve_ivp(ode,(event,probe),initial[:10],method='DOP853',rtol=args.rtol,
                  atol=args.atol,max_step=min(args.max_step,horizon/12))
              run_count+=1
              if not sol.success:raise RuntimeError('Perturbation IVP failed '+sol.message)
              endpoint=np.r_[sol.y[:,-1],reference_theta(probe,drive_amp)]
              ends[sgn]=(endpoint,endpoint_velocity(endpoint))
            yp,up=ends[1];ym,um=ends[-1]
            response_dir=centered(base_dir,up,um,eps)
            response_state=centered(refstate[:10],yp[:10],ym[:10],eps)
            first_two=float(np.linalg.norm(response_dir[:2]))
            last_two=float(np.linalg.norm(response_dir[2:]))
            resp={'kind':kind,'ramp_xi':r,'shape':shape,'intervention':intervention,'epsilon':eps,
                  'turn_xi':event,'horizon_xi':horizon,'xi_probe':probe,
                  'direction_gain':float(np.linalg.norm(response_dir)),
                  'response_theta_direction_norm':first_two,
                  'response_rate_direction_norm':last_two,
                  'rate_direction_fraction':float(last_two**2/(first_two**2+last_two**2)) if first_two**2+last_two**2>0 else None,
                  'response_dir_components':json.dumps(response_dir.tolist()),
                  'x_response_dx_per_eps':float((1/(1+np.exp(-yp[8]))-1/(1+np.exp(-ym[8])))/(2*eps)),
                  'theta1_response_per_eps':float(response_state[2]),
                  'theta2_response_per_eps':float(response_state[6]),
                  'angle_plus_deg':direction_angle(base_dir,up),
                  'angle_minus_deg':direction_angle(base_dir,um),
                  'odd_direction_error':float(np.linalg.norm((up-base_dir)+(um-base_dir)) / max(np.linalg.norm(up-um),1e-20)),
                  'endpoint_theta_difference_from_baseline':float(max(abs(yp[10]-refstate[10]),abs(ym[10]-refstate[10]))),
                  'x_and_hidden_are_controlled_separately':True}
            entries.append((eps,response_dir,resp));responses.append(resp)
          e0,dr0,_=entries[0];e1,dr1,_=entries[-1]
          change=float(np.linalg.norm(dr1-dr0)/max(np.linalg.norm(dr0),1e-20))
          linear.append({'kind':kind,'ramp_xi':r,'shape':shape,'intervention':intervention,
                'relative_derivative_drift_small_to_large_amplitude':change,
                'small_amplitude_gain':float(np.linalg.norm(dr0)),
                'large_amplitude_gain':float(np.linalg.norm(dr1))})
          print('  ',intervention,'first order gain',round(float(np.linalg.norm(dr0)),6),
                'amp sensitivity',round(change,8),flush=True)
        case_summary.append({'kind':kind,'ramp_xi':r,'turn_xi':event,'horizon_xi':horizon,
                             'baseline_ledger':float(ledger),'parent_scale':json.dumps(scale.tolist())})
      except Exception as e:
        failures.append({'kind':kind,'ramp_xi':r,'error':repr(e),'trace':traceback.format_exc(limit=7)})
        if args.fail_fast:raise
    csv_out('source_jacobian_at_turning.csv',source_rows)
    csv_out('controlled_intervention_responses.csv',responses)
    csv_out('amplitude_linearity_checks.csv',linear)
    csv_out('case_summary.csv',case_summary)
    csv_out('failures.csv',failures)
    if not responses:raise RuntimeError('No intervention response')
    report={'version':'v18.50d','title':'Hidden-Direction Controlled Perturbation & Causal Discrimination Audit',
      'classification':'CONTROLLED_IN_MODEL_SENSITIVITY_NOT_ESTABLISHED_PHYSICAL_CAUSALITY_OR_MATERIAL_MEMORY_CERTIFICATE',
      'ancestry':lineage,'common_metric_scale_4d':scale.tolist(),
      'method':{'source_event':'natural x turning from authenticated v18.50c',
         'interventions':['small symmetric kicks to logit-x coordinate at same baseline state',
                         'small symmetric kicks to theta1 at same baseline state',
                         'finite zero-net-integral clock-rate perturbation with matched start/end phase'],
         'amplitudes':amplitudes,'continuation':'authentic physical 11D RHS with same κ₀ and analytic clock',
         'response':'centered derivative of normalized 4D structural hidden jet direction at common probe time',
         'metric':'one pooled fixed diagonal chart from v18.50c',
         'limitations':['State kicks are mathematical counterfactuals; their energy is not constrained to be equal.',
                        'Independent x and theta1 kicks need not be physically realizable operations.',
                        'No randomized, physical or autonomous perturbation experiment is certified.',
                        'Causal arrows cannot be uniquely identified from correlated observational ramps.',
                        'The structural hidden jet follows v18.50c and is not a coordinate-free physical angular acceleration.',
                        'Smooth dependence at the tested amplitudes does not exclude distant thresholds.',
                        'No 8-octant, cubic lift, material memory, chiral physical rotation or spatial volume is inferred.']},
      'counts':{'cases':len(case_summary),'amplitudes':len(amplitudes),'response_rows':len(responses),
                'controlled_ivps':run_count,'failed_cases':len(failures)},
      'results':{'maximum_direct_jacobian_vs_physical_rhs_error':max(z['source_x_jacobian_physical_finite_difference_relative_error'] for z in source_rows),
                 'maximum_linear_response_drift':max(x['relative_derivative_drift_small_to_large_amplitude'] for x in linear),
                 'minimum_x_jacobian_norm':min(z['source_hidden_field_x_jac_norm'] for z in source_rows),
                 'maximum_x_jacobian_norm':max(z['source_hidden_field_x_jac_norm'] for z in source_rows),
                 'all_drive_pulse_theta_endpoints_match':all(x['endpoint_theta_difference_from_baseline']<1e-10 for x in responses if x['intervention']=='compensated_drive_pulse')},
      'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__}}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print('RESULT',json.dumps(report['counts']),json.dumps(report['results']),flush=True)
    if failures:raise RuntimeError('Failed cases: '+str(len(failures)))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true');p.add_argument('--kind',choices=['both','original','autonomous'],default='both')
    p.add_argument('--ramps',nargs='*',type=float);p.add_argument('--amplitudes',nargs='+',type=float,default=[1e-5,1e-4,1e-3]);p.add_argument('--horizon',type=float,default=.05)
    p.add_argument('--end-guard',type=float,default=1e-5)
    p.add_argument('--direct-jac-tolerance',type=float,default=1e-5)
    p.add_argument('--rtol',type=float,default=3e-12);p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025);p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    p.add_argument('--maximum_parent_share_difference',type=float,default=2e-6)
    p.add_argument('--max_generator_identity_error',type=float,default=1e-7)
    p.add_argument('--fail-fast',action='store_true')
    a=p.parse_args();assert min(a.amplitudes)>0 and a.horizon>0
    run(a)
