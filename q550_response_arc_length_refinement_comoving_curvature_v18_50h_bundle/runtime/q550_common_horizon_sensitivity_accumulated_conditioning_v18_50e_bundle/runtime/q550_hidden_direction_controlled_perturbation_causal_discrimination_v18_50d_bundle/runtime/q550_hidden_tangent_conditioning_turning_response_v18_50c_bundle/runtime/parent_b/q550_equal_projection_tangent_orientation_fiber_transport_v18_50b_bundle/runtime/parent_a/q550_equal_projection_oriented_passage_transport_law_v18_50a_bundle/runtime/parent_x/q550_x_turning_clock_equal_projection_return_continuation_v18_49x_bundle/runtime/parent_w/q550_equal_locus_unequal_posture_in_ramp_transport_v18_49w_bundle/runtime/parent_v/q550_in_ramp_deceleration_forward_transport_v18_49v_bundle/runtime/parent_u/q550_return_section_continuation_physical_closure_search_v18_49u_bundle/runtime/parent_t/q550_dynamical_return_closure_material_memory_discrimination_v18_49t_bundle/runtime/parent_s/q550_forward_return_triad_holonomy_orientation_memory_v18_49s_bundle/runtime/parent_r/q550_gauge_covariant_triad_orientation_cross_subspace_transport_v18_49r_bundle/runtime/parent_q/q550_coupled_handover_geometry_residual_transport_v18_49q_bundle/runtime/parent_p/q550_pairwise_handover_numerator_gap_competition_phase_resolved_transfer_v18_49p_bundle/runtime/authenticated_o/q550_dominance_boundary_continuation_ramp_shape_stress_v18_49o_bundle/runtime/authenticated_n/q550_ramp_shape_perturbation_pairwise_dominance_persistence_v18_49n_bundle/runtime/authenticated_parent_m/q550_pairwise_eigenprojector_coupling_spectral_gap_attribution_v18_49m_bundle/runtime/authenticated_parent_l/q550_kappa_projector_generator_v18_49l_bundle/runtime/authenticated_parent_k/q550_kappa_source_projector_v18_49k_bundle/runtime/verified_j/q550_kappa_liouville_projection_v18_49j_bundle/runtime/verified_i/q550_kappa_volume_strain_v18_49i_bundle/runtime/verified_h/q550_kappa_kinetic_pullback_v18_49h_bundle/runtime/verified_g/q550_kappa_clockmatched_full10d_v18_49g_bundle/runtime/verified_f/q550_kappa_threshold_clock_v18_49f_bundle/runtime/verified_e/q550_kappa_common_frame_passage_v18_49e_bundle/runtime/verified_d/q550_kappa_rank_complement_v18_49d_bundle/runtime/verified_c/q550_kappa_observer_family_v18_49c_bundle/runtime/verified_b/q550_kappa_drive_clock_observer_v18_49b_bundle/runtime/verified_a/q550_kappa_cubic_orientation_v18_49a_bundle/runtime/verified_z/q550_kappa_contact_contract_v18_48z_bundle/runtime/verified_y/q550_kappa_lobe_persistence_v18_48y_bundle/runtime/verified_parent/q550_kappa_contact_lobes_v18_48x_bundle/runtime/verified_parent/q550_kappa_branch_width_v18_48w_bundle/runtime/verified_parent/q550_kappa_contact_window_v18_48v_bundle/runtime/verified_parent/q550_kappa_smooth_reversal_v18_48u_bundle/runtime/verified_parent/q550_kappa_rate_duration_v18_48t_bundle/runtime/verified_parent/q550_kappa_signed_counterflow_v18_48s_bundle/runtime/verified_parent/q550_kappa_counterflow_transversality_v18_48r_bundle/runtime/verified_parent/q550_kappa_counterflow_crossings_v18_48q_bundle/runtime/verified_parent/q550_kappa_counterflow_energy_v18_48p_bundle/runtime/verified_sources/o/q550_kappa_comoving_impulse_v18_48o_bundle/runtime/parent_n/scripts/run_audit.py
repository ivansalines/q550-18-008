#!/usr/bin/env python3
"""v18.48n: physical-history/instantaneous-geometry rhythm, directional readouts.

The true forward observer history was integrated previously (v18.48h).
Reordering its cached snapshots is NOT a physical reverse ODE integration.
All observer/source projections are made in the inherited frozen 10D chart.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,sys,platform
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from verify_parent import verify
from rhythm_math import (unit,projective_angle,projection_loss,lag_correlation,
 circular_control,score_best,reverse_projector_symmetry,directed_loss,cancellation_signals)

def csv_out(filename,rows):
    if not rows:raise ValueError('Empty CSV')
    cols=list(rows[0]);
    if any(list(r)!=cols for r in rows):raise ValueError('CSV columns changed')
    with open(filename,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)

def do_main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-cutoffs',default='1e-6,1e-10')
    parser.add_argument('--cancel-cutoff',type=float,default=1e-2)
    parser.add_argument('--max-lag-steps',type=int,default=6)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results')
    args=parser.parse_args()
    cuts=[float(a) for a in args.source_cutoffs.split(',')]
    if not cuts or any(not 0<a<1 for a in cuts) or not 0<args.cancel_cutoff<1:raise ValueError('Invalid cutoffs')
    if not 0<=args.max_lag_steps<=12:raise ValueError('Lag window must be 0..12')
    out=args.output_dir.resolve();out.mkdir(exist_ok=True,parents=True)
    prov=verify()
    based=ROOT/'runtime/parent_m'
    sys.path.insert(0,str(based/'scripts'))
    sys.path.insert(0,str(based/'reference'))
    from principal_geometry import source_active_subspaces
    from structural_jet import structural_jet,coupling_jet
    from observer_geometry_v18_48k import matrices
    from test_support_mobius_monodromy_audit import ModelParameters
    physical=based/'runtime/parent_k/runtime/parent_j/runtime/physical_paths.npz'
    data=np.load(physical,allow_pickle=False)
    hist=json.loads((based/'runtime/parent_k/runtime/parent_j/runtime/report_v18_48h.json').read_text())
    kappa={'original':float(hist['kappa_original']),'autonomous':float(hist['kappa_autonomous'])}
    clock_speed=float(data['clock_speed']);slope=clock_speed/(2*math.pi)
    scale=np.asarray(data['chart_scale'],float);par=ModelParameters(gamma_rho=.3)
    paths=defaultdict(list)
    for i in range(len(data['xi'])):
        family=str(data['families'][i]);branch=int(data['seed_branches'][i]);kind=str(data['kappa_kind'][i])
        xi=float(data['xi'][i]);y=np.asarray(data['y'][i],float)
        f,_,_=structural_jet(y,kappa[kind],par,slope)
        Hb=structural_jet(y,0.,par,slope)[2]
        Hc=slope*kappa[kind]*coupling_jet(y,par)[2]
        B,C=matrices(Hb,Hc,f,scale)
        g=unit(np.asarray(data['covectors'][i,0,:10],float))
        # The other historical transported 11D covectors are kept in the CSV
        # as controls without interpreting them as material energy measurements.
        controls=[unit(np.asarray(data['covectors'][i,j,:10],float)) for j in (1,2,3,4)]
        paths[(family,branch,kind)].append(dict(xi=xi,index=i,y=y,g=g,controls=controls,B=B,C=C))
    for rr in paths.values():rr.sort(key=lambda r:r['xi'])
    assert len(paths)==8 and all(len(v)==41 for v in paths.values())
    assert all(np.allclose(np.diff([r['xi'] for r in rr]),.025,atol=1e-13) for rr in paths.values())
    state_rows=[];step_rows=[];lag_rows=[];lag_summaries=[];events=[]
    for key,rows in sorted(paths.items()):
        fam,branch,kind=key
        for cutoff in cuts:
            enriched=[]
            for r in rows:
                B,C,g=r['B'],r['C'],r['g']
                src=source_active_subspaces(B,C,cutoff,args.cancel_cutoff)
                U=src['near'];P=U@U.T
                historical_source_alignment_loss=projection_loss(g,src['src']@src['src'].T)
                obs=cancellation_signals(B,C,g)
                controls=[cancellation_signals(B,C,c) for c in r['controls']]
                record=dict(**r,P=P,U=U,source_rank=src['source_rank'],near_rank=src['near_rank'],
                            near_ratio=src['generalized_min'],alignment_loss=projection_loss(g,P),
                            source_alignment_loss=historical_source_alignment_loss,
                            g_activity_sin_logR=controls[0]['log_R'],g_activity_cos_logR=controls[1]['log_R'],
                            g_lie_sin_logR=controls[2]['log_R'],g_lie_cos_logR=controls[3]['log_R'],**obs)
                enriched.append(record)
                state_rows.append(dict(family=fam,branch=branch,kappa=kind,xi=r['xi'],clock_rad=clock_speed*(r['xi']-3.5),
                            source_cutoff=cutoff,cancel_cutoff=args.cancel_cutoff,
                            source_rank=src['source_rank'],near_rank=src['near_rank'],
                            generalized_min=src['generalized_min'],
                            historical_alignment_loss=record['alignment_loss'],
                            historical_source_active_alignment_loss=historical_source_alignment_loss,
                            historical_R=obs['R'],historical_logR=obs['log_R'],
                            historical_source_norm=obs['source_norm'],
                            historical_resultant_over_source=obs['resultant_over_source'],
                            historical_opposition_cosine=obs['opposition_cosine'],
                            historical_source_imbalance=obs['source_imbalance'],
                            historical_coupling_null=obs['coupling_null'],
                            transported_activity_sin_logR=record['g_activity_sin_logR'],
                            transported_activity_cos_logR=record['g_activity_cos_logR'],
                            transported_lie_sin_logR=record['g_lie_sin_logR'],
                            transported_lie_cos_logR=record['g_lie_cos_logR']))
            series=[]
            for i,(a,b) in enumerate(zip(enriched[:-1],enriched[1:])):
                dx=b['xi']-a['xi']
                pf,pb,psym=reverse_projector_symmetry(a['P'],b['P'])
                df,dr=directed_loss(a['g'],b['g'],a['P'],b['P'])
                hist_speed=projective_angle(a['g'],b['g'])/dx
                projector_speed=pf/dx
                same_rank=a['near_rank']==b['near_rank']
                # Signed mismatch: forward & reverse use different *historical*
                # anchored covectors; this is not a physically reversed evolution.
                s=dict(family=fam,branch=branch,kappa=kind,source_cutoff=cutoff,
                      xi_a=a['xi'],xi_b=b['xi'],clock_midrad=clock_speed*((a['xi']+b['xi'])/2-3.5),
                      delta_xi=dx,delta_clock_rad=clock_speed*dx,
                      rank_a=a['near_rank'],rank_b=b['near_rank'],same_rank=same_rank,
                      projector_gap_fro=pf,projector_gap_reversed=pb,projector_reverse_symmetry_abs_error=psym,
                      projector_speed_per_xi=projector_speed,
                      historical_observer_speed_deg_per_xi=hist_speed,
                      source_alignment_loss_a=a['alignment_loss'],source_alignment_loss_b=b['alignment_loss'],
                      forward_frozen_observer_alignment_change=df,
                      backward_frozen_observer_alignment_change=dr,
                      directed_sum=df+dr,directed_difference=df-dr,
                      delta_logR=b['log_R']-a['log_R'],
                      abs_logR_change_speed=abs(b['log_R']-a['log_R'])/dx,
                      signed_logR_change_speed=(b['log_R']-a['log_R'])/dx,
                      delta_observer_vs_subspace_loss=b['alignment_loss']-a['alignment_loss'],
                      change_of_source_imbalance=b['source_imbalance']-a['source_imbalance'],
                      source_is_not_physical_energy=True,
                      reverse_order_is_not_reverse_ODE=True)
                step_rows.append(s);series.append(s)
            assert len(series)==40
            pairs=[('projector_vs_historical_observer_speed','projector_speed_per_xi','historical_observer_speed_deg_per_xi'),
                   ('projector_vs_historical_logR_change','projector_speed_per_xi','abs_logR_change_speed'),
                   ('observer_speed_vs_logR_change','historical_observer_speed_deg_per_xi','abs_logR_change_speed')]
            for name,x_name,y_name in pairs:
                x=np.array([r[x_name] if r['same_rank'] else math.nan for r in series])
                y=np.array([r[y_name] for r in series])
                scan=lag_correlation(x,y,args.max_lag_steps)
                best=score_best(scan)
                control=circular_control(x,y,args.max_lag_steps)
                for z in scan:
                    lag_rows.append(dict(family=fam,branch=branch,kappa=kind,source_cutoff=cutoff,
                         signal_pair=name,lag_steps=z['lag_steps'],lag_xi=z['lag_steps']*.025,
                         lag_clock_rad=z['lag_steps']*.025*clock_speed,
                         compared_pairs=z['pairs'],correlation=z['correlation']))
                lag_summaries.append(dict(family=fam,branch=branch,kappa=kind,source_cutoff=cutoff,
                     signal_pair=name,
                     best_lag_steps=best['lag_steps'] if best else None,
                     best_lag_xi=best['lag_steps']*.025 if best else None,
                     best_correlation=best['correlation'] if best else None,
                     cyclic_shift_exceedance_fraction=control['exceedance_fraction'],
                     valid_cyclic_controls=control['valid_shifts'],
                     interpretation='EXPLORATORY_FINITE_HISTORY_NOT_CAUSAL_DELAY'))
            peak_hist=max(enriched,key=lambda r:r['R'] if not r['coupling_null'] else -math.inf)
            peak_proj=max(series,key=lambda r:r['projector_speed_per_xi'])
            peak_observer=max(series,key=lambda r:r['historical_observer_speed_deg_per_xi'])
            events.append(dict(family=fam,branch=branch,kappa=kind,source_cutoff=cutoff,
                  max_historical_R=peak_hist['R'],historical_peak_xi=peak_hist['xi'],
                  max_projector_speed=peak_proj['projector_speed_per_xi'],
                  projector_speed_peak_xi_mid=(peak_proj['xi_a']+peak_proj['xi_b'])/2,
                  max_historical_observer_speed=peak_observer['historical_observer_speed_deg_per_xi'],
                  historical_observer_speed_peak_xi_mid=(peak_observer['xi_a']+peak_observer['xi_b'])/2,
                  projector_minus_historical_peak_xi=(peak_proj['xi_a']+peak_proj['xi_b'])/2-peak_hist['xi'],
                  historical_speed_minus_historical_peak_xi=(peak_observer['xi_a']+peak_observer['xi_b'])/2-peak_hist['xi']))
            print(f'v18.48n {fam} branch {branch} {kind} cutoff {cutoff:g}: '
                  f'historical Rmax {peak_hist["R"]:.6g} at {peak_hist["xi"]:.3f}, '
                  f'projector pace max {peak_proj["projector_speed_per_xi"]:.6g}',flush=True)
    # Replay regression to signed-parent per-state records, not just ZIP hashes.
    parent_atlas={}
    with (based/'results/subspace_atlas.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            if float(row['cancel_cutoff'])==args.cancel_cutoff and float(row['source_cutoff']) in cuts:
                parent_atlas[(row['family'],int(row['branch']),row['kappa'],float(row['xi']),float(row['source_cutoff']))]=row
    max_parent_sigma_rel=0.0
    for row in state_rows:
        key=(row['family'],row['branch'],row['kappa'],row['xi'],row['source_cutoff'])
        saved=parent_atlas.get(key)
        if saved is None:raise RuntimeError('Missing parent atlas row '+str(key))
        if row['source_rank']!=int(saved['source_rank']) or row['near_rank']!=int(saved['cancellation_rank']):
            raise RuntimeError('Disagreement with v18.48m rank ledger '+str(key))
        v=float(saved['generalized_sigma_min'])
        discrepancy=abs(row['generalized_min']-v)/max(abs(v),1e-300)
        max_parent_sigma_rel=max(max_parent_sigma_rel,discrepancy)
    if max_parent_sigma_rel>1e-10:raise RuntimeError('v18.48m generalized-value regression')
    parent_R={}
    with (based/'runtime/parent_k/results/observer_crest_atlas.csv').open(newline='') as f:
        for row in csv.DictReader(f):
            parent_R[(row['family'],int(row['branch']),row['kappa'],float(row['xi']))]=float(row['R'])
    max_parent_R_rel=0.0
    for row in state_rows:
        key=(row['family'],row['branch'],row['kappa'],row['xi'])
        if key not in parent_R:raise RuntimeError('Missing original v18.48k observer value')
        v=parent_R[key];discrepancy=abs(row['historical_R']-v)/max(abs(v),1e-300)
        max_parent_R_rel=max(max_parent_R_rel,discrepancy)
    if max_parent_R_rel>1e-10:raise RuntimeError('v18.48k historical observer regression')
    csv_out(out/'rhythm_states.csv',state_rows)
    csv_out(out/'rhythm_steps.csv',step_rows)
    csv_out(out/'lag_correlations.csv',lag_rows)
    csv_out(out/'lag_summary.csv',lag_summaries)
    csv_out(out/'rhythm_events.csv',events)
    source_cut=1e-6
    s0=[r for r in step_rows if r['source_cutoff']==source_cut]
    all_sym_err=max(x['projector_reverse_symmetry_abs_error'] for x in step_rows)
    rep=dict(version='v18.48n',title='Forward/Backward Transport & Phase-Lag Audit',
             classification='AUTHENTICATED_HISTORY_VS_INSTANTANEOUS_GEOMETRY_RHYTHM_DIAGNOSTIC',
             original_physical_states=328,original_integrated_trajectories=8,
             cached_sections_per_trajectory=41,new_original_Q550_integrations=0,
             source_cutoffs=cuts,cancellation_cutoff=args.cancel_cutoff,
             lag_window_steps=args.max_lag_steps,section_step_xi=.025,clock_speed_rad_per_xi=clock_speed,
             total_phase_clock_rad=clock_speed,
             source_sha256=hashlib.sha256(physical.read_bytes()).hexdigest(),provenance=prov,
             output_records={'states':len(state_rows),'steps':len(step_rows),'lag_scans':len(lag_rows),
                             'lag_summary':len(lag_summaries),'events':len(events)},
             max_snapshot_reversal_projector_distance_error=all_sym_err,
             max_relative_regression_error_vs_v18_48m_generalized_sigma=max_parent_sigma_rel,
             max_relative_regression_error_vs_v18_48k_historical_R=max_parent_R_rel,
             reference_source_cutoff_1e_6=dict(
                comparisons=len(s0),
                median_projector_pace_per_xi=float(np.median([r['projector_speed_per_xi'] for r in s0])),
                median_observer_angular_pace_deg_per_xi=float(np.median([r['historical_observer_speed_deg_per_xi'] for r in s0])),
                median_directed_frozen_alignment_sum=float(np.median([r['directed_sum'] for r in s0])),
                median_historical_near_plane_alignment_loss=float(np.median([r['historical_alignment_loss'] for r in state_rows if r['source_cutoff']==1e-6])),
                median_historical_source_active_alignment_loss=float(np.median([r['historical_source_active_alignment_loss'] for r in state_rows if r['source_cutoff']==1e-6])),
                maximum_absolute_directed_frozen_alignment_sum=float(max(abs(r['directed_sum']) for r in s0)),
                ranks_different_steps=sum(not r['same_rank'] for r in s0)),
             lags_for_reference_source_cutoff=[r for r in lag_summaries if r['source_cutoff']==1e-6],
             scientific_boundaries=[
                'Xi and lifted Theta are model support/phase coordinates; no seconds are inferred.',
                'All numerical geometric angles are defined in one frozen normalized 10D covector chart.',
                'Historical covectors come from genuine forward cotangent integrations (v18.48h).',
                'Backward quantities only reread the cached states in reverse order: NO reverse physical IVP and NO inverse adjoint was propagated.',
                'The Frobenius projector distance is symmetric under reversing snapshot order, exactly; it cannot by itself diagnose time-reversal breaking.',
                'Directional observer anchoring can be asymmetric because the two cached historical observers differ; not a physical anti-flow energy cost.',
                'At source cutoff 1e-6 the historical observer is almost orthogonal to the selected near-null plane; small directed alignment costs are intrinsically low-sensitivity and should NOT be read as a strong physical reciprocity test.',
                'B and C are projected Hessian kernel contributions; their norms are not a verified physical energy or work flux.',
                'Lag maxima scan multiple shifts on 40 short section intervals. Cyclic-shift controls are descriptive and do not establish causal delays.',
                'No exact inter-subspace intersections, hysteresis-law theorem, dissipation or new material torsion certified.'])
    (out/'report.json').write_text(json.dumps(rep,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:rep[k] for k in ('version','output_records','max_snapshot_reversal_projector_distance_error',
                        'reference_source_cutoff_1e_6')},indent=2))
if __name__=='__main__':do_main()
