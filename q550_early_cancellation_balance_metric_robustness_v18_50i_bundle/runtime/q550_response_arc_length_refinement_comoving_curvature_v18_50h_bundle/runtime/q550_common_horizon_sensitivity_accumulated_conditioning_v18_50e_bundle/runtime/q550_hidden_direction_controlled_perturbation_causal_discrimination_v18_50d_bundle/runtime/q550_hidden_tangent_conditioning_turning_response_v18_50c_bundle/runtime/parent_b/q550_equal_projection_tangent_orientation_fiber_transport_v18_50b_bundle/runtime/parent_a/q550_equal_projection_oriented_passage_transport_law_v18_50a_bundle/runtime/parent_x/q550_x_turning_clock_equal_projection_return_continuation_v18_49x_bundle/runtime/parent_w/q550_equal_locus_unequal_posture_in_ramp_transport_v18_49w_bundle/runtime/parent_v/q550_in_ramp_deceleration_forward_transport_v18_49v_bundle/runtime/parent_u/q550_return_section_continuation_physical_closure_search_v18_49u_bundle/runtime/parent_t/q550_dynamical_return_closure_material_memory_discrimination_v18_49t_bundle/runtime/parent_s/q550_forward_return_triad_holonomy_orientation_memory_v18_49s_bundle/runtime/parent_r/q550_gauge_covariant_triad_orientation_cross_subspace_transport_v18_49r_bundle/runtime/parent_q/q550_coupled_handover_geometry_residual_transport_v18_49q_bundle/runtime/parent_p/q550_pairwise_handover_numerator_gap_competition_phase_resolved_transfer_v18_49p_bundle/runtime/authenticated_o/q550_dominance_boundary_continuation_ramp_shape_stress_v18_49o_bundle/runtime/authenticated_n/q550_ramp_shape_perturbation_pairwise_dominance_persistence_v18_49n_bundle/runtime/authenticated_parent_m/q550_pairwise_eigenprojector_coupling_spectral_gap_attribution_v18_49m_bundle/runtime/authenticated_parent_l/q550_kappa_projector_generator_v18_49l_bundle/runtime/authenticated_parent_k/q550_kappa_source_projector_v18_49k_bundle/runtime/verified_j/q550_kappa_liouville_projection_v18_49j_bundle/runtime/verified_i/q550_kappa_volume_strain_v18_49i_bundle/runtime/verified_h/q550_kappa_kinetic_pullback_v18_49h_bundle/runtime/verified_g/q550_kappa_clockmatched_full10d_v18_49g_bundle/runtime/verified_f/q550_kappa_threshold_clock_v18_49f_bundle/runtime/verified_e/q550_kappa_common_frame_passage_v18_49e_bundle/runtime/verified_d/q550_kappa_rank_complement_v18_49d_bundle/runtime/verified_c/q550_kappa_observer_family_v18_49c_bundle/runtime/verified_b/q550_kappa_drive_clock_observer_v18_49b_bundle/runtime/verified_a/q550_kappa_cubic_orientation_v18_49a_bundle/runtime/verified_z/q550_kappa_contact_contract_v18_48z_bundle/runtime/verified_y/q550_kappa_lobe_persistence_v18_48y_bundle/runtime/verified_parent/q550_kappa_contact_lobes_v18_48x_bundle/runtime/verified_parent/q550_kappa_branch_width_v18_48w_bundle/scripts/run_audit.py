#!/usr/bin/env python3
"""v18.48w: branch-specific ramp refinement, signed work and contact widths.

Source of original numerical v-grid is the authenticated original server
sendback. New refinements use exact inherited 11D material RHS and energy.
Alpha=1 only. All energy diagnostics are model work, not entropy.
"""
from __future__ import annotations
import argparse,csv,importlib.util,json,math,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from scipy.integrate import solve_ivp
from verify_parent import verify
from continuation_math import refinements,branch_key,sign_of,sign_transitions,phase_minimum,THRESHOLDS,FIXED_PHASES
ROOT=Path(__file__).resolve().parents[1]
VELOCITY_INDICES=(1,3,5,7,9)
def load(path,name):
    sp=importlib.util.spec_from_file_location(name,path)
    o=importlib.util.module_from_spec(sp);sys.modules[name]=o;sp.loader.exec_module(o)
    return o
def readcsv(path):
    with path.open(newline='',encoding='utf8') as f:return list(csv.DictReader(f))
def writecsv(path,rows):
    if not rows:return
    keys=list(dict.fromkeys(k for x in rows for k in x))
    with path.open('w',newline='',encoding='utf8') as f:
        w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
def tag(th):return str(th).replace('.','p')
def val(row,key):return float(row[key])
def eqkey(row):return (row['family'],int(row['branch']),row['kappa_kind'])
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--limit-groups',type=int,default=0,help='Only labeled partial preflight; 0=all eight original physical paths')
    ap.add_argument('--rtol',type=float,default=3e-12)
    ap.add_argument('--atol',type=float,default=3e-13)
    ap.add_argument('--max-step',type=float,default=.025)
    ap.add_argument('--output-dir',type=Path,default=ROOT/'results')
    args=ap.parse_args()
    if not all(v>0 for v in (args.rtol,args.atol,args.max_step)):raise ValueError('Invalid integrator tolerances')
    parent_v,u,t,s,r,j,provenance=verify()
    p=r/'runtime/verified_parent/q550_kappa_counterflow_crossings_v18_48q_bundle/runtime/verified_parent/q550_kappa_counterflow_energy_v18_48p_bundle'
    physical=load(ROOT/'reference/physical_math.py','w_q550_physical')
    geom=load(ROOT/'reference/transversality_math.py','w_q550_geometry')
    ramp=load(ROOT/'reference/parent_ramp_math.py','w_q550_ramp')
    support=load(p/'reference/test_support_q550_support_ode_interval_residual_pilot_v1.py','w_q550_support')
    audit=load(p/'reference/test_support_mobius_monodromy_audit.py','w_q550_audit')
    historical=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    y=np.asarray(historical['y'],float);xi=np.asarray(historical['xi'],float)
    h=json.loads((j/'runtime/report_v18_48h.json').read_text())
    kappas={'original':float(h['kappa_original']),'autonomous':float(h['kappa_autonomous'])}
    slope=float(historical['clock_speed'])/(2*math.pi);omega=2*math.pi*slope
    params=audit.ModelParameters(gamma_rho=.3)
    groups=defaultdict(list)
    for i in range(len(y)):
        groups[(str(historical['families'][i]),int(historical['seed_branches'][i]),str(historical['kappa_kind'][i]))].append(i)
    if len(y)!=328 or len(groups)!=8:raise RuntimeError('Historical state genealogy is not 8 x 41')
    keys=sorted(groups)
    if args.limit_groups:keys=keys[:args.limit_groups]
    parent_contacts=[x for x in readcsv(parent_v/'results/fine_ramp_contacts.csv') if float(x['alpha'])==1.]
    parent_fixed=[x for x in readcsv(parent_v/'results/fixed_phase_energy_history.csv') if float(x['alpha'])==1.]
    if len(parent_contacts)!=136 or len(parent_fixed)!=408:
        raise RuntimeError('Parent v alpha=1 cardinalities changed')
    parent_contact_map={(eqkey(x),float(x['ramp_duration_xi'])):x for x in parent_contacts}
    parent_fixed_map={(eqkey(x),float(x['ramp_duration_xi']),float(x['common_phase_q'])):x for x in parent_fixed}
    urows=readcsv(u/'results/common_phase_profiles.csv')
    qgrid=np.array(sorted({float(x['common_phase_q']) for x in urows}),float)
    if len(qgrid)!=81:raise RuntimeError('Original 81-point phase grid changed')
    out=args.output_dir;out.mkdir(exist_ok=True,parents=True)
    new_contacts=[];new_fixed=[];center_comparisons=[];regressions=[]
    max_balance=0.;max_ledger=0.;max_clock=0.;max_center=0.;max_replay=0.
    integrations=0
    def integrate(y0,k,design=None,forward=False):
        nonlocal integrations,max_balance
        duration=1. if forward else design.duration
        phase0=float(y0[10]);state=np.r_[y0[:10],np.zeros(4)]
        def clock(z):return phase0+omega*z if forward else phase0-omega*ramp.cubic_phase_excursion(z,design)
        def rhs(tt,z):
            cs=1. if forward else ramp.cubic_clock_sign(tt,design)
            yy=np.r_[z[:10],clock(tt)]
            return np.r_[physical.rhs_from_original(yy,k,params,slope,cs,support,audit)[:10],
                         physical.power_terms(yy,k,params,slope,cs)]
        sol=solve_ivp(rhs,(0.,duration),state,method='DOP853',rtol=args.rtol,atol=args.atol,max_step=args.max_step,dense_output=True)
        if not sol.success:raise RuntimeError('Original 11D integration failed: '+sol.message)
        integrations+=1
        def ev(tt):
            if np.ndim(tt)==0:
                v=sol.sol(float(tt));return np.r_[v[:10],clock(float(tt)),v[10:]]
            times=np.asarray(tt,float);v=sol.sol(times)
            return np.vstack([v[:10],np.array([clock(float(q)) for q in times])[None,:],v[10:]])
        end=ev(duration)
        de=physical.energy(end[:11],k,params)-physical.energy(y0,k,params)
        terms=end[11:];resid=abs(de-sum(terms))/max(1.,abs(de),float(sum(abs(terms))))
        max_balance=max(max_balance,float(resid))
        if resid>1e-8:raise RuntimeError('Mechanical energy ledger broken')
        return ev
    for key in keys:
        fam,b,kind=key
        ids=sorted(groups[key],key=lambda i:xi[i])
        if not np.allclose(xi[ids],np.linspace(3.5,4.5,41),atol=1e-12):raise RuntimeError('Historical physical sections changed')
        k=kappas[kind];F=integrate(y[ids[0]],k,forward=True)
        replay=float(np.max(np.linalg.norm(F(np.linspace(0,1,41)).T[:,:11]-y[ids],axis=1)))
        max_replay=max(replay,max_replay)
        if replay>1e-7:raise RuntimeError('Historical physical 11D replay differs')
        regressions.append({'family':fam,'branch':b,'kappa_kind':kind,'forward_replay_11D_max':replay})
        turn=F(1.)[:11];e_turn=physical.energy(turn,k,params)
        init=turn.copy();init[list(VELOCITY_INDICES)]*=-1.
        jump=physical.energy(init,k,params)-e_turn
        if abs(jump)>1e-8:raise RuntimeError('Alpha=1 full velocity flip must conserve initial kinetic energy')
        f_states=F(1.-qgrid).T
        f_shapes=np.array([geom.shape(yy[:11]) for yy in f_states])
        ramps=(*refinements(fam,b),float(ramp.FULL_RAMPS[{('phaseblind',0):13,('phaseblind',1):2,('phasecov',0):1,('phasecov',1):14}[(branch_key(fam),b)]]))
        # Include the original best grid ramp as an independent regression control.
        if len(set(ramps))!=9:raise RuntimeError('Nine continuation ramp values must be distinct')
        for rv in ramps:
            d=ramp.Design(f'cubic_{rv:.3f}','smoothstep',rv)
            R=integrate(init,k,design=d)
            r_state=R(rv+qgrid).T
            r_shapes=np.array([geom.shape(x[:11]) for x in r_state])
            gaps=np.linalg.norm(r_shapes-f_shapes,axis=1)
            def dist(q):
                return float(np.linalg.norm(geom.shape(R(ramp.phase_time(q,d))[:11])-geom.shape(F(1.-q)[:11])))
            dmin,qbest=phase_minimum(dist,qgrid,gaps)
            zr=R(ramp.phase_time(qbest,d));zf=F(1.-qbest)
            yr=zr[:11];yf=zf[:11]
            delta=yr-yf;delta[[2,6,10]]=geom.wrap(delta[[2,6,10]])
            Eret=physical.energy(yr,k,params);Efwd=physical.energy(yf,k,params)
            ledger=(Eret-Efwd)-(sum(F(1.)[11:])-sum(zf[11:])+jump+sum(zr[11:]))
            max_ledger=max(max_ledger,abs(ledger))
            if abs(ledger)>1e-7:raise RuntimeError('Contact energy ledger broken')
            phaseerror=abs(geom.wrap(yr[10]-yf[10]));max_clock=max(max_clock,phaseerror)
            if phaseerror>1e-8:raise RuntimeError('Phase mismatch in equal-drive comparison')
            pr=physical.power_terms(yr,k,params,slope,-1.)
            pf=physical.power_terms(yf,k,params,slope,1.)
            result={'family':fam,'branch':b,'kappa_kind':kind,'alpha':1.,'ramp_duration_xi':rv,
                'design':d.name,'minimum_3D_gap':dmin,'minimum_common_phase_q':qbest,
                'minimum_interior':int(qgrid[0]+1e-6<qbest<qgrid[-1]-1e-6),
                'minimum_11D_gap':float(np.linalg.norm(delta)),
                'minimum_velocity_gap':float(np.linalg.norm(delta[list(VELOCITY_INDICES)])),
                'minimum_energy_gap':float(Eret-Efwd),'minimum_return_energy':float(Eret),
                'minimum_forward_energy':float(Efwd),
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
                'energy_history_identity_residual':float(ledger),
                'clock_mismatch_rad':float(phaseerror)}
            for threshold in THRESHOLDS:
                spans=ramp.subthreshold_intervals(dist,qgrid,threshold,minq=qbest,precomputed=gaps)
                suffix=tag(threshold)
                result['contact_intervals_'+suffix]=spans['number_intervals']
                result['contact_longest_q_'+suffix]=spans['longest_phase_width']
                result['contact_total_q_'+suffix]=spans['total_phase_width']
                if dmin<threshold and not spans['min_inside']:
                    raise RuntimeError('Threshold width root bracketing inconsistent')
            for qf in FIXED_PHASES:
                a=R(ramp.phase_time(qf,d));bb=F(1.-qf)
                ya=a[:11];yb=bb[:11]
                diff=ya-yb;diff[[2,6,10]]=geom.wrap(diff[[2,6,10]])
                Egap=physical.energy(ya,k,params)-physical.energy(yb,k,params)
                led=sum(F(1.)[11:])-sum(bb[11:])+jump+sum(a[11:])
                if abs(Egap-led)>1e-7:raise RuntimeError('Fixed-phase energy conservation mismatch')
                new_fixed.append({'family':fam,'branch':b,'kappa_kind':kind,'alpha':1.,
                    'ramp_duration_xi':rv,'common_phase_q':qf,
                    'elapsed_return_xi':ramp.phase_time(qf,d),
                    'shape_distance_3D':float(np.linalg.norm(geom.shape(ya)-geom.shape(yb))),
                    'full_state_11D_distance':float(np.linalg.norm(diff)),
                    'velocity_L2_distance':float(np.linalg.norm(diff[list(VELOCITY_INDICES)])),
                    'energy_gap':float(Egap),'preparation_energy_jump':float(jump),
                    'return_cumulative_drive_work':float(a[11]),
                    'return_cumulative_radial_damping':float(a[12]),
                    'return_cumulative_x_damping':float(a[13]),
                    'return_cumulative_active_work':float(a[14]),
                    'forward_cumulative_drive_work_since_start':float(F(1.)[11]-bb[11]),
                    'forward_cumulative_radial_damping_since_start':float(F(1.)[12]-bb[12]),
                    'forward_cumulative_x_damping_since_start':float(F(1.)[13]-bb[13]),
                    'forward_cumulative_active_work_since_start':float(F(1.)[14]-bb[14]),
                    'energy_gap_ledger_residual':float(Egap-led)})
            old=parent_contact_map.get((key,rv))
            if old is not None:
                attrs=['minimum_3D_gap','minimum_common_phase_q','minimum_11D_gap',
                       'minimum_energy_gap','return_cumulative_drive_work_at_min',
                       'contact_total_q_0p01','contact_total_q_0p005','contact_total_q_0p0025']
                error=max(abs(float(old[x])-float(result[x])) for x in attrs)
                for qf in FIXED_PHASES:
                    oldf=parent_fixed_map.get((key,rv,qf))
                    latest=new_fixed[-3+FIXED_PHASES.index(qf)]
                    if oldf is None:raise RuntimeError('Parent matched-phase control missing')
                    error=max(error,*(abs(float(oldf[x])-float(latest[x])) for x in
                          ('shape_distance_3D','energy_gap','return_cumulative_drive_work')))
                max_center=max(max_center,error)
                center_comparisons.append({'family':fam,'branch':b,'kappa_kind':kind,
                    'ramp_duration_xi':rv,'maximum_parent_v_regression':error})
                if error>2e-7:raise RuntimeError('Original v contact/width/energy regression broken')
            else:new_contacts.append(result)
        print('v18.48w completed:',branch_key(fam),b,kind,'new ramps',len(refinements(fam,b)),flush=True)
    if len(center_comparisons)!=len(keys):raise RuntimeError('Original center regression missing for any physical path')
    if len(new_contacts)!=len(keys)*8 or len(new_fixed)!=len(keys)*9*3:
        raise RuntimeError('Unexpected number of newly integrated contact/fixed samples')
    joined_contacts=[x for x in parent_contacts if eqkey(x) in keys]+new_contacts
    joined_fixed=[x for x in parent_fixed if eqkey(x) in keys]+[x for x in new_fixed if (eqkey(x),float(x['ramp_duration_xi'])) not in parent_contact_map]
    # Each of eight paths now has 25 original/new ramp samples and 3 matched phases per ramp.
    if len(joined_contacts)!=len(keys)*25 or len(joined_fixed)!=len(keys)*25*3:
        raise RuntimeError('Joined numerical continuation cardinality mismatch')
    branchsummary=[];workrows=[]
    for key in keys:
        f,b,k=key
        cr=sorted([x for x in joined_contacts if eqkey(x)==key],key=lambda x:val(x,'ramp_duration_xi'))
        winner=min(cr,key=lambda x:val(x,'minimum_3D_gap'))
        widths={}
        for th in THRESHOLDS:
            widthfield='contact_total_q_'+tag(th)
            possible=[x for x in cr if val(x,widthfield)>0]
            broad=max(possible,key=lambda x:val(x,widthfield)) if possible else None
            widths[tag(th)]={'width_max':val(broad,widthfield) if broad else 0.,
                           'ramp_at_max_width':val(broad,'ramp_duration_xi') if broad else None,
                           'width_at_best_gap':val(winner,widthfield),
                           'number_with_contact':len(possible)}
        for qf in FIXED_PHASES:
            fr=sorted([x for x in joined_fixed if eqkey(x)==key and float(x['common_phase_q'])==qf],
                      key=lambda x:val(x,'ramp_duration_xi'))
            works=[val(x,'return_cumulative_drive_work') for x in fr]
            signs=[sign_of(w) for w in works]
            crossings=sign_transitions(fr,'ramp_duration_xi','return_cumulative_drive_work')
            workrows.append({'family':f,'branch':b,'kappa_kind':k,'common_phase_q':qf,
                'ramp_grid_count':len(fr),'positive_work':sum(v>0 for v in signs),
                'negative_work':sum(v<0 for v in signs),'numerical_zero':sum(v==0 for v in signs),
                'signed_work_min':min(works),'signed_work_max':max(works),
                'work_sign_change_brackets':len(crossings),
                'brackets_json':json.dumps(crossings),
                'median_energy_gap':float(np.median([val(x,'energy_gap') for x in fr]))})
        branchsummary.append({'family':f,'branch':b,'kappa_kind':k,
            'ramps_count':len(cr),'best_sampled_ramp_xi':val(winner,'ramp_duration_xi'),
            'best_sampled_3D_gap':val(winner,'minimum_3D_gap'),
            '11D_gap_at_best_shape_contact':val(winner,'minimum_11D_gap'),
            'energy_gap_at_best_shape_contact':val(winner,'minimum_energy_gap'),
            'q_at_best_shape_contact':val(winner,'minimum_common_phase_q'),
            **{f'width_at_best_{tag(th)}':widths[tag(th)]['width_at_best_gap'] for th in THRESHOLDS},
            **{f'widest_ramp_{tag(th)}':widths[tag(th)]['ramp_at_max_width'] for th in THRESHOLDS},
            **{f'widest_q_{tag(th)}':widths[tag(th)]['width_max'] for th in THRESHOLDS},
            **{f'contacts_present_{tag(th)}':widths[tag(th)]['number_with_contact'] for th in THRESHOLDS}})
    writecsv(out/'new_refined_contacts.csv',new_contacts)
    writecsv(out/'new_refined_fixed_phase_energy.csv',new_fixed)
    writecsv(out/'combined_branch_contacts.csv',joined_contacts)
    writecsv(out/'combined_branch_fixed_phase_energy.csv',joined_fixed)
    writecsv(out/'branch_resolved_window_summary.csv',branchsummary)
    writecsv(out/'branch_resolved_work_signs.csv',workrows)
    writecsv(out/'original_center_regression.csv',center_comparisons)
    writecsv(out/'historical_replay.csv',regressions)
    report={'version':'v18.48w',
        'status':'FULL_EIGHT_PATH_NUMERICAL_AUDIT' if len(keys)==8 else 'PARTIAL_PREFLIGHT_ONLY',
        'title':'Branch-Resolved Work-Sign & Contact-Width Continuation Audit',
        'historical_paths':len(keys),'genuine_new_material_integrations':integrations,
        'refined_new_ramps_per_path':8,'center_regression_integrations_per_path':1,
        'authenticated_original_v_contact_samples':len(keys)*17,
        'new_refinement_contacts':len(new_contacts),'combined_contact_samples':len(joined_contacts),
        'combined_fixed_phase_energy_samples':len(joined_fixed),
        'number_branch_work_sign_rows':len(workrows),
        'maximum_11D_original_replay_error':max_replay,
        'maximum_v18_48v_center_regression':max_center,
        'maximum_mechanical_ledger_relative_error':max_balance,
        'maximum_equal_phase_energy_ledger_absolute_error':max_ledger,
        'maximum_drive_phase_mismatch_rad':max_clock,
        'branches':branchsummary,'work_signs':workrows,'provenance':provenance,
        'limits':('Alpha=1 only; original 17 ramp points inherited from exact SHA-verified server data, '
             'eight additional samples and one independent center check integrated for each historical path. '
             'The selected shape phase moves with ramp duration. Widths are root-refined threshold diagnostics '
             'based on a finite 81-point phase scan, not interval or exhaustive certifications. '
             'Signed drive work is part of the chosen non-conservative mechanical ledger; '
             'changes in an ensemble median are not a physical work sign reversal of an individual path. '
             'The input command histories and the elapsed times differ between ramps even when drive phase matches. '
             'No universal constitutive law, physical 11D recurrence, or thermodynamic entropy conclusion.')}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('FINAL',json.dumps({k:report[k] for k in
       ('status','genuine_new_material_integrations','new_refinement_contacts','combined_contact_samples',
        'maximum_v18_48v_center_regression','maximum_mechanical_ledger_relative_error')},indent=2),flush=True)
if __name__=='__main__':main()
