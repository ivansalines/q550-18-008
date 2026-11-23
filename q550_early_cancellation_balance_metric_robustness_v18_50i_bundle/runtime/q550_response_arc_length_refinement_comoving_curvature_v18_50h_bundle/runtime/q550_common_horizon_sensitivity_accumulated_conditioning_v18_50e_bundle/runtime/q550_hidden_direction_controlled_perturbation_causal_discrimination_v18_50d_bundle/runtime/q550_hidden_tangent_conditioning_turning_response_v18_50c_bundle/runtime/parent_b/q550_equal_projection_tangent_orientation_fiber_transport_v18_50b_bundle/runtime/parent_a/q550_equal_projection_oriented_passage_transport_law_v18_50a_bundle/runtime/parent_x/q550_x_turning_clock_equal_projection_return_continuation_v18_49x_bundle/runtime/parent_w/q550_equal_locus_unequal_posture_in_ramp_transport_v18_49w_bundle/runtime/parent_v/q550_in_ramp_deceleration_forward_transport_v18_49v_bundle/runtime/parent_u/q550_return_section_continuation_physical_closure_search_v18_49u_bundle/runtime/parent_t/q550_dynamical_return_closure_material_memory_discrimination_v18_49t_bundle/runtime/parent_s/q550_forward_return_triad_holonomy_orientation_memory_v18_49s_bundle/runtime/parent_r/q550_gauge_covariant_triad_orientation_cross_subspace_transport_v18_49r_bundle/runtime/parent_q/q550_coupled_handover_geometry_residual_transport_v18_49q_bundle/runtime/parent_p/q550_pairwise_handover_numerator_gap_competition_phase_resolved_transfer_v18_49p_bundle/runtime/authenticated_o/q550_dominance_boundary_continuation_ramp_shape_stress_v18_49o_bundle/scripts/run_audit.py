#!/usr/bin/env python3
"""v18.49o — authentic Q550 11D/10D spectral dominance-boundary scout.

A sign change of M_67 = D_67 - max(other D) at the SAME REGISTERED PHASE
is a sampled, bracketted loss of leading rank, NOT a spectral crossing theorem.
Scans physical ramp duration independently from shape at fixed duration,
with exact equal-area shape controls and preserved kinetic metric.
"""
import argparse,csv,json,platform,sys,traceback
from collections import defaultdict
from pathlib import Path
import numpy as np
from verify_parent import verify,dynamic
from ramp_stress import properties,ShapeClock
from frame_math import transport_frame
from generator_math import kinetic_frame_derivative,deforming_frame,spectral_generator
from kinetic_metric import embedding_and_jac
from pairwise_math import PAIRS,pair_spectrum
ROOT=Path(__file__).resolve().parents[1]
PRIMARY=(5,6);P67=PAIRS.index(PRIMARY)
RAMPS=(.08,.12,.18,.24,.285,.30,.309,.33,.36,.40,.46,.55,.70,.90)
SHAPES=('beta:2:2','beta:3:3','beta:12:12','beta:64:64',
        'beta:2:24','beta:2:100','skew:-3','skew:3',
        'recoil:-4:1','recoil:4:1','recoil:-2:2','recoil:4:2','recoil:2:4')
PROBE=(.35,.50,.55,.60,.65)

def save_csv(name,rows):
    if not rows:raise RuntimeError('No rows to save: '+name)
    keys=list(dict.fromkeys(k for row in rows for k in row))
    dest=ROOT/'results'/name;dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=keys);wr.writeheader();wr.writerows(rows)

class Experiment:
    def __init__(self,args):
        self.args=args
        self.nroot,self.mroot,nodes,self.ancestry=verify()
        pk,pj,i,h0,g,f,e,d,c,b,a,z,y,j=nodes
        sys.path[:0]=[str(c/'reference'),str(c/'scripts')]
        self.physical=dynamic(c/'reference/physical_math.py','o_original_phys')
        self.original_ramp=dynamic(c/'reference/parent_ramp_math.py','o_original_ramp')
        self.original=dynamic(c/'reference/y_original_run_audit.py','o_original_integrator')
        self.jet=dynamic(c/'reference/structural_jet.py','o_original_structural_jet')
        support_sources=list(z.rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
        if len(support_sources)!=1:raise RuntimeError('Ambiguous authentic historical support')
        self.support=dynamic(support_sources[0],'o_original_support')
        self.audit=dynamic(support_sources[0].parent/'test_support_mobius_monodromy_audit.py','o_original_audit')
        history=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
        k_report=json.loads((j/'runtime/report_v18_48h.json').read_text())
        self.ks={'original':float(k_report['kappa_original']), 'autonomous':float(k_report['kappa_autonomous'])}
        self.omega=float(history['clock_speed']);self.slope=self.omega/(2*np.pi)
        self.params=self.audit.ModelParameters(gamma_rho=.3)
        groups=defaultdict(list)
        for idx in range(len(history['y'])):
            groups[(str(history['families'][idx]),int(history['seed_branches'][idx]),str(history['kappa_kind'][idx]))].append(idx)
        self.turning={};self.integrations={'physical_forward_11D':0,'physical_return_11D':0,'tangent_10D':0}
        self.regression=0.;self.ledger=0.;self.gap_min=1.
        for kind in (('original',) if args.smoke else ('original','autonomous')):
            inds=sorted(next(v for (fam,br,k),v in groups.items() if fam.startswith('phaseblind') and br==0 and k==kind),key=lambda idx:float(history['xi'][idx]))
            st=np.asarray(history['y'][inds[0]],float)
            fwd,err=self.original.integrate(self.physical,self.original_ramp,self.support,self.audit,
                self.ks[kind],self.params,self.slope,self.omega,st,args)
            self.integrations['physical_forward_11D']+=1
            reg=max(float(np.linalg.norm(fwd(t)[:11]-history['y'][idx])) for t,idx in zip(np.linspace(0,1,41),inds))
            self.regression=max(self.regression,reg)
            if reg>args.maximum_regression:raise RuntimeError('Historical 11D forward regression failed')
            turn=fwd(1.)[:11].copy();turn[[1,3,5,7,9]]*=-1
            self.turning[kind]=turn
        self.clock=ShapeClock(self.original_ramp)
        self.cache={};self.records=[];self.profiles=[];self.failures=[]
        self.parent_control={}
        with (self.nroot/'results/pairwise_dominance_case_summary.csv').open(newline='') as f:
            for r in csv.DictReader(f):
                if r['shape']=='cubic' and abs(float(r['ramp_xi'])-.3)<1e-10:
                    self.parent_control[r['kappa_kind']]=float(r['pair_67_share_q065'])
        self.max_parent_error=0.

    def evaluate(self,kind,r,shape,q=PROBE,stage='survey'):
        key=(kind,round(r,10),shape,tuple(float(x) for x in q))
        if key in self.cache:return self.cache[key]
        props=properties(shape)
        if not props['admissible']:raise ValueError('Shape fails bounded equal-area conditions: '+shape)
        k=self.ks[kind];a=self.args
        design=self.original_ramp.Design('o_'+shape.replace(':','_'),shape,float(r))
        back,err=self.original.integrate(self.physical,self.clock,self.support,self.audit,k,self.params,
            self.slope,self.omega,self.turning[kind],a,design=design)
        self.integrations['physical_return_11D']+=1
        self.ledger=max(self.ledger,err)
        def jac(st,kap,p,sl):return self.jet.structural_jet(st,k,self.params,self.slope)[1]
        frame,_=transport_frame(back,k,self.params,self.slope,jac,1.+r,
                 rtol=a.frame_rtol,atol=a.frame_atol,max_step=a.frame_max_step)
        self.integrations['tangent_10D']+=1
        _,J0=embedding_and_jac(back(0.)[:10],self.params.m_x,1.)
        sub=[];gaps=[]
        for qq in q:
            t=float(r+qq);st=back(t)[:11]
            field,Jmat,_=self.jet.structural_jet(st,k,self.params,self.slope)
            _,J=embedding_and_jac(st,self.params.m_x,1.)
            Jdot=kinetic_frame_derivative(st,field,self.params.m_x,1.,embedding_and_jac)
            B,Bdot=deforming_frame(J,frame(t),J0,Jdot,Jmat[:10,:10])
            out=spectral_generator(B,Bdot)
            pp=pair_spectrum(out)
            if abs(pp['total_K_frob_sq']-out['generator_frobenius']**2)>a.max_generator_identity_error:
                raise RuntimeError('Pairwise/Frobenius norm inconsistency')
            sq=np.asarray(pp['pair_K_frob_sq']);total=sq.sum()
            if not np.isfinite(total) or total<=1e-18:raise RuntimeError('Degenerate generator weight')
            shares=sq/total;rival=int(np.argmax(np.where(np.arange(45)==P67,-np.inf,shares)))
            winner=int(np.argmax(shares))
            p={'stage':stage,'kappa_kind':kind,'ramp_xi':float(r),'shape':shape,
               'phase_q':float(qq),'pair_67_share':float(shares[P67]),
               'pair_67_margin':float(shares[P67]-shares[rival]),
               'leading_pair':f'{PAIRS[winner][0]+1}-{PAIRS[winner][1]+1}',
               'runner_up_against_67':f'{PAIRS[rival][0]+1}-{PAIRS[rival][1]+1}',
               'runner_up_share':float(shares[rival]),
               'minimum_relative_eigen_gap':float(out['min_relative_eigengap']),
               'generator_frobenius':float(out['generator_frobenius'])}
            sub.append(p);gaps.append(out['min_relative_eigengap'])
        self.gap_min=min(self.gap_min,*gaps)
        final=sub[-1];tail=[x for x in sub if x['phase_q']>=.55-1e-12]
        if not tail:raise RuntimeError('No late-phase sample')
        row={'stage':stage,'kappa_kind':kind,'ramp_xi':float(r),'shape':shape,
             'shape_monotone':int(props['monotone']),
             'margin_at_q065':final['pair_67_margin'],'share_at_q065':final['pair_67_share'],
             'final_leader':final['leading_pair'],
             'minimum_observed_margin_q055_to_065':min(x['pair_67_margin'] for x in tail),
             'leader_at_all_sampled_late_phases':int(all(x['pair_67_margin']>0 for x in tail)),
             'minimum_relative_eigen_gap':min(gaps),
             'mechanical_ledger_error':float(err)}
        if shape=='beta:2:2' and abs(r-.3)<1e-12:
            difference=abs(final['pair_67_share']-self.parent_control[kind])
            self.max_parent_error=max(self.max_parent_error,difference)
            if difference>a.maximum_parent_share_difference:raise RuntimeError('v18.49n cubic baseline mismatch')
        self.records.append(row);self.profiles+=sub;self.cache[key]=row
        print('v18.49o',stage,kind,'r',round(r,7),shape,'margin',round(row['margin_at_q065'],9),
              'share',round(row['share_at_q065'],9),'winner',row['final_leader'],flush=True)
        return row

    def try_evaluate(self,*args,**kwargs):
        try:return self.evaluate(*args,**kwargs)
        except Exception as exc:
            self.failures.append({'kind':args[0],'r':float(args[1]),'shape':args[2],
                  'stage':kwargs.get('stage','survey'),'error_type':type(exc).__name__,
                  'error_message':str(exc)})
            print('v18.49o EVALUATION_FAIL',args[0],args[1],args[2],type(exc).__name__,str(exc),flush=True)
            return None

def run(args):
    exp=Experiment(args)
    kinds=('original',) if args.smoke else ('original','autonomous')
    ramps=(.285,.3,.309) if args.smoke else ((.309,.33) if args.focus else RAMPS)
    shapes=('beta:2:2','beta:12:12') if args.smoke else (('beta:2:2','beta:64:64','beta:2:100','recoil:4:1') if args.focus else SHAPES)
    shape_ramps=(.3,) if (args.smoke or args.focus) else (.3,.309)
    # 1. Authenticate the known continuation baseline before extrapolating.
    for kind in kinds:exp.evaluate(kind,.3,'beta:2:2',stage='baseline')
    # 2. Duration continuation with identical cubic shape and fixed q clock.
    duration_brackets=[]
    for kind in kinds:
        results={}
        for r in ramps:
            row=exp.try_evaluate(kind,r,'beta:2:2',stage='duration_survey')
            if row:results[float(r)]=row['margin_at_q065']
        ordered=sorted(results)
        for lo,hi in zip(ordered,ordered[1:]):
            if results[lo]*results[hi]<0:
                duration_brackets.append([kind,lo,hi,results[lo],results[hi]])
    # 3. Fixed-duration pure shape stress, SAME integral half-area.
    shape_brackets=[]
    for kind in kinds:
        for r in shape_ramps:
            for sh in shapes:
                if (kind,round(r,10),sh,tuple(map(float,PROBE))) in exp.cache:continue
                exp.try_evaluate(kind,r,sh,stage='shape_stress')
    # 4. First witnessed sign-change interval along r, genuine two-sided bisection.
    refined=[]
    for kind,lo0,hi0,flo0,fhi0 in duration_brackets[:args.max_brackets]:
        lo,hi,flo,fhi=lo0,hi0,flo0,fhi0
        iterations=[]
        for _ in range(args.bisection_steps):
            mid=.5*(lo+hi)
            case=exp.try_evaluate(kind,mid,'beta:2:2',stage='duration_bisection')
            if not case:break
            fm=case['margin_at_q065'];iterations.append([mid,fm])
            if fm==0:lo=hi=mid;break
            if flo*fm<0:hi,fhi=mid,fm
            else:lo,flo=mid,fm
        refined.append({'kind':kind,'r_lower':lo,'r_upper':hi,'margin_lower':flo,'margin_upper':fhi,
                         'boundary_estimate':.5*(lo+hi),'samples':iterations,
                         'sign_change_confirmed':bool(flo*fhi<0)})
    # 5. Dense phase checks only for r=.3 control and witnessed boundary-neighbor cases.
    dense_phase=np.linspace(.35,.65,args.dense_phase_points)
    for kind in kinds:
        exp.try_evaluate(kind,.3,'beta:2:2',tuple(dense_phase),stage='dense_control')
    for item in refined:
        kind=item['kind'];
        for r in (item['r_lower'],item['r_upper']):
            exp.try_evaluate(kind,r,'beta:2:2',tuple(dense_phase),stage='dense_boundary')
    save_csv('case_surveys.csv',exp.records)
    save_csv('phase_pair67_profiles.csv',exp.profiles)
    if exp.failures:save_csv('numerical_failures.csv',exp.failures)
    clock_rows=[]
    for sh in shapes:
        prop=properties(sh)
        if not prop['admissible']:raise RuntimeError('Invalid preflight shape '+sh)
        for t in np.linspace(0,1,201):
            from ramp_stress import h,area
            clock_rows.append({'shape':sh,'u':float(t),'h':float(h(t,sh)),
                 'clock_sign':float(1-2*h(t,sh)),
                 'phase_excursion_normalized':float(-t+2*area(t,sh)),
                 'monotone':int(prop['monotone'])})
    save_csv('shape_clock_controls.csv',clock_rows)
    surveyed=[r for r in exp.records if r['stage'] in ('duration_survey','shape_stress','baseline')]
    failures=exp.failures
    status=('BOUNDARY_BRACKETED_NUMERICALLY' if any(x['sign_change_confirmed'] for x in refined)
       else 'NO_ENDPOINT_CROSSING_FOUND_IN_TESTED_CASES')
    if failures:status+='__WITH_FAILED_CASES'
    rep={'audit':'v18.49o — Dominance-Boundary Continuation & Ramp-Shape Stress Audit',
         'status': 'SMOKE_ONLY' if args.smoke else ('FOCUSED_' + status if args.focus else status),
         'scope':'Q550; fixed initial kinetic metric tau=1; 11D original physical 10D original tangent',
         'parent':exp.ancestry,'baseline_parent_max_abs_share_error':exp.max_parent_error,
         'endpoint_phase_q':.65,'phase_probe_points':list(PROBE),
         'duration_scan':list(ramps),'shape_set':list(shapes),'shape_ramp_values':list(shape_ramps),
         'number_of_unique_cases':len({(r['kappa_kind'],r['ramp_xi'],r['shape']) for r in surveyed}),
         'number_of_evaluations':len(exp.records),'failed_evaluations':len(failures),
         'duration_brackets_initial':[{'kind':k,'r_low':l,'r_high':h,'margin_low':a,'margin_high':b} for k,l,h,a,b in duration_brackets],
         'duration_brackets_refined':refined,
         'shape_stress_endpoint_negative_cases':[r for r in surveyed if r['stage']=='shape_stress' and r['margin_at_q065']<0],
         'tested_duration_min_max':[min(ramps),max(ramps)],'integration_counts':exp.integrations,
         'numeric_controls':{'forward_regression':exp.regression,'max_mechanical_ledger_error':exp.ledger,
             'min_relative_eigen_gap':exp.gap_min,'max_parent_cubic_difference':exp.max_parent_error},
         'failed_case_details':failures,
         'limitations':['Sampled numerical brackets, not interval-certified topology or continuous-time roots.',
            'Changing ramp duration is distinct from changing shape at fixed duration.',
            'No universal domination beyond admissible shapes, sampled ramp ranges, or fixed kinetic metric.',
            'A sign change is a rank-pair contribution cross-over, not proof of physical torsion flip.',
            'Nonmonotonic recoil shapes may involve temporary re-acceleration without leaving clock rate [-1,1].',
            'If no opposing-signed endpoints found, no boundary is established.']}
    (ROOT/'results/report.json').write_text(json.dumps(rep,indent=2,allow_nan=False)+'\n')
    (ROOT/'results/environment.json').write_text(json.dumps({'python':platform.python_version(),
       'numpy':np.__version__,'scipy':__import__('scipy').__version__},indent=2)+'\n')
    return rep

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--smoke',action='store_true')
    ap.add_argument('--focus',action='store_true',help='Fast two-sided r=0.309 to 0.330 threshold audit for both kappa choices')
    ap.add_argument('--bisection-steps',type=int,default=7)
    ap.add_argument('--max-brackets',type=int,default=4)
    ap.add_argument('--dense-phase-points',type=int,default=61)
    ap.add_argument('--rtol',type=float,default=3e-12)
    ap.add_argument('--atol',type=float,default=3e-13)
    ap.add_argument('--max-step',type=float,default=.025)
    ap.add_argument('--frame-rtol',type=float,default=8e-11)
    ap.add_argument('--frame-atol',type=float,default=8e-13)
    ap.add_argument('--frame-max-step',type=float,default=.008)
    ap.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    ap.add_argument('--maximum-regression',type=float,default=1e-7)
    ap.add_argument('--maximum-parent-share-difference',type=float,default=2e-6)
    ap.add_argument('--max-generator-identity-error',type=float,default=1e-7)
    rep=run(ap.parse_args())
    print(json.dumps({k:rep[k] for k in ['status','number_of_unique_cases','number_of_evaluations',
          'failed_evaluations','duration_brackets_refined','numeric_controls']},indent=2))
