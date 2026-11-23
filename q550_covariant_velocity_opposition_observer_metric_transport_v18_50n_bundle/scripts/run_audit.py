#!/usr/bin/env python3
"""Q550 v18.50n: observer velocity and moving-frame covariance diagnostics.

No new RHS integrations. Authenticates the v18.50m sendback and its nested
v18.50l server sendback; checks four observer constructions, and exhibits
passive moving-coordinate versus genuine metric-change distinctions.
"""
from __future__ import annotations
import argparse, hashlib, io, json, platform, zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
MNAME='q550_resultant_advance_intensity_orientation_rate_v18_50m_bundle'
LNAME='q550_dense_gate_replay_model_gram_metric_v18_50l_bundle'
COMMON='common_parent_c'
GRMS=('model_jet_gram_alpha_0p1','model_jet_gram_alpha_1')
KINDS=('original','autonomous')
EPSILONS=(1e-4,1e-5)


def sha(buf:bytes)->str:return hashlib.sha256(buf).hexdigest()

def authenticate_archive(z,root):
    if z.testzip() is not None:raise RuntimeError('Bad ZIP CRC: '+root)
    sm=json.loads(z.read(root+'/SOURCE_MANIFEST.json'))
    om=json.loads(z.read(root+'/SHA256SUMS_OUTPUT.json'))
    if sm['root']!=root:raise RuntimeError('Wrong source manifest root')
    for name,digest in sm['files'].items():
        if name.startswith('/') or '..' in Path(name).parts:raise RuntimeError('Unsafe source path')
        if sha(z.read(root+'/'+name))!=digest:raise RuntimeError('Source drift: '+name)
    for name,digest in om['file_sha256'].items():
        if sha(z.read(root+'/'+name))!=digest:raise RuntimeError('Result drift: '+name)
    return {'source_count':len(sm['files']),'result_count':len(om['file_sha256']),'version':sm['version']}

def load_parent():
    path=ROOT/'inputs'/(MNAME+'_server_sendback.zip')
    parent_digest=sha(path.read_bytes())
    with zipfile.ZipFile(path) as m:
        m_check=authenticate_archive(m,MNAME)
        lbytes=m.read(MNAME+'/inputs/'+LNAME+'_server_sendback.zip')
        m_summary=pd.read_csv(io.BytesIO(m.read(MNAME+'/results/intensity_gate_summary.csv')))
        mreport=json.loads(m.read(MNAME+'/results/report.json'))
    with zipfile.ZipFile(io.BytesIO(lbytes)) as l:
        l_check=authenticate_archive(l,LNAME)
        ledger=pd.read_csv(io.BytesIO(l.read(LNAME+'/results/dense_gate_vector_ledger.csv')))
        events=pd.read_csv(io.BytesIO(l.read(LNAME+'/results/dense_gate_event_brackets.csv')))
        lreport=json.loads(l.read(LNAME+'/results/report.json'))
    if len(ledger)!=8208 or len(m_summary)!=4:raise RuntimeError('Unexpected parent data counts')
    return ledger,events,lreport,m_summary,mreport,{'parent_m_sha256':parent_digest,'m':m_check,'l':l_check}

def vectors(d):
    return (np.asarray([json.loads(s) for s in d.L_vec],float),np.asarray([json.loads(s) for s in d.T_vec],float))

def features(a,b):
    return np.array([(a[i]*b[j] if i==j else a[i]*b[j]+a[j]*b[i]) for i in range(4) for j in range(i,4)])

def reconstruct_metric(fit,validate,ref_eigenvalues):
    """Recover frozen parent Gram from redundant quadratic scalar measurements.

    Published ledger does not serialize W, but stores L,T, both norms and L.T.
    WARNING: the design matrix is ill-conditioned: independent held-out rows and
    eigenvalue checks are mandatory and W is strictly diagnostic.
    """
    L,T=vectors(fit)
    X=np.concatenate([np.array([features(v,v) for v in L]),np.array([features(v,v) for v in T]),np.array([features(v,w) for v,w in zip(L,T)])])
    y=np.r_[fit.L_norm.to_numpy(float)**2,fit.T_norm.to_numpy(float)**2,fit.LT_dot.to_numpy(float)]
    coeff,*_=np.linalg.lstsq(X,y,rcond=None)
    W=np.zeros((4,4));k=0
    for i in range(4):
        for j in range(i,4):W[i,j]=W[j,i]=coeff[k];k+=1
    ev=np.linalg.eigvalsh(W)
    if ev[0]<=0:raise RuntimeError('Recovered W not SPD')
    if max(abs(ev-np.asarray(ref_eigenvalues)))>2e-5:raise RuntimeError('Gram eigenvalue mismatch')
    Lv,Tv=vectors(validate)
    e=np.array([
        *[v@W@v-x*x for v,x in zip(Lv,validate.L_norm)],
        *[v@W@v-x*x for v,x in zip(Tv,validate.T_norm)],
        *[v@W@w-x for v,w,x in zip(Lv,Tv,validate.LT_dot)]])
    if max(abs(e))>1e-7:raise RuntimeError('Gram metric failed independent-epsilon validation')
    return W,{'normal_matrix_condition':float(np.linalg.cond(X)),
              'max_holdout_quadratic_error':float(max(abs(e))),
              'metric_eigenvalues':ev.tolist(),
              'fit_relative_residual':float(np.linalg.norm(X@coeff-y)/np.linalg.norm(y))}

def angle(v,w,W=None):
    if W is None:W=np.eye(len(v))
    c=float(v@W@w / np.sqrt((v@W@v)*(w@W@w)))
    return float(np.degrees(np.arccos(np.clip(c,-1,1))))

def case_at(frame,xi):
    t=frame.horizon_xi.to_numpy(float)
    L,T=vectors(frame)
    sl=CubicSpline(t,L,axis=0,bc_type='natural')
    st=CubicSpline(t,T,axis=0,bc_type='natural')
    return sl(xi),st(xi),sl(xi,1),st(xi,1)

def whiten(W):
    # np.linalg.cholesky(W)=H with H H^T=W. Therefore B=H^T.
    B=np.linalg.cholesky(W).T
    if np.linalg.norm(B.T@B-W)>1e-10:raise AssertionError('Bad metric square root')
    return B

def comoving(L,T,vL,vT,W):
    B=whiten(W)
    a,b,da,db=B@L,B@T,B@vL,B@vT
    R=a+b;v=da+db;rhat=R/np.linalg.norm(R)
    drhat=(v-(rhat@v)*rhat)/np.linalg.norm(R)
    omega=np.outer(drhat,rhat)-np.outer(rhat,drhat)
    da_co=da-omega@a;db_co=db-omega@b
    transverse=float(np.linalg.norm((da_co+db_co)-rhat*(rhat@(da_co+db_co))))
    if transverse>1e-8:raise AssertionError('R-locked local frame failed')
    return {'frozen_angle_deg':angle(da,db),'co_moving_relative_rate_angle_deg':angle(da_co,db_co),
            'comoving_L_speed':float(np.linalg.norm(da_co)),
            'comoving_T_speed':float(np.linalg.norm(db_co)),
            'resultant_normalized_frame_rotation_per_xi':float(np.linalg.norm(drhat)),
            'transverse_speed_before_frame_correction':float(np.linalg.norm(v-(rhat@v)*rhat)),
            'transverse_after_frame_correction':transverse}

def known_gauge(L,T,vL,vT,W,omega=300.0,plane=(0,2)):
    """At the reference instant Q=I, Q'=omega J; exact transported correction.
    q=Q Bv; q'=Q Bv'+Q' Bv; Dq=q'-omega J q =Q Bv'.
    """
    B=whiten(W);a,b,da,db=B@L,B@T,B@vL,B@vT
    J=np.zeros((4,4));i,j=plane;J[i,j]=-1.;J[j,i]=1.
    qa,qb=a,b;va=da+omega*J@a;vb=db+omega*J@b
    dqa=va-omega*J@qa;dqb=vb-omega*J@qb
    max_abs=float(max(np.max(abs(dqa-da)),np.max(abs(dqb-db))))
    if max_abs>5e-12:raise AssertionError('Known-gauge covariance failed')
    # A nonorthogonal (shearing) coordinate map provides an evolving pullback metric.
    K=np.zeros((4,4));K[0,1]=1;K[2,0]=-.35
    speed=800.
    sa=da+speed*K@a;sb=db+speed*K@b
    ca=sa-speed*K@a;cb=sb-speed*K@b
    shear_error=float(max(np.max(abs(ca-da)),np.max(abs(cb-db))))
    if shear_error>5e-12:raise AssertionError('Shear connection failed')
    # Check nonlocal metric pullback and its connection using exact exp of chosen K.
    from scipy.linalg import expm
    h=2.5e-6;S=expm(h*speed*K)
    Wq=np.linalg.inv(S).T@np.linalg.inv(S) # whitened base metric=I
    transport_error=float(abs((S@a)@Wq@(S@b)-a@b))
    if transport_error>1e-12:raise AssertionError('Pullback metric covariance failed')
    return {'angular_gauge_rate':omega,
            'naive_rotating_angle_deg':angle(va,vb),
            'covariant_rotating_angle_deg':angle(dqa,dqb),
            'rotating_correction_error':max_abs,
            'naive_sheared_angle_deg':angle(sa,sb),
            'covariant_sheared_angle_deg':angle(ca,cb),
            'shear_correction_error':shear_error,
            'finite_pulled_metric_invariance_error':transport_error}

def adversarial_metric(vL,vT):
    # Deliberately response-targeted SPD stress test, NOT a physical observer.
    bis=vL/np.linalg.norm(vL)+vT/np.linalg.norm(vT)
    bis=bis/np.linalg.norm(bis)
    W=np.eye(4)+64*np.outer(bis,bis)
    return float(angle(vL,vT,W))

def main():
    ledger,events,lreport,m_summary,mreport,genealogy=load_parent()
    out=ROOT/'results';out.mkdir(exist_ok=True)
    gram={} ; details=[]
    for kind in KINDS:
        gram[kind]={}
        for metric in GRMS:
            training=ledger[(ledger.kind==kind)&(ledger.metric==metric)&(ledger.epsilon==1e-4)].sort_values('horizon_xi')
            held=ledger[(ledger.kind==kind)&(ledger.metric==metric)&(ledger.epsilon==1e-5)].sort_values('horizon_xi')
            meta=lreport['observer_metric_meta'][kind+'_'+metric]
            gram[kind][metric],r=reconstruct_metric(training,held,meta['metric_eigenvalues'])
            details.append({'kind':kind,'metric':metric,**r})
    summary=[]; gauge_rows=[]; profiles=[]
    for kind in KINDS:
        for eps in EPSILONS:
            d=ledger[(ledger.kind==kind)&(ledger.epsilon==eps)&(ledger.metric==COMMON)].sort_values('horizon_xi')
            raw=ledger[(ledger.kind==kind)&(ledger.epsilon==eps)&(ledger.metric=='raw_coordinate')].sort_values('horizon_xi')
            e=events[(events.kind==kind)&(events.epsilon==eps)&(events.metric==COMMON)]
            if len(e)!=1:raise RuntimeError('Missing parent event')
            xi=float(e.iloc[0].stationary_xi)
            L,T,vL,vT=case_at(d,xi)
            _,_,vrL,vrT=case_at(raw,xi)
            ang0=angle(vL,vT)
            parent=m_summary[(m_summary.kind==kind)&(m_summary.epsilon==eps)].iloc[0]
            if abs(ang0-float(np.degrees(np.arccos(np.clip((np.linalg.norm(vL+vT)**2-np.linalg.norm(vL)**2-np.linalg.norm(vT)**2)/(2*np.linalg.norm(vL)*np.linalg.norm(vT)),-1,1)))))>1e-6:raise RuntimeError('Angle identity failure')
            if abs(np.linalg.norm(vL)-float(parent.L_vector_speed_at_stationary))>2e-5:raise RuntimeError('Parent local speed differs')
            if abs(np.linalg.norm(vT)-float(parent.T_vector_speed_at_stationary))>2e-5:raise RuntimeError('Parent transported speed differs')
            Wset={COMMON:np.eye(4),**gram[kind]}
            for metric,W in Wset.items():
                cm=comoving(L,T,vL,vT,W)
                gau=known_gauge(L,T,vL,vT,W,300.,(0,2))
                gau2=known_gauge(L,T,vL,vT,W,-1000.,(0,2))
                summary.append({'kind':kind,'epsilon':eps,'stationary_xi':xi,'metric':metric,
                                'angle_between_value_contributions_deg':angle(L,T,W),
                                'angle_between_derivatives_deg':angle(vL,vT,W),
                                'derivative_dot':float(vL@W@vT),
                                'L_derivative_speed':float(np.sqrt(vL@W@vL)),
                                'T_derivative_speed':float(np.sqrt(vT@W@vT)),**cm,
                                'gauge_rate_300_naive_angle_deg':gau['naive_rotating_angle_deg'],
                                'gauge_rate_300_covariant_angle_deg':gau['covariant_rotating_angle_deg'],
                                'gauge_rate_minus1000_naive_angle_deg':gau2['naive_rotating_angle_deg'],
                                'gauge_rate_minus1000_covariant_angle_deg':gau2['covariant_rotating_angle_deg'],
                                'max_gauge_restoration_error':max(gau['rotating_correction_error'],gau2['rotating_correction_error'],gau['shear_correction_error']),
                                'max_metric_pullback_error':gau['finite_pulled_metric_invariance_error']})
                gauge_rows.extend([{ 'kind':kind,'epsilon':eps,'metric':metric,'rate':rate,**known_gauge(L,T,vL,vT,W,rate,(0,2))} for rate in (-3000.,-1000.,-300.,0.,300.,1000.,3000.)])
            summary.append({'kind':kind,'epsilon':eps,'stationary_xi':xi,'metric':'raw_coordinate_separate_observable',
                            'angle_between_derivatives_deg':angle(vrL,vrT), 'derivative_dot':float(vrL@vrT),
                            'L_derivative_speed':float(np.linalg.norm(vrL)),'T_derivative_speed':float(np.linalg.norm(vrT))})
            # A deliberately chosen nonphysical SPD counterexample: demonstrate the limits of any universal sign claim.
            if eps==1e-4:
                test_ang=adversarial_metric(vL,vT)
                summary.append({'kind':kind,'epsilon':eps,'stationary_xi':xi,'metric':'adversarial_derivative_bisector_spd_control',
                                'angle_between_derivatives_deg':test_ang,'derivative_dot':None})
            # Samplewise common fixed-metric and local co-rotating derivative angles.
            t=d.horizon_xi.to_numpy(float)
            La,Ta=vectors(d)
            VL=CubicSpline(t,La,axis=0,bc_type='natural')(t,1)
            VT=CubicSpline(t,Ta,axis=0,bc_type='natural')(t,1)
            for j in range(len(t)):
                cm=comoving(La[j],Ta[j],VL[j],VT[j],np.eye(4))
                profiles.append({'kind':kind,'epsilon':eps,'xi':float(t[j]),
                                 'fixed_angle_deg':angle(VL[j],VT[j]),
                                 'co_moving_uncorrected_angle_deg':cm['co_moving_relative_rate_angle_deg'],
                                 'covariant_angle_deg':angle(VL[j],VT[j]),
                                 'frame_rotation_rate_per_xi':cm['resultant_normalized_frame_rotation_per_xi']})
    summary=pd.DataFrame(summary); gauges=pd.DataFrame(gauge_rows); profiles=pd.DataFrame(profiles);fitdiag=pd.DataFrame(details)
    summary.to_csv(out/'observer_velocity_angle_summary.csv',index=False,float_format='%.17g')
    gauges.to_csv(out/'moving_gauge_controls.csv',index=False,float_format='%.17g')
    profiles.to_csv(out/'co_moving_phase_ledger.csv',index=False,float_format='%.17g')
    fitdiag.to_csv(out/'recovered_metric_validation.csv',index=False,float_format='%.17g')
    # Plot 1: per-metric angular opposition under fixed metrics and moving response-locked frame.
    fig,ax=plt.subplots(figsize=(10.8,5.4))
    case=summary[(summary.kind=='original')&(summary.epsilon==1e-4)&(summary.metric.isin([COMMON,*GRMS,'raw_coordinate_separate_observable','adversarial_derivative_bisector_spd_control']))]
    labels=['Common','Gram 0.1','Gram 1','Raw observable','Adversarial SPD']
    order=[COMMON,*GRMS,'raw_coordinate_separate_observable','adversarial_derivative_bisector_spd_control']
    v=[float(case[case.metric==k].angle_between_derivatives_deg.iloc[0]) for k in order]
    ax.bar(labels,v);ax.axhline(90,ls='--',c='0.35',lw=1)
    ax.set(ylabel='Angle between response derivatives (degrees)',title='Q550 v18.50n | Angular opposition depends on observer metric',ylim=(0,190));ax.tick_params(axis='x',rotation=12)
    for j,val in enumerate(v):ax.text(j,val+3,f'{val:.2f}°',ha='center',fontsize=9)
    fig.tight_layout();fig.savefig(out/'velocity_opposition_metric_comparison.png',dpi=145);plt.close(fig)
    # Plot 2: artificial moving frame makes ordinary derivatives gauge dependent.
    fig,ax=plt.subplots(figsize=(10,5.3))
    g=gauges[(gauges.kind=='original')&(gauges.epsilon==1e-4)&(gauges.metric==COMMON)].sort_values('rate')
    ax.plot(g.rate,g.naive_rotating_angle_deg,'o-',label='Ordinary derivative in rotating chart')
    ax.plot(g.rate,g.covariant_rotating_angle_deg,'s--',label='Connection-corrected derivative')
    ax.axhline(90,ls=':',c='0.35');ax.set(xlabel='Artificial chart angular rate (radians per model ξ)',ylabel='Angle (degrees)',title='Passive moving-frame gauge: naive vs covariant velocity opposition');ax.grid(alpha=.18);ax.legend()
    fig.tight_layout();fig.savefig(out/'gauge_covariance_velocity_control.png',dpi=145);plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,5.3))
    for kind in KINDS:
        p=profiles[(profiles.kind==kind)&(profiles.epsilon==1e-4)]
        ax.plot(p.xi,p.fixed_angle_deg,label=kind+' fixed',ls='-')
        ax.plot(p.xi,p.co_moving_uncorrected_angle_deg,label=kind+' co-rotating',ls='--')
    ax.set(xlabel='Evolution offset Δξ',ylabel='Angle between derivative contributions (degrees)',title='Response-locked co-moving observer versus fixed observer')
    ax.grid(alpha=.2);ax.legend(ncol=2,fontsize=8);fig.tight_layout();fig.savefig(out/'response_locked_frame_comparison.png',dpi=145);plt.close(fig)
    key=summary[(summary.kind=='original')&(summary.epsilon==1e-4)&(summary.metric==COMMON)].iloc[0]
    report={'version':'v18.50n','title':'Covariant Velocity Opposition & Observer-Metric Transport Audit',
            'classification':'AUTHENTICATED_POSTPROCESSING_PASSIVE_GAUGE_COVARIANCE_NOT_PHYSICAL_CONNECTION_OR_KINETIC_METRIC',
            'parent':genealogy,'counts':{'parent_l_rows':len(ledger),'angle_case_rows':len(summary),'gauge_control_rows':len(gauges),'phase_rows':len(profiles),'new_physical_integrations':0},
            'primary':{'fixed_derivative_angle_deg':float(key.angle_between_derivatives_deg),
                       'response_locked_uncorrected_derivative_angle_deg':float(key.co_moving_relative_rate_angle_deg),
                       'gauge_rate_300_naive_deg':float(key.gauge_rate_300_naive_angle_deg),
                       'gauge_rate_300_covariant_deg':float(key.gauge_rate_300_covariant_angle_deg)},
            'metric_fit_diagnostics':details,
            'limitations':['This is analysis of the authenticated v18.50l RHS replay from the v18.50m parent, not a new integration.',
                'All angles, norms, and connection terms are attached to declared 4D sensitivities in model ξ.',
                'Gram metrics recovered from redundant published quadratic measurements have an ill-conditioned design; holdout and eigenvalue checks are enforced.',
                'Raw-coordinate observer is a distinct normalized nonlinear observable, not a passive pullback metric of the common chart.',
                'Artificial orthogonal and shear gauges prove covariance of an explicitly chosen passive connection by algebra; this does not identify a material or kinetic connection.',
                'A response-locked rotation-minimizing local frame is chosen, not physically privileged; it removes the resultant transverse component by construction.',
                'The deliberately derivative-targeted SPD negative control is not a candidate physical material metric.',
                'No universal metric-independent directional opposition, polymer analogy, material memory or torsional flip certified.'],
            'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__}}
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print('v18.50n COMPLETED',json.dumps({'parent_verified':genealogy,'rows':len(summary),'main':report['primary'],'metrics_original_1e4':[(k,round(float(summary[(summary.kind=='original')&(summary.epsilon==1e-4)&(summary.metric==k)].angle_between_derivatives_deg.iloc[0]),4)) for k in [COMMON,*GRMS,'raw_coordinate_separate_observable','adversarial_derivative_bisector_spd_control']]},indent=2),flush=True)

if __name__=='__main__':main()
