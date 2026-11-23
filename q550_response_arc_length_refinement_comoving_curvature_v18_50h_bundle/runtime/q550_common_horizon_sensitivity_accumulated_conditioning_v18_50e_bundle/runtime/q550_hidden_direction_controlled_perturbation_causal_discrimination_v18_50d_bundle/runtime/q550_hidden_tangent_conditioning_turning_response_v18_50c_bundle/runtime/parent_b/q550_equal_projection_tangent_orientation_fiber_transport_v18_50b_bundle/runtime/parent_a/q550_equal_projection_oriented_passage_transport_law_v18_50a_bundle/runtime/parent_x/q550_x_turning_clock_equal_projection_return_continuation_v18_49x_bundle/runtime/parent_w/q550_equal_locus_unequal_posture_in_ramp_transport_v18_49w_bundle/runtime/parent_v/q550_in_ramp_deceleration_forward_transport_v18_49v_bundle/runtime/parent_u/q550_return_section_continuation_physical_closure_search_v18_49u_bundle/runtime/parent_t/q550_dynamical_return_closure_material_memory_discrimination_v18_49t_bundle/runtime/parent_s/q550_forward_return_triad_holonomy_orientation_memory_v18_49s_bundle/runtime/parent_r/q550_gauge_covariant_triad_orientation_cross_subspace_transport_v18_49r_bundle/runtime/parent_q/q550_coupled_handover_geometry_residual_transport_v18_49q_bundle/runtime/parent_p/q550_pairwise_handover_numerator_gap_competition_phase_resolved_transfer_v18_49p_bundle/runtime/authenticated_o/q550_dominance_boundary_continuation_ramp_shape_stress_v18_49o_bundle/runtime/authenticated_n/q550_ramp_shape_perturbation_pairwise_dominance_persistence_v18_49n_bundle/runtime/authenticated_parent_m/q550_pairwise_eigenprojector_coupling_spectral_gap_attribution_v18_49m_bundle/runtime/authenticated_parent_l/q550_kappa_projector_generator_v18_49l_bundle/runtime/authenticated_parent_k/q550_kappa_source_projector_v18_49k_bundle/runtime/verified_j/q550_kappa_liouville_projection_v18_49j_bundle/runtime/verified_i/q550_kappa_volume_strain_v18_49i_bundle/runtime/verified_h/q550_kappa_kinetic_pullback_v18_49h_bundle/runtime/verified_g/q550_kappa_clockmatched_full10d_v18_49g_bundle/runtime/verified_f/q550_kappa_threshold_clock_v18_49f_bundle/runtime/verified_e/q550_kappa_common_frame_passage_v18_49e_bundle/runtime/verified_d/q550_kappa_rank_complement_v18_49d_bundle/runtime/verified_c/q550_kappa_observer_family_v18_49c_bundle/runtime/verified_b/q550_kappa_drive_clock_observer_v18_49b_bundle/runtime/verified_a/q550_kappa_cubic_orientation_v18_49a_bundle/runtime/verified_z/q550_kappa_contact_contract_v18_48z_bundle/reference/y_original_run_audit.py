#!/usr/bin/env python3
"""v18.48y: genuine 11D phase-locked contact-lobe barrier and curvature audit.

All parent files are SHA-256 authenticated, original 11D RHS/energy is unchanged.
A lobe is a connected component of a 3D-projected STRICT sublevel set;
no statement about material topological transitions or interval certification.
"""
from __future__ import annotations
import argparse,csv,importlib.util,json,math,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.integrate import solve_ivp
from verify_parent import verify
from persistence_math import barrier,minimum,root_intervals,critical_bracket
ROOT=Path(__file__).resolve().parents[1]
VELOCITY=(1,3,5,7,9)
RAMPS=(.280,.285,.290,.292,.294,.295,.296,.29625,.296333,.2965,.29653,.297,
       .298,.299,.300,.301,.302,.303,.304,.305,.307,.309,.312)
LEVELS=(.004,.006,.008,.010,.012,.014,.016)
PROFILE_LEVELS=(.005,.008,.010,.012,.015)
Q_LIMITS=(.10,.90)

def mod(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module

def write_csv(path,rows):
    if not rows:raise ValueError('Attempted empty output table: '+str(path))
    cols=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',newline='',encoding='utf-8') as o:
        wr=csv.DictWriter(o,fieldnames=cols);wr.writeheader();wr.writerows(rows)

def read_csv(path):
    with path.open(newline='',encoding='utf-8') as inp:return list(csv.DictReader(inp))

def integrate(phys,rmp,support,audit,k,params,slope,omega,y0,args,design=None):
    """Exact functional 11D/ledger protocol of parent v18.48x; no model edits."""
    fwd=design is None
    duration=1. if fwd else 1.+design.ramp
    start_theta=float(y0[10])
    init=np.r_[y0[:10],np.zeros(4)]
    def theta(t):
        return start_theta+omega*t if fwd else start_theta-omega*rmp.cubic_phase_excursion(t,design)
    def rhs(t,z):
        sign=1. if fwd else rmp.cubic_clock_sign(t,design)
        state=np.r_[z[:10],theta(t)]
        field=phys.rhs_from_original(state,k,params,slope,sign,support,audit)
        power=phys.power_terms(state,k,params,slope,sign)
        return np.r_[field[:10],power]
    result=solve_ivp(rhs,(0.,duration),init,method='DOP853',rtol=args.rtol,atol=args.atol,
                     max_step=args.max_step,dense_output=True)
    if not result.success:raise RuntimeError('Original 11D IVP failed: '+result.message)
    def evaluate(t):
        z=result.sol(t)
        if np.ndim(t)==0:return np.r_[z[:10],theta(float(t)),z[10:]]
        return np.vstack((z[:10],np.array([theta(float(u)) for u in t])[None,:],z[10:]))
    final=evaluate(duration)
    de=phys.energy(final[:11],k,params)-phys.energy(y0,k,params)
    err=abs(de-sum(final[11:]))/max(1.,abs(de),sum(abs(final[11:])))
    if err>args.maximum_ledger_error:raise RuntimeError('Original mechanical balance failed')
    return evaluate,err

def run(args):
    xroot,j,provenance=verify()
    phys=mod(ROOT/'reference/physical_math.py','y_original_11d_phys')
    ramp=mod(ROOT/'reference/parent_ramp_math.py','y_original_drive')
    p=xroot/'runtime/verified_parent/q550_kappa_branch_width_v18_48w_bundle/runtime/verified_parent/q550_kappa_contact_window_v18_48v_bundle/runtime/verified_parent/q550_kappa_smooth_reversal_v18_48u_bundle/runtime/verified_parent/q550_kappa_rate_duration_v18_48t_bundle/runtime/verified_parent/q550_kappa_signed_counterflow_v18_48s_bundle/runtime/verified_parent/q550_kappa_counterflow_transversality_v18_48r_bundle/runtime/verified_parent/q550_kappa_counterflow_crossings_v18_48q_bundle/runtime/verified_parent/q550_kappa_counterflow_energy_v18_48p_bundle'
    # Parent X verifier has already located and authenticated the same original support sources.
    # Derive the reliable path by traversing the actual verified ancestor directory.
    ancestor=list((xroot/'runtime/verified_parent').rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
    if len(ancestor)!=1:raise RuntimeError('Original support physics source not uniquely found: '+str(len(ancestor)))
    parentp=ancestor[0].parent
    support=mod(ancestor[0],'y_historical_support')
    audit=mod(parentp/'test_support_mobius_monodromy_audit.py','y_historical_audit')
    old_lobes=mod(ROOT/'reference/parent_lobe_math.py','y_historical_lobe_shapes')
    data=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    j_report=json.loads((j/'runtime/report_v18_48h.json').read_text())
    ks={'original':float(j_report['kappa_original']),'autonomous':float(j_report['kappa_autonomous'])}
    omega=float(data['clock_speed']);slope=omega/(2*math.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    qgrid=np.linspace(*Q_LIMITS,args.phase_samples)
    groups=defaultdict(list)
    for i in range(len(data['y'])):
        groups[(str(data['families'][i]),int(data['seed_branches'][i]),str(data['kappa_kind'][i]))].append(i)
    if len(groups)!=8 or len(data['y'])!=328:raise RuntimeError('Authentic 328-state x 8 history missing')
    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    xprofiles=read_csv(xroot/'results/focus_lobe_profiles.csv')
    original_profile={}
    for row in xprofiles:
        key=(row['kappa_kind'],round(float(row['ramp_duration_xi']),8),round(float(row['common_phase_q']),8))
        original_profile[key]=float(row['geometric_gap_3D'])
    raw=[];persist=[];profiles=[];reference_regress=[]
    max_ledger=0.;max_replay=0.;max_parent_profile_error=0.;physical_runs=0
    all_ram=RAMPS[:args.smoke_ramps] if args.smoke_ramps else RAMPS
    for kind in ('original','autonomous')[:args.smoke_kinds or 2]:
        key=next((v for v in groups if v[0].startswith('phaseblind') and v[1]==0 and v[2]==kind),None)
        if key is None:raise RuntimeError('Original phaseblind branch 0 path missing')
        ids=sorted(groups[key],key=lambda i:float(data['xi'][i]))
        if not np.allclose(data['xi'][ids],np.linspace(3.5,4.5,41),atol=1e-12):
            raise RuntimeError('Historical physical section clock mismatch')
        k=ks[kind];start=np.asarray(data['y'][ids[0]],float)
        forward,err=integrate(phys,ramp,support,audit,k,params,slope,omega,start,args)
        physical_runs+=1;max_ledger=max(max_ledger,err)
        replay=max(float(np.linalg.norm(forward(t)[:11]-data['y'][ix])) for t,ix in zip(np.linspace(0,1,41),ids))
        max_replay=max(max_replay,replay)
        if replay>1e-7:raise RuntimeError('Historical original 11D state replay mismatch')
        turn=forward(1.)[:11].copy();turn[list(VELOCITY)]*=-1.
        for rv in all_ram:
            des=ramp.Design(f'y_cubic_{rv:.8f}','smoothstep',rv)
            back,e=integrate(phys,ramp,support,audit,k,params,slope,omega,turn,args,design=des)
            physical_runs+=1;max_ledger=max(max_ledger,e)
            def difference(q):
                zr=back(rv+float(q))[:11];zf=forward(1.-float(q))[:11]
                return float(np.linalg.norm(old_lobes.shapes(zr)-old_lobes.shapes(zf)))
            rmat=back(rv+qgrid).T;fmat=forward(1.-qgrid).T
            gaps=np.linalg.norm(old_lobes.shapes(rmat[:,:11])-old_lobes.shapes(fmat[:,:11]),axis=1)
            b=barrier(difference)
            left=minimum(difference,(.355,.466));right=minimum(difference,(.505,.645))
            if not b['is_strict_local_max'] or not (left['q']<b['q']<right['q']):
                raise RuntimeError('Contact-lobe stationary maximum/minimum ordering failed')
            zr=back(rv+b['q'])[:11];zf=forward(1.-b['q'])[:11]
            delta=zr-zf;delta[[2,6,10]]=(delta[[2,6,10]]+np.pi)%(2*np.pi)-np.pi
            row={'family':'phaseblind','branch':0,'kappa_kind':kind,'kappa0':k,
                'ramp_duration_xi':rv,'barrier_phase_q':b['q'],'barrier_distance_3D':b['distance'],
                'barrier_curvature_q2_richardson':b['curvature_richardson'],
                'barrier_curvature_h_0p002':b['curvatures'][0],
                'barrier_curvature_h_0p001':b['curvatures'][1],
                'barrier_curvature_h_0p0005':b['curvatures'][2],
                'barrier_curvature_h_0p00025':b['curvatures'][3],
                'relative_curvature_step_variation':b['curvature_step_variation'],
                'left_minimum_q':left['q'],'left_minimum_d3':left['distance'],
                'right_minimum_q':right['q'],'right_minimum_d3':right['distance'],
                'barrier_full11d_distance':float(np.linalg.norm(delta)),
                'barrier_energy_difference':float(phys.energy(zr,k,params)-phys.energy(zf,k,params)),
                'maximum_integrated_energy_residual':e}
            raw.append(row)
            # Numeric sublevel persistence: use genuine dense-IVP roots, 5 thresholds.
            for th in PROFILE_LEVELS:
                iv=root_intervals(qgrid,gaps,th,difference)
                persistent={'kappa_kind':kind,'ramp_duration_xi':rv,'threshold_d3':th,
                    'components':len(iv),'total_width_q':sum(y-x for x,y in iv),
                    'lobe_intervals_json':json.dumps(iv,separators=(',',':')),
                    'touches_left':int(bool(iv) and abs(iv[0][0]-qgrid[0])<1e-10),
                    'touches_right':int(bool(iv) and abs(iv[-1][1]-qgrid[-1])<1e-10)}
                persist.append(persistent)
            # All phase samples allow independent scrutiny of hidden subgrid events.
            for q,g in zip(qgrid,gaps):
                profiles.append({'kappa_kind':kind,'ramp_duration_xi':rv,
                                 'common_phase_q':float(q),'distance_3D':float(g)})
                prev=original_profile.get((kind,round(rv,8),round(float(q),8)))
                if prev is not None:
                    discrepancy=abs(prev-float(g))
                    max_parent_profile_error=max(max_parent_profile_error,discrepancy)
            if (kind,round(rv,8),round(float(qgrid[0]),8)) in original_profile:
                reference_regress.append({'kappa_kind':kind,'ramp_duration_xi':rv,
                     'max_original_x_profile_error_so_far':max_parent_profile_error})
            print(f'v18.48y {kind:10} ramp={rv:.6f} barrier={b["distance"]:.9f}'
                  f' curvature={b["curvature_richardson"]:.6f}',flush=True)
    critical=[];sensitivity=[]
    for kind in ('original','autonomous')[:args.smoke_kinds or 2]:
        subset=[z for z in raw if z['kappa_kind']==kind]
        subset.sort(key=lambda z:z['ramp_duration_xi'])
        for l,r in zip(subset[:-1],subset[1:]):
            derivative=(r['barrier_distance_3D']-l['barrier_distance_3D'])/(r['ramp_duration_xi']-l['ramp_duration_xi'])
            sensitivity.append({'kappa_kind':kind,'ramp_midpoint_xi':.5*(l['ramp_duration_xi']+r['ramp_duration_xi']),
                'secant_dbarrier_dr':derivative})
        for th in LEVELS:
            result=critical_bracket(subset,th)
            if result is not None:
                result['kappa_kind']=kind
                # Interpolated location is a descriptive estimate, not another IVP.
                d0=result['left_barrier'];d1=result['right_barrier']
                if abs(d1-d0)>0:
                    result['secant_interpolated_ramp']=(result['left_ramp']+(th-d0)*
                        (result['right_ramp']-result['left_ramp'])/(d1-d0))
                critical.append(result)
    if not args.smoke_ramps:
        if len(critical)!=len(LEVELS)*2:raise RuntimeError('Critical threshold surface incomplete')
        if max_parent_profile_error>1e-7:raise RuntimeError('Original x profile regression failed')
    write_csv(out/'barrier_height_curvature.csv',raw)
    write_csv(out/'threshold_persistence_components.csv',persist)
    write_csv(out/'critical_threshold_curve.csv',critical)
    write_csv(out/'barrier_ramp_sensitivity.csv',sensitivity)
    write_csv(out/'dense_contact_profiles.csv',profiles)
    if reference_regress:write_csv(out/'original_x_profile_regression.csv',reference_regress)
    summary={'version':'v18.48y','status':'FULL_FLOATING_POINT_11D_AUDIT' if not args.smoke_ramps else 'SMOKE_ONLY',
       'genuine_new_11D_integrations':physical_runs,'original_states_authenticated':328,
       'original_paths_total':8,'newly_integrated_paths':'phaseblind branch0 original and autonomous',
       'return_ramps_per_kappa':len(all_ram),'q_phase_samples_per_profile':args.phase_samples,
       'phase_window':list(Q_LIMITS),'thresholds':list(LEVELS),'sublevel_thresholds':list(PROFILE_LEVELS),
       'max_original_x_profile_reproduction_error':max_parent_profile_error,
       'max_original_11D_replay_error':max_replay,'maximum_energy_ledger_relative_error':max_ledger,
       'maximum_curvature_step_variation':max(a['relative_curvature_step_variation'] for a in raw),
       'threshold_brackets':critical,'historical_authentication':provenance,
       'limits':'No validated interval bounds, no global topological theorem, no full-11D recurrence or energetic reversibility claim. Critical curve interpolated between genuinely integrated ramp samples.'}
    (out/'report.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'integrations':physical_runs,'threshold_brackets':len(critical),
                      'max_profile_regression':max_parent_profile_error,
                      'max_ledger_relative_error':max_ledger,
                      'max_curvature_step_variation':summary['maximum_curvature_step_variation']},indent=2),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke-ramps',type=int,default=0)
    p.add_argument('--smoke-kinds',type=int,default=0)
    p.add_argument('--phase-samples',type=int,default=1601)
    p.add_argument('--rtol',type=float,default=3e-12)
    p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025)
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--output-dir',type=Path,default=ROOT/'results')
    a=p.parse_args()
    if a.phase_samples<801:raise ValueError('At least 801 q samples required')
    run(a)
