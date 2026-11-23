#!/usr/bin/env python3
"""Q550 v18.48q: continuous near-crossings and phase/energy separation.

Uses genuine ORIGINAL 11D support RHS with forward-time negative drive clock.
Two controlled experimental designs: phase-closed duration T=1/rate, and
fixed-time T=1 (not phase-closed except rate=1).  This separates timing
comparisons from the amount of imposed phase.  No constitutive hysteresis
or physical time-reversal theorem is claimed.
"""
from __future__ import annotations
import argparse,csv,hashlib,importlib.util,json,math,sys
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from verify_parent import verify
from crossing_math import shape,matched_progress_min,free_pair_min,state_differences
ROOT=Path(__file__).resolve().parents[1]
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

def save_csv(file,records):
    if not records:return
    with file.open('w',newline='',encoding='utf8') as w:
        writer=csv.DictWriter(w,fieldnames=list(dict.fromkeys(k for record in records for k in record)));writer.writeheader();writer.writerows(records)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--rtol',type=float,default=3e-12)
    ap.add_argument('--atol',type=float,default=3e-13)
    ap.add_argument('--max-step',type=float,default=.0125)
    ap.add_argument('--output-dir',type=Path,default=ROOT/'results')
    a=ap.parse_args()
    if a.rtol<=0 or a.atol<=0 or a.max_step<=0:raise ValueError('Integration tolerances positive')
    out=a.output_dir;out.mkdir(parents=True,exist_ok=True)
    parent,prov=verify()
    j=parent/'runtime/verified_sources/j/q550_kappa_gauge_covariant_v18_48j_bundle'
    sys.path[:0]=[str(ROOT/'reference'),str(ROOT/'scripts')]
    physical=module(ROOT/'reference/physical_math.py','physical_v1848q')
    audit=module(parent/'reference/test_support_mobius_monodromy_audit.py','audit_v1848q')
    support=module(parent/'reference/test_support_q550_support_ode_interval_residual_pilot_v1.py','support_v1848q')
    p=audit.ModelParameters(gamma_rho=.3)
    original=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    hrep=json.loads((j/'runtime/report_v18_48h.json').read_text())
    slope=float(original['clock_speed'])/(2*math.pi)
    ks={'original':float(hrep['kappa_original']),'autonomous':float(hrep['kappa_autonomous'])}
    xs=np.asarray(original['xi'],float);historical=np.asarray(original['y'],float)
    groups={}
    for i in range(328):
        group=(str(original['families'][i]),int(original['seed_branches'][i]),str(original['kappa_kind'][i]))
        groups.setdefault(group,[]).append(i)
    if len(groups)!=8:raise RuntimeError('8 source trajectories required')
    savedp=np.load(parent/'results/full_11d_protocol_trajectories.npz',allow_pickle=False)
    sample_progress=np.linspace(0.,1.,81)
    rows=[];comparisons=[];balance=[];samples=[];regression=[]
    bestcase=[];total_ivps=0;worst_balance=0.;worst_regression=0.;clock_speed=2*math.pi*slope
    def rhs(y,k,sign):return physical.rhs_from_original(y,k,p,slope,sign,support,audit)
    def solve(tfinal,start,k,sign):
        nonlocal total_ivps,worst_balance
        start15=np.r_[start,np.zeros(4)]
        def f(t,y):return np.r_[rhs(y[:11],k,sign),physical.power_terms(y[:11],k,p,slope,sign)]
        sol=solve_ivp(f,(0.,float(tfinal)),start15,method='DOP853',rtol=a.rtol,atol=a.atol,
                      max_step=a.max_step,dense_output=True)
        total_ivps+=1
        if not sol.success:raise RuntimeError(sol.message)
        delta=float(physical.energy(sol.y[:11,-1],k,p)-physical.energy(sol.y[:11,0],k,p))
        works=sol.y[11:,-1]-sol.y[11:,0]
        error=abs(delta-float(sum(works)))/max(1.,abs(delta),sum(abs(works)))
        worst_balance=max(worst_balance,error)
        if error>1e-7:raise RuntimeError(f'Energy balance residual {error:.3e}')
        def evaluate(u):
            arr=np.asarray(u,float);values=sol.sol(arr*float(tfinal))[:11]
            return values.T if arr.ndim else values
        return sol,evaluate,dict(delta_E=delta,drive_work=float(works[0]),
                                 radial_dissipation=float(works[1]),x_dissipation=float(works[2]),
                                 active_x_work=float(works[3]),energy_balance_relative_residual=error)
    design=[('phase_closed',.5,2.),('phase_closed',1.,1.),('phase_closed',2.,.5),
            ('fixed_duration',.5,1.),('fixed_duration',2.,1.)]
    for (fam,branch,kind),indices in sorted(groups.items()):
        ix=sorted(indices,key=lambda t:xs[t]);hist=historical[ix];k=ks[kind]
        if not np.allclose(xs[ix],np.linspace(3.5,4.5,41),atol=1e-13,rtol=0):
            raise RuntimeError('Original 41-section support mismatch')
        refsol,forward,fwbal=solve(1.,hist[0],k,+1.)
        forward_grid=forward(np.linspace(0.,1.,41))
        referr=float(np.max(np.linalg.norm(forward_grid-hist,axis=1)))
        worst_regression=max(referr,worst_regression)
        if referr>5e-6:raise RuntimeError('Original source replay mismatch '+str(referr))
        old=np.where((savedp['family']==fam)&(savedp['branch']==branch)&
                     (savedp['kappa_kind']==kind)&(savedp['protocol']=='forward_replay'))[0]
        if len(old)!=1:raise RuntimeError('Parent p original forward trajectory absent')
        perror=float(np.max(np.linalg.norm(savedp['state'][old[0]]-forward_grid,axis=1)))
        if perror>5e-8:raise RuntimeError('Parent p forward regression mismatch')
        regression.append(dict(family=fam,branch=branch,kappa_kind=kind,
                               max_authentic_regression=referr,max_p_regression=perror))
        yturn=forward(1.)
        for design_name,rate,duration in design:
            for flip in (False,True):
                seed=yturn.copy()
                if flip:seed[[1,3,5,7,9]]*=-1.
                flip_E=float(physical.energy(seed,k,p)-physical.energy(yturn,k,p))
                sol,reverse,terms=solve(duration,seed,k,-rate)
                clock_offset=float(sol.y[10,-1]-forward(0.)[10])
                if design_name=='phase_closed' and abs(clock_offset)>1e-9:
                    raise RuntimeError('Phase-closed protocol did not close clock')
                if not np.isfinite(sol.y).all():raise RuntimeError('Nonfinite 11D state')
                protocol=f'{design_name}_rate{rate:g}_flip{int(flip)}'
                row=dict(family=fam,branch=branch,kappa_kind=kind,protocol=protocol,
                    design=design_name,reverse_clock_rate_multiplier=rate,
                    actual_reverse_duration_xi=duration,flip_tau_velocities=int(flip),
                    clock_offset_unwrapped=clock_offset,clock_offset_wrapped=float((clock_offset+math.pi)%(2*math.pi)-math.pi),
                    flip_instantaneous_energy_jump=flip_E,**terms)
                # A continuous optimization on the REAL dense 11D IVPs.
                matching=matched_progress_min(forward,reverse,physical.energy,k,p)
                free=free_pair_min(forward,reverse,physical.energy,k,p)
                row['endpoint_shape_distance']=float(np.linalg.norm(shape(reverse(1.))-shape(forward(0.))))
                row['endpoint_energy_difference']=float(physical.energy(reverse(1.),k,p)-physical.energy(forward(0.),k,p))
                for comp in (matching,free):
                    cr=dict(family=fam,branch=branch,kappa_kind=kind,protocol=protocol,
                            design=design_name,rate_multiplier=rate,duration_xi=duration,
                            flip_tau_velocities=int(flip),**comp)
                    comparisons.append(cr)
                    row[comp['comparison']+'_shape_min']=comp['shape_distance']
                    row[comp['comparison']+'_full11D_delta_at_min']=comp['full11D_chart_delta_L2']
                    row[comp['comparison']+'_energy_delta_at_min']=comp['energy_delta']
                rows.append(row)
                balance.append({a:row[a] for a in ['family','branch','kappa_kind','protocol','design',
                          'reverse_clock_rate_multiplier','actual_reverse_duration_xi',
                          'delta_E','drive_work','radial_dissipation','x_dissipation','active_x_work',
                          'energy_balance_relative_residual','flip_instantaneous_energy_jump']})
                rs=reverse(sample_progress);fs=forward(1-sample_progress)
                for u,yst,yref in zip(sample_progress,rs,fs):
                    sm=state_differences(yst,yref,physical.energy,k,p)
                    samples.append(dict(family=fam,branch=branch,kappa_kind=kind,protocol=protocol,
                        design=design_name,rate_multiplier=rate,duration_xi=duration,
                        flip_tau_velocities=int(flip),return_progress=float(u),
                        physical_elapsed_xi=float(u*duration),
                        reference_forward_progress=float(1-u),
                        **{key:sm[key] for key in ['shape_distance','Theta_delta_rad','energy_delta','velocity_delta_L2']}))
                if fam.startswith('phasecov') and branch==0 and kind=='original':
                    bestcase.append((protocol,rs,forward(sample_progress),matching,free))
        print('v18.48q',fam,branch,kind,'source-regression',f'{referr:.3e}',
              'protocols',len(design)*2,flush=True)
    save_csv(out/'sweep_summary.csv',rows)
    save_csv(out/'near_crossing_pairs.csv',comparisons)
    save_csv(out/'energy_balance.csv',balance)
    save_csv(out/'matched_progress_samples.csv',samples)
    save_csv(out/'source_regression.csv',regression)
    savecase=[b for b in bestcase if b[0]=='phase_closed_rate1_flip1']
    if len(savecase)!=1:raise RuntimeError('Missing selected plot case')
    selection=savecase[0]
    # Full continuous histories in this selected case are recomputable from initial data and script.
    np.savez_compressed(out/'selected_case_dense_samples.npz',
        protocol=np.array(selection[0]),fraction=sample_progress,reverse_state=selection[1],
        forward_state=selection[2],
        matched_return_progress=np.array(selection[3]['return_progress']),
        matched_forward_progress=np.array(selection[3]['forward_progress']),
        free_return_progress=np.array(selection[4]['return_progress']),
        free_forward_progress=np.array(selection[4]['forward_progress']))
    def stats(items,key):
        z=np.array([float(v[key]) for v in items]);return {'min':float(z.min()),'median':float(np.median(z)),'max':float(z.max())}
    phaseclosed=[r for r in rows if r['design']=='phase_closed']
    perdesign={}
    for design_name,rate,duration in design:
        sub=[r for r in rows if r['design']==design_name and r['reverse_clock_rate_multiplier']==rate]
        perdesign[f'{design_name}_{rate:g}']={
            'count':len(sub),'endpoint_shape':stats(sub,'endpoint_shape_distance'),
            'matched_min_shape':stats(sub,'progress_matched_shape_min'),
            'free_min_shape':stats(sub,'asynchronous_free_pair_shape_min'),
            'endpoint_energy_difference':stats(sub,'endpoint_energy_difference'),
            'delta_E':stats(sub,'delta_E'),'command_work':stats(sub,'drive_work')}
    report={'version':'v18.48q','title':'Counterflow Near-Crossings & Phase–Energy Separation Audit',
        'original_11D_states':328,'genuine_new_11D_integrations':total_ivps,
        'reference_11D_integrations':8,'counterflow_11D_integrations':len(rows),
        'total_counterflow_samples':len(samples),'comparison_pairs':len(comparisons),
        'phase_closed_count':len(phaseclosed),'fixed_duration_count':len(rows)-len(phaseclosed),
        'clock_speed_original_rad_per_xi':clock_speed,
        'phase_closed_definition':'start Theta at original turnaround, integrate dTheta/dxi=-rate*omega, duration=1/rate',
        'fixed_duration_definition':'same drive speeds at fixed return duration 1 xi; external Theta generally does not close',
        'geometric_comparison':'(logrho1,logrho2,x) only; full11D compares theta1/theta2/Theta modulo 2pi and tau velocities',
        'near_crossing_search':'continuous DOP853 dense-output multi-start numeric refinement; boundaries exclude common turnaround; global optimality is not certified',
        'comparison_modes':['progress_matched','asynchronous_free_pair'],
        'source_regression_max':worst_regression,
        'energy_identity_max_relative_residual':worst_balance,
        'protocol_summary':perdesign,
        'numerical':{'method':'DOP853','rtol':a.rtol,'atol':a.atol,'max_step':a.max_step,
            'rate_multipliers':[.5,1,2],'phase_closed_durations_xi':[2,1,.5],
            'fixed_durations_xi':[1,1], 'pair_multistart_grid':61},
        'provenance':prov,
        'scientific_boundary':'Nonzero position/phase/energy mismatches in driven counterflow do not alone establish thermodynamic irreversibility. Closest 3D projections do not imply intersections of 11D states. Rate and duration are coupled in phase-closed scans; fixed-duration controls decouple duration but do not close the phase. No global minimization certificate.'}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'integrations':total_ivps,'new_11D_counterflows':len(rows),
                      'comparisons':len(comparisons),'energy_residual':worst_balance,
                      'source_regression':worst_regression,
                      'phaseclosed_rate1':perdesign['phase_closed_1']},indent=2))
if __name__=='__main__':main()
