#!/usr/bin/env python3
"""Q550 v18.48u — authentic 11D continuously controlled phase-reversal audit.

Use the unchanged original RHS and mechanical ledger, replacing ONLY externally
imposed Theta' with smooth chronological forcing. The independent variables
q and s represent exactly matched unwrapped external phase, not clock time.
A geometrical near-contact is neither a full-state reunion nor an invariant
hysteresis theorem.
"""
from __future__ import annotations
import argparse,csv,importlib.util,json,math,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar
from verify_parent import verify
from drive_math import (designs,clock_sign,phase_excursion,same_phase_time,
                        prepare_reversal,signed_power_opposition,width_under_threshold)
ROOT=Path(__file__).resolve().parents[1]
def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
    return m

def savecsv(path,rows):
    if not rows:return
    keys=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)

def summary(xs):
    if not xs:return None
    x=np.asarray(xs,float)
    return {'minimum':float(np.min(x)),'median':float(np.median(x)),
            'maximum':float(np.max(x)),'count':len(x)}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rtol',type=float,default=3e-12)
    ap.add_argument('--atol',type=float,default=3e-13)
    ap.add_argument('--max-step',type=float,default=.025)
    ap.add_argument('--alpha',type=float,nargs='+',default=[0.,.75,1.])
    ap.add_argument('--limit-groups',type=int,default=0,help='Diagnostic subset; zero runs all 8 original paths')
    ap.add_argument('--minimizer-nodes',type=int,default=81)
    ap.add_argument('--output-dir',type=Path,default=ROOT/'results')
    args=ap.parse_args()
    if args.limit_groups<0 or args.minimizer_nodes<31:raise ValueError('Invalid numerical sampling')
    if len(set(args.alpha))!=len(args.alpha) or any(not 0<=a<=1 for a in args.alpha):raise ValueError('Invalid alpha')
    parent,s,r,j,ancestry=verify()
    p=r/'runtime/verified_parent/q550_kappa_counterflow_crossings_v18_48q_bundle/runtime/verified_parent/q550_kappa_counterflow_energy_v18_48p_bundle'
    physical=load_module(ROOT/'reference/physical_math.py','q550_u_physical')
    geometry=load_module(ROOT/'reference/transversality_math.py','q550_u_geometry')
    support=load_module(p/'reference/test_support_q550_support_ode_interval_residual_pilot_v1.py','q550_u_support')
    audit=load_module(p/'reference/test_support_mobius_monodromy_audit.py','q550_u_audit')
    history=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    y=np.asarray(history['y'],float);xi=np.asarray(history['xi'],float)
    historical=json.loads((j/'runtime/report_v18_48h.json').read_text())
    kappa={'original':float(historical['kappa_original']),'autonomous':float(historical['kappa_autonomous'])}
    slope=float(history['clock_speed'])/(2*math.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    groups=defaultdict(list)
    for i in range(len(y)):
        key=(str(history['families'][i]),int(history['seed_branches'][i]),str(history['kappa_kind'][i]))
        groups[key].append(i)
    if len(groups)!=8 or len(y)!=328:raise RuntimeError('Unexpected Q550 ancestry')
    keys=sorted(groups)
    if args.limit_groups:keys=keys[:args.limit_groups]
    ds=designs()
    # Reuse the exact archived v18.48t common-phase grid to permit a genuine
    # regression of constant-reversal control without interpolation.
    with (parent/'results/common_phase_profiles.csv').open(newline='') as f:
        old=list(csv.DictReader(f))
    qgrid=np.asarray(sorted({float(x['common_phase_q']) for x in old}),float)
    if len(qgrid)!=81 or not .30<qgrid[0]<qgrid[-1]<.73:raise RuntimeError('Unexpected historical common phase grid')
    tlookup={(x['family'],int(x['branch']),x['kappa_kind'],float(x['alpha']),
              x['design'],float(x['common_phase_q'])):x for x in old}
    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    contacts=[];profiles=[];regressions=[]
    run_count=0;max_ledger=0.;max_gap_ledger=0.;max_clock=0.;max_parent=0.;max_jump=0.
    def integrate(y0,T,k,d,forward=False):
        """Integrate 10 material ODEs + 4 work channels with the analytic clock.

        Theta is externally prescribed, so solving its known scalar IVP by
        quadrature would inject unnecessary ~1e-9 rad numerical phase error.
        Here Theta(t) is evaluated exactly from the declared analytic control,
        and the ORIGINAL support RHS is used for all ten material coordinates.
        The returned full state has 11 genuine physical coordinates + 4 works.
        """
        nonlocal run_count,max_ledger
        omega=2*math.pi*slope
        phase0=float(y0[10])
        z0=np.r_[y0[:10],np.zeros(4)]
        def theta(t):
            return phase0+omega*t if forward else phase0-omega*phase_excursion(t,d)
        def aug(t,z):
            c=1. if forward else clock_sign(t,d)
            current_y=np.r_[z[:10],theta(t)]
            material_rhs=physical.rhs_from_original(current_y,k,params,slope,c,support,audit)[:10]
            powers=physical.power_terms(current_y,k,params,slope,c)
            return np.r_[material_rhs,powers]
        sol=solve_ivp(aug,(0.,T),z0,method='DOP853',rtol=args.rtol,
            atol=args.atol,max_step=args.max_step,dense_output=True)
        if not sol.success:raise RuntimeError('Original 11D material integration failed: '+sol.message)
        run_count+=1
        def evaluate(t):
            if np.ndim(t)==0:
                z=sol.sol(float(t))
                return np.r_[z[:10],theta(float(t)),z[10:]]
            ts=np.asarray(t,float)
            z=sol.sol(ts)
            clock=np.array([theta(float(ti)) for ti in ts],float)
            return np.vstack([z[:10],clock[None,:],z[10:]])
        zT=evaluate(T)
        diff=physical.energy(zT[:11],k,params)-physical.energy(y0,k,params)
        pieces=zT[11:]
        resid=abs(diff-float(sum(pieces)))/max(1.,abs(diff),float(sum(abs(pieces))))
        max_ledger=max(max_ledger,float(resid))
        if resid>1e-8:raise RuntimeError('Model mechanical energy ledger failed')
        return evaluate
    for family,branch,kind in keys:
        inds=sorted(groups[family,branch,kind],key=lambda i:xi[i]);k=kappa[kind]
        if not np.allclose(xi[inds],np.linspace(3.5,4.5,41),atol=1e-12):raise RuntimeError('Historical grid changed')
        F=integrate(y[inds[0]],1.,k,None,forward=True)
        h_err=float(np.max(np.linalg.norm(F(np.linspace(0.,1.,41)).T[:,:11]-y[inds],axis=1)))
        if h_err>1e-7:raise RuntimeError('Original 11D historical replay failed')
        regressions.append(dict(family=family,branch=branch,kappa_kind=kind,maximum_11D_replay_error=h_err))
        turn=F(1.)[:11];Eturn=physical.energy(turn,k,params)
        Fmatched=F(1.-qgrid).T
        base_shapes=geometry.shape(Fmatched[:,:11])
        for alpha in args.alpha:
            init=prepare_reversal(turn,alpha)
            prepjump=physical.energy(init,k,params)-Eturn
            expected=((1.-2*alpha)**2-1.)*(physical.energy(turn,k,params)-physical.energy(prepare_reversal(turn,.5),k,params))
            max_jump=max(max_jump,abs(prepjump-expected))
            if max_jump>1e-8:raise RuntimeError('Velocity preparation kinetic jump failed')
            for d in ds:
                R=integrate(init,d.duration,k,d)
                times=np.array([same_phase_time(float(q),d) for q in qgrid])
                rv=R(times).T
                rstates=rv[:,:11]
                gaps=np.linalg.norm(geometry.shape(rstates)-base_shapes,axis=1)
                # Local optimizer solves the same-clock 1D geometry-only contact.
                possibilities=[(float(gaps[0]),float(qgrid[0])),(float(gaps[-1]),float(qgrid[-1]))]
                def evalq(q):
                    rr=R(same_phase_time(float(q),d))[:11]
                    ff=F(1.-float(q))[:11]
                    return float(np.linalg.norm(geometry.shape(rr)-geometry.shape(ff)))
                for index in range(1,len(qgrid)-1):
                    if gaps[index]<=gaps[index-1] and gaps[index]<=gaps[index+1]:
                        opt=minimize_scalar(evalq,method='bounded',
                            bounds=(float(qgrid[index-1]),float(qgrid[index+1])),
                            options={'xatol':1e-12})
                        possibilities.append((float(opt.fun),float(opt.x)))
                dmin,qmin=min(possibilities,key=lambda x:x[0])
                zr=R(same_phase_time(qmin,d));zf=F(1.-qmin)
                yR=zr[:11];yF=zf[:11]
                clockerr=abs(geometry.wrap(yR[10]-yF[10]));max_clock=max(max_clock,float(clockerr))
                if clockerr>5e-9:raise RuntimeError('Clock phase not matched')
                ER=physical.energy(yR,k,params);EF=physical.energy(yF,k,params)
                predicted=float(sum(F(1.)[11:])-sum(zf[11:])+prepjump+sum(zr[11:]))
                gap_ledger=(ER-EF)-predicted;max_gap_ledger=max(max_gap_ledger,abs(gap_ledger))
                if abs(gap_ledger)>1e-7:raise RuntimeError('Phase-matched energy-gap identity failed')
                pF=physical.power_terms(yF,k,params,slope,1.)
                pR=physical.power_terms(yR,k,params,slope,clock_sign(same_phase_time(qmin,d),d))
                diff=yR-yF;diff[[2,6,10]]=geometry.wrap(diff[[2,6,10]])
                ratios=[];opposites=[];preparation_energies=[]
                instant_comparison=[]
                for i,q in enumerate(qgrid):
                    yf=Fmatched[i,:11];yr=rstates[i]
                    eR=physical.energy(yr,k,params);eF=physical.energy(yf,k,params)
                    pdriveR=physical.power_terms(yr,k,params,slope,-1.)[0]
                    pdriveF=physical.power_terms(yf,k,params,slope,1.)[0]
                    opp=signed_power_opposition(pdriveR,pdriveF)
                    opposites.append(opp)
                    profiles.append(dict(family=family,branch=branch,kappa_kind=kind,
                       alpha=alpha,drive_design=d.name,ramp_duration_xi=d.ramp,
                       stop_dwell_xi=d.dwell,common_phase_q=float(q),
                       return_elapsed_xi=float(times[i]),forward_elapsed_xi=float(1.-q),
                       shape_distance_3D=float(gaps[i]),energy_difference=float(eR-eF),
                       drive_power_forward=float(pdriveF),drive_power_return=float(pdriveR),
                       drive_power_opposite=opp,
                       return_work_drive=float(rv[i,11]),
                       return_work_radial_damping=float(rv[i,12]),
                       return_work_x_damping=float(rv[i,13]),
                       return_work_active_x=float(rv[i,14]),
                       preparation_energy_jump=float(prepjump)))
                    if d.name=='instant' and alpha in (0.,1.):
                        key=(family,branch,kind,alpha,'phaseclosed_reference',float(q))
                        if key not in tlookup:raise RuntimeError('Missing exact v18.48t control sample')
                        oldrow=tlookup[key]
                        err=max(abs(float(oldrow['shape_distance'])-float(gaps[i])),
                            abs(float(oldrow['energy_difference'])-float(eR-eF)),
                            abs(float(oldrow['drive_power_return'])-float(pdriveR)))
                        max_parent=max(max_parent,err)
                near={}
                for th in (.0025,.005,.01,.02):
                    metrics=width_under_threshold(qgrid,gaps,th)
                    key=str(th).replace('.','p')
                    near['fraction_shape_below_'+key]=metrics['fraction']
                    near['longest_q_span_shape_below_'+key]=metrics['longest_q_span']
                contacts.append(dict(family=family,branch=branch,kappa_kind=kind,alpha=float(alpha),
                   drive_design=d.name,protocol_kind=d.kind,ramp_duration_xi=d.ramp,
                   stop_dwell_xi=d.dwell,total_duration_xi=d.duration,
                   phase_matched_min_distance_3D=dmin,
                   matched_min_common_phase_q=qmin,matched_min_elapsed_return=same_phase_time(qmin,d),
                   matched_min_elapsed_forward=1.-qmin,
                   matched_min_is_interior=int(qmin>qgrid[0]+1e-6 and qmin<qgrid[-1]-1e-6),
                   matched_min_full_state_11D_distance=float(np.linalg.norm(diff)),
                   matched_min_velocities_L2=float(np.linalg.norm(diff[[1,3,5,7,9]])),
                   matched_min_energy_gap=float(ER-EF),
                   matched_min_phase_difference_rad=float(geometry.wrap(diff[10])),
                   matched_min_drive_power_forward=float(pF[0]),
                   matched_min_drive_power_return=float(pR[0]),
                   matched_min_opposite_drive_power=signed_power_opposition(pF[0],pR[0]),
                   preparation_energy_jump=float(prepjump),
                   return_cumulative_drive_work_at_min=float(zr[11]),
                   return_cumulative_radial_damping_at_min=float(zr[12]),
                   return_cumulative_x_damping_at_min=float(zr[13]),
                   return_cumulative_active_x_work_at_min=float(zr[14]),
                   phase_matched_energy_ledger_residual=float(gap_ledger),
                   common_phase_median_3D_distance=float(np.median(gaps)),
                   common_phase_opposite_drive_power_fraction=float(np.mean(opposites)),
                   **near))
        print('v18.48u original path completed:',family,branch,kind,'original regression',f'{h_err:.3e}',flush=True)
    if max_parent>2e-7:raise RuntimeError('Archived v18.48t instant-drive regression failed')
    savecsv(out/'phase_locked_contacts.csv',contacts)
    savecsv(out/'common_phase_profiles.csv',profiles)
    savecsv(out/'historical_regression.csv',regressions)
    family_stats={}
    for family in sorted({x['family'] for x in contacts}):
        subset=[x for x in contacts if x['family']==family]
        family_stats[family]={
          'cases':len(subset),
          'min_3D_gap':summary([x['phase_matched_min_distance_3D'] for x in subset]),
          'opposite_drive_power_min_count':sum(x['matched_min_opposite_drive_power'] for x in subset)}
    control_stats={}
    for d in ds:
        control_stats[d.name]={}
        for alpha in args.alpha:
            sub=[x for x in contacts if x['drive_design']==d.name and x['alpha']==alpha]
            control_stats[d.name][str(alpha)]={
                'n':len(sub),
                'geometry_gap_3D':summary([x['phase_matched_min_distance_3D'] for x in sub]),
                'energy_gap':summary([x['matched_min_energy_gap'] for x in sub]),
                'drive_power_opposite_count':sum(x['matched_min_opposite_drive_power'] for x in sub)}
    report={'version':'v18.48u','status':'FULL_ORIGINAL_11D_NUMERICAL_AUDIT' if len(keys)==8 else 'PARTIAL_PREFLIGHT_ONLY',
        'title':'Smooth Drive Reversal & Phase–Energy Path Dependence Audit',
        'historical_paths_used':len(keys),'genuine_11D_integrations':run_count,
        'expected_11D_integrations':len(keys)*(1+len(args.alpha)*len(ds)),
        'phase_matched_minima':len(contacts),'common_phase_profile_points':len(profiles),
        'drive_designs':[vars(x) for x in ds], 'alpha_values':args.alpha,
        'phase_window_q':[float(qgrid[0]),float(qgrid[-1])],
        'phase_nodes':len(qgrid),'minimum_3D_gap':min(x['phase_matched_min_distance_3D'] for x in contacts),
        'minimum_full11D_gap':min(x['matched_min_full_state_11D_distance'] for x in contacts),
        'opposite_drive_power_at_minima':sum(x['matched_min_opposite_drive_power'] for x in contacts),
        'maximum_original_path_regression':max(x['maximum_11D_replay_error'] for x in regressions),
        'maximum_return_energy_relative_residual':max_ledger,
        'maximum_phase_matched_ledger_absolute_residual':max_gap_ledger,
        'maximum_external_phase_mismatch':max_clock,
        'maximum_original_t_control_regression':max_parent,
        'maximum_preparation_jump_identity_residual':max_jump,
        'family_stats':family_stats,'control_stats':control_stats,'provenance':ancestry,
        'scientific_boundary':(
           'The time-varying external drive is an imposed control and all results are floating-point numerical diagnostics. '
           'The total post-turn phase excursion is identical for every design, but ramp duration changes elapsed clock time. '
           'Matched-q comparisons use post-reversal q>0 and compare the same external phase, not equal elapsed time. '
           'A 3D chart near-contact is not 11D recurrence; signed mechanical work is not entropy. '
           'No physical counterflow hysteresis theorem or intrinsic material response time follows.')}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('v18.48u REPORT',json.dumps({k:report[k] for k in ('status','genuine_11D_integrations','phase_matched_minima','common_phase_profile_points','minimum_3D_gap','maximum_return_energy_relative_residual','maximum_original_t_control_regression')},indent=2))
if __name__=='__main__':main()
