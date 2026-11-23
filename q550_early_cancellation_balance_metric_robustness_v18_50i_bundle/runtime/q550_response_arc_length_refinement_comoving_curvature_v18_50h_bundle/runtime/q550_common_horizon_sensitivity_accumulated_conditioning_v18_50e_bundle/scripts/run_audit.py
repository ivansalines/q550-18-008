#!/usr/bin/env python3
"""v18.50e — Common-Horizon Sensitivity & Accumulated Conditioning Audit.

Same elapsed XI interval from natural x-turning events, plus same-seed drive
counterfactual. Decompose response to an x-logit state kick into instantaneous
endpoint-chart sensitivity and transported tangent displacement. The split is a
linearized coordinate ledger, not a uniquely identifiable physical causal split.
"""
import argparse,csv,json,platform,traceback
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from verify_parent_d import verify
from response_math import unit,centered,angle,central_directional,split_response
ROOT=Path(__file__).resolve().parents[1]

def write_csv(name,rs):
    if not rs:return
    p=ROOT/'results'/name;p.parent.mkdir(exist_ok=True)
    fields=list(dict.fromkeys(k for r in rs for k in r))
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rs)

def run(args):
    parent,report,ancestry=verify()
    from parent_o_experiment import Experiment
    ex=Experiment(args)
    import csv as _csv
    with (parent/'results/case_summary.csv').open() as f: prev=list(_csv.DictReader(f))
    event_rows={(v['kind'],round(float(v['ramp_xi']),9),v.get('shape','beta:2:2')):float(v['turn_xi']) for v in prev}
    # v18.50d's case_summary did not carry shape: use v18.50c authenticated case ledger.
    croot=ROOT/'runtime'/parent.name/'runtime'/'q550_hidden_tangent_conditioning_turning_response_v18_50c_bundle'
    creport=json.loads((croot/'results/report.json').read_text())
    events={(z['kind'],round(float(z['ramp_xi']),9),z['shape']):float(z['turn_xi']) for z in creport['cases'] if z['metric']=='common'}
    if len(events)!=10:raise RuntimeError('Authenticated turning case count !=10')
    keys=sorted(events)
    if args.smoke: keys=[('original',.24,'beta:2:2')]
    if args.kind!='both':keys=[k for k in keys if k[0]==args.kind]
    scale=np.asarray(report['common_metric_scale_4d'],float)
    horizons=tuple(sorted({float(a) for a in args.horizons}))
    if min(horizons)<=0:raise ValueError('All horizons must be positive')
    eps=args.epsilon
    rows=[]; controls=[]; failures=[]; num_ivps=0;checks=[]

    def structural(y,kappa):
        f,j,_=ex.jet.structural_jet(y,kappa,ex.params,ex.slope)
        return np.asarray([f[2],f[6],(j@f)[2],(j@f)[6]],float)

    def do_case(kind,r,shape,event,seed,horizon_list,mode,source,metric):
        nonlocal num_ivps
        kappa=ex.ks[kind]
        design=ex.original_ramp.Design('50e_'+mode+'_'+kind+'_'+str(r),shape,r)
        th0=float(seed[10]);exc0=ex.clock.cubic_phase_excursion(event,design)
        def theta(t):return th0-ex.omega*(ex.clock.cubic_phase_excursion(t,design)-exc0)
        def sig(t):return ex.clock.cubic_clock_sign(t,design)
        def ode(t,z):
            y=np.r_[z,theta(t)]
            return ex.physical.rhs_from_original(y,kappa,ex.params,ex.slope,sig(t),ex.support,ex.audit)[:10]
        direction=lambda y:unit(structural(y,kappa),scale)
        max_h=max(horizon_list)
        if event+max_h>=r:raise RuntimeError('Horizon leaves ramp support')
        times=[event]+[event+h for h in horizon_list]
        ts=sorted(set(times))
        sols={}
        for s,label in [(0,'base'),(+1,'plus'),(-1,'minus')]:
            y=seed[:10].copy();y[8]+=s*eps
            sol=solve_ivp(ode,(event,event+max_h),y,t_eval=ts,
                 method='DOP853',rtol=args.rtol,atol=args.atol,max_step=min(args.max_step,max_h/20))
            num_ivps+=1
            if not sol.success:raise RuntimeError(label+' integration failed: '+sol.message)
            sols[s]=np.asarray(sol.y).T
        base=sols[0];plus=sols[1];minus=sols[-1]
        base_ref=direction(np.r_[seed[:10],theta(event)])
        for h in [0.]+list(horizon_list):
            i=ts.index(event+h)
            y=np.r_[base[i],theta(event+h)]
            yp=np.r_[plus[i],theta(event+h)];ym=np.r_[minus[i],theta(event+h)]
            deriv=centered(direction(yp),direction(ym),eps)
            transported=centered(yp[:10],ym[:10],eps)
            f,a,lin,res=split_response(direction,y,np.r_[transported,0.0],step=args.direction_step)
            obs_res=float(np.linalg.norm(lin-deriv)/max(1,np.linalg.norm(deriv)))
            # Source cross Jacobian (un-normalized RHS) is a separate local observable.
            jv=central_directional(lambda z:structural(z,kappa),y,np.eye(11)[8],args.direction_step)
            tnorm=float(np.linalg.norm(deriv))
            records={'mode':mode,'source':source,'kind':kind,'ramp_xi':r,'shape':shape,'turn_xi':event,
                 'horizon_xi':h,'probe_xi':event+h,'metric':'common_4d_parent_c',
                 'gain':tnorm,'baseline_hidden_direction_drift_deg':angle(base_ref,direction(y)),
                 'frozen_endpoint_x_gain':float(np.linalg.norm(f)),
                 'transported_component_gain':float(np.linalg.norm(a)),
                 'split_alignment_cos':float(np.dot(f,a)/max(np.linalg.norm(f)*np.linalg.norm(a),1e-20)),
                 'relative_residual_linearized_vs_IVP':obs_res,
                 'linearized_decomposition_residual':res,
                 'direction_response':json.dumps(deriv.tolist()),
                 'frozen_endpoint_response':json.dumps(f.tolist()),
                 'transported_component_response':json.dumps(a.tolist()),
                 'transported_state_tangent':json.dumps(transported.tolist()),
                 'local_hidden_structural_x_jet_jac_norm':float(np.linalg.norm(jv)),
                 'x_logit_tangent_response':float(transported[8]),
                 'is_same_seed_control':mode=='same_seed'}
            rows.append(records)
            if h==0 and np.linalg.norm(transported-np.eye(10)[8])>2e-8:raise RuntimeError('Kick tangent not identity at start')
            if obs_res>args.max_linearized_residual:raise RuntimeError('Endpoint response / propagated tangent mismatch')
        # Add amplitude sensitivity check on far endpoint, for first natural reference case only.
        return rows[-1]

    natural_seeds={}
    for kind,r,shape in keys:
        try:
            print('natural',kind,r,shape,flush=True)
            design=ex.original_ramp.Design('50e_natural',shape,r)
            back,ledger=ex.original.integrate(ex.physical,ex.clock,ex.support,ex.audit,
                 ex.ks[kind],ex.params,ex.slope,ex.omega,ex.turning[kind],args,design=design)
            event=events[(kind,r,shape)]
            seed=np.asarray(back(event)[:11],float)
            natural_seeds[(kind,r,shape)]=(event,seed)
            if max(horizons)>r-event-1e-5:raise RuntimeError('Horizon too long for natural case')
            far=do_case(kind,r,shape,event,seed,horizons,'natural_turn','authentic_v18_50c_turn',scale)
            # Check natural baseline at terminal time vs historic baseline trajectory.
            # Separate short replay to inspect x kick response scale when necessary.
            checks.append({'mode':'natural_turn','kind':kind,'ramp_xi':r,'shape':shape,
                           'ledger':ledger,'terminal_gain':far['gain']})
        except Exception as e:
            failures.append({'mode':'natural','kind':kind,'ramp_xi':r,'shape':shape,'error':repr(e),'trace':traceback.format_exc(limit=5)})
            if args.fail_fast:raise
    # All ramps in this family begin at exactly the SAME 11D seed and clock phase.
    # Drive-phase offset is explicitly adjusted to keep the initial phase unchanged.
    for kind in sorted({k[0] for k in keys}):
        basekey=(kind,.24,'beta:2:2')
        if basekey not in natural_seeds:continue
        event,seed=natural_seeds[basekey]
        for kr,rr,shape in keys:
            if kr!=kind:continue
            try:
                print('same seed',kind,rr,shape,flush=True)
                do_case(kind,rr,shape,event,seed,horizons,'same_seed','reference_024_cubic_turn',scale)
            except Exception as e:
                failures.append({'mode':'same_seed','kind':kind,'ramp_xi':rr,'shape':shape,'error':repr(e),'trace':traceback.format_exc(limit=5)})
                if args.fail_fast:raise
    write_csv('common_horizon_direction_responses.csv',rows)
    write_csv('baseline_replay_checks.csv',checks)
    write_csv('failures.csv',failures)
    if not rows:raise RuntimeError('No successful cases')
    full=[z for z in rows if z['horizon_xi']==max(horizons)]
    res={'version':'v18.50e','title':'Common-Horizon Sensitivity & Accumulated Conditioning Audit',
         'classification':'COMMON_HORIZON_IN_MODEL_RESPONSE_DECOMPOSITION_NOT_PHYSICAL_CAUSAL_OR_REGIME_CERTIFICATE',
         'genealogy':ancestry,'metric_scale_4d':scale.tolist(),
         'protocol':{'modes':['natural_turn','same_seed'], 'horizons_xi':horizons,'epsilon':eps,
             'intervention':'symmetric +/- kick to x logit at event; exact 11D physical RHS afterwards',
             'same_seed':'same exact 11D Q550 turning state from original cubic r=0.24, including initial phase; future drive varies',
             'frozen_endpoint':'directional derivative of endpoint hidden unit-jet w.r.t. x-logit only, holding other endpoint coordinates fixed',
             'accumulated':'endpoint directional derivative along transported state tangent minus frozen-endpoint x basis vector',
             'caveat':'coordinate decomposition of linearized response; not a physical causal mediation or a uniquely invariant attribution'},
         'counts':{'natural_cases':len([z for z in rows if z['mode']=='natural_turn' and z['horizon_xi']==max(horizons)]),
             'same_seed_cases':len([z for z in rows if z['mode']=='same_seed' and z['horizon_xi']==max(horizons)]),
             'rows':len(rows),'11D_IVPs_short':num_ivps,'failures':len(failures)},
         'results':{'max_linearized_response_relative_residual':max(z['relative_residual_linearized_vs_IVP'] for z in rows),
             'max_split_residual':max(z['linearized_decomposition_residual'] for z in rows),
             'natural_endpoint_gain_range':[min(z['gain'] for z in full if z['mode']=='natural_turn'),max(z['gain'] for z in full if z['mode']=='natural_turn')],
             'same_seed_endpoint_gain_range':[min(z['gain'] for z in full if z['mode']=='same_seed'),max(z['gain'] for z in full if z['mode']=='same_seed')]},
         'limitations':['Each natural turning seed differs across ramp protocols; only same_seed control removes this confounder.',
            'The hidden structural jet depends on the original coordinate chart; the pooled diagonal metric is declared, not physical.',
            'The centered kick requires an intervention on a mathematical state component, not a physically available actuator.',
            'No unique causal division between direct x and accumulated path exists: this decomposition depends on the chosen endpoint basis.',
            'An increasing gain does not alone indicate a bifurcation or a change of dynamical regime.',
            'No spatial volume, material memory, physical fiber, or cubic realization is inferred.'],
         'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__}}
    (ROOT/'results/report.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
    print('RESULT',json.dumps(res['counts']),json.dumps(res['results']),flush=True)
    if failures:raise RuntimeError('Some cases failed')
    return res

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true');p.add_argument('--kind',choices=['original','autonomous','both'],default='both')
    p.add_argument('--horizons',nargs='+',type=float,default=[.0125,.025,.0375,.05])
    p.add_argument('--epsilon',type=float,default=1e-4)
    p.add_argument('--direction-step',type=float,default=1e-6)
    p.add_argument('--rtol',type=float,default=3e-12);p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025);p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    p.add_argument('--maximum-parent-share-difference',type=float,default=2e-6)
    p.add_argument('--max-generator-identity-error',type=float,default=1e-7)
    p.add_argument('--max-linearized-residual',type=float,default=5e-3)
    p.add_argument('--fail-fast',action='store_true')
    a=p.parse_args();run(a)
