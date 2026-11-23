#!/usr/bin/env python3
"""Q550 v18.48z: authentic, phase-locked barrier normal form and contract test.

Parent Y: 46 exact numerical 11D IVPs and their archived phase-distance
profiles. Z independently integrates selected original 11D IVPs to obtain
continuously evaluated roots; no pixel interpolation used for this validation.

Physical interpretation is deliberately limited to one two-lobe family:
phaseblind branch0, two kappa values; cross-branch comparison is only a
screening of authenticated parent W summaries.
"""
from __future__ import annotations
import argparse,csv,json,math,sys,platform,importlib.util
from pathlib import Path
from collections import defaultdict
import numpy as np
import scipy
from scipy.optimize import brentq
from verify_parent import verify
from normal_form_math import fit_jet,normal_profile,polynomial_gap,asymptotic_gaps,contract_ratio,measured_bracketed_gap,affine_check
ROOT=Path(__file__).resolve().parents[1]
RAMPS=(.285,.292,.296333,.300,.305,.309)
DELTAS=(1e-5,3e-5,1e-4,3e-4)
WINDOWS=(.008,.012,.016)
VELOCITY=(1,3,5,7,9)

def dynamic(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj;spec.loader.exec_module(obj)
    return obj

def read_csv(path):
    with path.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
def write_csv(path,rows):
    if not rows:raise RuntimeError('No rows to write '+str(path))
    cols=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)

def archived_root(profileq,profiled,qb,threshold):
    """Only a SCREENING root from samples (not dense-IVP/root certificate)."""
    f=profiled-threshold
    center=int(np.searchsorted(profileq,qb))
    if not 2<center<len(profileq)-3:raise ValueError('Barrier outside sampled profile')
    crossings=[]
    for direction in (-1,1):
        i=center if direction==1 else center-1
        while 0<=i<len(f)-1:
            if f[i]*f[i+1]<=0:
                alpha=f[i]/(f[i]-f[i+1]) if f[i]!=f[i+1] else 0.
                crossings.append(float(profileq[i]+alpha*(profileq[i+1]-profileq[i])))
                break
            i+=direction
        else:raise ValueError('No local gap crossing at '+str(threshold))
    return abs(crossings[1]-crossings[0])

def archive_reanalysis(out,yroot):
    profiles=read_csv(yroot/'results/dense_contact_profiles.csv')
    bars=read_csv(yroot/'results/barrier_height_curvature.csv')
    grouped=defaultdict(list)
    for r in profiles:
        grouped[(r['kappa_kind'],round(float(r['ramp_duration_xi']),8))].append(
            (float(r['common_phase_q']),float(r['distance_3D'])))
    jets=[];predictions=[]
    for row in bars:
        kind=row['kappa_kind'];ramp=float(row['ramp_duration_xi']);key=(kind,round(ramp,8))
        arr=np.asarray(grouped[key],float)
        arr=arr[np.argsort(arr[:,0])]
        qs,ds=arr[:,0],arr[:,1]
        B=float(row['barrier_distance_3D']);qb=float(row['barrier_phase_q']);C=float(row['barrier_curvature_q2_richardson'])
        if not C<-1 or not .46<qb<.51:raise RuntimeError('Historical nondegenerate barrier lost')
        for window in WINDOWS:
            for degree in (4,6):
                fit=fit_jet(qs,ds,qb,B,window,degree)
                d=fit['derivatives']
                jets.append({'kappa_kind':kind,'ramp_duration_xi':ramp,'window_q':window,'degree':degree,
                             'barrier_phase':qb,'barrier_height':B,'parent_dense_curvature':C,
                             'fitted_first':d[1],'fitted_curvature':d[2],'fitted_cubic':d[3],
                             'fitted_quartic':d[4],'fitted_fifth':d.get(5,float('nan')),
                             'fitted_sixth':d.get(6,float('nan')),
                             'relative_curvature_discrepancy':abs(d[2]-C)/abs(C),
                             'rms_profile_fit':fit['rms_fit_error'],'max_profile_fit':fit['max_abs_fit_error']})
        d4=fit_jet(qs,ds,qb,B,.012,4)['derivatives']
        d6=fit_jet(qs,ds,qb,B,.012,6)['derivatives']
        for delta in DELTAS:
            th=B-delta
            G=archived_root(qs,ds,qb,th)
            quad,asym_corr,correction=asymptotic_gaps(delta,C,d4[3],d4[4])
            quartic=polynomial_gap(B,d4,4,delta)
            sextic=polynomial_gap(B,d6,6,delta)
            ratio=contract_ratio(G,delta,C)
            predictions.append({'kappa_kind':kind,'ramp_duration_xi':ramp,
                 'barrier_minus_level':delta,'level_d3':th,'parent_grid_gap_q':G,
                 'parent_grid_sampling_step_q':.0005,
                 'contract_I_from_parent_grid':ratio,
                 'quadratic_pred_gap_q':quad,'quartic_pred_gap_q':quartic,
                 'sextic_pred_gap_q':sextic,'asymptotic_d3d4_gap_q':asym_corr,
                 'quartic_vs_parent_grid_relerr':abs(quartic-G)/G,
                 'quadratic_vs_parent_grid_relerr':abs(quad-G)/G,
                 'sextic_vs_parent_grid_relerr':abs(sextic-G)/G,
                 'affine_gauge_contract_residual':abs(ratio-affine_check(G,delta,C))})
    write_csv(out/'normal_form_jets.csv',jets)
    write_csv(out/'parent_grid_gap_screen.csv',predictions)
    return bars,jets,predictions

def branch_screening(yroot,out):
    matches=list(yroot.rglob('branch_resolved_window_summary.csv'))
    if len(matches)!=1:raise RuntimeError('Expected authenticated W summary in unique ancestor, found '+str(len(matches)))
    data=read_csv(matches[0]);rows=[]
    for d in data:
        rows.append({'family':d['family'],'branch':d['branch'],'kappa_kind':d['kappa_kind'],
          'best_3D_distance_in_W':d['best_sampled_3D_gap'],
          'full_11D_distance_in_W':d['11D_gap_at_best_shape_contact'],
          'best_ramp_in_W':d['best_sampled_ramp_xi'],
          'W_result_scope':'25-ramp contact-width screening only, NOT a demonstrated 2-lobe central barrier'})
    write_csv(out/'historical_W_cross_branch_screen.csv',rows)
    return rows

def continuous_replay(args,yroot,j,out,bars):
    phys=dynamic(ROOT/'reference/physical_math.py','z_original_11d_math')
    ramp=dynamic(ROOT/'reference/parent_ramp_math.py','z_original_smoothstep_math')
    lobe=dynamic(ROOT/'reference/parent_lobe_math.py','z_original_lobe_math')
    yrunner=dynamic(ROOT/'reference/y_original_run_audit.py','z_byte_identical_y_runner')
    src=list(yroot.rglob('test_support_q550_support_ode_interval_residual_pilot_v1.py'))
    if len(src)!=1:raise RuntimeError('Historical physical RHS source not unique')
    support=dynamic(src[0],'z_original_support_field')
    audit=dynamic(src[0].parent/'test_support_mobius_monodromy_audit.py','z_original_support_audit')
    data=np.load(j/'runtime/physical_paths.npz',allow_pickle=False)
    hist=json.loads((j/'runtime/report_v18_48h.json').read_text())
    ks={'original':float(hist['kappa_original']),'autonomous':float(hist['kappa_autonomous'])}
    omega=float(data['clock_speed']);slope=omega/(2*math.pi)
    params=audit.ModelParameters(gamma_rho=.3)
    groups=defaultdict(list)
    for i in range(len(data['y'])):
        groups[(str(data['families'][i]),int(data['seed_branches'][i]),str(data['kappa_kind'][i]))].append(i)
    by_barrier={(row['kappa_kind'],round(float(row['ramp_duration_xi']),8)):row for row in bars}
    output=[];runs=0;max_replay=0;max_ledger=0
    for kind in ('original','autonomous'):
        key=next((g for g in groups if g[0].startswith('phaseblind') and g[1]==0 and g[2]==kind),None)
        if key is None:raise RuntimeError('Missing historical phaseblind branch0')
        ids=sorted(groups[key],key=lambda i:float(data['xi'][i]));start=np.asarray(data['y'][ids[0]],float)
        k=ks[kind]
        forward,err=yrunner.integrate(phys,ramp,support,audit,k,params,slope,omega,start,args)
        runs+=1;max_ledger=max(max_ledger,err)
        replay=max(float(np.linalg.norm(forward(t)[:11]-data['y'][ix]))
                   for t,ix in zip(np.linspace(0,1,41),ids))
        max_replay=max(max_replay,replay)
        if replay>1e-7:raise RuntimeError('11D historical trajectory failed')
        turn=forward(1.)[:11].copy();turn[list(VELOCITY)]*=-1.
        for rv in RAMPS:
            back,ledger=yrunner.integrate(phys,ramp,support,audit,k,params,slope,omega,turn,args,
                 design=ramp.Design('z_cubic_'+str(rv),'smoothstep',rv))
            runs+=1;max_ledger=max(max_ledger,ledger)
            def gap(q):
                zr=back(rv+float(q))[:11];zf=forward(1.-float(q))[:11]
                return float(np.linalg.norm(lobe.shapes(zr)-lobe.shapes(zf)))
            r=by_barrier[(kind,round(rv,8))]
            qb=float(r['barrier_phase_q']);B=float(r['barrier_distance_3D']);C=float(r['barrier_curvature_q2_richardson'])
            if abs(gap(qb)-B)>2e-7:raise RuntimeError('Dense 11D physical replay differs from Y barrier')
            qgrid=qb+np.linspace(-.033,.033,133)
            ds=np.array([gap(q) for q in qgrid])
            d4=fit_jet(qgrid,ds,qb,B,.012,4)['derivatives']
            d6=fit_jet(qgrid,ds,qb,B,.012,6)['derivatives']
            zr=back(rv+qb)[:11];zf=forward(1.-qb)[:11]
            diff=zr-zf;diff[[2,6,10]]=(diff[[2,6,10]]+np.pi)%(2*np.pi)-np.pi
            full=float(np.linalg.norm(diff))
            for delta in DELTAS:
                actual,left,right=measured_bracketed_gap(gap,qb,delta)
                g2,g_corr,_=asymptotic_gaps(delta,C,d4[3],d4[4])
                g4=polynomial_gap(B,d4,4,delta)
                g6=polynomial_gap(B,d6,6,delta)
                output.append({'kappa_kind':kind,'ramp_duration_xi':rv,'delta_B_minus_threshold':delta,
                     'threshold_d3':B-delta,'barrier_phase':qb,'barrier_height':B,
                     'dense_IVP_left_root_q':left,'dense_IVP_right_root_q':right,
                     'true_dense_IVP_gap_q':actual,'quadratic_gap_q':g2,
                     'quartic_jet_gap_q':g4,'sextic_jet_gap_q':g6,'quartic_asymptotic_gap_q':g_corr,
                     'ratio_I_dense_IVP':contract_ratio(actual,delta,C),
                     'quadratic_relative_gap_error':abs(g2-actual)/actual,
                     'quartic_relative_gap_error':abs(g4-actual)/actual,
                     'sextic_relative_gap_error':abs(g6-actual)/actual,
                     'asymptotic_relative_gap_error':abs(g_corr-actual)/actual,
                     'cubic_jet':d4[3],'quartic_jet':d4[4],
                     'barrier_full_11D_distance':full,
                     'barrier_energy_gap':float(phys.energy(zr,k,params)-phys.energy(zf,k,params)),
                     'parent_barrier_replay_abs_error':abs(gap(qb)-B)})
            print(f'Z physical {kind:10} ramp={rv:.6f} B={B:.9f} full11D={full:.4f}',flush=True)
    write_csv(out/'continuous_11D_root_validation.csv',output)
    return output,runs,max_replay,max_ledger

def main():
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('--rtol',type=float,default=3e-12)
    a.add_argument('--atol',type=float,default=3e-13)
    a.add_argument('--max-step',type=float,default=.025)
    a.add_argument('--maximum-ledger-error',type=float,default=1e-8)
    a.add_argument('--output-dir',type=Path,default=ROOT/'results')
    a.add_argument('--parent-only',action='store_true',help='Archived authentic-Y normal-form screening; skip fresh 11D integrations')
    args=a.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
    yroot,xroot,j,provenance=verify()
    bars,jets,preds=archive_reanalysis(args.output_dir,yroot)
    branch=branch_screening(yroot,args.output_dir)
    fresh=[];runs=0;max_replay=0.;max_ledger=0.
    if not args.parent_only:
        fresh,runs,max_replay,max_ledger=continuous_replay(args,yroot,j,args.output_dir,bars)
    original=[r for r in fresh if r['kappa_kind']=='original']
    rel_fit=[float(r['relative_curvature_discrepancy']) for r in jets if r['degree']==4 and r['window_q']==.012]
    summary={'version':'v18.48z','status':'FULL_AUTHENTIC_11D_NORMAL_FORM_DIAGNOSTIC' if fresh else 'AUTHENTIC_PARENT_ONLY_SCREEN',
        'parent_Y_sha256':provenance['historical_parent_sha256'],'parent_authenticated_11D_profiles':len(bars),
        'historical_original_11D_states':328,'cross_branch_W_screen_rows':len(branch),
        'fresh_11D_integration_count':runs,'fresh_continuous_root_comparisons':len(fresh),
        'archived_grid_root_comparisons':len(preds),'high_order_jet_fits':len(jets),
        'maximum_relative_jet_curvature_deviation_in_selected_window':max(rel_fit),
        'max_full_11D_replay_error':max_replay,'maximum_mechanical_ledger_relative_error':max_ledger,
        'max_quadratic_relative_gap_error_direct':max([float(r['quadratic_relative_gap_error']) for r in fresh],default=None),
        'max_quartic_relative_gap_error_direct':max([float(r['quartic_relative_gap_error']) for r in fresh],default=None),
        'max_sextic_relative_gap_error_direct':max([float(r['sextic_relative_gap_error']) for r in fresh],default=None),
        'minimum_full_11D_separation_direct':min([float(r['barrier_full_11D_distance']) for r in fresh],default=None),
        'max_affine_parameterization_ratio_error':max(float(r['affine_gauge_contract_residual']) for r in preds),
        'model_conclusion':'Near-critical squared-gap ratio follows smooth nondegenerate-maximum Taylor geometry; not a physical invariant, universal critical exponent theorem, or material-lobe merger.',
        'scope':'Physical direct validation only phaseblind branch0, both kappa values, six ramp durations per kappa; other branches only authenticated W negative/contrast screening.'}
    (args.output_dir/'report.json').write_text(json.dumps(summary,indent=2)+'\n')
    (args.output_dir/'runtime_environment.json').write_text(json.dumps({'python':platform.python_version(),
        'numpy':np.__version__,'scipy':scipy.__version__},indent=2)+'\n')
    print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
