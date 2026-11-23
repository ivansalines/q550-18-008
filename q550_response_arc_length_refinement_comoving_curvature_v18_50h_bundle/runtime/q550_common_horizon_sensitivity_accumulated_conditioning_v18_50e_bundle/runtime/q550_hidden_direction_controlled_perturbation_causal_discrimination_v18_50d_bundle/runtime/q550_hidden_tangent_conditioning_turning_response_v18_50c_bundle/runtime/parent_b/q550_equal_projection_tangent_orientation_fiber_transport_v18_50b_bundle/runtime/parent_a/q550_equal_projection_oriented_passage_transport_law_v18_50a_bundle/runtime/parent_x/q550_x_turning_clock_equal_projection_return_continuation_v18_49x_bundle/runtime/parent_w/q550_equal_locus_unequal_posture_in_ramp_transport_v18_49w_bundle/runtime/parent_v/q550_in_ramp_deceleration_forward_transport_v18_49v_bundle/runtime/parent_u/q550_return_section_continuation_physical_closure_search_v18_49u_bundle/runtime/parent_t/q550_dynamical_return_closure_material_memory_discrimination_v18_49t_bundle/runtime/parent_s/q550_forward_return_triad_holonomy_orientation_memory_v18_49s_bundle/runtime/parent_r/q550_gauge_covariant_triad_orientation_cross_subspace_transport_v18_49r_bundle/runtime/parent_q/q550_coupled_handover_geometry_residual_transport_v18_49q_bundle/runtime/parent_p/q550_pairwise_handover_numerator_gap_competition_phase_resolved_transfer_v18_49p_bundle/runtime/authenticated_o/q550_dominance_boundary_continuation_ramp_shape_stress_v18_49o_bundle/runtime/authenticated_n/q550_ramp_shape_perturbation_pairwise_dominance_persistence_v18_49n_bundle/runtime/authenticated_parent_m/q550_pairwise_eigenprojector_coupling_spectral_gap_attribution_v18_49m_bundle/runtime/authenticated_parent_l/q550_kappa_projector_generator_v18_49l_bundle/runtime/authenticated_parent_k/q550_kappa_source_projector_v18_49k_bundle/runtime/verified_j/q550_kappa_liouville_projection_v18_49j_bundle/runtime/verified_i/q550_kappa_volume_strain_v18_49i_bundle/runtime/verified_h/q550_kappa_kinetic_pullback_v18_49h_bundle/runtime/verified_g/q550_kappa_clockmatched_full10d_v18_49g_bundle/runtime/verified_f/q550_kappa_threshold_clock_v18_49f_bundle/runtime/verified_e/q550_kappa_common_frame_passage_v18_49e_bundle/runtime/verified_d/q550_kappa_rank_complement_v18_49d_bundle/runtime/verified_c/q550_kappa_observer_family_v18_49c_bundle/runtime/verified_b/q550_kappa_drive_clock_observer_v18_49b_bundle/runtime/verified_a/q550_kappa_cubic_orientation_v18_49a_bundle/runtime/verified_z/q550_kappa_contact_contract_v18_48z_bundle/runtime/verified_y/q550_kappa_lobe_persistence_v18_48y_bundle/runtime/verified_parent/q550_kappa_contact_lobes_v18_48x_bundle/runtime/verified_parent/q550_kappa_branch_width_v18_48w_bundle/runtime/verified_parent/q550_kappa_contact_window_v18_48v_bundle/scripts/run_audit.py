#!/usr/bin/env python3
"""Q550 v18.48v: fine ramp window and phase-conditioned mechanical history.

Uses original authenticated 11D material field and model energy unchanged.
Theta is an exact analytic externally imposed control. All state differences
are numerical diagnostics in the fixed original chart, not geometric invariants.
"""
from __future__ import annotations
import argparse,csv,importlib.util,json,math,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar
from verify_parent import verify
from ramp_math import designs,cubic_clock_sign,cubic_phase_excursion,phase_time,subthreshold_intervals
ROOT=Path(__file__).resolve().parents[1]
VELOCITY_INDICES=(1,3,5,7,9)
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj)
    return obj
def csvout(path,records):
    if not records:return
    cols=list(dict.fromkeys(k for x in records for k in x))
    with path.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(records)
def summarize(rows,key):
    x=np.array([float(r[key]) for r in rows],float)
    return {'count':len(x),'median':float(np.median(x)),'min':float(x.min()),'max':float(x.max())}
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--limit-groups',type=int,default=0,help='Only for labeled partial preflight, 0=all 8')
    ap.add_argument('--rtol',type=float,default=3e-12)
    ap.add_argument('--atol',type=float,default=3e-13)
    ap.add_argument('--max-step',type=float,default=.025)
    ap.add_argument('--output-dir',type=Path,default=ROOT/'results')
    args=ap.parse_args()
    if args.rtol<=0 or args.atol<=0 or args.max_step<=0:raise ValueError('Integration tolerances and max step must be positive')
    parent_u,t,s,r,j,provenance=verify()
    p=r/'runtime/verified_parent/q550_kappa_counterflow_crossings_v18_48q_bundle/runtime/verified_parent/q550_kappa_counterflow_energy_v18_48p_bundle'
    physical=load(ROOT/'reference/physical_math.py','v_q550_physical')
    geom=load(ROOT/'reference/transversality_math.py','v_q550_geometry')
    support=load(p/'reference/test_support_q550_support_ode_interval_residual_pilot_v1.py','v_q550_support')
    audit=load(p/'reference/test_support_mobius_monodromy_audit.py','v_q550_audit')
    history=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    y=np.asarray(history['y'],float);xi=np.asarray(history['xi'],float)
    h=json.loads((j/'runtime/report_v18_48h.json').read_text())
    kappa={'original':float(h['kappa_original']),'autonomous':float(h['kappa_autonomous'])}
    slope=float(history['clock_speed'])/(2*math.pi);omega=2*math.pi*slope
    params=audit.ModelParameters(gamma_rho=.3)
    g=defaultdict(list)
    for i in range(len(y)):
        g[(str(history['families'][i]),int(history['seed_branches'][i]),str(history['kappa_kind'][i]))].append(i)
    if len(y)!=328 or len(g)!=8:raise RuntimeError('Historical 8x41 physical state genealogy changed')
    keys=sorted(g)
    if args.limit_groups:keys=keys[:args.limit_groups]
    with (parent_u/'results/common_phase_profiles.csv').open(newline='') as f:orig=list(csv.DictReader(f))
    qgrid=np.array(sorted({float(x['common_phase_q']) for x in orig}),float)
    if len(qgrid)!=81:raise RuntimeError('Historical 81-point common-phase grid changed')
    origmap={(x['family'],int(x['branch']),x['kappa_kind'],float(x['alpha']),x['drive_design'],
             float(x['common_phase_q'])):x for x in orig}
    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    contacts=[];fixed=[];regressions=[];group_optima=[]
    run_count=0;max_balance=0.;max_gap_ledger=0.;max_clock=0.;max_u_compare=0.;max_prep=0.
    def integrate(y0, k,d=None,forward=False):
        nonlocal run_count,max_balance
        duration=1. if forward else d.duration
        phase0=float(y0[10]);start=np.r_[y0[:10],np.zeros(4)]
        def clock(t):return phase0+omega*t if forward else phase0-omega*cubic_phase_excursion(t,d)
        def aug(t,z):
            cs=1. if forward else cubic_clock_sign(t,d)
            yhere=np.r_[z[:10],clock(t)]
            return np.r_[physical.rhs_from_original(yhere,k,params,slope,cs,support,audit)[:10],
                         physical.power_terms(yhere,k,params,slope,cs)]
        sol=solve_ivp(aug,(0.,duration),start,method='DOP853',rtol=args.rtol,
                     atol=args.atol,max_step=args.max_step,dense_output=True)
        if not sol.success:raise RuntimeError('11D integration failed: '+sol.message)
        run_count+=1
        def ev(tt):
            if np.ndim(tt)==0:
                v=sol.sol(float(tt));return np.r_[v[:10],clock(float(tt)),v[10:]]
            ts=np.asarray(tt,float);v=sol.sol(ts)
            return np.vstack([v[:10],np.array([clock(float(ti)) for ti in ts])[None,:],v[10:]])
        end=ev(duration)
        de=physical.energy(end[:11],k,params)-physical.energy(y0,k,params)
        terms=end[11:]
        resid=abs(de-sum(terms))/max(1.,abs(de),float(sum(abs(terms))))
        max_balance=max(max_balance,float(resid))
        if resid>1e-8:raise RuntimeError('Original mechanical ledger broken')
        return ev
    for family,branch,kind in keys:
        ids=sorted(g[(family,branch,kind)],key=lambda i:xi[i])
        if not np.allclose(xi[ids],np.linspace(3.5,4.5,41),atol=1e-12):raise RuntimeError('Original physical sections shifted')
        k=kappa[kind];F=integrate(y[ids[0]],k,forward=True)
        err=float(np.max(np.linalg.norm(F(np.linspace(0,1,41)).T[:,:11]-y[ids],axis=1)))
        if err>1e-7:raise RuntimeError('Historical 11D replay failed')
        regressions.append({'family':family,'branch':branch,'kappa_kind':kind,'max_11D_replay_error':err})
        turn=F(1.)[:11];e_turn=physical.energy(turn,k,params)
        fw_states=F(1.-qgrid).T
        fw_shapes=np.array([geom.shape(x[:11]) for x in fw_states])
        pathrows=[]
        for alpha in (0.,.75,1.):
            init=turn.copy();init[list(VELOCITY_INDICES)]*=1.-2*alpha
            jump=physical.energy(init,k,params)-e_turn
            zero_vel=turn.copy();zero_vel[list(VELOCITY_INDICES)]=0.
            Ek=physical.energy(turn,k,params)-physical.energy(zero_vel,k,params)
            residual=abs(jump-(((1.-2*alpha)**2)-1.)*Ek)
            max_prep=max(max_prep,float(residual))
            if residual>1e-8:raise RuntimeError('Velocity preparation energy jump fails')
            for design in designs(alpha):
                R=integrate(init,k,d=design)
                times=design.ramp+qgrid
                rt=R(times).T
                shapes=np.array([geom.shape(x[:11]) for x in rt])
                gaps=np.linalg.norm(shapes-fw_shapes,axis=1)
                def evq(q):
                    zr=R(phase_time(q,design))[:11];zf=F(1.-q)[:11]
                    return float(np.linalg.norm(geom.shape(zr)-geom.shape(zf)))
                cands=[(float(gaps[0]),float(qgrid[0])),(float(gaps[-1]),float(qgrid[-1]))]
                for i in range(1,len(qgrid)-1):
                    if gaps[i]<=gaps[i-1] and gaps[i]<=gaps[i+1]:
                        fit=minimize_scalar(evq,method='bounded',bounds=(float(qgrid[i-1]),float(qgrid[i+1])),options={'xatol':1e-12})
                        cands.append((float(fit.fun),float(fit.x)))
                dmin,qbest=min(cands,key=lambda pair:pair[0])
                zr=R(phase_time(qbest,design));zf=F(1.-qbest)
                yr=zr[:11];yf=zf[:11]
                delta=yr-yf;delta[[2,6,10]]=geom.wrap(delta[[2,6,10]])
                er=physical.energy(yr,k,params);ef=physical.energy(yf,k,params)
                balance=(er-ef)-(sum(F(1.)[11:])-sum(zf[11:])+jump+sum(zr[11:]))
                max_gap_ledger=max(max_gap_ledger,abs(balance))
                if abs(balance)>1e-7:raise RuntimeError('Equal-phase energy history identity failed')
                cerr=abs(geom.wrap(yr[10]-yf[10]));max_clock=max(max_clock,float(cerr))
                if cerr>1e-8:raise RuntimeError('External command phases not matched')
                pr=physical.power_terms(yr,k,params,slope,-1.)
                pf=physical.power_terms(yf,k,params,slope,1.)
                common={
                    'family':family,'branch':branch,'kappa_kind':kind,'alpha':alpha,
                    'ramp_duration_xi':float(design.ramp),'design':design.name,
                    'minimum_3D_gap':float(dmin),'minimum_common_phase_q':float(qbest),
                    'minimum_interior':int(qgrid[0]+1e-6<qbest<qgrid[-1]-1e-6),
                    'minimum_11D_gap':float(np.linalg.norm(delta)),
                    'minimum_velocity_gap':float(np.linalg.norm(delta[list(VELOCITY_INDICES)])),
                    'minimum_energy_gap':float(er-ef),
                    'minimum_return_energy':float(er), 'minimum_forward_energy':float(ef),
                    'minimum_return_drive_power':float(pr[0]),'minimum_forward_drive_power':float(pf[0]),
                    'opposite_drive_power':int(pr[0]*pf[0]<0 and abs(pr[0])>1e-13 and abs(pf[0])>1e-13),
                    'preparation_energy_jump':float(jump),
                    'return_cumulative_drive_work_at_min':float(zr[11]),
                    'return_cumulative_radial_damping_at_min':float(zr[12]),
                    'return_cumulative_x_damping_at_min':float(zr[13]),
                    'return_cumulative_active_work_at_min':float(zr[14]),
                    'forward_cumulative_drive_work_at_min':float(zf[11]),
                    'forward_cumulative_radial_damping_at_min':float(zf[12]),
                    'forward_cumulative_x_damping_at_min':float(zf[13]),
                    'forward_cumulative_active_work_at_min':float(zf[14]),
                    'energy_history_identity_residual':float(balance),
                    'clock_mismatch_rad':float(cerr),
                }
                # Resolve persistence in external phase, not elapsed xi.
                for th in (.0025,.005,.01):
                    spans=subthreshold_intervals(evq,qgrid,th,minq=qbest,precomputed=gaps)
                    tag=str(th).replace('.','p')
                    common['contact_intervals_'+tag]=spans['number_intervals']
                    common['contact_longest_q_'+tag]=spans['longest_phase_width']
                    common['contact_total_q_'+tag]=spans['total_phase_width']
                    if dmin<th and not spans['min_inside']:raise RuntimeError('Contact threshold root check inconsistent')
                # The minimum shape phase is allowed to depend on the ramp.
                contacts.append(common);pathrows.append(common)
                # Second view: fixed-phase history avoids comparing moving minima.
                for qfixed in (.35,.50,.65):
                    a=R(phase_time(qfixed,design));b=F(1.-qfixed)
                    aa=a[:11];bb=b[:11]
                    diff=aa-bb;diff[[2,6,10]]=geom.wrap(diff[[2,6,10]])
                    ep=physical.energy(aa,k,params)-physical.energy(bb,k,params)
                    ledger=(sum(F(1.)[11:])-sum(b[11:])+jump+sum(a[11:]))
                    if abs(ep-ledger)>1e-7:raise RuntimeError('Fixed-phase energy ledger inconsistent')
                    fixed.append({'family':family,'branch':branch,'kappa_kind':kind,'alpha':alpha,
                      'ramp_duration_xi':float(design.ramp),'common_phase_q':float(qfixed),
                      'elapsed_return_xi':float(phase_time(qfixed,design)),
                      'shape_distance_3D':float(np.linalg.norm(geom.shape(aa)-geom.shape(bb))),
                      'full_state_11D_distance':float(np.linalg.norm(diff)),
                      'velocity_L2_distance':float(np.linalg.norm(diff[list(VELOCITY_INDICES)])),
                      'energy_gap':float(ep),'preparation_energy_jump':float(jump),
                      'return_cumulative_drive_work':float(a[11]),
                      'return_cumulative_radial_damping':float(a[12]),
                      'return_cumulative_x_damping':float(a[13]),
                      'return_cumulative_active_work':float(a[14]),
                      'forward_cumulative_drive_work_since_start':float(F(1.)[11]-b[11]),
                      'forward_cumulative_radial_damping_since_start':float(F(1.)[12]-b[12]),
                      'forward_cumulative_x_damping_since_start':float(F(1.)[13]-b[13]),
                      'forward_cumulative_active_work_since_start':float(F(1.)[14]-b[14]),
                      'energy_gap_ledger_residual':float(ep-ledger)})
                if float(design.ramp) in (0.,.15,.35,.65):
                    for index,q in enumerate(qgrid):
                        old=origmap.get((family,branch,kind,alpha,('instant' if design.ramp==0 else {0.15:'smooth_short',0.35:'smooth_medium',0.65:'smooth_long'}[design.ramp]),float(q)))
                        if old is None:raise RuntimeError('Missing parent u original sample')
                        discrepancy=max(abs(float(old['shape_distance_3D'])-float(gaps[index])),
                             abs(float(old['energy_difference'])-float(physical.energy(rt[index,:11],k,params)-physical.energy(fw_states[index,:11],k,params))),
                             abs(float(old['drive_power_return'])-float(physical.power_terms(rt[index,:11],k,params,slope,-1.)[0])))
                        max_u_compare=max(max_u_compare,discrepancy)
        candidates=[rr for rr in pathrows if rr['alpha']==1.]
        winner=min(candidates,key=lambda x:x['minimum_3D_gap'])
        group_optima.append({'family':family,'branch':branch,'kappa_kind':kind,
            'scanned_best_ramp_duration_xi':winner['ramp_duration_xi'],
            'best_3D_gap':winner['minimum_3D_gap'],
            'best_at_common_phase_q':winner['minimum_common_phase_q'],
            'best_11D_gap':winner['minimum_11D_gap'],
            'best_energy_gap':winner['minimum_energy_gap']})
        print('v18.48v completed:',family,branch,kind,'best ramp',winner['ramp_duration_xi'],
              '3D=',f"{winner['minimum_3D_gap']:.6g}",flush=True)
    if max_u_compare>2e-7:raise RuntimeError('Original u ramp regression exceeded bound')
    csvout(out/'fine_ramp_contacts.csv',contacts)
    csvout(out/'fixed_phase_energy_history.csv',fixed)
    csvout(out/'historical_replay.csv',regressions)
    csvout(out/'per_path_window_optima.csv',group_optima)
    alpha1=[x for x in contacts if x['alpha']==1.]
    ramps=sorted({x['ramp_duration_xi'] for x in alpha1})
    summaries=[]
    for ramp in ramps:
        rows=[x for x in alpha1 if x['ramp_duration_xi']==ramp]
        summaries.append({'ramp_duration_xi':ramp,'number_paths':len(rows),
              'median_3D_gap':float(np.median([x['minimum_3D_gap'] for x in rows])),
              'median_11D_gap':float(np.median([x['minimum_11D_gap'] for x in rows])),
              'median_energy_gap_at_contact':float(np.median([x['minimum_energy_gap'] for x in rows])),
              'opposite_drive_power_count':sum(x['opposite_drive_power'] for x in rows),
              'number_contacts_below_0p0025':sum(x['minimum_3D_gap']<.0025 for x in rows),
              'number_contacts_below_0p01':sum(x['minimum_3D_gap']<.01 for x in rows),
              'median_total_phase_contact_width_below_0p01':float(np.median([x['contact_total_q_0p01'] for x in rows]))})
    csvout(out/'ramp_window_summary.csv',summaries)
    report={'version':'v18.48v','status':'FULL_EIGHT_PATH_NUMERICAL_AUDIT' if len(keys)==8 else 'PARTIAL_PREFLIGHT_ONLY',
      'title':'Smooth-Reversal Contact Window & Phase–Energy History Audit',
      'historical_paths':len(keys),'genuine_material_11D_integrations':run_count,
      'optimized_phase_contacts':len(contacts),'fixed_phase_energy_comparisons':len(fixed),
      'ramp_scan_alpha1':list(ramps),'other_alpha_controls':[0.,.75],
      'common_phase_window':[float(qgrid[0]),float(qgrid[-1])],
      'best_observed_3D_gap':float(min(x['minimum_3D_gap'] for x in contacts)),
      'smallest_observed_full11D_gap':float(min(x['minimum_11D_gap'] for x in contacts)),
      'maximum_historical_11D_regression':max(x['max_11D_replay_error'] for x in regressions),
      'maximum_parent_u_profile_regression':max_u_compare,
      'maximum_relative_mechanical_ledger_residual':max_balance,
      'maximum_phase_matched_energy_ledger_abs_residual':max_gap_ledger,
      'maximum_preparation_energy_jump_error':max_prep,
      'maximum_command_phase_difference_rad':max_clock,
      'best_per_path':group_optima,'alpha1_ramp_summary':summaries,
      'provenance':provenance,
      'limits':('Only a prescribed drive history, not an inferred constitutive law. '
        'Numerical matched phase q differs from matched elapsed time. '
        'The minimized phase location changes with ramp and should not be mistaken for a fixed-event history. '
        'Chart distances are not geometric invariants; signed model work does not establish entropy or thermal irreversibility. '
        'This finite ramp grid cannot certify a unique optimum or exclude sub-grid minima.')}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('FINAL',json.dumps({k:report[k] for k in ('status','genuine_material_11D_integrations','optimized_phase_contacts',
        'best_observed_3D_gap','smallest_observed_full11D_gap','maximum_parent_u_profile_regression','maximum_relative_mechanical_ledger_residual')},indent=2))
if __name__=='__main__':main()
