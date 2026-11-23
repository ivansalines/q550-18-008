#!/usr/bin/env python3
"""v18.48x: genuine branch-resolved 11D contact-lobe numerical topology audit.

All physical initial conditions are recovered from the authenticated w
server sendback, with original byte-identical physics sources.
No topology/interval theorem is claimed. q=0 is excluded because the
geometric turn is an imposed trivial common-position contact.
"""
from __future__ import annotations
import argparse,csv,json,math,importlib.util,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import minimize_scalar
from verify_parent import verify
from lobe_math import THRESHOLDS,EXTENDED,PARENT,shapes,analyze,in_window,merger_diagnostic
ROOT=Path(__file__).resolve().parents[1]
FOCUS_RAMPS=(.275,.285,.290,.292,.294,.295,.296,.29625,.2965,.29675,.297,.29725,.2975,.298,.299,.300,.302,.305)
BASE_RAMPS={('phaseblind',0):(.275,.300),('phaseblind',1):(.07,),('phasecov',0):(.04,),('phasecov',1):(.335,)}
VELOCITY_INDICES=(1,3,5,7,9)
def mod(path,name):
    sp=importlib.util.spec_from_file_location(name,path)
    o=importlib.util.module_from_spec(sp);sys.modules[name]=o;sp.loader.exec_module(o)
    return o
def branch_key(f):
    if f.startswith('phaseblind'):return 'phaseblind'
    if f.startswith('phasecov'):return 'phasecov'
    raise ValueError('Unexpected original branch')
def csvwrite(path,rows):
    if not rows:return
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
def readcsv(path):
    with path.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def make_pair(phys,rmp,support,audit,k,params,slope,omega,y0,args,design=None):
    forward=design is None
    T=1. if forward else 1.+design.ramp
    theta=float(y0[10]);initial=np.r_[y0[:10],np.zeros(4)]
    def clock(t):return theta+omega*t if forward else theta-omega*rmp.cubic_phase_excursion(t,design)
    def rhs(t,z):
        sign=1. if forward else rmp.cubic_clock_sign(t,design)
        y=np.r_[z[:10],clock(t)]
        return np.r_[phys.rhs_from_original(y,k,params,slope,sign,support,audit)[:10],
                     phys.power_terms(y,k,params,slope,sign)]
    sol=solve_ivp(rhs,(0,T),initial,method='DOP853',rtol=args.rtol,atol=args.atol,
                  max_step=args.max_step,dense_output=True)
    if not sol.success:raise RuntimeError('Authentic model IVP failed: '+sol.message)
    def ev(t):
        z=sol.sol(t)
        if np.ndim(t)==0:return np.r_[z[:10],clock(float(t)),z[10:]]
        times=np.asarray(t,float)
        return np.vstack((z[:10],np.array([clock(float(x)) for x in times])[None,:],z[10:]))
    ef=ev(T);de=phys.energy(ef[:11],k,params)-phys.energy(y0,k,params)
    rel=abs(de-sum(ef[11:]))/max(1.,abs(de),sum(abs(ef[11:])))
    if rel>args.max_energy_residual:raise RuntimeError('Mechanical ledger failed: '+str(rel))
    return ev,rel

def run(args):
    w,v,u,t,s,r,j,prov=verify()
    phys=mod(ROOT/'reference/physical_math.py','x_original_phys')
    ramp=mod(ROOT/'reference/parent_ramp_math.py','x_original_ramp')
    p=r/'runtime/verified_parent/q550_kappa_counterflow_crossings_v18_48q_bundle/runtime/verified_parent/q550_kappa_counterflow_energy_v18_48p_bundle'
    support=mod(p/'reference/test_support_q550_support_ode_interval_residual_pilot_v1.py','x_original_support')
    audit=mod(p/'reference/test_support_mobius_monodromy_audit.py','x_original_audit')
    data=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    report_h=json.loads((j/'runtime/report_v18_48h.json').read_text())
    kappas={'original':float(report_h['kappa_original']),'autonomous':float(report_h['kappa_autonomous'])}
    omega=float(data['clock_speed']);slope=omega/(2*math.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    groups=defaultdict(list)
    for i in range(len(data['y'])):
        groups[(str(data['families'][i]),int(data['seed_branches'][i]),str(data['kappa_kind'][i]))].append(i)
    if len(groups)!=8 or len(data['y'])!=328:raise RuntimeError('Original history is not 8 x 41')
    keys=sorted(groups)
    if args.limit_groups:keys=keys[:args.limit_groups]
    parentw=readcsv(w/'results/combined_branch_contacts.csv')
    parentmap={(branch_key(z['family']),int(z['branch']),z['kappa_kind'],round(float(z['ramp_duration_xi']),6)):z for z in parentw}
    old=readcsv(w/'results/branch_resolved_window_summary.csv')
    out=args.output_dir;out.mkdir(parents=True,exist_ok=True)
    qgrid=np.linspace(EXTENDED[0],EXTENDED[1],args.phase_samples)
    oldgrid=np.linspace(PARENT[0],PARENT[1],args.parent_phase_samples)
    rows=[];profile=[];boundaries=[];regress=[];transitions=[];critical=[]
    max_replay=0.;max_energy=0.;max_width_regress=0.;integrations=0
    for key in keys:
        fam,b,kind=key
        ids=sorted(groups[key],key=lambda ix:float(data['xi'][ix]))
        if not np.allclose(data['xi'][ids],np.linspace(3.5,4.5,41),atol=1e-12):
            raise RuntimeError('Original physical clock sections changed')
        k=kappas[kind]
        F,bal=make_pair(phys,ramp,support,audit,k,params,slope,omega,np.asarray(data['y'][ids[0]],float),args)
        integrations+=1;max_energy=max(max_energy,bal)
        replay=max(float(np.linalg.norm(F(vv)[:11]-data['y'][ii])) for vv,ii in zip(np.linspace(0,1,41),ids))
        max_replay=max(max_replay,replay)
        if replay>1e-7:raise RuntimeError('Original physical replay failed')
        turn=F(1.)[:11].copy();turn[list(VELOCITY_INDICES)]*=-1.
        ramps=FOCUS_RAMPS if (branch_key(fam),b)==('phaseblind',0) else BASE_RAMPS[(branch_key(fam),b)]
        for rv in ramps:
            des=ramp.Design(f'cubic_{rv:.5f}','smoothstep',rv)
            R,bal=make_pair(phys,ramp,support,audit,k,params,slope,omega,turn,args,design=des)
            integrations+=1;max_energy=max(max_energy,bal)
            qs=qgrid; stateR=R(rv+qs).T;stateF=F(1.-qs).T
            dvec=shapes(stateR[:,:11])-shapes(stateF[:,:11]);gaps=np.linalg.norm(dvec,axis=1)
            def shape_gap(q):return float(np.linalg.norm(shapes(R(rv+float(q))[:11])-shapes(F(1.-float(q))[:11])))
            m1=minimize_scalar(shape_gap,method='bounded',bounds=(.38,.49),options={'xatol':1e-12}) if b==0 and branch_key(fam)=='phaseblind' else None
            m2=minimize_scalar(shape_gap,method='bounded',bounds=(.49,.64),options={'xatol':1e-12}) if b==0 and branch_key(fam)=='phaseblind' else None
            for threshold in THRESHOLDS:
                ext=analyze(qs,gaps,threshold,shape_gap)
                par=in_window(oldgrid,None,*PARENT,shape_gap,threshold)
                row={'family':fam,'family_short':branch_key(fam),'branch':b,'kappa_kind':kind,
                     'ramp_duration_xi':rv,'threshold':threshold,
                     'extended_q_min':EXTENDED[0],'extended_q_max':EXTENDED[1],
                     'components_extended':ext['component_count'],'components_parent_window':par['component_count'],
                     'extended_total_width_q':ext['total_width_q'],
                     'parent_total_width_q':par['total_width_q'],
                     'extended_left_clip':int(ext['touches_left_boundary']),
                     'extended_right_clip':int(ext['touches_right_boundary']),
                     'parent_left_clip':int(par['touches_left_boundary']),
                     'parent_right_clip':int(par['touches_right_boundary']),
                     'intervals_extended_json':json.dumps(ext['intervals'],separators=(',',':')),
                     'intervals_parent_json':json.dumps(par['intervals'],separators=(',',':')),
                     'inter_lobe_separation_q':ext['gap_between_first_two_q']}
                boundaries.append(row)
                if threshold==.01:
                    ss=stateR[int(np.argmin(gaps))][:11]
                    ff=stateF[int(np.argmin(gaps))][:11]
                    full=ss-ff
                    full[[2,6,10]]=((full[[2,6,10]]+np.pi)%(2*np.pi))-np.pi
                    firstlast=dict(row)
                    firstlast.update({'minimum_grid_gap':float(np.min(gaps)),
                                      'minimum_grid_q':float(qs[int(np.argmin(gaps))]),
                                      'minimum_grid_full11D_gap':float(np.linalg.norm(full)),
                                      'minimum_grid_energy_gap':float(phys.energy(ss,k,params)-phys.energy(ff,k,params)),
                                      'mechanical_ledger_relative_error':bal,
                                      'forward_replay_11D_error':replay})
                    rows.append(firstlast)
                    parent=parentmap.get((branch_key(fam),b,kind,round(rv,6)))
                    if parent:
                        diff=abs(float(parent['contact_total_q_0p01'])-par['total_width_q'])
                        max_width_regress=max(max_width_regress,diff)
                        regress.append({'family':fam,'branch':b,'kappa_kind':kind,'ramp':rv,
                             'parent_w_width':float(parent['contact_total_q_0p01']),
                             'recomputed_parent_width':par['total_width_q'],'absolute_width_error':diff})
                        if diff>3e-5:raise RuntimeError('Existing w lobe-width regression failed: '+str((key,rv,diff)))
            if (branch_key(fam),b)==('phaseblind',0):
                # Save all focus profiles for genuine 2D phase-ramp contour analysis.
                for q,g in zip(qs,gaps):
                    profile.append({'family':fam,'branch':b,'kappa_kind':kind,'ramp_duration_xi':rv,
                                    'common_phase_q':float(q),'geometric_gap_3D':float(g)})
            print(f'v18.48x {branch_key(fam)} b{b} {kind} ramp={rv:.5f} components={rows[-1]["components_extended"]}',flush=True)
        if (branch_key(fam),b)==('phaseblind',0) and not args.skip_critical_refinement:
            # Resolve the barrier between the two lobes independently from
            # the phase-grid crossing count. The local barrier maximum is
            # tracked in a fixed, declared q bracket near the merger.
            left,right=((.29625,.2965) if kind=='original' else (.2965,.29675))
            def barrier_at(rv):
                nonlocal integrations,max_energy
                d=ramp.Design(f'critical_{rv:.10f}','smoothstep',rv)
                rr,be=make_pair(phys,ramp,support,audit,k,params,slope,omega,turn,args,design=d)
                integrations+=1;max_energy=max(max_energy,be)
                def gap(q):return float(np.linalg.norm(shapes(rr(rv+float(q))[:11])-shapes(F(1.-float(q))[:11])))
                sol=minimize_scalar(lambda q:-gap(q),method='bounded',bounds=(.467,.5),options={'xatol':1e-13})
                if not sol.success or not .47<float(sol.x)<.49:
                    raise RuntimeError('Local inter-lobe saddle escaped fixed bracket')
                # Midpoint energies distinguish coincidence of projected
                # envelope edges from a full-state/energy recurrence.
                zr=rr(rv+sol.x)[:11];zf=F(1.-sol.x)[:11]
                delta=zr-zf;delta[[2,6,10]]=((delta[[2,6,10]]+np.pi)%(2*np.pi))-np.pi
                return {'kappa_kind':kind,'ramp_duration_xi':rv,'barrier_phase_q':float(sol.x),
                        'barrier_distance_3D':float(-sol.fun),
                        'barrier_minus_threshold':float(-sol.fun-.01),
                        'barrier_full_11D_gap':float(np.linalg.norm(delta)),
                        'barrier_energy_gap':float(phys.energy(zr,k,params)-phys.energy(zf,k,params))}
            a,beta=barrier_at(left),barrier_at(right)
            if not (a['barrier_minus_threshold']>0 and beta['barrier_minus_threshold']<0):
                raise RuntimeError('Critical topology bracket lacks positive/negative barrier signs')
            critical.extend([a,beta])
            for step in range(args.critical_bisection_steps):
                mid=.5*(left+right);entry=barrier_at(mid);entry['iteration']=step+1
                critical.append(entry)
                if entry['barrier_minus_threshold']>0:left=mid
                else:right=mid
            critical.append({'kappa_kind':kind,'ramp_duration_xi':.5*(left+right),
                'critical_bracket_left':left,'critical_bracket_right':right,
                'critical_bracket_width_xi':right-left,'is_final_bracket':1})
            print(f'v18.48x {kind} bracket: [{left:.10f}, {right:.10f}] width={right-left:.3g}',flush=True)
    for kind in ('original','autonomous'):
        samples=sorted((x for x in rows if x['family_short']=='phaseblind' and x['branch']==0 and x['kappa_kind']==kind),key=lambda r:r['ramp_duration_xi'])
        for a,b in zip(samples[:-1],samples[1:]):
            if int(a['components_extended'])==2 and int(b['components_extended'])==1:
                transitions.append({'family':'phaseblind','branch':0,'kappa_kind':kind,
                  'left_ramp_xi':a['ramp_duration_xi'],'right_ramp_xi':b['ramp_duration_xi'],
                  'bracket_width_xi':b['ramp_duration_xi']-a['ramp_duration_xi'],
                  'event_classification':merger_diagnostic(
                     {'component_count':a['components_extended'],'touches_left_boundary':bool(a['extended_left_clip']),
                      'touches_right_boundary':bool(a['extended_right_clip'])},
                     {'component_count':b['components_extended'],'touches_left_boundary':bool(b['extended_left_clip']),
                      'touches_right_boundary':bool(b['extended_right_clip'])}),
                  'left_intervals':a['intervals_extended_json'],'right_intervals':b['intervals_extended_json']})
    csvwrite(out/'extended_lobe_intervals.csv',boundaries)
    csvwrite(out/'focus_lobe_profiles.csv',profile)
    csvwrite(out/'phase_lobe_summary.csv',rows)
    csvwrite(out/'original_w_width_regression.csv',regress)
    csvwrite(out/'candidate_two_to_one_brackets.csv',transitions)
    csvwrite(out/'critical_barrier_refinement.csv',critical)
    nfocus=sum(1 for x in rows if x['family_short']=='phaseblind' and x['branch']==0)
    summary={'version':'v18.48x','status':'FULL_EIGHT_PATH_FLOATING_POINT_AUDIT' if len(keys)==8 else 'PARTIAL_ONLY',
       'historical_paths':len(keys),'actual_new_11D_integrations':integrations,
       'phase_samples_per_profile':len(qgrid),'extended_window':list(EXTENDED),'parent_window':list(PARENT),
       'focusing_on':'phaseblind branch 0 two kappa choices',
       'number_focus_ramps_per_kappa':len(FOCUS_RAMPS),'new_lobe_profile_rows':len(profile),
       'number_threshold_rows':len(boundaries),'number_new_matched_profile_rows':len(rows),
       'regression_rows':len(regress),'maximum_w_width_regression_error':max_width_regress,
       'maximum_original_11D_replay_error':max_replay,'maximum_energy_ledger_relative_error':max_energy,
       'candidate_two_to_one_transition_brackets':transitions,
       'refined_critical_brackets': [x for x in critical if x.get('is_final_bracket')==1],
       'critical_refinement_steps':args.critical_bisection_steps,'source':prov,
       'interpretation':'Finite-grid and root-refined numerical subthreshold-lobe merger; no interval topology proof; q=0 excluded as imposed turn contact.'}
    (out/'report.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'integrations':integrations,'max_balance':max_energy,'max_replay':max_replay,
                      'max_w_regression':max_width_regress,'candidate_mergers':transitions},indent=2),flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit-groups',type=int,default=0)
    parser.add_argument('--skip-critical-refinement',action='store_true',help='Cheap smoke only; full server run includes critical refinement')
    parser.add_argument('--critical-bisection-steps',type=int,default=9)
    parser.add_argument('--rtol',type=float,default=3e-12)
    parser.add_argument('--atol',type=float,default=3e-13)
    parser.add_argument('--max-step',type=float,default=.025)
    parser.add_argument('--max-energy-residual',type=float,default=1e-8)
    parser.add_argument('--phase-samples',type=int,default=1601)
    parser.add_argument('--parent-phase-samples',type=int,default=817)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'results')
    args=parser.parse_args()
    if args.phase_samples<401 or args.parent_phase_samples<401:raise ValueError('Insufficient phase grid')
    run(args)
