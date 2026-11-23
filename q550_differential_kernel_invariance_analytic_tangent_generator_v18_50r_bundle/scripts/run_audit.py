#!/usr/bin/env python3
"""Q550 v18.50r: differential 10D kernel invariance, using an analytic tangent generator.

The authentic q sendback supplies the independent structural-jet observer and
original solver. The generator J_10 is the top-left 10x10 block of the
analytic 11D structural Jacobian in the inherited diagonal chart. The imposed
clock replaces only the eleventh RHS component, so it does not change that
10x10 block. This equality is checked against the driven RHS finite difference.

B_dot involves a derivative of the observer Hessian and therefore uses a
fourth-order temporal stencil; it is NOT an analytic third-derivative jet.
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

ROOT=Path(__file__).resolve().parents[1]
Q='q550_analytic_observer_jacobian_nullspace_projector_transport_v18_50q_bundle'
P='q550_near_null_tangent_direction_stencil_order_transport_v18_50p_bundle'
QP=ROOT/'inputs'/(Q+'_server_sendback.zip')


def sha(data): return hashlib.sha256(data).hexdigest()


def authenticate_q():
    with zipfile.ZipFile(QP) as z:
        bad=z.testzip()
        if bad is not None:raise RuntimeError('Parent q ZIP CRC failure: '+bad)
        sm=json.loads(z.read(Q+'/SOURCE_MANIFEST.json'))
        om=json.loads(z.read(Q+'/SHA256SUMS_OUTPUT.json'))
        if sm['root']!=Q or om['root']!=Q:raise RuntimeError('Parent root mismatch')
        for manifest,key in [(sm,'files'),(om,'file_sha256')]:
            for rel,digest in manifest[key].items():
                if sha(z.read(Q+'/'+rel))!=digest:raise RuntimeError('Parent q digest mismatch: '+rel)
        script=z.read(Q+'/scripts/run_audit.py')
        p_blob=z.read(Q+'/inputs/'+P+'_server_sendback.zip')
        report=json.loads(z.read(Q+'/results/report.json'))
        tr=pd.read_csv(io.BytesIO(z.read(Q+'/results/nullspace_projector_transport_ledger.csv')))
    if report['version']!='v18.50q' or sorted(report['numeric']['rank_counts']['original'])!=[3]:
        raise RuntimeError('Unexpected parent q rank classification')
    return {'q_sha256':sha(QP.read_bytes()),'source_files':len(sm['files']),
            'output_files':len(om['file_sha256']),'classification':report['classification']},script,p_blob,report,tr


def stage_q(tmp,q_script,p_blob):
    stage=tmp/Q
    (stage/'scripts').mkdir(parents=True)
    (stage/'inputs').mkdir(parents=True)
    (stage/'scripts/run_audit.py').write_bytes(q_script)
    (stage/'inputs'/(P+'_server_sendback.zip')).write_bytes(p_blob)
    spec=importlib.util.spec_from_file_location('q550_v18_50r_authenticated_q',stage/'scripts/run_audit.py')
    mod=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=mod
    spec.loader.exec_module(mod)
    return mod


def chart_analytic_generator(physical_jet_j,chart_scale):
    """Original state -> chart z_i=s_i(y_i-y_ref_i), clock held external."""
    j=np.asarray(physical_jet_j,float);s=np.asarray(chart_scale,float)
    if j.shape!=(11,11) or s.shape!=(10,) or np.any(s<=0):
        raise ValueError('Invalid analytic 11D Jacobian or chart scale')
    return (s[:,None]*j[:10,:10])/s[None,:]


def null_projector(B,rtol=1e-9):
    """Rank-three instantaneous orthogonal projector and stable pseudoinverse."""
    U,s,Vh=np.linalg.svd(B,full_matrices=True)
    rank=int(np.count_nonzero(s>rtol*s[0]))
    if rank!=3:raise RuntimeError(f'Expected rank 3, found {rank}')
    V=Vh[:rank,:].T
    P=np.eye(10)-V@V.T
    # Moore-Penrose inverse for positive singular values, not for the structurally zero fourth mode.
    Bplus=V@np.diag(1./s[:rank])@U[:,:rank].T
    return P,Bplus,s


def projector_derivative(B,Bdot,rtol=1e-9):
    """Exact constant-rank differential identity for the orthogonal kernel projector."""
    P,Bplus,s=null_projector(B,rtol)
    cross=Bplus@Bdot@P
    Pdot=-(cross+cross.T)
    return P,Pdot,Bplus,s


def kernel_defect(B,Bdot,J):
    """Source, variational term, total defect, and corrected projector generator."""
    P,Pdot,Bplus,s=projector_derivative(B,Bdot)
    Iminus=np.eye(10)-P
    shape=Bdot@P
    tangent=B@J@P
    D=shape+tangent
    transport=Iminus@J@P
    Pdot_flow=transport+transport.T
    discrepancy=Pdot-Pdot_flow
    lifted=Bplus@D
    # The following is exact for constant-rank B with the Euclidean chart projector:
    # discrepancy = -(lifted + lifted.T).
    proof=np.linalg.norm(discrepancy+lifted+lifted.T,'fro')
    source_identity=np.linalg.norm(B@discrepancy+D,'fro')
    return {'P':P,'Pdot':Pdot,'Bplus':Bplus,'s':s,'D':D,'shape':shape,'tangent':tangent,
            'Pdot_flow':Pdot_flow,'discrepancy':discrepancy,'lifted':lifted,
            'identity_residual':proof,'B_defect_identity_residual':source_identity}


def fivepoint_derivative(values,h):
    """Fourth-order derivative from [f(-2h),f(-h),f(+h),f(+2h)]."""
    m2,m1,p1,p2=values
    return (m2-8*m1+8*p1-p2)/(12*h)


def observer_at(q,engine,ctx,t,common_scale):
    z=np.asarray(ctx['sol'].sol(t),float)
    y=np.r_[z,ctx['theta'](t)]
    f,j,h=engine.jet.structural_jet(y,ctx['kappa0'],engine.params,engine.slope)
    d,B,_,_=q.analytic_structural_observer_jet(f,j,h,common_scale,ctx['scale'])
    return d,B,j,z,y


def time_differential(q,engine,ctx,t,common_scale,dt,with_projectors=False):
    B_list=[];P_list=[]
    for shift in (-2,-1,1,2):
        _,B,_,_,_=observer_at(q,engine,ctx,t+shift*dt,common_scale)
        B_list.append(B)
        if with_projectors:
            P,_,_=null_projector(B)
            P_list.append(P)
    return (fivepoint_derivative(B_list,dt),
            fivepoint_derivative(P_list,dt) if with_projectors else None)


def run_branch(q,o,p,engine,unit,drpt,creport,events,kind,points,dt1,dt2,old):
    ctx=p.make_context(o,kind,engine,unit,drpt,creport)
    ev=events[(events.kind==kind)&(events.metric=='common_parent_c')&np.isclose(events.epsilon,1e-4)]
    if len(ev)!=1:raise RuntimeError('Missing unique 50l inherited gate events')
    a,b=float(ev.iloc[0].parity_xi),float(ev.iloc[0].stationary_xi)
    ts=np.linspace(a,b,points)
    common_scale=np.asarray(drpt['common_metric_scale_4d'],float)
    rows=[];valid=[]
    for k,xi in enumerate(ts):
        t=ctx['event']+xi
        _,B,j,z,y=observer_at(q,engine,ctx,t,common_scale)
        J=chart_analytic_generator(j,ctx['scale'])
        Bdot1,Pdotfd=time_differential(q,engine,ctx,t,common_scale,dt1,with_projectors=True)
        Bdot2,_=time_differential(q,engine,ctx,t,common_scale,dt2)
        r=kernel_defect(B,Bdot1,J)
        v1=np.linalg.norm(r['shape'],'fro');v2=np.linalg.norm(r['tangent'],'fro')
        v=np.linalg.norm(r['D'],'fro')
        E=r['discrepancy'];lift=r['lifted']
        # Induced tangent vector angle rates: principal singular values of the off-block mismatch.
        sv=np.linalg.svd(lift,compute_uv=False)
        J_num=o.numerical_J(ctx['ode'],t,z,ctx['scale'],1e-6) if k in (0,points//2,points-1) else None
        j_rel=float(np.linalg.norm(J-J_num,'fro')/max(1,np.linalg.norm(J,'fro'))) if J_num is not None else np.nan
        j_max=float(np.max(np.abs(J-J_num))) if J_num is not None else np.nan
        # Independent check against true RHS first ten components (clock-controlled):
        f11,_,_=engine.jet.structural_jet(y,ctx['kappa0'],engine.params,engine.slope)
        rhs=ctx['ode'](t,z)
        f_rel=float(np.linalg.norm(f11[:10]-rhs)/max(1,np.linalg.norm(rhs)))
        cos=float(np.sum(r['shape']*r['tangent'])/max(v1*v2,1e-300))
        rrow={'kind':kind,'kappa0':float(ctx['kappa0']),'index':k,'xi':float(xi),
            'rank':3,'kernel_dimension':7,'singular_s3':float(r['s'][2]),
            'singular_s4':float(r['s'][3]),'tangent_J_analytic_norm':float(np.linalg.norm(J,'fro')),
            'relative_analytic_vs_fd_J':j_rel,'max_abs_analytic_vs_fd_J':j_max,
            'relative_analytic_vs_driven_RHS':f_rel,
            'Bdot_norm':float(np.linalg.norm(Bdot1,'fro')),
            'Bdot_refinement_relative':float(np.linalg.norm(Bdot1-Bdot2,'fro')/max(1,np.linalg.norm(Bdot2,'fro'))),
            'shape_term_norm':float(v1),'tangent_term_norm':float(v2),
            'shape_tangent_cos':cos,
            'kernel_invariance_defect_norm':float(v),
            'kernel_invariance_defect_relative_to_B':float(v/max(np.linalg.norm(B,'fro'),1e-300)),
            'cancellation_fraction':float(1-v/max(v1+v2,1e-300)),
            'projector_actual_rate_norm':float(np.linalg.norm(r['Pdot'],'fro')),
            'projector_dynamical_rate_norm':float(np.linalg.norm(r['Pdot_flow'],'fro')),
            'projector_differential_gap_norm':float(np.linalg.norm(E,'fro')),
            'projector_differential_gap_relative':float(np.linalg.norm(E,'fro')/max(np.linalg.norm(r['Pdot'],'fro'),np.linalg.norm(r['Pdot_flow'],'fro'),1e-300)),
            'max_lifted_principal_rate_rad_per_xi':float(sv[0]),
            'projector_rate_fd_relative_error':float(np.linalg.norm(r['Pdot']-Pdotfd,'fro')/max(1,np.linalg.norm(r['Pdot'],'fro'))),
            'projector_identity_rel_residual':float(r['identity_residual']/max(1,np.linalg.norm(E,'fro'))),
            'B_projector_defect_rel_residual':float(r['B_defect_identity_residual']/max(1,np.linalg.norm(r['D'],'fro'))),
            'orthogonal_projector_identity':float(np.linalg.norm(r['P']@r['P']-r['P'],'fro'))}
        if not np.isfinite(list(rrow.values())[4:]).all():
            # NaN is permitted only in J FD comparison at unselected intermediate sections.
            if any(not np.isfinite(x) for key,x in rrow.items() if key not in ('relative_analytic_vs_fd_J','max_abs_analytic_vs_fd_J') and isinstance(x,(int,float))):
                raise RuntimeError('Nonfinite audit value')
        rows.append(rrow)
        if J_num is not None:valid.append({'kind':kind,'xi':xi,'j_rel':j_rel,'j_max':j_max,'rhs_rel':f_rel})
    # Explicit comparison of the cumulative endpoint mismatch observed in the authentic q sendback.
    inherited=old[old.kind==kind].sort_values('xi')
    last=inherited.iloc[-1]
    comparison={'kind':kind,'kappa0':float(ctx['kappa0']),
        'parent_endpoint_max_principal_angle_deg':float(last.max_angle_deg),
        'parent_endpoint_projector_frobenius_gap':float(last.projector_frobenius_gap),
        'q_span_delta_xi':b-a,
        'r_initial_principal_rate_rad_per_xi':rows[0]['max_lifted_principal_rate_rad_per_xi'],
        'r_initial_linear_angle_prediction_deg':float(rows[0]['max_lifted_principal_rate_rad_per_xi']*(b-a)*180/np.pi),
        'r_interval_max_defect_norm':max(v['kernel_invariance_defect_norm'] for v in rows),
        'r_max_generator_relative_difference':max(v['j_rel'] for v in valid),
        'model_natural_nfev':int(ctx['nfev'])}
    return rows,comparison


def make_figures(df,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    for fname,key,ylabel,title in [
       ('kernel_source_competition.png',('shape_term_norm','tangent_term_norm','kernel_invariance_defect_norm'),'Frobenius rate / ξ','Observer variation and tangent transport contributions'),
       ('kernel_projector_rate_balance.png',('projector_actual_rate_norm','projector_dynamical_rate_norm','projector_differential_gap_norm'),'Frobenius rate / ξ','Instantaneous vs dynamically induced 7D projector rates')]:
        fig,ax=plt.subplots(figsize=(9.2,4.8))
        for kind,color in [('original','tab:blue'),('autonomous','tab:orange')]:
            rows=df[df.kind==kind]
            for col,style in zip(key,['-','--',':']):
                ax.plot(rows.xi,rows[col],style,color=color,label=kind+' '+col)
        ax.set(xlabel='Evolution offset Δξ',ylabel=ylabel,title='Q550 v18.50r — '+title)
        ax.grid(alpha=.25);ax.legend(fontsize=7,ncol=2);fig.tight_layout();fig.savefig(output/fname,dpi=140);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9.2,4.8))
    for kind in ['original','autonomous']:
        d=df[df.kind==kind]
        ax.plot(d.xi,d.Bdot_refinement_relative,'o-',label=kind+' Bdot refinement')
        ax.plot(d.xi,d.projector_rate_fd_relative_error,'--',label=kind+' Pdot identity vs stencil')
    ax.set(xlabel='Evolution offset Δξ',ylabel='Relative error',title='Q550 v18.50r — Temporal derivative controls')
    ax.grid(alpha=.25);ax.legend(fontsize=8);fig.tight_layout();fig.savefig(output/'temporal_derivative_stability.png',dpi=140);plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--preflight-only',action='store_true',help='Verify parent q manifest and algebra; no model replay or results overwrite')
    parser.add_argument('--points',type=int,default=17)
    parser.add_argument('--dt',type=float,default=5e-7)
    parser.add_argument('--dt-refined',type=float,default=2.5e-7)
    args=parser.parse_args()
    if args.points<5 or args.dt<=0 or args.dt_refined<=0 or args.dt_refined>=args.dt:
        raise ValueError('Invalid points or temporal steps')
    parent,qscript,pblob,prpt,pt=authenticate_q()
    print('AUTHENTICATED q SEND-BACK',parent,flush=True)
    print('EXACT IDENTITIES: B P=0; Pdot=-Bplus Bdot P -transpose; kernel drift=(Bdot+B J)P',flush=True)
    if args.preflight_only:return
    rows=[];compare=[]
    # The complete source archive is only staged temporarily and never returned in the sendback.
    with tempfile.TemporaryDirectory(prefix='q550_v18_50r_runtime_',dir=str(ROOT)) as tmp:
        tmp=Path(tmp)
        q=stage_q(tmp,qscript,pblob)
        p=q.stage_p(*q.authenticate_parent()[1:3],tmp)
        o,p,engine,unit,drpt,creport,events=q.stage_model(p,tmp)
        for kind in ('original','autonomous'):
            print('REPLAY v18.50r',kind,flush=True)
            data,summary=run_branch(q,o,p,engine,unit,drpt,creport,events,kind,args.points,args.dt,args.dt_refined,pt)
            rows.extend(data);compare.append(summary)
            print('BRANCH COMPLETE',kind,'max defect',summary['r_interval_max_defect_norm'],flush=True)
    out=ROOT/'results';out.mkdir(exist_ok=True)
    frame=pd.DataFrame(rows)
    frame.to_csv(out/'differential_kernel_invariance_ledger.csv',index=False,float_format='%.17g')
    pd.DataFrame(compare).to_csv(out/'parent_q_transport_comparison.csv',index=False,float_format='%.17g')
    make_figures(frame,out)
    num={'sampled_sections':len(rows),'max_generator_fd_rel_error':float(np.nanmax(frame.relative_analytic_vs_fd_J)),
         'max_structural_vs_driven_rhs_rel_error':float(frame.relative_analytic_vs_driven_RHS.max()),
         'max_Bdot_refinement_rel':float(frame.Bdot_refinement_relative.max()),
         'max_projector_fd_relative':float(frame.projector_rate_fd_relative_error.max()),
         'max_kernel_defect':float(frame.kernel_invariance_defect_norm.max()),
         'min_kernel_defect':float(frame.kernel_invariance_defect_norm.min()),
         'max_projector_rate_defect':float(frame.projector_differential_gap_norm.max()),
         'max_algebraic_identity_rel':float(max(frame.projector_identity_rel_residual.max(),frame.B_projector_defect_rel_residual.max()))}
    if num['max_generator_fd_rel_error']>5e-5 or num['max_structural_vs_driven_rhs_rel_error']>5e-8:
        raise RuntimeError('Analytic tangent generator not verified against the actual driven RHS; results must not be classified.')
    if num['max_algebraic_identity_rel']>1e-7:
        raise RuntimeError('Projector identities inconsistent')
    report={'version':'v18.50r','title':'Differential Kernel Invariance & Analytic Tangent Generator Audit',
        'classification':'MODEL_JET_TANGENT_AND_SAMPLED_DIFFERENTIAL_KERNEL_DIAGNOSTIC_NOT_MATERIAL_INVARIANCE_CERTIFICATE',
        'parent':parent,'observed':num,'per_branch':compare,
        'methods':{'J10':'Analytic 11D structural Jacobian top-left block, with fixed chart scale transform; driven RHS 10D is independently differentiated for verification',
                   'B':'Analytic normalized structural observer Jacobian inherited from q',
                   'Bdot':'Fourth-order centered differences along freshly integrated driven 10D natural trajectory; two resolutions, not analytic third derivative',
                   'kernel':'Rank-three Euclidean 10D chart null projector, full 7D kernel',
                   'invariance_source':'(Bdot+B J10)P; leakage per unit evolution xi',
                   'projector_differential':'Pdot versus (I-P)J P+P J^T(I-P)'},
        'limitations':['Bdot uses time finite differences, not an analytic or interval-certified third jet.',
           'Numerical rank 3 and defect values are evaluated at sampled trajectory points only.',
           'Orthogonal projector and its rate depend on the selected Euclidean state chart; no certified material kinetic metric.',
           'The source defect is not physical energy, stress, polymer strain or material memory.',
           'A nonzero defect is not a validated physical torsional flip or constitutive law.',
           'The driven structural-Jacobian identity is verified against the true model RHS, rather than assumed silently.'],
        'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':__import__('scipy').__version__}}
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('v18.50r COMPLETE',json.dumps(num,indent=2),flush=True)

if __name__=='__main__':main()
