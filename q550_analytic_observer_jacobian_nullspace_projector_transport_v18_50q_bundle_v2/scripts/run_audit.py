#!/usr/bin/env python3
"""v18.50q: analytic Jacobian of normalized 4D structural-jet observer,
10D nullspace projector, and independent tangent-generator transport.

One authenticated v18.50p sendback is included. The long historical chain is
staged transiently and never packed. All scientific comments are in English.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import io
import json
import platform
import sys
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.integrate import solve_ivp

ROOT=Path(__file__).resolve().parents[1]
P='q550_near_null_tangent_direction_stencil_order_transport_v18_50p_bundle'
O='q550_dynamical_connection_material_metric_attribution_v18_50o_bundle'
PARENT=ROOT/'inputs'/(P+'_server_sendback.zip')

def sha(b):return hashlib.sha256(b).hexdigest()

def authenticate_parent():
    with zipfile.ZipFile(PARENT) as z:
        if z.testzip() is not None:raise RuntimeError('Parent ZIP CRC error')
        sm=json.loads(z.read(P+'/SOURCE_MANIFEST.json'))
        om=json.loads(z.read(P+'/SHA256SUMS_OUTPUT.json'))
        if sm['root']!=P or om['root']!=P:raise RuntimeError('Parent root mismatch')
        for manifest,field in ((sm,'files'),(om,'file_sha256')):
            for name,h in manifest[field].items():
                if sha(z.read(P+'/'+name))!=h:raise RuntimeError('Parent digest error: '+name)
        report=json.loads(z.read(P+'/results/report.json'))
        spec_blob=z.read(P+'/scripts/run_audit.py')
        o_blob=z.read(P+'/inputs/'+O+'_server_sendback.zip')
        spectrum=pd.read_csv(io.BytesIO(z.read(P+'/results/ten_d_stencil_singular_spectrum.csv')))
        tangent=pd.read_csv(io.BytesIO(z.read(P+'/results/weak_direction_tangent_transport.csv')))
    if report['version']!='v18.50p':raise RuntimeError('Parent version mismatch')
    return {'parent_sha256':sha(PARENT.read_bytes()),'source_count':len(sm['files']),
            'output_count':len(om['file_sha256']),'parent_classification':report['classification']}, spec_blob,o_blob,spectrum,tangent

def analytic_structural_observer_jet(f,j,h,weights,seed_scales):
    """Exact chain-rule first derivative using supplied analytic F,J,H tensors.

    F,J,H are the original physical 11D structural RHS jet, not finite differences.
    Observable h4=[F[2],F[6],(J F)[2],(J F)[6]].
    The observer is normalize(diag(1/weights)*h4). Chart coordinate
    z_i=seed_scales_i*(y_i-y_i_ref), hence d/dz_i=(d/dy_i)/seed_scales_i.
    The final clock coordinate y[10] is held fixed as in v18.50p.
    """
    f=np.asarray(f,float);j=np.asarray(j,float);h=np.asarray(h,float)
    w=np.asarray(weights,float);scale=np.asarray(seed_scales,float)
    if f.shape!=(11,) or j.shape!=(11,11) or h.shape!=(11,11,11):raise ValueError('Jet shapes')
    if w.shape!=(4,) or scale.shape!=(10,) or np.any(w<=0) or np.any(scale<=0):raise ValueError('Scales')
    g=j@f
    h4=np.array([f[2],f[6],g[2],g[6]])
    # d/dy_k [(J F)_a] = H[a,j,k] F[j] + J[a,j] J[j,k]
    dh=np.stack((j[2,:10],j[6,:10],
         (np.einsum('jk,j->k',h[2,:,:10],f)+j[2]@j[:,:10]),
         (np.einsum('jk,j->k',h[6,:,:10],f)+j[6]@j[:,:10])))
    raw=h4/w
    n=np.linalg.norm(raw)
    if n<=1e-12:raise ValueError('Undefined normalized observer')
    d=raw/n
    G=(np.eye(4)-np.outer(d,d))@(dh/w[:,None])/(n*scale[None,:])
    return d,G,h4,dh

def projector(B,rtol=1e-9):
    """Orthogonal 10D nullspace projector, full rank-3 row space only."""
    U,s,Vt=np.linalg.svd(B,full_matrices=True)
    rank=int(np.count_nonzero(s>rtol*s[0]))
    K=Vt[rank:,:].T
    P=K@K.T
    return P,K,s,rank

def subspace_diagnostics(A,B):
    """Two orthonormal 10x7 subspace bases; principal angles and projector gap."""
    sv=np.clip(np.linalg.svd(A.T@B,compute_uv=False),0.,1.)
    angles=np.degrees(np.arccos(sv))
    gap=np.linalg.norm(A@A.T-B@B.T,'fro')
    return {'max_angle_deg':float(np.max(angles)),
            'rms_angle_deg':float(np.linalg.norm(angles)/np.sqrt(len(angles))),
            'projector_frobenius_gap':float(gap),
            'max_sin_principal_angle':float(np.max(np.sqrt(np.clip(1-sv**2,0,1))))}

def stage_p(p_script,o_blob,tmp):
    stage=tmp/P
    (stage/'scripts').mkdir(parents=True)
    (stage/'inputs').mkdir(parents=True)
    (stage/'scripts/run_audit.py').write_bytes(p_script)
    (stage/'inputs'/(O+'_server_sendback.zip')).write_bytes(o_blob)
    spec=importlib.util.spec_from_file_location('q550_v18_50q_auth_p',stage/'scripts/run_audit.py')
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    return mod

def stage_model(p,tmp):
    history,o_source,n_blob,oreport=p.verify_parent()
    o=p.stage_o(o_source,n_blob,tmp)
    pdata,ledger,events,lscript,kblob=o.parent_data()
    lmod=o.stage_original_model(lscript,kblob,tmp)
    print('AUTHENTICATED MODEL: staging 10D physical solver',flush=True)
    Experiment,unit,central,drpt,ireport,jreport,kreport,ancestry=lmod.stage_authenticated()
    engine=Experiment(o.make_engine_args())
    droot,_,_=sys.modules['verify_parent_d'].verify()
    creport=json.loads((droot/'runtime/q550_hidden_tangent_conditioning_turning_response_v18_50c_bundle/results/report.json').read_text())
    return o,p,engine,unit,drpt,creport,events

def analyze_branch(o,p,engine,unit,drpt,creport,events,kind,npoints):
    ctx=p.make_context(o,kind,engine,unit,drpt,creport)
    evt=events[(events.kind==kind)&(events.metric=='common_parent_c')&(np.isclose(events.epsilon,1e-4))]
    if len(evt)!=1:raise RuntimeError('Event not uniquely identified')
    parity=float(evt.iloc[0].parity_xi);station=float(evt.iloc[0].stationary_xi)
    x=np.linspace(parity,station,npoints)
    w=np.asarray(drpt['common_metric_scale_4d'],float)
    records=[];basis=[];proj=[];jacobians=[]
    
    for i,xi in enumerate(x):
        t=ctx['event']+xi
        z=np.asarray(ctx['sol'].sol(t),float)
        y=np.r_[z,ctx['theta'](t)]
        f,j,h=engine.jet.structural_jet(y,ctx['kappa0'],engine.params,engine.slope)
        d,B,h4,dh=analytic_structural_observer_jet(f,j,h,w,ctx['scale'])
        P,K,s,rank=projector(B)
        if rank!=3:raise RuntimeError(f'Analytic observer rank not 3: {kind} index {i} -> {rank}')
        # Independent finite-difference comparison, same inherited chart and observer.
        Bfd2=o.numerical_B(ctx['direction'],y,ctx['scale'],2e-6)
        Bfd1=o.numerical_B(ctx['direction'],y,ctx['scale'],1e-6)
        Brich=(4*Bfd1-Bfd2)/3
        relative_fd=np.linalg.norm(B-Bfd1)/max(np.linalg.norm(B),1e-30)
        relative_rich=np.linalg.norm(B-Brich)/max(np.linalg.norm(B),1e-30)
        records.append({'kind':kind,'kappa0':ctx['kappa0'],'xi':xi,'index':i,
                        'analytic_s1':s[0],'analytic_s2':s[1],'analytic_s3':s[2],
                        'analytic_s4':s[3],'rank':rank,'kernel_dimension':10-rank,
                        'observer_unit_defect':abs(float(d@d)-1),
                        'observer_left_null_defect':float(np.linalg.norm(d@B)/np.linalg.norm(B)),
                        'analytic_kernel_defect':float(np.linalg.norm(B@K)/np.linalg.norm(B)),
                        'projector_idempotence':float(np.linalg.norm(P@P-P)),
                        'FD2_rel_error':relative_fd,'Richardson_rel_error':relative_rich,
                        'FD2_s4':np.linalg.svd(Bfd1,compute_uv=False)[-1],
                        'Richardson_s4':np.linalg.svd(Brich,compute_uv=False)[-1]})
        basis.append(K);proj.append(P);jacobians.append(B)

    # Transport the full 10D tangent fundamental operator, not a selected singular vector.
    t0=ctx['event']+parity;t1=ctx['event']+station
    def phi_rhs(t,flat):
        zz=np.asarray(ctx['sol'].sol(t),float)
        J=o.numerical_J(ctx['ode'],t,zz,ctx['scale'],1e-6)
        return (J@flat.reshape(10,10)).ravel()
        
    # --- NUOVO BLOCCO SWEEP LOGARITMICO ---
    print(f"\n[SCALING TEST] Avvio verifica di plateau strutturale vs deriva per {kind}...", flush=True)
    scaling_records = []
    for method in ['DOP853', 'Radau']:
        for exp in range(8, 15):
            test_rtol = 10.0**(-exp)
            test_atol = test_rtol * 1e-1
            print(f" -> {method} | rtol={test_rtol:.1e}")
            
            psol = solve_ivp(
                phi_rhs, (t0, t1), np.eye(10).ravel(),
                method=method, rtol=test_rtol, atol=test_atol,
                max_step=max((t1-t0)/8, 1e-8), dense_output=True
            )
            
            if psol.success:
                Phi_final = np.asarray(psol.sol(t1), float).reshape(10, 10)
                Q_final, _ = np.linalg.qr(Phi_final @ basis[0], mode='reduced')
                gap = subspace_diagnostics(Q_final, basis[-1])
                induced = float(np.linalg.norm(jacobians[-1] @ Q_final, 'fro') / max(np.linalg.norm(jacobians[-1], 'fro'), 1e-30))
                scaling_records.append({
                    'kind': kind, 'method': method, 'rtol': test_rtol, 'atol': test_atol,
                    'max_angle_deg': gap['max_angle_deg'], 'induced_leakage': induced,
                    'evals': psol.nfev
                })
    
    pd.DataFrame(scaling_records).to_csv(f"results/tolerance_scaling_plateau_{kind}.csv", index=False)
    print(f"[SCALING TEST] Salvato in results/tolerance_scaling_plateau_{kind}.csv\n")
    # --- FINE BLOCCO SWEEP ---

    # Esecuzione originale del solver per non rompere il resto del codice (trows, return, ecc.)
    phisol=solve_ivp(phi_rhs,(t0,t1),np.eye(10).ravel(),method='DOP853',rtol=3e-11,atol=3e-12,
                     max_step=max((t1-t0)/8,1e-8),dense_output=True)
    if not phisol.success:raise RuntimeError('10D fundamental matrix integration failed: '+phisol.message)
    trows=[];K0=basis[0];P0=proj[0]
    for i,xi in enumerate(x):
        Phi=np.asarray(phisol.sol(ctx['event']+xi),float).reshape(10,10)
        Q,_=np.linalg.qr(Phi@K0,mode='reduced')
        Pd=Q@Q.T
        gap=subspace_diagnostics(Q,basis[i])
        B=jacobians[i]
        induced=float(np.linalg.norm(B@Q,'fro')/np.linalg.norm(B,'fro'))
        instant=float(np.linalg.norm(B@basis[i],'fro')/np.linalg.norm(B,'fro'))
        trows.append({'kind':kind,'xi':xi,'index':i,**gap,
                      'dynamically_transported_kernel_observer_leakage':induced,
                      'instantaneous_kernel_observer_leakage':instant,
                      'phi_identity_distance':float(np.linalg.norm(Phi-np.eye(10),'fro')),
                      'projector_trace':float(np.trace(proj[i])),
                      'projector_local_change_from_initial':float(np.linalg.norm(proj[i]-P0,'fro'))})
                      
    dynamic_change = float(np.linalg.norm(Pd-P0,'fro')) if 'Pd' in locals() else 0.0
    trows[-1]['dynamic_projector_change_from_initial'] = dynamic_change 

    return records, trows, {'kind':kind,'kappa0':ctx['kappa0'],'xi_start':parity,'xi_end':station,
                        'natural_ivp_nfev':ctx['nfev'],'tangent_fundamental_nfev':phisol.nfev,
                        'natural_integrations':1,'tangent_fundamental_integrations':1,'natural_seed_replays':1}
                      

def make_plots(df,tr,out):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(8,4.5))
    for kind in ('original','autonomous'):
        t=df[df.kind==kind]
        ax.plot(t.xi,t.analytic_s4,'o-',label=f'{kind}: analytic s4')
        ax.plot(t.xi,t.FD2_s4,'--',label=f'{kind}: centered FD s4')
    ax.set(xlabel='Evolution offset Δξ',ylabel='Fourth singular value s4',title='Q550 v18.50q — Structural rank-three observer')
    ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(out/'analytic_rank_vs_stencil.png',dpi=140);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.5))
    for kind in ('original','autonomous'):
        t=tr[tr.kind==kind]
        ax.plot(t.xi,t.max_angle_deg,'o-',label=kind)
    ax.set(xlabel='Evolution offset Δξ',ylabel='Maximum principal angle (degrees)',title='Q550 v18.50q — Transported 7D kernel vs instantaneous kernel')
    ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(out/'kernel_projector_transport.png',dpi=140);plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.5))
    for kind in ('original','autonomous'):
        t=tr[tr.kind==kind]
        ax.plot(t.xi,t.dynamically_transported_kernel_observer_leakage,'o-',label=kind)
    ax.set(xlabel='Evolution offset Δξ',ylabel='Relative projected kernel leakage',title='Q550 v18.50q — Hidden subspace is not automatically invariant')
    ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(out/'transported_kernel_leakage.png',dpi=140);plt.close(fig)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--preflight-only',action='store_true',help='Verify parent and exact normalization rank constraint only')
    ap.add_argument('--points',type=int,default=17)
    a=ap.parse_args()
    if a.points<5:raise RuntimeError('At least 5 sections required')
    out=ROOT/'results';out.mkdir(exist_ok=True)
    info,p_script,o_blob,spectrum,tangent=authenticate_parent()
    # Parent spectrum is evidence; no parent data are altered.
    print('AUTHENTICATED v18.50p SEND-BACK',info,flush=True)
    rows=[];transport=[];replays=[]
    if not a.preflight_only:
        with tempfile.TemporaryDirectory(prefix='q550_50q_',dir=str(ROOT)) as tmp:
            tmp=Path(tmp)
            p=stage_p(p_script,o_blob,tmp)
            o,p,ex,unit,drpt,creport,events=stage_model(p,tmp)
            for kind in ('original','autonomous'):
                print('ANALYTIC JACOBIAN + 10D KERNEL PROJECTOR',kind,flush=True)
                r,t,m=analyze_branch(o,p,ex,unit,drpt,creport,events,kind,a.points)
                rows+=r;transport+=t;replays.append(m)
                print('COMPLETE',kind,'rank',set(x['rank'] for x in r),'max angle',max(v['max_angle_deg'] for v in t),flush=True)
        pd.DataFrame(rows).to_csv(out/'analytic_observer_rank_ledger.csv',index=False,float_format='%.17g')
        pd.DataFrame(transport).to_csv(out/'nullspace_projector_transport_ledger.csv',index=False,float_format='%.17g')
        make_plots(pd.DataFrame(rows),pd.DataFrame(transport),out)
    rep={'version':'v18.50q','title':'Analytic Observer Jacobian & Nullspace Projector Transport Audit',
         'classification':'ANALYTIC_NORMALIZATION_RANK_BOUND_AND_NUMERICAL_10D_PROJECTOR_TRANSPORT_NOT_MATERIAL_CERTIFICATE',
         'parent':info,
         'analytic_rank_identity':'For d=u/||u||, Bd=(I-dd^T)Du/||u||, hence d^T Bd=0 and rank(Bd)<=3; this is exact in real arithmetic wherever u!=0.',
         'chart':'z_i=seed_scale_i * (state_i-state_ref_i); observer derivatives are /seed_scale_i; Euclidean chart only.',
         'counts':{'sample_rows':len(rows),'transport_rows':len(transport)},'replays':replays,
         'numeric':{},
         'limitations':['The exact rank upper bound is a structural consequence of four-vector normalization, not a physical null mode.',
             'Rank exactly three is supported by sampled analytic-jet evaluations, not certified everywhere on a continuous trajectory.',
             'The 7D tangent kernel is a pointwise observer kernel and need not be invariant under the 10D variational flow.',
             'The model tangent generator is evaluated by 2nd-order finite differences of the physical 10D RHS; it is not a certified interval Jacobian.',
             'The observer chart metric is fixed/normalized; there is no derived material kinetic metric.',
             'No material memory, physical flip, torsional holonomy, polymer constitutive identity or global rank proof is claimed.'],
         'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__}}
    if rows:
        r=pd.DataFrame(rows);t=pd.DataFrame(transport)
        rep['numeric']={'rank_counts':r.groupby('kind')['rank'].value_counts().to_dict() if False else
                      {kind:sorted(set(int(v) for v in r[r.kind==kind]['rank'])) for kind in ('original','autonomous')},
                      'analytic_s4_max':float(r.analytic_s4.max()),'analytic_s3_min':float(r.analytic_s3.min()),
                      'left_null_defect_max':float(r.observer_left_null_defect.max()),
                      'analytic_vs_Richardson_rel_max':float(r.Richardson_rel_error.max()),
                      'kernel_projector_idempotence_max':float(r.projector_idempotence.max()),
                      'max_principal_angle_deg':float(t.max_angle_deg.max()),
                      'max_dynamic_kernel_leakage':float(t.dynamically_transported_kernel_observer_leakage.max()),
                      'max_inst_kernel_leakage':float(t.instantaneous_kernel_observer_leakage.max())}
    (out/'report.json').write_text(json.dumps(rep,indent=2)+'\n')
    print('v18.50q COMPLETED',json.dumps(rep['numeric'],indent=2),flush=True)

if __name__=='__main__':main()
