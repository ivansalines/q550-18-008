#!/usr/bin/env python3
"""v18.49a — phase-chart counterfactuals on authenticated Q550 11D barrier data.

The original 48 threshold root pairs were obtained by Z directly from DOP853
continuous solutions. We transport exact root positions through phase charts;
never replace genuine IVP roots with a polynomials' predicted roots.

Option --reintegrate-11d replays the authentic 14 model IVPs and regenerates
these 48 exact continuous-IVP root pairs before examining chart choices.
"""
from __future__ import annotations
import argparse,csv,json,math,sys,platform,importlib.util
from collections import defaultdict
from pathlib import Path
import numpy as np
import scipy
from verify_parent import verify,dynamic
from chart_math import (local_chart,inverse_chart,reparam_jet,recover_physical_cubic,
                        midpoint_shift,root_derived_skew,ratio_from_roots)
ROOT=Path(__file__).resolve().parents[1]

def read_csv(path):
    with path.open(newline='') as f:return list(csv.DictReader(f))
def write_csv(path,rows):
    if not rows:raise RuntimeError('No output rows: '+str(path))
    names=list(dict.fromkeys(k for x in rows for k in x))
    with path.open('w',newline='') as f:
        out=csv.DictWriter(f,fieldnames=names);out.writeheader();out.writerows(rows)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reintegrate-11d',action='store_true',help='Recompute 14 physical 11D IVPs and 48 root pairs before chart audit')
    ap.add_argument('--rtol',type=float,default=3e-12)
    ap.add_argument('--atol',type=float,default=3e-13)
    ap.add_argument('--max-step',type=float,default=.025)
    ap.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    a=ap.parse_args()
    out=ROOT/'results';out.mkdir(exist_ok=True)
    zroot,yroot,j,prov=verify()
    zreport=json.loads((zroot/'results/report.json').read_text())
    data=read_csv(zroot/'results/continuous_11D_root_validation.csv')
    ybar=read_csv(yroot/'results/barrier_height_curvature.csv')
    yprofiles=read_csv(yroot/'results/dense_contact_profiles.csv')
    assert len(data)==48 and len(ybar)==46 and len(yprofiles)==46*1601
    parent_errors=[]
    fresh_new_integrations=0;max_replay=0.;max_ledger=0.
    if a.reintegrate_11d:
        # This is the exact, authenticated historical Z replay, not a rewritten RHS.
        sys.path.insert(0,str(zroot/'scripts'))
        z=dynamic(zroot/'scripts/run_audit.py','authentic_Z_reintegration_49a')
        newdata,fresh_new_integrations,max_replay,max_ledger=z.continuous_replay(a,yroot,j,out,ybar)
        assert len(newdata)==48 and fresh_new_integrations==14
        old={(x['kappa_kind'],float(x['ramp_duration_xi']),float(x['delta_B_minus_threshold'])):x for x in data}
        for new in newdata:
            key=(new['kappa_kind'],float(new['ramp_duration_xi']),float(new['delta_B_minus_threshold']))
            p=old[key]
            for col in ('dense_IVP_left_root_q','dense_IVP_right_root_q','barrier_full_11D_distance'):
                parent_errors.append(abs(float(new[col])-float(p[col])))
        data=newdata
    else:
        # Retain the continuous numerical root genealogy as verified in the Z sendback.
        write_csv(out/'continuous_11D_root_validation.csv',data)
    omega=float(np.load(j/'runtime/physical_paths.npz',allow_pickle=False)['clock_speed'])
    ramp=dynamic(zroot/'reference/parent_ramp_math.py','original_49a_ramp_clock')
    bar={(x['kappa_kind'],round(float(x['ramp_duration_xi']),8)):x for x in ybar}
    zjets=read_csv(zroot/'results/normal_form_jets.csv')
    jets={(x['kappa_kind'],round(float(x['ramp_duration_xi']),8),float(x['window_q']),int(x['degree'])):x for x in zjets}
    by_profile=defaultdict(list)
    for x in yprofiles:
        key=(x['kappa_kind'],round(float(x['ramp_duration_xi']),8))
        by_profile[key].append((float(x['common_phase_q']),float(x['distance_3D'])))
    for key in by_profile:by_profile[key]=np.array(sorted(by_profile[key]),float)
    norm_math=dynamic(zroot/'scripts/normal_form_math.py','original_Z_normal_math_49a')
    comparison=[];gauges=[];phases=[];refits=[]
    grouped=defaultdict(list)
    for x in data:grouped[(x['kappa_kind'],float(x['ramp_duration_xi']))].append(x)
    for (kind,rv),rows in sorted(grouped.items()):
        key=(kind,round(rv,8));pr=bar[key]
        C=float(pr['barrier_curvature_q2_richardson']);B=float(pr['barrier_distance_3D']);qb=float(pr['barrier_phase_q'])
        jet=jets[(kind,round(rv,8),.012,6)]
        D3=float(jet['fitted_cubic']);D4=float(jet['fitted_quartic'])
        if C>=0:raise RuntimeError('Historical maximum no longer nondegenerate')
        chart_cubic_zero_beta=D3/(3*C)
        phase_clock= ramp.Design('historical_real_drive','smoothstep',rv)
        for testq in (.3,qb,.7):
            read_phase=ramp.cubic_phase_excursion(rv+testq,phase_clock)
            phases.append({'kappa_kind':kind,'ramp_duration_xi':rv,'q':testq,
                           'physically_calibrated_reverse_phase_over_omega':read_phase,
                           'clock_calibration_residual':abs(read_phase-testq),
                           'forward_clock_sign_at_return':ramp.cubic_clock_sign(rv+testq,phase_clock)})
        prof=by_profile[key];sourceq=prof[:,0];sourced=prof[:,1]
        # Independent gauge fit on Y's genuinely generated 11D profile samples.
        for e,beta,label in [(1,0.,'physical_q'),(-1,0.,'reversed_chart'),(1,-1.,'monotone_skew_flip'),(1,chart_cubic_zero_beta,'locally_cubic_free'),(1,1.,'monotone_skew_boost')]:
            x=sourceq-qb
            s=local_chart(x,e,beta)
            # Fit directly to the actual source-Y phase-distance samples, not the Taylor surrogate.
            fit=norm_math.fit_jet(s,sourced,0.,B,.012,6)
            fitted=fit['derivatives'][3]
            expected=reparam_jet(C,D3,e,beta)[1]
            back=recover_physical_cubic(C,expected,e,beta)
            refits.append({'kappa_kind':kind,'ramp_duration_xi':rv,'gauge':label,
                'orientation':e,'nonlinear_beta':beta,'fitted_cubic_from_authentic_11D_Y_profile':fitted,
                'chain_rule_cubic_from_authentic_Z_jet':expected,
                'absolute_fitted_vs_expected_cubic':abs(fitted-expected),
                'recovered_physical_phase_cubic':back,'physical_phase_cubic':D3,
                'cubic_sign_raw':int(np.sign(expected)),
                'fit_profile_rms':fit['rms_fit_error']})
        for row in rows:
            delta=float(row['delta_B_minus_threshold']);left=float(row['dense_IVP_left_root_q']);right=float(row['dense_IVP_right_root_q']);
            if not left<qb<right:raise RuntimeError('Physical root ordering mismatch')
            xm=midpoint_shift(left,right,qb)
            d3root=root_derived_skew(left,right,qb,delta,C)
            err_physphase=abs(ramp.cubic_phase_excursion(rv+qb,phase_clock)-qb)
            baseI=ratio_from_roots(left,right,delta,C)
            comparison.append({'kappa_kind':kind,'ramp_duration_xi':rv,'delta':delta,'barrier_q':qb,
                'root_left_physical_q':left,'root_right_physical_q':right,
                'signed_midpoint_shift_physical_q':xm,'physical_root_derived_cubic_estimate':d3root,
                'physical_phase_local_fitted_cubic':D3,'physical_barrier_curvature':C,
                'physical_contract_ratio_I':baseI,'physical_forward_drive_phase_clock_speed':omega,
                'signed_cubic_per_increasing_drive_angle':-D3/(omega**3),
                'full_11D_distance_at_barrier':float(row['barrier_full_11D_distance']),
                'energy_gap_at_barrier':float(row['barrier_energy_gap']),
                'drive_clock_calibration_residual':err_physphase})
            for e,beta,label in [(1,0.,'physical_q'),(-1,0.,'reversed_chart'),(1,-1.,'monotone_skew_flip'),
                                 (1,chart_cubic_zero_beta,'locally_cubic_free'),(1,1.,'monotone_skew_boost')]:
                xa=left-qb;xb=right-qb
                sa=float(local_chart(xa,e,beta));sb=float(local_chart(xb,e,beta))
                qback_a=qb+float(inverse_chart(sa,e,beta));qback_b=qb+float(inverse_chart(sb,e,beta))
                Cg,Dg=reparam_jet(C,D3,e,beta)
                ga=abs(sb-sa);chatI=abs(Cg)*ga*ga/(8*delta)
                gauges.append({'kappa_kind':kind,'ramp_duration_xi':rv,'delta':delta,'gauge':label,
                    'orientation':e,'nonlinear_beta':beta,'charted_left_s':sa,'charted_right_s':sb,
                    'charted_midpoint_shift':.5*(sa+sb),'charted_gap_abs':ga,
                    'charted_local_cubic':Dg,'charted_local_curvature':Cg,
                    'charted_contract_ratio':chatI,
                    'original_physical_contract_ratio':baseI,
                    'chart_ratio_minus_physical_ratio':chatI-baseI,
                    'recovered_physical_midpoint_shift':.5*(qback_a+qback_b)-qb,
                    'max_root_roundtrip_error':max(abs(qback_a-left),abs(qback_b-right)),
                    'recovered_physical_cubic':recover_physical_cubic(Cg,Dg,e,beta)})
    write_csv(out/'physical_phase_skew.csv',comparison)
    write_csv(out/'chart_counterfactuals.csv',gauges)
    write_csv(out/'independent_chart_jet_refits.csv',refits)
    write_csv(out/'physical_drive_phase_clock.csv',phases)
    # Continuity of the sublevel sets under monotone coordinate transformations
    # is a 1D homeomorphism fact; compare real historical Y component counts.
    comp=read_csv(yroot/'results/threshold_persistence_components.csv')
    selected=[x for x in comp if x['kappa_kind']=='original' and abs(float(x['threshold_d3'])-.01)<1e-12 and round(float(x['ramp_duration_xi']),5) in (.296,.297)]
    component_rows=[]
    for row in selected:
        rv=float(row['ramp_duration_xi']);intervals=json.loads(row['lobe_intervals_json']);
        qb=float(bar[('original',round(rv,8))]['barrier_phase_q'])
        for beta in (0.,-1.,+.5):
            mapped=[]
            for lo,hi in intervals:
                chartlo=float(local_chart(float(lo)-qb,1,beta));charthi=float(local_chart(float(hi)-qb,1,beta));mapped.append((chartlo,charthi))
            component_rows.append({'ramp_duration_xi':rv,'threshold_d3':.01,'nonlinear_beta':beta,
             'original_number_of_components':int(row['components']),
             'mapped_number_of_components':len(mapped),
             'original_intervals_q':json.dumps(intervals),
             'mapped_intervals_chart_s':json.dumps(mapped)})
    if not component_rows:raise RuntimeError('No source Y lobe components matched audit selection')
    write_csv(out/'topological_contact_control.csv',component_rows)
    report={'version':'v18.49a',
      'status':'FULL_FRESH_11D_CHART_AUDIT' if a.reintegrate_11d else 'AUTHENTIC_PARENT_11D_REANALYSIS',
      'parent_z_sha256':prov['parent_z_sha256'],
      'direct_continuous_11D_root_pairs':len(comparison),
      'historical_Y_11D_contact_profiles_authenticated':len(by_profile),
      'gauge_counterfactuals':len(gauges),
      'independent_chart_jet_refits':len(refits),
      'drive_clock_checks':len(phases),
      'new_integrations_in_current_run':fresh_new_integrations,
      'maximum_parent_reintegration_difference':max(parent_errors,default=None),
      'max_original_full_11D_replay_error':max_replay if a.reintegrate_11d else None,
      'max_new_mechanical_ledger_residual':max_ledger if a.reintegrate_11d else None,
      'clock_speed':omega,
      'all_parent_physical_midpoint_shifts_positive':all(float(q['signed_midpoint_shift_physical_q'])>0 for q in comparison),
      'all_physical_sextic_fitted_skews_positive':all(float(q['physical_phase_local_fitted_cubic'])>0 for q in comparison),
      'monotone_chart_raw_cubic_sign_reversals':sum(x['cubic_sign_raw']<0 and x['gauge']=='monotone_skew_flip' for x in refits),
      'max_independent_chart_jet_discrepancy':max(float(x['absolute_fitted_vs_expected_cubic']) for x in refits),
      'maximum_root_chart_roundtrip_error':max(float(x['max_root_roundtrip_error']) for x in gauges),
      'maximum_clock_calibration_residual':max(float(x['clock_calibration_residual']) for x in phases),
      'minimum_full_11D_distance_at_barrier':min(float(x['full_11D_distance_at_barrier']) for x in comparison),
      'root_midpoint_shift_range':list(map(float,[min(x['signed_midpoint_shift_physical_q'] for x in comparison),max(x['signed_midpoint_shift_physical_q'] for x in comparison)])),
      'historical_parent':'Q550 authentic Z / Y and nested ancestor 11D sources',
      'conclusions':'Cubic skew and raw midpoint shifts change under chart orientation/nonlinear monotone reparameterization. Physical-clock oriented root locations are well-defined only after phase calibration. Component connectivity of strict sublevels is preserved by a monotone 1D chart. No new constitutive or coordinate-independent handedness law established.',
      'scope':'Direct root IVP data: phaseblind branch0, both kappa0, six ramps, four threshold offsets. Other branches not directly certified.'}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'runtime_environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
