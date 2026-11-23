#!/usr/bin/env python3
"""v18.48k: observer-covector sphere geometry of analytic Hessian cancellation.

Uses the authenticated original 328 Q550 states from v18.48j; it does not
integrate new Q550 trajectories. No observer-only geodesic is called physical.
"""
from __future__ import annotations
import argparse,csv,json,math,sys
from pathlib import Path
import numpy as np
from verify_parent import verify
from observer_geometry import (unit,matrices,ratio_from_maps,principal_direction,
    tangent_to_sphere,rotate_observer,width_diagnostics,spectral_report,gauge_check)
ROOT=Path(__file__).resolve().parents[1]
def as_float(x):return float(x) if np.isfinite(x) else None
def write_csv(path,rows):
    if not rows:raise ValueError('Cannot save empty ledger')
    fields=list(rows[0]);assert all(list(row)==fields for row in rows)
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def crest_label(fam,xi):
    if fam.startswith('phaseblind') and abs(xi-3.575)<1e-9:return 'phaseblind_xi3.575'
    if fam.startswith('phasecov') and abs(xi-4.25)<1e-9:return 'phasecov_xi4.25'
    return None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output-dir',type=Path,default=ROOT/'results')
    ap.add_argument('--directions',type=int,default=64)
    ap.add_argument('--profile-points',type=int,default=121)
    args=ap.parse_args()
    if args.directions<16 or args.profile_points<31 or args.profile_points%2!=1:
        raise ValueError('Need >=16 transverse directions and >=31 odd profile points')
    out=args.output_dir.resolve();out.mkdir(exist_ok=True,parents=True)
    p=verify()
    sys.path.insert(0,str(ROOT/'reference'))
    from structural_jet import structural_jet,coupling_jet,chart_kernel
    from test_support_mobius_monodromy_audit import ModelParameters
    data=np.load(ROOT/'runtime/parent_j/runtime/physical_paths.npz',allow_pickle=False)
    rr=json.loads((ROOT/'runtime/parent_j/runtime/report_v18_48h.json').read_text())
    params=ModelParameters(gamma_rho=.3)
    sc=np.asarray(data['chart_scale'],float)
    slope=float(data['clock_speed'])/(2*math.pi)
    kappas={'original':float(rr['kappa_original']),'autonomous':float(rr['kappa_autonomous'])}
    if len(data['xi'])!=328 or sc.shape!=(10,):raise ValueError('Unexpected authenticated input')
    rng=np.random.default_rng(18484811)
    atlas=[];widths=[];profiles=[];spectra=[];gauge=[];sampling=[];crossing_checks=[];maps={};errors=[]
    S=np.diag([2.5,.38,1.7,.55,1.35,.8,1.2,.7,1.6,.65]);S[0,3]=.8;S[1,5]=-.25;S[4,8]=.6
    for idx in range(len(data['xi'])):
        xi=float(data['xi'][idx]);fam=str(data['families'][idx]);br=int(data['seed_branches'][idx]);kind=str(data['kappa_kind'][idx]);kap=kappas[kind]
        yy=np.asarray(data['y'][idx],float)
        f=structural_jet(yy,kap,params,slope)[0]
        Hb=structural_jet(yy,0.,params,slope)[2]
        Hc=slope*kap*coupling_jet(yy,params)[2]
        Lb,Lc=matrices(Hb,Hc,f,sc)
        graw=np.asarray(data['covectors'][idx,0,:10],float)
        g=unit(graw)
        R,nb,nc,nt,zero=ratio_from_maps(Lb,Lc,g)
        B0=chart_kernel(Hb,f,sc,g);C0=chart_kernel(Hc,f,sc,g)
        mm=max(np.linalg.norm(B0-Lb@g),np.linalg.norm(C0-Lc@g))/max(1.,nb,nc)
        errors.append(mm)
        if mm>3e-9:raise ValueError('Matrix/analytic chart kernel mismatch')
        rmetric=gauge_check(Lb,Lc,g,S)
        err=abs(R-rmetric)/max(1.,R)
        if err>2e-8:raise ValueError('Metric-covariant ratio mismatch')
        gauge.append(dict(family=fam,branch=br,kappa=kind,xi=xi,original_ratio=R,coherently_transformed_ratio=rmetric,relative_error=err))
        atlas.append(dict(family=fam,branch=br,kappa=kind,xi=xi,R=R,logR=math.log(R),norm_B=nb,norm_C=nc,norm_resultant=nt,coupling_null=zero,chart_observer_norm_before_normalization=float(np.linalg.norm(graw)),source='authenticated_v18.48j_IVP'))
        label=crest_label(fam,xi)
        if br!=0 or label is None:continue
        label=label+'_'+kind
        print('focal',label,'R',round(R,6),flush=True)
        d=principal_direction(Lb,Lc,g)
        half=R/2
        w=width_diagnostics(Lb,Lc,g,d)
        # Independently evaluate the ORIGINAL analytic Hessian contraction
        # at the observer-angle threshold, not merely the cached linear maps.
        for side,angle_deg in [('negative',-w[0]),('positive',w[1])]:
            gg=rotate_observer(g,d,math.radians(float(angle_deg)))
            b0=chart_kernel(Hb,f,sc,gg);c0=chart_kernel(Hc,f,sc,gg)
            n0=float(np.linalg.norm(b0));n1=float(np.linalg.norm(c0));ns=float(np.linalg.norm(b0+c0))
            direct=(n0+n1)/ns
            via=ratio_from_maps(Lb,Lc,gg)[0]
            crossing_checks.append(dict(crest=label,side=side,angle_deg=float(angle_deg),
                half_initial_ratio=half,analytic_direct_ratio=direct,linear_map_ratio=via,
                relative_ratio_discrepancy=abs(direct-via)/max(1.,direct),
                relative_distance_to_threshold=abs(via-half)/half,
                direct_norm_resultant=ns))
        main=dict(crest=label,family=fam,branch=br,kappa=kind,xi=xi,R0=R,
                  gradient_tangent_norm=float(np.linalg.norm(np.asarray(d))),
                  half_target=half,width_half_negative_deg=as_float(w[0]),width_half_positive_deg=as_float(w[1]),
                  width_half_total_deg=as_float(w[2]),width_R10_negative_deg=as_float(w[3]),width_R10_positive_deg=as_float(w[4]),
                  coupling_null=zero,norm_B=nb,norm_C=nc,norm_resultant=nt)
        widths.append(main)
        ss,st=spectral_report(Lb,Lc)
        for i,(sa,stot) in enumerate(zip(ss,st)):
            spectra.append(dict(crest=label,singular_index=i,stacked_source_sigma=float(sa),resultant_sigma=float(stot),
                 stacked_relative=float(sa/ss[0]),resultant_relative=float(stot/st[0])))
        # Diagnostic geodesic centered at the authenticated physical covector;
        # scan arcs at a scale set by the first half-height crossing.
        width=max(x for x in w[:2] if np.isfinite(x))
        span=max(10*width,1e-9)
        span=min(span,.1)
        angles=np.linspace(-span,span,args.profile_points)
        for angle in angles:
            gg=rotate_observer(g,d,math.radians(float(angle)))
            r,b,c,t,null=ratio_from_maps(Lb,Lc,gg)
            profiles.append(dict(crest=label,direction='steepest_local_log_gradient',angle_deg=float(angle),ratio=r,
                norm_B=b,norm_C=c,norm_resultant=t,coupling_null=null))
        # Directional geometry: deterministic random transverse tangents and
        # one gradient tangent; widths are SIGNED and are not asserted uniform.
        dirs=[('steepest_local_log_gradient',d)]
        for q in range(args.directions):
            du=tangent_to_sphere(g,rng.normal(size=10))
            dirs.append((f'random_tangent_{q:03d}',du))
        for name,du in dirs:
            wm,wp,wt,rm,rp=width_diagnostics(Lb,Lc,g,du)
            widths.append(dict(crest=label,family=fam,branch=br,kappa=kind,xi=xi,R0=R,
                 gradient_tangent_norm=None,half_target=half,
                 width_half_negative_deg=as_float(wm),width_half_positive_deg=as_float(wp),
                 width_half_total_deg=as_float(wt),width_R10_negative_deg=as_float(rm),width_R10_positive_deg=as_float(rp),
                 coupling_null=zero,norm_B=nb,norm_C=nc,norm_resultant=nt,
                 direction=name,alignment_with_steepest=float(du@d)))
        widths[-(args.directions+1)]['direction']='steepest_local_log_gradient' # explicit name for main record
        # Local random probe: uniform random tangent orientation at fixed angular radii.
        for angle in [1e-7,1e-6,1e-5,1e-4,1e-3,.01,.1,1.]:
            vals=[]
            for j in range(args.directions):
                du=tangent_to_sphere(g,rng.normal(size=10))
                vals.append(ratio_from_maps(Lb,Lc,rotate_observer(g,du,math.radians(angle)))[0])
            v=np.asarray(vals)
            sampling.append(dict(crest=label,angle_deg=angle,count=len(v),min_R=float(v.min()),median_R=float(np.median(v)),max_R=float(v.max()),
                       fraction_above_half_height=float(np.mean(v>=half)),fraction_above_10=float(np.mean(v>=10.))))
        maps[label]=(Lb,Lc,g,d)
    # Trim the repeated main direction record: one canonical record per direction.
    uniq=[];seen=set()
    for row in widths:
        if 'direction' not in row:continue
        key=(row['crest'],row['direction'])
        if key not in seen:uniq.append(row);seen.add(key)
    widths=uniq
    write_csv(out/'observer_crest_atlas.csv',atlas)
    write_csv(out/'observer_widths.csv',widths)
    write_csv(out/'observer_direction_profiles.csv',profiles)
    write_csv(out/'observer_random_sphere.csv',sampling)
    write_csv(out/'observer_singular_spectra.csv',spectra)
    write_csv(out/'covariant_metric_controls.csv',gauge)
    write_csv(out/'independent_crossing_checks.csv',crossing_checks)
    summaries=[]
    for label,(Lb,Lc,g,d) in maps.items():
        ss=[a for a in widths if a['crest']==label]
        tt=np.array([x['width_half_total_deg'] for x in ss if x['width_half_total_deg'] is not None])
        steep=next(x for x in ss if x['direction']=='steepest_local_log_gradient')
        summaries.append(dict(crest=label,ratio=steep['R0'],steep_half_width_total_deg=steep['width_half_total_deg'],
                     median_random_half_width_deg=float(np.median(tt[1:])),min_random_half_width_deg=float(np.min(tt[1:])),max_random_half_width_deg=float(np.max(tt[1:])),
                     observer_tangent_samples=args.directions,angular_space='10D historical Euclidean covector chart; not arbitrary-gauge Euclidean angle'))
    write_csv(out/'crest_width_summary.csv',summaries)
    report=dict(version='v18.48k',status='ORIGINAL_Q550_OBSERVER_SPACE_CANCEL_GEOMETRY_DIAGNOSTIC',
       parent='SHA-pinned authentic v18.48j server sendback, nested v18.48i and v18.48h verified',
       parent_provenance=p,physical_ivps=8,physical_states=328,
       new_integrations=0,parameter_values=kappas,focal_crests=4,
       observer_perturbations='Frozen chart covectors, not physical adjoint solution or independent observer',
       chart_metric='Original frozen 10D Euclidean chart; coherent anisotropic covector metric control',
       widths=summaries,observables=dict(observer_width_ledger=len(widths),random_angle_records=len(sampling),
          max_analytic_map_relative_error=max(errors),max_covariance_ratio_relative_error=max(x['relative_error'] for x in gauge),
          max_independent_crossing_ratio_error=max(z['relative_ratio_discrepancy'] for z in crossing_checks),
          max_crossing_threshold_relative_error=max(z['relative_distance_to_threshold'] for z in crossing_checks)),
       caveats=['Crest width is direction-dependent; angular volumes and total sphere measure are not certified.',
                'Observer rotations are frozen-state geometric counterfactuals, not integrated adjoint trajectories.',
                'Large ratios can be ill-conditioned near a tiny resultant; all numerator/resultant norms reported.',
                'The quotient observer space and effective numerical rank are scale- and cutoff-sensitive; raw singular spectra are provided.',
                'Gauge invariance requires transforming input and output covector cometrics; unchanged naive Euclidean angles are not invariant under shear.'])
    (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':report['status'],'physical_states':328,'focal_crests':4,
     'max_map_error':report['observables']['max_analytic_map_relative_error'],
     'max_covariance_error':report['observables']['max_covariance_ratio_relative_error'],
     'max_crossing_independent_error':report['observables']['max_independent_crossing_ratio_error'],
     'widths':summaries},indent=2))
if __name__=='__main__':main()
