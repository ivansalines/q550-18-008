#!/usr/bin/env python3
"""v18.48t: physically integrated rate/duration/partial-flip contact persistence.

Every reverse is an original-support forward-time 11D IVP under a prescribed
negative drive clock. Partial reversals require an explicit kinetic-energy
preparation jump. All contact minima are same external UNWRAPPED phase, not
free-time matches. Comparisons on a common phase q avoid unequal clock spans.
"""
from __future__ import annotations
import argparse,csv,importlib.util,json,math,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from verify_parent import verify
from protocol_math import (designs,common_phase_domain,minimum_on_shared_clock,
             prepare_reversal,sample_persistence,signed_power_opposition)
ROOT=Path(__file__).resolve().parents[1]
def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def writecsv(path,rows):
    if not rows:return
    keys=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def summarize(rows, key):
    a=np.asarray([float(r[key]) for r in rows],float)
    return {'count':len(a),'min':float(a.min()),'median':float(np.median(a)),'max':float(a.max())} if len(a) else {}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rtol',type=float,default=3e-12)
    ap.add_argument('--atol',type=float,default=3e-13)
    ap.add_argument('--max-step',type=float,default=.025)
    ap.add_argument('--alpha',type=float,nargs='+',default=[0.,.25,.5,.75,1.])
    ap.add_argument('--limit-groups',type=int,default=0,help='Preflight subset ONLY: 0 means all 8 physical paths')
    ap.add_argument('--profile-nodes',type=int,default=81)
    ap.add_argument('--minimizer-nodes',type=int,default=141)
    ap.add_argument('--output-dir',type=Path,default=ROOT/'results')
    args=ap.parse_args()
    if args.limit_groups<0 or args.profile_nodes<31 or args.minimizer_nodes<51:raise ValueError('Insufficient numerical resolution')
    if len(args.alpha)!=len(set(args.alpha)) or any(not 0<=a<=1 for a in args.alpha):raise ValueError('Alpha values must be distinct and in [0,1]')
    dlist=designs();qmin,qmax=common_phase_domain(dlist)
    # 1e-9 shrinking avoids exactly touching bounds after floating-point arithmetic.
    qgrid=np.linspace(qmin+1.e-9,qmax-1.e-9,args.profile_nodes)
    parent,r,j,provenance=verify()
    p=r/'runtime/verified_parent/q550_kappa_counterflow_crossings_v18_48q_bundle/runtime/verified_parent/q550_kappa_counterflow_energy_v18_48p_bundle'
    physical=load_module(ROOT/'reference/physical_math.py','q550_v1848t_physical')
    geometry=load_module(ROOT/'reference/transversality_math.py','q550_v1848t_geometry')
    support=load_module(p/'reference/test_support_q550_support_ode_interval_residual_pilot_v1.py','q550_v1848t_support')
    audit=load_module(p/'reference/test_support_mobius_monodromy_audit.py','q550_v1848t_audit')
    history=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    state=np.asarray(history['y'],float);times=np.asarray(history['xi'],float)
    h=json.loads((j/'runtime/report_v18_48h.json').read_text())
    kappas={'original':float(h['kappa_original']),'autonomous':float(h['kappa_autonomous'])}
    slope=float(history['clock_speed'])/(2*math.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    groups=defaultdict(list)
    for i in range(len(times)):
        key=(str(history['families'][i]),int(history['seed_branches'][i]),str(history['kappa_kind'][i]))
        groups[key].append(i)
    if len(groups)!=8 or len(times)!=328:raise RuntimeError('Historical source contains unexpected paths')
    selected=sorted(groups)
    if args.limit_groups:selected=selected[:args.limit_groups]
    output=args.output_dir;output.mkdir(parents=True,exist_ok=True)
    contacts=[];profiles=[];regr=[];max_energy_error=0.;max_gap_ledger=0.;max_clock=0.
    max_jump_identity=0.;runs=0
    def rhs(y,k,rate):return physical.rhs_from_original(y,k,params,slope,rate,support,audit)
    def integrate(y0,tf,k,rate):
        nonlocal runs,max_energy_error
        z0=np.r_[y0,np.zeros(4)]
        def augmented(t,z):
            return np.r_[rhs(z[:11],k,rate),physical.power_terms(z[:11],k,params,slope,rate)]
        sol=solve_ivp(augmented,(0.,tf),z0,dense_output=True,method='DOP853',
                     rtol=args.rtol,atol=args.atol,max_step=args.max_step)
        if not sol.success:raise RuntimeError('Original Q550 IVP failed: '+sol.message)
        runs+=1
        e=physical.energy(sol.y[:11,-1],k,params)-physical.energy(y0,k,params)
        parts=sol.y[11:,-1]
        error=abs(e-sum(parts))/max(1.,abs(e),sum(abs(parts)))
        max_energy_error=max(max_energy_error,float(error))
        if error>1e-8:raise RuntimeError('Constitutive energy ledger rejected')
        def evaluate(u):
            x=np.asarray(u,float)
            z=sol.sol(x*tf)
            return np.moveaxis(z,0,-1) if x.ndim else z
        return evaluate
    for family,branch,kind in selected:
        indexes=sorted(groups[family,branch,kind],key=lambda i:times[i]);k=kappas[kind]
        if not np.allclose(times[indexes],np.linspace(3.5,4.5,41),atol=1e-12):raise RuntimeError('Historical section grid changed')
        F=integrate(state[indexes[0]],1.,k,1.)
        hist_deviation=float(np.max(np.linalg.norm(F(np.linspace(0,1,41))[:,:11]-state[indexes],axis=1)))
        if hist_deviation>1e-7:raise RuntimeError('Original 11D path regression')
        regr.append(dict(family=family,branch=branch,kappa_kind=kind,maximum_11D_historical_replay_error=hist_deviation))
        turn=F(1.)[:11];turn_E=physical.energy(turn,k,params)
        original_initial_energy=physical.energy(F(0.)[:11],k,params)
        forward_ledger=float(np.sum(F(1.)[11:]))
        if abs((turn_E-original_initial_energy)-forward_ledger)>1e-7:raise RuntimeError('Historical forward balance')
        for d in dlist:
            a=d.rate*d.duration
            fprofile=F(1.-qgrid)[...,:11]
            fshape=geometry.shape(fprofile)
            for alpha in args.alpha:
                init=prepare_reversal(turn,alpha)
                jump=physical.energy(init,k,params)-turn_E
                # Independently evaluate kinetic-energy jump, with all five
                # material velocities scaled by the same factor c=1-2alpha.
                factor=(1.-2.*alpha)**2-1.
                kinetic=physical.energy(turn,k,params)-physical.energy(prepare_reversal(turn,.5),k,params)
                expected_jump=factor*kinetic
                max_jump_identity=max(max_jump_identity,abs(jump-expected_jump))
                if abs(jump-expected_jump)>1e-9:raise RuntimeError('Partial-flip energy preparation formula failed')
                R=integrate(init,d.duration,k,-d.rate)
                minimum=minimum_on_shared_clock(F,R,geometry,d,nodes=args.minimizer_nodes)
                u=minimum['u'];s=minimum['s'];zr=R(u);zf=F(s)
                yR=zr[:11];yF=zf[:11]
                clock_delta=float(geometry.wrap(yR[10]-yF[10]))
                max_clock=max(max_clock,abs(clock_delta))
                if abs(clock_delta)>1e-9:raise RuntimeError('External phase not locked')
                E_R=physical.energy(yR,k,params);E_F=physical.energy(yF,k,params)
                predicted_gap=(float(sum(F(1.)[11:]))-float(sum(zf[11:])))+jump+float(sum(zr[11:]))
                gap_residual=(E_R-E_F)-predicted_gap
                max_gap_ledger=max(max_gap_ledger,abs(gap_residual))
                if abs(gap_residual)>1e-7:raise RuntimeError('Wrong energy-gap ledger at matched phase')
                pF=physical.power_terms(yF,k,params,slope,1.)
                pR=physical.power_terms(yR,k,params,slope,-d.rate)
                dr=geometry.shape_tangent(yR,rhs(yR,k,-d.rate))*d.duration
                df=geometry.shape_tangent(yF,rhs(yF,k,1.))
                cos=float(np.dot(dr,df)/(np.linalg.norm(dr)*np.linalg.norm(df)))
                ang=float(np.degrees(np.arccos(np.clip(cos,-1.,1.))))
                full=yR-yF;full[[2,6,10]]=geometry.wrap(full[[2,6,10]])
                # Common phase comparisons: identical q across every design,
                # WITHOUT optimizing each protocol over a different interval.
                uprofile=qgrid/a
                rprofile=R(uprofile)[...,:11]
                dist=np.linalg.norm(geometry.shape(rprofile)-fshape,axis=1)
                drive_opp=[];pRdrive=[];deltaE=[]
                for ix in range(len(qgrid)):
                    vR=rprofile[ix];vF=fprofile[ix]
                    dP=physical.power_terms(vR,k,params,slope,-d.rate)[0]
                    fP=physical.power_terms(vF,k,params,slope,1.)[0]
                    drive_opp.append(signed_power_opposition(dP,fP))
                    pRdrive.append(float(dP))
                    deltaE.append(physical.energy(vR,k,params)-physical.energy(vF,k,params))
                near={}
                for th in (.0025,.005,.01,.02):
                    met=sample_persistence(qgrid,dist,th)
                    prefix='shape_below_'+str(th).replace('.','p')
                    near[prefix+'_fraction']=met['fraction']
                    near[prefix+'_contiguous_q']=met['max_contiguous_phase_width']
                contacts.append(dict(family=family,branch=branch,kappa_kind=kind,
                    design=d.name,rate=d.rate,duration_xi=d.duration,total_phase_excursion=a,
                    alpha=float(alpha),initial_velocity_multiplier=1.-2.*alpha,
                    phase_locked_min_distance=minimum['gap'],min_return_progress=u,
                    min_forward_progress=s,min_common_phase_q=minimum['q'],
                    min_is_interior=int(minimum['interior']),number_local_candidates=minimum['number_local_candidates'],
                    min_full11D_distance=float(np.linalg.norm(full)),
                    min_velocity_mismatch_L2=float(np.linalg.norm(full[[1,3,5,7,9]])),
                    min_angle_chronological_deg=ang,min_theta1_difference_rad=float(full[2]),
                    min_theta2_difference_rad=float(full[6]),
                    min_external_phase_difference_rad=clock_delta,
                    min_energy_difference=float(E_R-E_F),
                    preparation_energy_jump=float(jump),
                    min_drive_power_forward=float(pF[0]),min_drive_power_return=float(pR[0]),
                    min_drive_power_opposite=int(signed_power_opposition(pR[0],pF[0])),
                    min_energy_ledger_residual=float(gap_residual),
                    common_phase_q_lo=float(qgrid[0]),common_phase_q_hi=float(qgrid[-1]),
                    common_phase_min_distance=float(np.min(dist)),
                    common_phase_median_distance=float(np.median(dist)),
                    common_phase_opposite_drive_fraction=float(np.mean(drive_opp)),
                    common_phase_energy_gap_median=float(np.median(deltaE)),**near))
                for i,q in enumerate(qgrid):
                    profiles.append(dict(family=family,branch=branch,kappa_kind=kind,
                       design=d.name,rate=d.rate,duration_xi=d.duration,alpha=float(alpha),
                       common_phase_q=float(q),return_progress=float(q/a),forward_progress=float(1.-q),
                       shape_distance=float(dist[i]),drive_power_return=float(pRdrive[i]),
                       drive_power_opposite=int(drive_opp[i]),energy_difference=float(deltaE[i])))
        print('v18.48t group',family,branch,kind,'finished; historical regression',f'{hist_deviation:.3e}',flush=True)
    # Source regression against both endpoint controls of authenticated v18.48s.
    import csv as _csv
    with (parent/'results/signed_contacts.csv').open(newline='') as _f:
        source_s=[v for v in _csv.DictReader(_f) if v['contact_kind']=='phase_locked_min'
                  and float(v['rate'])==1. and float(v['duration_xi'])==1.]
    source_lookup={(v['family'],int(v['branch']),v['kappa_kind'],int(v['velocity_flip'])):v
                   for v in source_s}
    parent_shape_regression=0.;parent_power_regression=0.;parent_comparisons=0
    for v in contacts:
        if v['design']!='phaseclosed_reference' or v['alpha'] not in (0.,1.):continue
        key=(v['family'],v['branch'],v['kappa_kind'],int(v['alpha']))
        old=source_lookup[key];parent_comparisons+=1
        parent_shape_regression=max(parent_shape_regression,
            abs(v['phase_locked_min_distance']-float(old['shape_distance'])))
        parent_power_regression=max(parent_power_regression,
            abs(v['min_drive_power_forward']-float(old['drive_power_forward_per_xi'])),
            abs(v['min_drive_power_return']-float(old['drive_power_return_per_xi'])))
    if parent_shape_regression>1e-8 or parent_power_regression>1e-7:
        raise RuntimeError('Original v18.48s physical endpoint regression failed')

    # Causality control: at identical drive rate, matching initial alpha and
    # matching elapsed phase, the programmed stopping duration cannot affect
    # the trajectory prior to that stop. Each array uses identical shared q.
    keyed={(v['family'],v['branch'],v['kappa_kind'],v['alpha'],v['design']):v
           for v in contacts}
    group_index={ (v['family'],v['branch'],v['kappa_kind'],v['alpha'],v['design']):[] for v in contacts }
    for row in profiles:
        group_index[(row['family'],row['branch'],row['kappa_kind'],row['alpha'],row['design'])].append(row)
    equal_rate_pairs=(('phaseclosed_slow','durationfixed_slow'),
          ('phaseclosed_fast','durationfixed_fast'),
          ('phaseclosed_reference','ratefixed_short'),
          ('phaseclosed_reference','ratefixed_long'))
    same_rate_max_phase_gap=0.;same_rate_max_energy_gap=0.;same_rate_comparisons=0
    for family,branch,kind in selected:
        for alpha in args.alpha:
            for design1,design2 in equal_rate_pairs:
                first=group_index[(family,branch,kind,float(alpha),design1)]
                second=group_index[(family,branch,kind,float(alpha),design2)]
                for a,b in zip(first,second):
                    same_rate_comparisons+=1
                    same_rate_max_phase_gap=max(same_rate_max_phase_gap,
                        abs(a['shape_distance']-b['shape_distance']))
                    same_rate_max_energy_gap=max(same_rate_max_energy_gap,
                        abs(a['energy_difference']-b['energy_difference']),
                        abs(a['drive_power_return']-b['drive_power_return']))
    if max(same_rate_max_phase_gap,same_rate_max_energy_gap)>1e-9:
        raise RuntimeError('Equal-rate matched-prefix identity violated')

    writecsv(output/'protocol_contacts.csv',contacts)
    writecsv(output/'common_phase_profiles.csv',profiles)
    writecsv(output/'historical_regression.csv',regr)
    summary={}
    for family in sorted(set(v['family'] for v in contacts)):
        sub=[c for c in contacts if c['family']==family]
        summary[family]={'cases':len(sub),'shape_distance':summarize(sub,'phase_locked_min_distance'),
          'energy_gap':summarize(sub,'min_energy_difference'),
          'opposite_drive_power_count':sum(c['min_drive_power_opposite'] for c in sub),
          'interior_minima_count':sum(c['min_is_interior'] for c in sub)}
    report={'version':'v18.48t','title':'Counterflow Rate–Duration Separation & Contact Persistence Audit',
      'status':'complete' if len(selected)==8 and len(args.alpha)==5 else 'limited_preflight',
      'historical_paths_used':len(selected),'historical_states_parent':len(times),
      'genuine_11D_integrations':runs,'expected_11D_integrations':len(selected)*(1+len(dlist)*len(args.alpha)),
      'independent_designs':len(dlist),'alpha_values':args.alpha,
      'rate_duration_designs':[vars(d) for d in dlist],
      'same_external_phase_minima':len(contacts),'common_phase_profile_points':len(profiles),
      'common_phase_interval_q':[float(qgrid[0]),float(qgrid[-1])],
      'minima_drive_power_opposite_signs':sum(c['min_drive_power_opposite'] for c in contacts),
      'minima_interior':sum(c['min_is_interior'] for c in contacts),
      'min_3D_gap':min(c['phase_locked_min_distance'] for c in contacts),
      'min_11D_gap':min(c['min_full11D_distance'] for c in contacts),
      'max_original_11D_path_regression':max(v['maximum_11D_historical_replay_error'] for v in regr),
      'max_reverse_ledger_relative_residual':max_energy_error,
      'max_partial_flip_kinetic_jump_error':max_jump_identity,
      'max_phase_locked_ledger_absolute_residual':max_gap_ledger,
      'max_phase_clock_mismatch':max_clock,
      'original_v18_48s_control_regression':{'matched_endpoints':parent_comparisons,
          'max_shape_gap':parent_shape_regression,'max_signed_drive_power_gap':parent_power_regression},
      'equal_rate_duration_prefix_test':{'profile_pair_comparisons':same_rate_comparisons,
          'max_shape_gap':same_rate_max_phase_gap,
          'max_energy_or_power_difference':same_rate_max_energy_gap,
          'interpretation':'At fixed rate and initial state, changing only the planned stopping duration cannot alter the preceding matched-phase IVP prefix.'},
      'by_family':summary,
      'controls':{'integration':{'method':'DOP853','rtol':args.rtol,'atol':args.atol,'max_step':args.max_step},
       'common_phase_nodes':args.profile_nodes,'minimizer_nodes':args.minimizer_nodes,
       'nontrivial_progress_window':[.25,.96],
       'forward_phase_window':[.04,.75],
       'shape_thresholds':[.0025,.005,.01,.02]},
      'provenance':provenance,
      'scientific_boundary':'Seven moderate controlled designs and sampled partial reversals, not a continuous proof. Same-clock shape minima are geometry 3D only, not intersections in 11D. Rate/duration/fraction are imposed controls. Partial velocity preparation has nonzero externally imposed kinetic-energy jump. The mechanical energy is model-defined, not entropy. No universal hysteresis law or intrinsic counterflow metric is certified.'}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('AUDIT REPORT',json.dumps({k:report[k] for k in ('status','genuine_11D_integrations','same_external_phase_minima','common_phase_profile_points','minima_drive_power_opposite_signs','min_3D_gap','max_reverse_ledger_relative_residual','max_phase_locked_ledger_absolute_residual')},indent=2),flush=True)
if __name__=='__main__':main()
