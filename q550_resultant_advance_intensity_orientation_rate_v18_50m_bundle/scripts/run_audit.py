#!/usr/bin/env python3
"""v18.50m: quantify response-vector advance from the authenticated v18.50l sendback.

Strictly a postprocessing and metric-declaration audit: no physical IVP is integrated.
"""
import hashlib
import io
import json
from pathlib import Path
import sys
import zipfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

HERE = Path(__file__).resolve().parents[1]
PARENT_NAME = 'q550_dense_gate_replay_model_gram_metric_v18_50l_bundle_server_sendback.zip'
PARENT_DIR = 'q550_dense_gate_replay_model_gram_metric_v18_50l_bundle/'
CASES = ('original', 'autonomous')
EPS = (1e-4, 1e-5)
COMMON = 'common_parent_c'
METRICS = (COMMON, 'raw_coordinate', 'model_jet_gram_alpha_0p1', 'model_jet_gram_alpha_1')


def sha_bytes(buf):
    return hashlib.sha256(buf).hexdigest()


def read_parent():
    """Read and authenticate the v18.50l parent without extracting its nested runtime."""
    archive = HERE/'inputs'/PARENT_NAME
    with zipfile.ZipFile(archive) as z:
        bad = z.testzip()
        if bad:
            raise RuntimeError('Parent ZIP failed CRC at: '+bad)
        manifest_source = json.loads(z.read(PARENT_DIR+'SOURCE_MANIFEST.json'))
        manifest_out = json.loads(z.read(PARENT_DIR+'SHA256SUMS_OUTPUT.json'))
        for rel, digest in manifest_source['files'].items():
            actual=sha_bytes(z.read(PARENT_DIR+rel))
            if actual != digest:
                raise RuntimeError('Parent immutable source hash mismatch: '+rel)
        for rel, digest in manifest_out['file_sha256'].items():
            actual=sha_bytes(z.read(PARENT_DIR+rel))
            if actual != digest:
                raise RuntimeError('Parent output hash mismatch: '+rel)
        data = pd.read_csv(io.BytesIO(z.read(PARENT_DIR+'results/dense_gate_vector_ledger.csv')))
        events = pd.read_csv(io.BytesIO(z.read(PARENT_DIR+'results/dense_gate_event_brackets.csv')))
        report = json.loads(z.read(PARENT_DIR+'results/report.json'))
    digest=hashlib.file_digest(open(archive,'rb'),'sha256').hexdigest()
    return data, events, report, digest, manifest_source, manifest_out


def vector_frame(frame):
    return (np.array([json.loads(s) for s in frame.L_vec]),
            np.array([json.loads(s) for s in frame.T_vec]))


def cs_eval(t, vals, x, derivative=0):
    return float(CubicSpline(t, np.asarray(vals),bc_type='natural')(x,derivative))


def vector_eval(t, vec, x, derivative=0):
    return np.array([cs_eval(t,vec[:,j],x,derivative) for j in range(vec.shape[1])])


def compute_common(frame, event):
    t=frame.horizon_xi.to_numpy(dtype=float)
    L,T=vector_frame(frame); R=L+T
    norms=np.linalg.norm(R,axis=1)
    if np.max(np.abs(norms-frame.R_norm.to_numpy()))>1e-10:
        raise AssertionError('Parent R_norm disagrees with reconstructed Euclidean resultant')
    parity=float(event.parity_xi); stationary=float(event.stationary_xi)
    if not (t[0]<parity<stationary<t[-1]):
        raise AssertionError('Two events must lie strictly inside the sampled window')
    L0=vector_eval(t,L,parity); L1=vector_eval(t,L,stationary)
    T0=vector_eval(t,T,parity); T1=vector_eval(t,T,stationary)
    R0=L0+T0; R1=L1+T1
    vL=vector_eval(t,L,stationary,1)
    vT=vector_eval(t,T,stationary,1)
    vR=vL+vT
    rhat=R1/np.linalg.norm(R1)
    vr=float(vR@rhat)
    vt=float(np.linalg.norm(vR - vr*rhat))
    speed=float(np.linalg.norm(vR))
    delta=float(stationary-parity)
    ang=float(np.degrees(np.arccos(np.clip((R0@R1)/(np.linalg.norm(R0)*np.linalg.norm(R1)),-1,1))))
    delta_vec=float(np.linalg.norm(R1-R0))
    # Endpoint-adjusted polyline length: includes every sample strictly between events.
    mid=R[(t>parity)&(t<stationary)]
    curve=np.vstack([R0,mid,R1])
    poly=float(np.linalg.norm(np.diff(curve,axis=0),axis=1).sum())
    ang_rel0=float(np.degrees(np.arccos(np.clip(L0@T0/(np.linalg.norm(L0)*np.linalg.norm(T0)),-1,1))))
    ang_rel1=float(np.degrees(np.arccos(np.clip(L1@T1/(np.linalg.norm(L1)*np.linalg.norm(T1)),-1,1))))
    # Independent rate cross check via central slope of sampled vector.
    gradients=np.gradient(R,t,axis=0,edge_order=2)
    fd=np.array([np.interp(stationary,t,gradients[:,j]) for j in range(4)])
    record={
      'kind':str(event.kind),'epsilon':float(event.epsilon),'metric':COMMON,
      'parity_xi':parity,'stationary_xi':stationary,'delay_xi':delta,
      'norm_R_at_parity':float(np.linalg.norm(R0)),
      'norm_R_at_stationary':float(np.linalg.norm(R1)),
      'norm_R_increment':float(np.linalg.norm(R1)-np.linalg.norm(R0)),
      'norm_R_increment_percent':float(100*(np.linalg.norm(R1)/np.linalg.norm(R0)-1)),
      'rate_norm_R_at_stationary':vr,
      'vector_speed_at_stationary':speed,
      'transverse_speed_at_stationary':vt,
      'transverse_speed_fraction':vt/speed,
      'radial_speed_fraction':vr/speed,
      'L_vector_speed_at_stationary':float(np.linalg.norm(vL)),
      'T_vector_speed_at_stationary':float(np.linalg.norm(vT)),
      'vector_displacement_parity_to_peak':delta_vec,
      'polyline_length_parity_to_peak':poly,
      'straightness_ratio':delta_vec/poly,
      'resultant_direction_turn_deg':ang,
      'relative_LT_turn_deg':ang_rel1-ang_rel0,
      'relative_LT_angle_parity_deg':ang_rel0,
      'relative_LT_angle_peak_deg':ang_rel1,
      'rate_crosscheck_gradient_relative':float(np.linalg.norm(vR-fd)/speed),
      'parent_report_rate':float(event.resultant_rate_at_stationary),
      'rate_vs_parent_report_abs':abs(vr-float(event.resultant_rate_at_stationary)),
      'C_at_parity':cs_eval(t,frame.cancellation,parity),
      'C_at_peak':cs_eval(t,frame.cancellation,stationary),
      'b_at_parity':cs_eval(t,frame.b_ratio,parity),
      'b_at_peak':cs_eval(t,frame.b_ratio,stationary),
    }
    return record, (t,L,T,R)


def main():
    df, events, parent_report, parent_hash, srcmanifest, outputmanifest=read_parent()
    assert len(df)==8208 and len(events)==16
    out=HERE/'results';out.mkdir(exist_ok=True)
    records=[]; metric_records=[]; profiles=[]
    for kind in CASES:
        for eps in EPS:
            ref_event=events[(events.kind==kind)&(events.epsilon==eps)&(events.metric==COMMON)]
            assert len(ref_event)==1
            ref_event=ref_event.iloc[0]
            for metric in METRICS:
                d=df[(df.kind==kind)&(df.epsilon==eps)&(df.metric==metric)].sort_values('horizon_xi')
                assert len(d)==513 and d.horizon_xi.is_monotonic_increasing
                t=d.horizon_xi.to_numpy(dtype=float)
                a,b=float(ref_event.parity_xi),float(ref_event.stationary_xi)
                # Identical time anchors for all metrics. Other metrics have no local parity+max.
                metric_records.append({
                  'kind':kind,'epsilon':eps,'metric':metric,
                  'reference_parity_xi':a,'reference_stationary_xi':b,
                  'R_norm_at_reference_parity':cs_eval(t,d.R_norm,a),
                  'R_norm_at_reference_stationary':cs_eval(t,d.R_norm,b),
                  'R_norm_delta_same_anchors':cs_eval(t,d.R_norm,b)-cs_eval(t,d.R_norm,a),
                  'R_norm_rate_same_stationary':cs_eval(t,d.R_norm,b,1),
                  'C_same_stationary':cs_eval(t,d.cancellation,b),
                  'opposing_dot_across_window':bool(np.all(d.LT_dot.to_numpy()<0)),
                })
                if metric!=COMMON: continue
                case,(t,L,T,R)=compute_common(d,ref_event)
                records.append(case)
                # Fine rates are descriptive; only Euclidean common observer makes them interpretable.
                dR=np.gradient(R,t,axis=0,edge_order=2)
                dL=np.gradient(L,t,axis=0,edge_order=2)
                dT=np.gradient(T,t,axis=0,edge_order=2)
                Rnorm=np.linalg.norm(R,axis=1)
                rhat=R/Rnorm[:,None]
                radial=(dR*rhat).sum(axis=1)
                trans=np.linalg.norm(dR-radial[:,None]*rhat,axis=1)
                speed=np.linalg.norm(dR,axis=1)
                for j in range(len(t)):
                    profiles.append({
                      'kind':kind,'epsilon':eps,'xi':t[j],
                      'R_norm':Rnorm[j], 'R_vector_speed':speed[j],
                      'R_radial_speed':radial[j],'R_transverse_speed':trans[j],
                      'L_vector_speed':np.linalg.norm(dL[j]),
                      'T_vector_speed':np.linalg.norm(dT[j]),
                      'C':float(d.cancellation.iloc[j]),
                      'relative_LT_angle_deg':float(d.angle_deg.iloc[j]),
                      'parity_xi':a,'stationary_xi':b,
                    })
    intensity=pd.DataFrame(records)
    metrics=pd.DataFrame(metric_records)
    profile=pd.DataFrame(profiles)
    intensity.to_csv(out/'intensity_gate_summary.csv',index=False,float_format='%.17g')
    metrics.to_csv(out/'metric_same_anchor_rates.csv',index=False,float_format='%.17g')
    profile.to_csv(out/'intensity_phase_ledger.csv',index=False,float_format='%.17g')
    # Render plots without dependency on styling/metadata reproducibility.
    fig,ax=plt.subplots(figsize=(10,5.6))
    for kind in CASES:
        g=profile[(profile.kind==kind)&(profile.epsilon==1e-4)]
        ls='-' if kind=='original' else '--'
        ax.plot(g.xi,g.R_vector_speed,ls,label=f'{kind}: total vector speed')
        ax.plot(g.xi,g.R_transverse_speed,ls,label=f'{kind}: transverse speed')
        ax.plot(g.xi,g.R_radial_speed,ls,label=f'{kind}: norm growth rate')
    ax.set(xlabel='Evolution coordinate Δξ',ylabel='Response-vector rate per Δξ',title='Q550 v18.50m | Speed of resultant and its two components')
    ax.legend(fontsize=8,ncol=2);ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'resultant_intensity_decomposition.png',dpi=160);plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,4.5))
    for kind in CASES:
        g=intensity[(intensity.kind==kind)&(intensity.epsilon==1e-4)].iloc[0]
        axes[0].bar(kind,[g.transverse_speed_fraction*100][0],label='Transverse % of vector speed')
        axes[1].bar(kind,g.resultant_direction_turn_deg,label='Resultant direction turn')
    axes[0].set(ylabel='Transverse speed fraction (%)',title='Direction-change contribution')
    axes[1].set(ylabel='Degrees between event vectors',title='Turn between parity and peak')
    for ax in axes:ax.grid(axis='y',alpha=.15)
    fig.tight_layout();fig.savefig(out/'gate_orientation_intensity.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9.5,5))
    sub=metrics[metrics.epsilon==1e-4]
    for kind in CASES:
        g=sub[sub.kind==kind]
        ax.scatter(g.metric,g.R_norm_rate_same_stationary,label=kind,s=65)
    ax.set(xlabel='Declared observer metric', ylabel='d||R|| / dξ at common-geometry stationary anchor',title='Metric dependence: same event times, different reported intensity')
    ax.tick_params(axis='x',rotation=15);ax.legend();ax.grid(axis='y',alpha=.25)
    fig.tight_layout();fig.savefig(out/'metric_dependency_of_intensity.png',dpi=160);plt.close(fig)
    original=intensity[(intensity.kind=='original')&(intensity.epsilon==1e-4)].iloc[0]
    auto=intensity[(intensity.kind=='autonomous')&(intensity.epsilon==1e-4)].iloc[0]
    report={
      'version':'v18.50m','title':'Resultant Advance Intensity & Orientation-Rate Ledger',
      'classification':'AUTHENTICATED_PARENT_POSTPROCESSING_4D_OBSERVER_SPEED_NOT_PHYSICAL_KINETIC_INTENSITY',
      'parent_zip':PARENT_NAME,'parent_sha256':parent_hash,
      'parent_source_verified':len(srcmanifest['files']),
      'parent_results_verified':len(outputmanifest['file_sha256']),
      'source_parent_cases':int(len(df)),'new_IVPs':0,
      'intensity_cases':len(intensity),'metric_cases':len(metrics),
      'phase_rows':len(profile),
      'original_primary':json.loads(original.to_json()),
      'autonomous_primary':json.loads(auto.to_json()),
      'checks':{
        'all_four_common_cases_positive_radial_growth':bool(np.all(intensity.rate_norm_R_at_stationary>0)),
        'all_four_common_cases_transverse_dominates_radial':bool(np.all(intensity.transverse_speed_at_stationary>intensity.rate_norm_R_at_stationary)),
        'all_16_observer_metric_cases_opposing_dot':bool(metrics.opposing_dot_across_window.all()),
        'max_rate_parent_mismatch':float(intensity.rate_vs_parent_report_abs.max()),
        'max_vector_rate_fd_crosscheck':float(intensity.rate_crosscheck_gradient_relative.max()),
        'eps_relative_spread_speed_original':float(np.ptp(intensity[intensity.kind=='original'].vector_speed_at_stationary)/original.vector_speed_at_stationary),
        'eps_relative_spread_speed_autonomous':float(np.ptp(intensity[intensity.kind=='autonomous'].vector_speed_at_stationary)/auto.vector_speed_at_stationary),
      },
      'constraints':[
        'No new model integration: only authenticated v18.50l tabulated response vectors.',
        'R is a sensitivity response vector, not a position vector or material energy.',
        'Rates are per dimensionless model evolution coordinate Δξ, not seconds.',
        'The numerical 4D speed and direction are in inherited observer normalization; not gauge/metric invariant.',
        'Other metrics use the same reference time anchors, not their own parity or stationary roots.',
        'Cubic-spline event derivatives are numerical estimates, not continuous-root certificates.',
        'Two κ₀ branches use separately prepared natural turning states.',
      ],
    }
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('v18.50m COMPLETED',json.dumps({
      'parent_src_checks':len(srcmanifest['files']),'parent_output_checks':len(outputmanifest['file_sha256']),
      'rows':len(profile),'new_IVPs':0,
      'original_speed':original.vector_speed_at_stationary,
      'original_transverse':original.transverse_speed_at_stationary,
      'original_radial':original.rate_norm_R_at_stationary,
      'original_turn_deg':original.resultant_direction_turn_deg,
      'autonomous_speed':auto.vector_speed_at_stationary,
      'max_rate_check_diff':report['checks']['max_rate_parent_mismatch'],
    },indent=2))
    if report['checks']['max_rate_parent_mismatch']>0.05:
        raise AssertionError('Rate mismatch against authenticated parent exceeds 0.05')
    if report['checks']['max_vector_rate_fd_crosscheck']>0.001:
        raise AssertionError('Finite-difference rate cross-check exceeds 0.1%')

if __name__=='__main__':main()
