#!/usr/bin/env python3
"""Q550 v18.49p: phase-resolved 6-7 / 7-8 pairwise handover.

Physical 11D return and 10D tangent are freshly integrated per (kappa,r).
Rank-ordered pairwise numerator N and eigen-gap g satisfy A=2|N/g|^2.
The two-factor Shapley accounting is an exact algebraic decomposition,
not a dynamical intervention. Crossings are sampled and numerically refined,
not interval-certified. All measurements use the inherited kinetic metric.
"""
from pathlib import Path
import argparse,csv,json,platform
import numpy as np
from scipy.optimize import brentq
from parent_o_experiment import Experiment
from frame_math import transport_frame
from generator_math import kinetic_frame_derivative,deforming_frame,spectral_generator
from kinetic_metric import embedding_and_jac
from pairwise_math import PAIRS,pair_spectrum,shapley_pair_attribution
ROOT=Path(__file__).resolve().parents[1]
P67=PAIRS.index((5,6));P78=PAIRS.index((6,7));SHAPE='beta:2:2'
BASELINE_R=.3
BRACKET=(.32671875,.327375)
DEFAULT_R=[.30,.32671875,.327046875,.327375,.33]

def csv_write(name,rows):
    if not rows:raise RuntimeError('Missing results '+name)
    p=ROOT/'results'/name;p.parent.mkdir(exist_ok=True,parents=True)
    with p.open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for x in rows for k in x)))
        wr.writeheader();wr.writerows(rows)

def exact_decomposition(before,after):
    """Two-factor algebraic Shapley decomposition for each raw pair power."""
    sh=shapley_pair_attribution(before,after)
    return sh

def pair_ratio_ledger(s):
    n=np.asarray(s['numerator']);g=np.asarray(s['gap'])
    if min(n[P67],n[P78],g[P67],g[P78])<=0:raise RuntimeError('Invalid log pair ratio')
    log_raw=np.log(s['pair_K_frob_sq'][P78]/s['pair_K_frob_sq'][P67])
    log_n=2*np.log(n[P78]/n[P67]);log_inv_g=-2*np.log(g[P78]/g[P67])
    if abs(log_raw-log_n-log_inv_g)>1e-9:raise RuntimeError('Log ratio identity fails')
    return {'log_power_ratio_78_over_67':float(log_raw),'log_numerator_ratio_term':float(log_n),
            'log_inverse_gap_ratio_term':float(log_inv_g), 'identity_residual':float(log_raw-log_n-log_inv_g)}

class Handover:
    def __init__(self,args):
        self.args=args
        self.parent=Experiment(args)
        self.rows=[];self.pair_rows=[];self.events=[];self.shapley_rows=[];self.control=[]
        self.failures=[];self.max_norm_identity=0.;self.max_log_identity=0.
        self.max_parent_difference=0.;self.min_gap=1.;self.max_ledger=0.
        self.parent_csv=self._load_parent_csv()
    def _load_parent_csv(self):
        parent_source=ROOT/'runtime/authenticated_o'/json.loads((ROOT/'inputs/SOURCE_PINS.json').read_text())['parent_root']
        path=parent_source/'results/case_surveys.csv'
        if not path.is_file():raise RuntimeError('Authenticated parent results unavailable')
        with path.open(newline='') as f:return list(csv.DictReader(f))
    def spectrum_from(self,back,frame,J0,kind,r,q):
        t=float(r+q);st=back(t)[:11]
        field,Jmat,_=self.parent.jet.structural_jet(st,self.parent.ks[kind],self.parent.params,self.parent.slope)
        _,J=embedding_and_jac(st,self.parent.params.m_x,1.)
        Jdot=kinetic_frame_derivative(st,field,self.parent.params.m_x,1.,embedding_and_jac)
        B,Bdot=deforming_frame(J,frame(t),J0,Jdot,Jmat[:10,:10])
        out=spectral_generator(B,Bdot)
        spec=pair_spectrum(out)
        power=np.asarray(spec['pair_K_frob_sq']);total=float(power.sum())
        self.max_norm_identity=max(self.max_norm_identity,abs(total-out['generator_frobenius']**2))
        self.min_gap=min(self.min_gap,float(out['min_relative_eigengap']))
        if total<=0 or out['min_relative_eigengap']<self.args.min_relative_gap:
            raise RuntimeError('Generator or spectral-gap degeneracy')
        return out,spec,power/total
    def one_case(self,kind,r):
        a=self.args;p=self.parent;k=p.ks[kind]
        design=p.original_ramp.Design('p_hand_'+kind,SHAPE,float(r))
        back,err=p.original.integrate(p.physical,p.clock,p.support,p.audit,k,p.params,p.slope,p.omega,p.turning[kind],a,design=design)
        p.integrations['physical_return_11D']+=1
        self.max_ledger=max(self.max_ledger,err)
        def jac(st,kap,par,sl):return p.jet.structural_jet(st,k,p.params,p.slope)[1]
        frame,_=transport_frame(back,k,p.params,p.slope,jac,1.+r,rtol=a.frame_rtol,atol=a.frame_atol,max_step=a.frame_max_step)
        p.integrations['tangent_10D']+=1
        _,J0=embedding_and_jac(back(0.)[:10],p.params.m_x,1.)
        qs=np.linspace(a.q_start,a.q_end,a.phase_samples)
        specs={}; phases=[]
        for q in qs:
            out,s,shares=self.spectrum_from(back,frame,J0,kind,r,q)
            s['numerator']=np.asarray(s['numerator']);s['gap']=np.asarray(s['gap'])
            power=np.asarray(s['pair_K_frob_sq']);D=power/power.sum()
            other=np.argmax(np.where(np.arange(45)==P67,-np.inf,D))
            win=np.argmax(D)
            log=pair_ratio_ledger(s)
            x={'kappa_kind':kind,'ramp_xi':float(r),'phase_q':float(q),
                'share_67':float(D[P67]),'share_78':float(D[P78]),
                'share_78_minus_67':float(D[P78]-D[P67]),
                'margin_67_over_all_others':float(D[P67]-D[other]),
                'leading_pair':f'{PAIRS[win][0]+1}-{PAIRS[win][1]+1}',
                'leader_is_67_or_78':bool(win in (P67,P78)),
                'min_relative_eigengap':float(out['min_relative_eigengap']),
                'generator_norm':float(out['generator_frobenius']),**log}
            self.rows.append(x);phases.append(x);specs[round(float(q),13)]=s
            self.max_log_identity=max(self.max_log_identity,abs(log['identity_residual']))
            for index,name in [(P67,'6-7'),(P78,'7-8')]:
                self.pair_rows.append({'kappa_kind':kind,'ramp_xi':float(r),'phase_q':float(q),
                    'pair':name,'numerator_abs':float(s['numerator'][index]),
                    'gap':float(s['gap'][index]),'inverse_gap':float(1/s['gap'][index]),
                    'omega_abs':float(s['omega_abs'][index]),'raw_power':float(power[index]),
                    'share':float(D[index])})
        # Regression against the audited v18.49o *measured* q=.65 output.
        if abs(a.q_end-.65)<1e-12:
            candidates=[z for z in self.parent_csv if z['kappa_kind']==kind and z['shape']==SHAPE and abs(float(z['ramp_xi'])-r)<1e-10]
            if candidates:
                dif=max(abs(float(z['share_at_q065'])-phases[-1]['share_67']) for z in candidates)
                self.max_parent_difference=max(self.max_parent_difference,dif)
                if dif>a.max_parent_regression:raise RuntimeError(f'v18.49o parent regression failed {dif}')
                self.control.append({'kappa_kind':kind,'ramp_xi':r,'parent_matched_cases':len(candidates),'abs_share_error':dif})
        # Crossing refined from actual physics interpolation at arbitrary q on the SAME trajectory.
        f=np.array([z['share_78_minus_67'] for z in phases])
        crossings=[]
        for j in range(len(f)-1):
            if f[j]*f[j+1]<0:
                lo,hi=qs[j:j+2]
                def diff(x):
                    _,sp,_=self.spectrum_from(back,frame,J0,kind,r,x)
                    pw=sp['pair_K_frob_sq'];return float((pw[P78]-pw[P67])/sum(pw))
                root=float(brentq(diff,lo,hi,xtol=1e-13,rtol=1e-13,maxiter=80))
                _,ss,dshare=self.spectrum_from(back,frame,J0,kind,r,root)
                ranked=np.argsort(-dshare)[:3]
                crossings.append({'kappa_kind':kind,'ramp_xi':float(r),
                    'phase_q_root':root,'phase_bracket_low':float(lo),'phase_bracket_high':float(hi),
                    'leading_at_root':[f'{PAIRS[i][0]+1}-{PAIRS[i][1]+1}' for i in ranked],
                    'six_seven_seven_eight_top_two':bool(set(ranked[:2])=={P67,P78}),
                    'share_at_root':float(dshare[P67]),'numerator_ratio_78_over_67':float(ss['numerator'][P78]/ss['numerator'][P67]),
                    'gap_ratio_78_over_67':float(ss['gap'][P78]/ss['gap'][P67]),
                    'crossing_residual':diff(root)})
        # Accounting q_start to q_end by exact two-factor Shapley identity, including changes in competitor lead.
        start=specs[round(float(qs[0]),13)];end=specs[round(float(qs[-1]),13)]
        sh=exact_decomposition(start,end)
        deltas=[]
        for i,label in ((P67,'6-7'),(P78,'7-8')):
            v={'kappa_kind':kind,'ramp_xi':float(r),'pair':label,
                'q_start':float(qs[0]),'q_end':float(qs[-1]),
                'raw_power_initial':float(sh['initial_norm_sq']) if False else float(start['pair_K_frob_sq'][i]),
                'raw_power_final':float(end['pair_K_frob_sq'][i]),
                'delta_raw_power':float(sh['delta_pair_norm_sq'][i]),
                'numerator_shapley':float(sh['numerator_attribution'][i]),
                'inverse_gap_shapley':float(sh['gap_attribution'][i]),
                'numerator_log_gain':float(2*np.log(end['numerator'][i]/start['numerator'][i])),
                'inverse_gap_log_gain':float(-2*np.log(end['gap'][i]/start['gap'][i])),
                'total_log_gain':float(np.log(end['pair_K_frob_sq'][i]/start['pair_K_frob_sq'][i]))}
            self.shapley_rows.append(v);deltas.append(v)
        diff_num=deltas[1]['numerator_shapley']-deltas[0]['numerator_shapley']
        diff_gap=deltas[1]['inverse_gap_shapley']-deltas[0]['inverse_gap_shapley']
        diff_final=end['pair_K_frob_sq'][P78]-end['pair_K_frob_sq'][P67]
        diff_initial=start['pair_K_frob_sq'][P78]-start['pair_K_frob_sq'][P67]
        close=float(diff_num+diff_gap-(diff_final-diff_initial))
        if max(abs(close),sh['closure_error'])>1e-6:raise RuntimeError('Two-pair Shapley accounting did not close')
        case={'kappa_kind':kind,'ramp_xi':float(r),'shape':SHAPE,
              'q_start':float(qs[0]),'q_end':float(qs[-1]),'sample_count':len(qs),
              'phase_crossing_count':len(crossings),
              'root_phases':[x['phase_q_root'] for x in crossings],
              'leading_pair_at_start':phases[0]['leading_pair'],'leading_pair_at_end':phases[-1]['leading_pair'],
              'relative_share_78_minus_67_at_start':phases[0]['share_78_minus_67'],
              'relative_share_78_minus_67_at_end':phases[-1]['share_78_minus_67'],
              'raw_difference_initial':float(diff_initial),'raw_difference_final':float(diff_final),
              'delta_raw_difference':float(diff_final-diff_initial),
              'numerator_share_of_raw_difference_change':float(diff_num/(diff_final-diff_initial)) if abs(diff_final-diff_initial)>1e-30 else None,
              'inverse_gap_share_of_raw_difference_change':float(diff_gap/(diff_final-diff_initial)) if abs(diff_final-diff_initial)>1e-30 else None,
              'numerator_shapley_difference':float(diff_num),'inverse_gap_shapley_difference':float(diff_gap),
              'shapley_closure_error':close,'min_relative_eigengap':min(z['min_relative_eigengap'] for z in phases),
              'ledger_error':err}
        self.events+=crossings
        print('v18.49p',kind,'r',r,'lead',case['leading_pair_at_start'],'→',case['leading_pair_at_end'],
              'crossings',case['root_phases'],'at end D78-D67',round(phases[-1]['share_78_minus_67'],9),flush=True)
        return case

def run(a):
    if a.phase_samples<3 or not 0<a.q_start<a.q_end<=.65 or a.q_end<=a.q_start:raise ValueError('Invalid phase grid')
    if a.smoke:ramps=[.327375];kinds=['original']
    elif a.focus:ramps=list(BRACKET)+[.327046875];kinds=['original','autonomous']
    else:ramps=DEFAULT_R;kinds=['original','autonomous']
    h=Handover(a);cases=[]
    for kind in kinds:
        for r in ramps:
            try:cases.append(h.one_case(kind,r))
            except Exception as e:
                h.failures.append({'kappa_kind':kind,'ramp_xi':r,'error':repr(e)})
                print('FAILED',kind,r,repr(e),flush=True)
                if not a.continue_on_error:raise
    csv_write('phase_resolved_pair_67_vs_78.csv',h.rows)
    csv_write('numerator_gap_pair_traces.csv',h.pair_rows)
    csv_write('endpoint_shapley_pair_attribution.csv',h.shapley_rows)
    if h.events:csv_write('numerical_handover_events.csv',[dict(x,leading_at_root=';'.join(x['leading_at_root'])) for x in h.events])
    if h.control:csv_write('v18_49o_parent_regression.csv',h.control)
    report={'audit':'Q550 v18.49p — Pairwise Handover: Numerator–Gap Competition & Phase-Resolved Transfer Audit',
      'status':'SMOKE_DIAGNOSTIC_ONLY' if a.smoke else ('FOCUSED_PHASE_RESOLVED_NUMERICAL_AUDIT' if a.focus else 'PHASE_RESOLVED_NUMERICAL_AUDIT'),
      'kappa_kinds':kinds,'ramp_durations':ramps,'phase_window':[a.q_start,a.q_end],
      'sample_count_per_case':a.phase_samples,'cases':cases,'phase_crossing_events':h.events,
      'failed_cases':h.failures,
      'identity_controls':{'maximum_pair_generator_norm_sq_residual':h.max_norm_identity,
        'maximum_log_ratio_identity_residual':h.max_log_identity,
        'maximum_parent_o_pair67_share_difference':h.max_parent_difference,
        'minimum_relative_eigen_gap':h.min_gap,
        'maximum_11D_mechanical_ledger_error':h.max_ledger,
        'maximum_11D_forward_replay_error':h.parent.regression},
      'integrations':h.parent.integrations,
      'parent_source_authentication':h.parent.ancestry,
      'limitations':['Numerically refined same-trajectory roots, not interval-certified crossing events.',
       'Pairwise rank indices are spectrum-ordered, not identities of individual physical particles.',
       'Algebraic Shapley allocation is not an intervention; its contribution shares can be signed or exceed 1.',
       'Rank-pair generator results apply to the fixed historical kinetic metric, not arbitrary observers.',
       'A sign crossing of two pair contributions alone is not sufficient for global lead handover; check top two.',
       'Changing duration alters physical drive and therefore is not a pure shape perturbation.']}
    (ROOT/'results/report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),'numpy':np.__version__,
        'scipy':__import__('scipy').__version__},indent=2)+'\n')
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--smoke',action='store_true');p.add_argument('--focus',action='store_true')
    p.add_argument('--continue-on-error',action='store_true')
    p.add_argument('--phase-samples',type=int,default=151)
    p.add_argument('--q-start',type=float,default=.60);p.add_argument('--q-end',type=float,default=.65)
    p.add_argument('--rtol',type=float,default=3e-12);p.add_argument('--atol',type=float,default=3e-13)
    p.add_argument('--max-step',type=float,default=.025)
    p.add_argument('--frame-rtol',type=float,default=8e-11);p.add_argument('--frame-atol',type=float,default=8e-13)
    p.add_argument('--frame-max-step',type=float,default=.008)
    p.add_argument('--min-relative-gap',type=float,default=1e-7)
    p.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    p.add_argument('--maximum-regression',type=float,default=1e-7)
    p.add_argument('--maximum-parent-share-difference',type=float,default=2e-6)
    p.add_argument('--max-generator-identity-error',type=float,default=1e-7)
    p.add_argument('--max-parent-regression',type=float,default=2e-6)
    rep=run(p.parse_args())
    print(json.dumps({'status':rep['status'],'cases':len(rep['cases']),
      'events':len(rep['phase_crossing_events']),'controls':rep['identity_controls']},indent=2),flush=True)
