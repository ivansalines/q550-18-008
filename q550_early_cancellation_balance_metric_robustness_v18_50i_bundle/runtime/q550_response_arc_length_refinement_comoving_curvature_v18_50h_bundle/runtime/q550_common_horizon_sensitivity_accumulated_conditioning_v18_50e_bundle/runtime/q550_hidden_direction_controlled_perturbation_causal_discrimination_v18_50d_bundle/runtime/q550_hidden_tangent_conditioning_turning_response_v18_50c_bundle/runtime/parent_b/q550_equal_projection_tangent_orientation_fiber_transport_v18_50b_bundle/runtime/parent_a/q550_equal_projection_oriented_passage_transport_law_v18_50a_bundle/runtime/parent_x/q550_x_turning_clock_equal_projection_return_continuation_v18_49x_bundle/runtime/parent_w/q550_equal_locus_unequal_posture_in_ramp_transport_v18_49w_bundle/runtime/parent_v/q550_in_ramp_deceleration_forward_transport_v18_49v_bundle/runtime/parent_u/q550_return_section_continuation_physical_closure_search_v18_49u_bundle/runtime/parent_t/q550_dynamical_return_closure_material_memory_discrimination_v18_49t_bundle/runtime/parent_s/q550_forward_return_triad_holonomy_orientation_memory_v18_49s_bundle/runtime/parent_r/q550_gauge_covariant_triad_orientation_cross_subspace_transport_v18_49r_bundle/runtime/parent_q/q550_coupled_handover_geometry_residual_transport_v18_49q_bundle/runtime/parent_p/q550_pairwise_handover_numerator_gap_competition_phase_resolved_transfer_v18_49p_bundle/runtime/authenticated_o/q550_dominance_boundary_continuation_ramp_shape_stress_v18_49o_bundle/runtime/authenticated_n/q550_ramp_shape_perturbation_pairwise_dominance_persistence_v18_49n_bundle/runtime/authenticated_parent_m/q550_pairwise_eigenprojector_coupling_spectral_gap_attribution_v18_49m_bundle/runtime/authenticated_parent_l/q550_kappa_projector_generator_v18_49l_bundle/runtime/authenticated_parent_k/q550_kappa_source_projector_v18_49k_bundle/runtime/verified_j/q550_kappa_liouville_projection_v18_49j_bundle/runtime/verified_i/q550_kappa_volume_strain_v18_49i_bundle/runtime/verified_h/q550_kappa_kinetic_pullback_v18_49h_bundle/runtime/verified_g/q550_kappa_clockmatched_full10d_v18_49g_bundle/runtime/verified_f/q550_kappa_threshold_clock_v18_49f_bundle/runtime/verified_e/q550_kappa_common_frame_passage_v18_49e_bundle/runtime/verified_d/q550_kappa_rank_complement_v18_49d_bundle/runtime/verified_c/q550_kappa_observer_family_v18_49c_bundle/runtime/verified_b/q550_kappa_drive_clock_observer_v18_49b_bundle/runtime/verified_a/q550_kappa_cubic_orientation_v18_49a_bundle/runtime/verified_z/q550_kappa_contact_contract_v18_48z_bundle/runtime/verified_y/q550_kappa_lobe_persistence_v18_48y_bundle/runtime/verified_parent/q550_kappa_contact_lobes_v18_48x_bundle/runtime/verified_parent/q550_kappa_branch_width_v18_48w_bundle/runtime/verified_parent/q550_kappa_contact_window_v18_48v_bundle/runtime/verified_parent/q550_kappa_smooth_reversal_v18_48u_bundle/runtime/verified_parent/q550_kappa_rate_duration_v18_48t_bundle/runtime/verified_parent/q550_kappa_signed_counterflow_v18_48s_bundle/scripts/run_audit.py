#!/usr/bin/env python3
"""v18.48s: signed tangent, phase-corresponding near contact, signed energy ledger.

Reintegrate the 88 original-support Q550 11D IVPs using authenticated r rows as
contact anchors. Compare historical asynchrony, phase-conditioned minima, and
2D crossings at their actual continuous IVP positions. No 2D contact is
promoted to a 3D/11D contact or a thermodynamic irreversibility certificate.
"""
from __future__ import annotations
import argparse,csv,importlib.util,json,math,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from verify_parent import verify
from signed_math import (alignment,projected_chirality,signed_contact_derivative,
 signed_energy_gap_derivative,phase_locked_component_roots)
ROOT=Path(__file__).resolve().parents[1]
def load_module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def readcsv(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))
def writecsv(path,rows):
    if not rows:return
    fields=list(dict.fromkeys(k for x in rows for k in x))
    with path.open('w',newline='',encoding='utf-8') as f:
        wr=csv.DictWriter(f,fieldnames=fields);wr.writeheader();wr.writerows(rows)
def stats(rows,field):
    a=np.array([float(r[field]) for r in rows if r.get(field) not in ('',None)],float)
    a=a[np.isfinite(a)]
    return {'count':len(a),'min':float(a.min()),'median':float(np.median(a)),
            'max':float(a.max())} if len(a) else {}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rtol',type=float,default=3e-12)
    parser.add_argument('--atol',type=float,default=3e-13)
    parser.add_argument('--max-step',type=float,default=.025)
    parser.add_argument('--phase-root-nodes',type=int,default=151)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results')
    args=parser.parse_args()
    if not (args.rtol>0 and args.atol>0 and args.max_step>0 and args.phase_root_nodes>=51):
        raise ValueError('Bad numeric setup')
    output=args.output_dir;output.mkdir(parents=True,exist_ok=True)
    r, j, genealogy=verify()
    q=r/'runtime/verified_parent/q550_kappa_counterflow_crossings_v18_48q_bundle'
    p=q/'runtime/verified_parent/q550_kappa_counterflow_energy_v18_48p_bundle'
    physical=load_module(ROOT/'reference/physical_math.py','q550_v1848s_physical')
    geometry=load_module(ROOT/'reference/transversality_math.py','q550_v1848s_geometry')
    support=load_module(p/'reference/test_support_q550_support_ode_interval_residual_pilot_v1.py','q550_v1848s_support')
    audit=load_module(p/'reference/test_support_mobius_monodromy_audit.py','q550_v1848s_audit')
    history=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    state=np.asarray(history['y'],float);times=np.asarray(history['xi'],float)
    hreport=json.loads((j/'runtime/report_v18_48h.json').read_text())
    kappas={'original':float(hreport['kappa_original']),
            'autonomous':float(hreport['kappa_autonomous'])}
    slope=float(history['clock_speed'])/(2*math.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    contacts=readcsv(r/'results/crossing_transversality.csv')
    roots2d=readcsv(r/'results/projection_crossings_2d.csv')
    groups=defaultdict(list)
    for i in range(len(times)):
        key=(str(history['families'][i]),int(history['seed_branches'][i]),str(history['kappa_kind'][i]))
        groups[key].append(i)
    if len(groups)!=8 or len(times)!=328:raise RuntimeError('Wrong original historical inputs')
    contact_ix=defaultdict(list);root_ix=defaultdict(list)
    for row in contacts:contact_ix[row['family'],int(row['branch']),row['kappa_kind'],row['protocol']].append(row)
    for row in roots2d:root_ix[row['family'],int(row['branch']),row['kappa_kind'],row['protocol']].append(row)
    configs=[('phase_closed',.5,2.),('phase_closed',1.,1.),('phase_closed',2.,.5),
             ('fixed_duration',.5,1.),('fixed_duration',2.,1.)]
    comparisons=[];crossing=[];signed_onecoord=[];protocols=[];regr=[]
    total_integrations=0;max_balance=0.;max_r_distance_diff=0.;max_r_angle_diff=0.
    max_ledger_reconcile=0.;max_phase_error=0.
    sample=None
    def rhs(y,k,drive):return physical.rhs_from_original(y,k,params,slope,drive,support,audit)
    def integrate(y0,tfinal,k,drive):
        nonlocal total_integrations,max_balance
        z0=np.r_[y0,np.zeros(4)]
        def diff(t,z):
            return np.r_[rhs(z[:11],k,drive),physical.power_terms(z[:11],k,params,slope,drive)]
        sol=solve_ivp(diff,(0.,tfinal),z0,dense_output=True,
                method='DOP853',rtol=args.rtol,atol=args.atol,max_step=args.max_step)
        if not sol.success:raise RuntimeError(sol.message)
        total_integrations+=1
        e_delta=physical.energy(sol.y[:11,-1],k,params)-physical.energy(y0,k,params)
        work=np.sum(sol.y[11:,-1])
        error=abs(e_delta-work)/max(1.,abs(e_delta),sum(abs(sol.y[11:,-1])))
        max_balance=max(max_balance,float(error))
        if error>1e-8:raise RuntimeError('Energy ledger mismatch '+str(error))
        def evaluate(u):
            x=np.asarray(u,float)
            v=sol.sol(x*tfinal)
            return np.moveaxis(v,0,-1) if x.ndim else v
        return evaluate
    def one_contact(F,R,u,s,k,rate,duration,kind,original_row=None):
        nonlocal max_r_distance_diff,max_r_angle_diff,max_ledger_reconcile,max_phase_error
        zy=R(u);fy=F(s);a=zy[:11];b=fy[:11]
        sh_r=geometry.shape(a);sh_f=geometry.shape(b);delta=sh_r-sh_f
        tr=geometry.shape_tangent(a,rhs(a,k,-rate))*duration
        tf=geometry.shape_tangent(b,rhs(b,k,1.))
        signed=alignment(tr,tf)
        phases=geometry.wrap(a[[2,6,10]]-b[[2,6,10]])
        full=a-b;full[[2,6,10]]=phases
        eR=physical.energy(a,k,params);eF=physical.energy(b,k,params)
        powerR=physical.power_terms(a,k,params,slope,-rate)
        powerF=physical.power_terms(b,k,params,slope,1.)
        # Flip of five material velocity signs at the turn preserves kinetic energy.
        parent_energy=physical.energy(F(1.)[:11],k,params)
        initial_energy=physical.energy(F(0.)[:11],k,params)
        # Forward full ledger at turn - forward ledger at meeting + reverse ledger at meeting.
        predicted=(float(np.sum(F(1.)[11:]))-float(np.sum(fy[11:]))+float(np.sum(zy[11:])))
        ledger_err=(eR-eF)-predicted
        max_ledger_reconcile=max(max_ledger_reconcile,abs(ledger_err))
        if abs(parent_energy-initial_energy-float(np.sum(F(1.)[11:])))>1e-7:
            raise RuntimeError('Forward ledger inconsistent')
        drivephase=float(phases[2]);max_phase_error=max(max_phase_error,abs(drivephase)) if kind=='phase_locked_min' else max_phase_error
        distance=float(np.linalg.norm(delta))
        if original_row is not None:
            max_r_distance_diff=max(max_r_distance_diff,abs(distance-float(original_row['shape_distance'])))
            max_r_angle_diff=max(max_r_angle_diff,abs(signed['chronological_angle_deg']-float(original_row['chronological_tangent_angle_deg'])))
        signclamp=lambda t:int(np.sign(t)) if abs(t)>1e-14 else 0
        return dict(return_progress=float(u),forward_progress=float(s),
          shape_distance=distance,shape_gap_logrho1=float(delta[0]),shape_gap_logrho2=float(delta[1]),
          shape_gap_x=float(delta[2]),full11D_distance=float(np.linalg.norm(full)),
          velocity_difference_L2=float(np.linalg.norm(a[[1,3,5,7,9]]-b[[1,3,5,7,9]])),
          theta1_delta_rad=float(phases[0]),theta2_delta_rad=float(phases[1]),
          Theta_delta_rad=drivephase,
          energy_difference=float(eR-eF),energy_difference_sign=signclamp(eR-eF),
          chronological_angle_deg=signed['chronological_angle_deg'],
          chronological_cos=signed['chronological_cos'],
          phase_corresponding_angle_deg=signed['phase_corresponding_angle_deg'],
          phase_corresponding_cos=signed['phase_corresponding_cos'],
          line_angle_deg=min(signed['chronological_angle_deg'],signed['phase_corresponding_angle_deg']),
          tangent_cross_normalized=signed['cross_magnitude'],
          tangent_return_rate=float(np.linalg.norm(tr)),tangent_forward_rate=float(np.linalg.norm(tf)),
          tangent_equal_phase_forward_rate=float(rate*duration*np.linalg.norm(tf)),
          drive_power_forward_per_xi=float(powerF[0]),drive_power_return_per_xi=float(powerR[0]),
          drive_power_forward_sign=signclamp(powerF[0]),drive_power_return_sign=signclamp(powerR[0]),
          net_power_forward_per_xi=float(powerF.sum()),net_power_return_per_xi=float(powerR.sum()),
          phase_locked_energy_gap_derivative_per_u=signed_energy_gap_derivative(powerR.sum(),powerF.sum(),rate,duration),
          phase_locked_half_distance_squared_derivative_per_u=signed_contact_derivative(delta,tr,tf,rate,duration),
          # Cumulative components (4) from turn on reverse and from start on forward.
          forward_drive_work_to_s=float(fy[11]),reverse_drive_work_to_u=float(zy[11]),
          forward_radial_dissipation_to_s=float(fy[12]),reverse_radial_dissipation_to_u=float(zy[12]),
          forward_x_dissipation_to_s=float(fy[13]),reverse_x_dissipation_to_u=float(zy[13]),
          forward_active_work_to_s=float(fy[14]),reverse_active_work_to_u=float(zy[14]),
          energy_gap_ledger_residual=float(ledger_err),
          phase_locked_forward_progress_expected=float(1.-rate*duration*u),
          phase_locked_forward_progress_mismatch=float(s-(1.-rate*duration*u)))
    for (family,branch,kind),indexes in sorted(groups.items()):
        indexes=sorted(indexes,key=lambda i:times[i])
        if not np.allclose(times[indexes],np.linspace(3.5,4.5,41),atol=1e-12):raise RuntimeError('Historical section clock mismatch')
        k=kappas[kind]
        F=integrate(state[indexes[0]],1.,k,1.)
        deviation=float(np.max(np.linalg.norm(F(np.linspace(0,1,41))[:,:11]-state[indexes],axis=1)))
        if deviation>1e-7:raise RuntimeError('Historical physical curve drift')
        regr.append({'family':family,'branch':branch,'kappa_kind':kind,'max_historical_11D_error':deviation})
        turn=F(1.)[:11]
        for design,rate,duration in configs:
            for flip in (0,1):
                protocol=f'{design}_rate{rate:g}_flip{flip}'
                key=family,branch,kind,protocol
                init=turn.copy()
                if flip:init[[1,3,5,7,9]]*=-1.
                R=integrate(init,duration,k,-rate)
                parent_contacts=contact_ix[key]
                if len(parent_contacts)!=2:raise RuntimeError('Unexpected r contact entries '+repr(key))
                for original in parent_contacts:
                    label=original['comparison']
                    ctype='phase_locked_min' if label=='phase_conditioned_min' else 'async_free_min'
                    u=float(original['return_progress']);s=float(original['forward_progress'])
                    out=one_contact(F,R,u,s,k,rate,duration,ctype,original)
                    if ctype=='phase_locked_min' and abs(out['Theta_delta_rad'])>1e-9:
                        raise RuntimeError('r phase-locked point is not phase matched')
                    comparisons.append(dict(family=family,branch=branch,kappa_kind=kind,protocol=protocol,
                       design=design,rate=rate,duration_xi=duration,velocity_flip=flip,
                       contact_kind=ctype,original_interior=original['interior_minimum'],**out))
                for root in root_ix[key]:
                    u=float(root['return_progress']);s=float(root['forward_progress'])
                    out=one_contact(F,R,u,s,k,rate,duration,'2D_projection_root',root)
                    axes=tuple(int(v) for v in root['projection_axes'].split('-'))
                    tR=geometry.shape_tangent(R(u)[:11],rhs(R(u)[:11],k,-rate))*duration
                    tF=geometry.shape_tangent(F(s)[:11],rhs(F(s)[:11],k,1.))
                    chirality=projected_chirality(tR,tF,axes)
                    crossing.append(dict(family=family,branch=branch,kappa_kind=kind,protocol=protocol,
                        projection_axes=root['projection_axes'],projection_root_index=int(root['root_index']),
                        phase_matched_within_1e_9=int(abs(out['Theta_delta_rad'])<1e-9),
                        projected_2D_chirality_signed=chirality,
                        projected_crossing_regular=int(abs(chirality)>1e-7),
                        projected_chirality_sign=int(np.sign(chirality)) if abs(chirality)>1e-14 else 0,
                        r_projected_root_residual=float(root['projection_root_residual']),**out))
                # Scan true 1D same-phase curve: zeros of ONE shape component, without
                # mistaking them for 3D or full-state intersections.
                lock=next(x for x in parent_contacts if x['comparison']=='phase_conditioned_min')
                lo=float(lock['phase_domain_lower_u']);hi=float(lock['phase_domain_upper_u'])
                def S_F(x):return geometry.shape(F(x)[...,:11])
                def S_R(x):return geometry.shape(R(x)[...,:11])
                count_roots=0
                for comp in range(3):
                    for u in phase_locked_component_roots(S_F,S_R,rate,duration,lo,hi,comp,args.phase_root_nodes):
                        s=1.-rate*duration*u
                        out=one_contact(F,R,u,s,k,rate,duration,'phase_locked_one_coordinate')
                        if abs(out['Theta_delta_rad'])>1e-9:raise RuntimeError('Root phase mismatch')
                        count_roots+=1
                        signed_onecoord.append(dict(family=family,branch=branch,kappa_kind=kind,
                            protocol=protocol,rate=rate,duration_xi=duration,velocity_flip=flip,
                            matched_coordinate=('logrho1','logrho2','x')[comp],**out))
                protocols.append(dict(family=family,branch=branch,kappa_kind=kind,protocol=protocol,
                   design=design,rate=rate,duration_xi=duration,velocity_flip=flip,
                   number_phase_locked_coordinate_roots=count_roots,
                   phase_locked_min_distance=float(next(a['shape_distance'] for a in comparisons[-2:] if a['contact_kind']=='phase_locked_min'))))
                if family.startswith('phasecov') and branch==0 and kind=='original' and protocol=='phase_closed_rate1_flip1':
                    grid=np.linspace(0,1,401)
                    sample={'progress':grid,'forward_state':F(grid)[:,:11],
                            'return_state':R(grid)[:,:11],
                            'forward_work':F(grid)[:,11:], 'return_work':R(grid)[:,11:],
                            'synchronous_forward_state':F(1-grid)[:,:11],
                            'synchronous_forward_work':F(1-grid)[:,11:]}
        print('v18.48s',family,branch,kind,'historical_error',f'{deviation:.3e}',flush=True)
    if total_integrations!=88 or len(comparisons)!=160 or len(crossing)!=len(roots2d):
        raise RuntimeError('Unexpected integration/contact count')
    for filename,rows in [('signed_contacts.csv',comparisons),('signed_projected_crossings.csv',crossing),
                          ('phase_locked_one_coordinate_roots.csv',signed_onecoord),
                          ('protocol_summary.csv',protocols),('source_regression.csv',regr)]:writecsv(output/filename,rows)
    if sample is not None:np.savez_compressed(output/'phasecov_phase_locked_paths.npz',**sample)
    free=[v for v in comparisons if v['contact_kind']=='async_free_min']
    locked=[v for v in comparisons if v['contact_kind']=='phase_locked_min']
    report={'version':'v18.48s','title':'Signed Counterflow Tangent & Phase-Locked Near-Contact Audit',
      'genuine_11D_integrations':total_integrations,'historical_states':len(times),
      'asynchronous_contact_pairs':len(free),'phase_locked_contact_pairs':len(locked),
      'projected_2D_crossings_reexamined':len(crossing),
      'phase_locked_one_coordinate_roots':len(signed_onecoord),
      'phase_locked_one_coordinate_min_full3D_gap':min([v['shape_distance'] for v in signed_onecoord],default=None),
      'projected_crossings_clock_matched':sum(v['phase_matched_within_1e_9'] for v in crossing),
      'projected_crossings_chronological_opposite_over_170deg':sum(v['chronological_angle_deg']>170 for v in crossing),
      'projected_crossings_chronological_similar_under_10deg':sum(v['chronological_angle_deg']<10 for v in crossing),
      'phase_locked_min_chronological_opposite_over_170deg':sum(v['chronological_angle_deg']>170 for v in locked),
      'phase_locked_min_phase_corresponding_opposite_over_170deg':sum(v['phase_corresponding_angle_deg']>170 for v in locked),
      'phase_locked_min_drive_power_opposite_signs':sum(v['drive_power_forward_sign']*v['drive_power_return_sign']==-1 for v in locked),
      'phase_locked_min_energy_difference_positive':sum(v['energy_difference']>0 for v in locked),
      'phase_locked_min_energy_difference_negative':sum(v['energy_difference']<0 for v in locked),
      'asynchronous_chronological_angle':stats(free,'chronological_angle_deg'),
      'phase_locked_chronological_angle':stats(locked,'chronological_angle_deg'),
      'phase_locked_shape_distance':stats(locked,'shape_distance'),
      'phase_locked_energy_difference':stats(locked,'energy_difference'),
      'phase_locked_signed_drive_power_return':stats(locked,'drive_power_return_per_xi'),
      'phase_locked_signed_drive_power_forward':stats(locked,'drive_power_forward_per_xi'),
      'max_source_r_distance_recheck':max_r_distance_diff,
      'max_source_r_chronological_angle_deg_recheck':max_r_angle_diff,
      'max_historical_11D_replay_error':max(a['max_historical_11D_error'] for a in regr),
      'max_integrated_energy_balance_relative_error':max_balance,
      'max_meeting_energy_ledger_absolute_residual':max_ledger_reconcile,
      'max_phase_locked_clock_mismatch_rad':max_phase_error,
      'integration':{'solver':'DOP853','rtol':args.rtol,'atol':args.atol,'max_step':args.max_step,
                     'phase_root_nodes':args.phase_root_nodes},
      'declared_reference':'Chronological tangent R du versus F ds; equal-drive-phase corresponds to s(u)=1-rate*duration*u, so compare R du with -rate*duration*F ds.',
      'provenance':genealogy,
      'limitations':'Orientation and chirality depend on the declared geometric chart/projection and temporal convention. Signed drive power is a term in the chosen mechanical ledger, not an independently measured energy flux. One-coordinate matched roots do not imply a full geometric or material crossing. No unperturbed continuum of inversion-rate/initial-condition variation or universal hysteresis claim.'}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('genuine_11D_integrations','asynchronous_contact_pairs','phase_locked_contact_pairs','projected_2D_crossings_reexamined','phase_locked_one_coordinate_roots','phase_locked_min_drive_power_opposite_signs','max_integrated_energy_balance_relative_error','max_meeting_energy_ledger_absolute_residual')},indent=2))
if __name__=='__main__':main()
