#!/usr/bin/env python3
"""Q550 v18.49n: genuine ramp-shape interventions and pairwise dominance persistence.

True 11D dynamics, analytic 10D tangent propagators, inherited v18.49m
fixed tau_ref=1 kinetic metric, 45 squared eigenprojector couplings. The
prescribed brake command changes while ramp duration and accumulated phase
at the registered return clock are fixed; only command-shape robustness
is tested, not a physical-causal energy decomposition or metric universality.
"""
import argparse,csv,json,platform,sys
from pathlib import Path
from collections import defaultdict
import numpy as np
from verify_parent import verify,dynamic
from ramp_shapes import SHAPES,ShapeClock,validate_shapes,h,area
from frame_math import transport_frame
from kinetic_metric import embedding_and_jac
from generator_math import kinetic_frame_derivative,deforming_frame,spectral_generator
from pairwise_math import PAIRS,pair_spectrum,shapley_pair_attribution
ROOT=Path(__file__).resolve().parents[1]
PRIMARY=(5,6) # zero-based eigenvalue ranks => displayed pair 6-7.
P67=PAIRS.index(PRIMARY)
FULL_RAMPS=(.285,.300,.309)
Q0=.35;Q1=.65

def save_csv(name,rows):
    if not rows:raise RuntimeError('No results: '+name)
    p=ROOT/'results'/name;p.parent.mkdir(parents=True,exist_ok=True)
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def onset(q,signal,cutoff=0.,tol=1e-13):
    """Sample-bracketed first strictly positive onset, not certified root."""
    d=np.asarray(signal)-cutoff;which=np.flatnonzero(d>tol)
    if not len(which):return None,None,None
    i=int(which[0])
    if i==0:return float(q[0]),float(q[0]),float(q[0])
    lo=float(q[i-1]);hi=float(q[i]);a,b=float(d[i-1]),float(d[i]);
    est=lo+(hi-lo)*(-a)/(b-a) if a*b<=0 and abs(b-a)>1e-25 else hi
    return float(est),lo,hi

def positive_width(q,y):
    """Piecewise-linear estimate of the domain width on the sampled interval."""
    total=0.
    for i in range(len(q)-1):
        a=float(y[i]);b=float(y[i+1]);step=float(q[i+1]-q[i])
        if a>0 and b>0:total+=step
        elif a<=0 and b<=0:pass
        elif b!=a:
            fraction=max(0.,min(1.,-a/(b-a)))
            total+=step*(1-fraction if a<=0 else fraction)
    return float(total)

def case_reduce(kind,rv,shape,q,profs,gaps,errs):
    sq=np.vstack([p['pair_K_frob_sq'] for p in profs]);total=sq.sum(axis=1)
    shares=sq/total[:,None]
    target=shares[:,P67];rivals=np.max(np.delete(shares,P67,axis=1),axis=1)
    margin=target-rivals
    leaders=np.argmax(shares,axis=1)
    over,over_lo,over_hi=onset(q,margin)
    maj,maj_lo,maj_hi=onset(q,target,.5)
    first=q>=.55-1e-12
    after=shapley_pair_attribution(profs[np.argmin(abs(q-.5))],profs[-1])
    if np.max(abs((after['numerator_attribution']+after['gap_attribution'])-after['delta_pair_norm_sq']))>1e-8:
        raise RuntimeError('Shapley identity failed')
    endpoint_sq=sq[-1];endpoint_rank=np.argsort(endpoint_sq)[::-1]
    winner=int(endpoint_rank[0]);pair=PAIRS[winner]
    numerator_share=float(np.sum(after['numerator_attribution']))
    gap_share=float(np.sum(after['gap_attribution']))
    shift=float(np.sum(after['delta_pair_norm_sq']))
    if abs(shift)<1e-12:raise RuntimeError('Degenerate comparison between phase endpoints')
    detail={'kappa_kind':kind,'ramp_xi':rv,'shape':shape,
        'leading_pair_at_q065':f'{pair[0]+1}-{pair[1]+1}',
        'pair_67_rank_at_q065':1+int(np.sum(endpoint_sq>endpoint_sq[P67])),
        'pair_67_share_q050':float(shares[np.argmin(abs(q-.5)),P67]),
        'pair_67_share_q065':float(target[-1]),
        'pair_67_max_sampled_share':float(target.max()),
        'pair_67_q_of_max_sampled_share':float(q[target.argmax()]),
        'pair_67_margin_over_runnerup_q065':float(margin[-1]),
        'pair_67_runnerup_pair_q065':f'{PAIRS[int(endpoint_rank[1])][0]+1}-{PAIRS[int(endpoint_rank[1])][1]+1}',
        'first_overall_dominance_q_estimate':over,
        'first_overall_dominance_bracket_lo':over_lo,
        'first_overall_dominance_bracket_hi':over_hi,
        'first_majority_q_estimate':maj,
        'first_majority_bracket_lo':maj_lo,
        'first_majority_bracket_hi':maj_hi,
        'dominance_width_q035_to_065_estimate':positive_width(q,margin),
        'dominance_fraction_sampled':float(np.mean(leaders==P67)),
        'persists_every_sample_q055_to_065':bool(np.all(leaders[first]==P67)),
        'has_majority_at_q065':bool(target[-1]>.5),
        'minimum_margin_q055_to_065':float(np.min(margin[first])),
        'minimum_share_q055_to_065':float(np.min(target[first])),
        'top5_final_share':float(np.sum(np.sort(shares[-1])[-5:])),
        'generator_norm_q050':float(np.sqrt(total[np.argmin(abs(q-.5))])),
        'generator_norm_q065':float(np.sqrt(total[-1])),
        'numerator_shapley_fraction_signed':numerator_share/shift,
        'gap_shapley_fraction_signed':gap_share/shift,
        'pair_67_fraction_of_generator_norm_sq_rise':float(after['delta_pair_norm_sq'][P67]/shift),
        'pair_67_numerator_q050':float(profs[np.argmin(abs(q-.5))]['numerator'][P67]),
        'pair_67_numerator_q065':float(profs[-1]['numerator'][P67]),
        'pair_67_gap_q050':float(profs[np.argmin(abs(q-.5))]['gap'][P67]),
        'pair_67_gap_q065':float(profs[-1]['gap'][P67]),
        'minimum_relative_eigen_gap':float(np.min(gaps)),
        'mechanical_ledger_relative_error':float(errs)}
    phase=[];pair=[]
    for n,qq in enumerate(q):
        phase.append({'kappa_kind':kind,'ramp_xi':rv,'shape':shape,'phase_q':float(qq),
          'pair_67_share':float(target[n]),'largest_other_pair_share':float(rivals[n]),
          'pair_67_margin':float(margin[n]),'pair_67_is_leader':int(leaders[n]==P67),
          'pair_67_is_majority':int(target[n]>.5),
          'largest_other_pair':f'{PAIRS[int(np.argmax(np.where(np.arange(45)==P67,-np.inf,shares[n])))][0]+1}-{PAIRS[int(np.argmax(np.where(np.arange(45)==P67,-np.inf,shares[n])))][1]+1}',
          'generator_norm':float(np.sqrt(total[n])),'min_relative_eigen_gap':float(gaps[n])})
        for idx,(i,j) in enumerate(PAIRS):
            pp=profs[n]
            pair.append({'kappa_kind':kind,'ramp_xi':rv,'shape':shape,'phase_q':float(qq),
              'axis_rank_a':i+1,'axis_rank_b':j+1,
              'numerator_abs':float(pp['numerator'][idx]),'lambda_gap':float(pp['gap'][idx]),
              'omega_abs':float(pp['omega_abs'][idx]),
              'generator_norm_sq_contribution':float(sq[n,idx]),'generator_fraction_sq':float(shares[n,idx])})
    return detail,phase,pair,shares

def run(args):
    if args.phase_points<31 or (args.phase_points-1)%2:raise ValueError('phase-points must be odd >= 31 with q=0.50 included')
    validate_shapes()
    parent,nodes,provenance=verify()
    pk,pj,i,h0,g,f,e,d,c,b,a,z,y,j=nodes
    sys.path[:0]=[str(c/'reference'),str(c/'scripts')]
    physical=dynamic(c/'reference/physical_math.py','n_original_physical')
    original_ramp=dynamic(c/'reference/parent_ramp_math.py','n_original_ramp')
    original=dynamic(c/'reference/y_original_run_audit.py','n_original_run')
    jet=dynamic(c/'reference/structural_jet.py','n_original_structural_jet')
    support_sources=list(z.rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
    if len(support_sources)!=1:raise RuntimeError('Ambiguous historical support source')
    support=dynamic(support_sources[0],'n_original_support')
    audit=dynamic(support_sources[0].parent/'test_support_mobius_monodromy_audit.py','n_original_audit')
    history=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    k_report=json.loads((j/'runtime/report_v18_48h.json').read_text())
    ks={'original':float(k_report['kappa_original']), 'autonomous':float(k_report['kappa_autonomous'])}
    omega=float(history['clock_speed']);slope=omega/(2*np.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    groups=defaultdict(list)
    for ind in range(len(history['y'])):
        groups[(str(history['families'][ind]),int(history['seed_branches'][ind]),str(history['kappa_kind'][ind]))].append(ind)
    q=np.linspace(Q0,Q1,args.phase_points)
    shapes=('cubic','quintic') if args.smoke else SHAPES
    ramps=(.300,) if args.smoke else FULL_RAMPS
    kinds=('original',) if args.smoke else ('original','autonomous')
    shape_driver=ShapeClock(original_ramp)
    case_rows=[];phase_rows=[];pair_rows=[];agreement=[]
    per_case={};numeric={'forward_regression':0.,'mechanical_ledger':0.,
        'pair_frobenius_identity':0.,'upstream_cubic_max_abs_share_difference':0.,
        'identity_at_q050_q065':0.}
    previous={}
    with (parent/'results/pairwise_generator_phase_profiles.csv').open(newline='') as fprev:
        for row in csv.DictReader(fprev):
            if row['axis_rank_a']=='6' and row['axis_rank_b']=='7':
                key=(row['kappa_kind'],round(float(row['ramp_xi']),6),round(float(row['phase_q']),8))
                previous[key]=float(row['generator_fraction_sq'])
    integrations={'physical_forward_11D':0,'physical_return_11D':0,'tangent_10D':0}
    for kind in kinds:
        inds=sorted(next(vals for (fam,br,k),vals in groups.items() if fam.startswith('phaseblind') and br==0 and k==kind),key=lambda idx:float(history['xi'][idx]))
        kap=ks[kind];seed=np.asarray(history['y'][inds[0]],float)
        forward,err=original.integrate(physical,original_ramp,support,audit,kap,params,slope,omega,seed,args)
        integrations['physical_forward_11D']+=1
        regression=max(float(np.linalg.norm(forward(t)[:11]-history['y'][idx])) for t,idx in zip(np.linspace(0,1,41),inds))
        numeric['forward_regression']=max(numeric['forward_regression'],regression)
        if regression>args.maximum_regression:raise RuntimeError('Historical 11D forward replay failed')
        turning=forward(1.)[:11].copy();turning[[1,3,5,7,9]]*=-1
        for rv in ramps:
            for shape in shapes:
                design=original_ramp.Design('n_'+shape,shape,rv)
                back,err=original.integrate(physical,shape_driver,support,audit,kap,params,slope,omega,turning,args,design=design)
                numeric['mechanical_ledger']=max(numeric['mechanical_ledger'],err)
                integrations['physical_return_11D']+=1
                def local_jac(st,k,p,sl):return jet.structural_jet(st,kap,params,slope)[1]
                frame,_=transport_frame(back,kap,params,slope,local_jac,1.+rv,
                         rtol=args.frame_rtol,atol=args.frame_atol,max_step=args.frame_max_step)
                integrations['tangent_10D']+=1
                _,J0=embedding_and_jac(back(0.)[:10],params.m_x,1.)
                prof=[];gaps=[]
                for qq in q:
                    t=float(rv+qq);state=back(t)[:11]
                    flow,Jmat,_=jet.structural_jet(state,kap,params,slope)
                    _,J=embedding_and_jac(state,params.m_x,1.)
                    Jdot=kinetic_frame_derivative(state,flow,params.m_x,1.,embedding_and_jac)
                    B,Bdot=deforming_frame(J,frame(t),J0,Jdot,Jmat[:10,:10])
                    out=spectral_generator(B,Bdot)
                    pp=pair_spectrum(out)
                    numeric['pair_frobenius_identity']=max(numeric['pair_frobenius_identity'],
                         abs(pp['total_K_frob_sq']-out['generator_frobenius']**2))
                    gaps.append(out['min_relative_eigengap']);prof.append(pp)
                    if shape=='cubic':
                        key=(kind,round(rv,6),round(float(qq),8))
                        if key in previous:
                            err1=abs(pp['pair_K_frob_sq'][P67]/pp['total_K_frob_sq']-previous[key])
                            numeric['upstream_cubic_max_abs_share_difference']=max(numeric['upstream_cubic_max_abs_share_difference'],err1)
                numeric['identity_at_q050_q065']=max(numeric['identity_at_q050_q065'],
                    abs(prof[-1]['total_K_frob_sq']-sum(prof[-1]['pair_K_frob_sq'])))
                detail,phase,pair,share=case_reduce(kind,rv,shape,q,prof,gaps,err)
                case_rows.append(detail);phase_rows+=phase;pair_rows+=pair
                per_case[(kind,rv,shape)]=share
                print(f'v18.49n {kind:10s} r={rv:.6f} {shape:11s}: 6-7 share@.65={detail["pair_67_share_q065"]:.6%}, '+
                      f'onset={detail["first_overall_dominance_q_estimate"]}, persistent@.55={detail["persists_every_sample_q055_to_065"]}',flush=True)
    # Baseline controlled differences: compare at identical kind, ramp and return phase.
    for (kind,rv,shape),shares in per_case.items():
        ref=per_case[(kind,rv,'cubic')]
        a=np.argsort(-shares[-1]);b=np.argsort(-ref[-1]);
        rank1=np.empty(45,dtype=int);rank2=np.empty(45,dtype=int)
        rank1[a]=np.arange(45);rank2[b]=np.arange(45)
        rho=float(np.corrcoef(rank1,rank2)[0,1])
        agreement.append({'kappa_kind':kind,'ramp_xi':rv,'shape':shape,
            'pair_67_share_change_q065_vs_cubic':float(shares[-1,P67]-ref[-1,P67]),
            'pair_67_largest_abs_share_difference_all_q':float(np.max(np.abs(shares[:,P67]-ref[:,P67]))),
            'rank_correlation_final_vs_cubic':rho,
            'same_final_top_pair_as_cubic':bool(np.argmax(shares[-1])==np.argmax(ref[-1]))})
    envelope=[]
    for ii,qq in enumerate(q):
        sub=[(case,share[ii]) for case,share in per_case.items()]
        target=[float(v[P67]) for _,v in sub]
        margins=[float(v[P67]-np.max(np.delete(v,P67))) for _,v in sub]
        envelope.append({'phase_q':float(qq),'tested_cases':len(sub),
            'pair_67_min_share':min(target),'pair_67_max_share':max(target),
            'pair_67_min_margin':min(margins),'pair_67_max_margin':max(margins),
            'fraction_cases_pair_67_leads':sum(x>0 for x in margins)/len(margins),
            'fraction_cases_pair_67_majority':sum(x>.5 for x in target)/len(target)})
    command=[]
    for shape in shapes:
        for s in np.linspace(0,1,101):
            command.append({'shape':shape,'normalized_ramp_time':float(s),
             'reversal_completion_h':float(h(s,shape)),
             'signed_clock_rate':float(1-2*h(s,shape)),
             'phase_excursion_ramp_normalized':float(-s+2*area(s,shape))})
    save_csv('ramp_command_shapes.csv',command)
    save_csv('pairwise_dominance_phase_profiles.csv',phase_rows)
    save_csv('pairwise_generator_phase_profiles.csv',pair_rows)
    save_csv('pairwise_dominance_case_summary.csv',case_rows)
    save_csv('shape_vs_cubic_control.csv',agreement)
    save_csv('cross_case_dominance_envelope.csv',envelope)
    if numeric['upstream_cubic_max_abs_share_difference']>args.maximum_parent_share_difference:
        raise RuntimeError('Authentic v18.49m cubic baseline mismatch')
    all_persistent=all(c['persists_every_sample_q055_to_065'] for c in case_rows)
    all_final=all(c['leading_pair_at_q065']=='6-7' for c in case_rows)
    all_majority=all(c['has_majority_at_q065'] for c in case_rows)
    report={'version':'v18.49n','status':'NUMERICAL_AUDIT_COMPLETED' if not args.smoke else 'SMOKE_DIAGNOSTIC_ONLY',
      'question':'Persistence of 6-7 pairwise dominance under equal-duration, equal-phase-area brake command perturbations',
      'source':provenance,'shape_set':list(shapes),'ramp_durations':list(ramps),'kappa_choices':list(kinds),
      'phase_interval':[Q0,Q1],'phase_samples':len(q),'metric':'fixed initial kinetic embedding tau=1',
      'pair_weight':'2*abs(a_j.T*Cdot*a_i/(lambda_i-lambda_j))**2',
      'total_case_count':len(case_rows),'pair_count':45,'integration_counts':integrations,
      'numeric_controls':numeric,
      'all_cases_final_leader_6_7':all_final,'all_cases_final_majority_6_7':all_majority,
      'all_cases_6_7_leader_at_all_samples_q055_to_065':all_persistent,
      'worst_final_share_6_7':min(c['pair_67_share_q065'] for c in case_rows),
      'worst_final_leader_margin_6_7':min(c['pair_67_margin_over_runnerup_q065'] for c in case_rows),
      'worst_margin_q055_to_065':min(c['minimum_margin_q055_to_065'] for c in case_rows),
      'case_summary':case_rows,
      'limitations':['Finite selected shape families only, not all possible ramp shapes.',
        'Sampled dominance on the phase grid, bracket/linear onset estimates, not interval-certified roots.',
        'Metric and initial kinetic frame are inherited from v18.49m; no metric-universal dominance claim.',
        'Pair ranks require a simple ordered eigenvalue spectrum; algorithm rejects small spectral gaps.',
        'Numerator/gap Shapley split is an endpoint algebraic attribution, not a physical causal intervention.',
        'No test of nonlinear forcing mechanism or energy transfer between pair modes.']}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),
        'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true',help='One kappa, one ramp, cubic and quintic only; NOT full-domain evidence')
    p.add_argument('--phase-points',type=int,default=121)
    p.add_argument('--rtol',type=float,default=3e-12)
    p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025)
    p.add_argument('--frame-rtol',type=float,default=8e-11)
    p.add_argument('--frame-atol',type=float,default=8e-13)
    p.add_argument('--frame-max-step',type=float,default=.008)
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    p.add_argument('--maximum-parent-share-difference',type=float,default=2e-6)
    result=run(p.parse_args())
    print(json.dumps({k:result[k] for k in ('status','total_case_count','integration_counts',
          'all_cases_final_leader_6_7','all_cases_6_7_leader_at_all_samples_q055_to_065','worst_final_share_6_7','numeric_controls')},indent=2))
