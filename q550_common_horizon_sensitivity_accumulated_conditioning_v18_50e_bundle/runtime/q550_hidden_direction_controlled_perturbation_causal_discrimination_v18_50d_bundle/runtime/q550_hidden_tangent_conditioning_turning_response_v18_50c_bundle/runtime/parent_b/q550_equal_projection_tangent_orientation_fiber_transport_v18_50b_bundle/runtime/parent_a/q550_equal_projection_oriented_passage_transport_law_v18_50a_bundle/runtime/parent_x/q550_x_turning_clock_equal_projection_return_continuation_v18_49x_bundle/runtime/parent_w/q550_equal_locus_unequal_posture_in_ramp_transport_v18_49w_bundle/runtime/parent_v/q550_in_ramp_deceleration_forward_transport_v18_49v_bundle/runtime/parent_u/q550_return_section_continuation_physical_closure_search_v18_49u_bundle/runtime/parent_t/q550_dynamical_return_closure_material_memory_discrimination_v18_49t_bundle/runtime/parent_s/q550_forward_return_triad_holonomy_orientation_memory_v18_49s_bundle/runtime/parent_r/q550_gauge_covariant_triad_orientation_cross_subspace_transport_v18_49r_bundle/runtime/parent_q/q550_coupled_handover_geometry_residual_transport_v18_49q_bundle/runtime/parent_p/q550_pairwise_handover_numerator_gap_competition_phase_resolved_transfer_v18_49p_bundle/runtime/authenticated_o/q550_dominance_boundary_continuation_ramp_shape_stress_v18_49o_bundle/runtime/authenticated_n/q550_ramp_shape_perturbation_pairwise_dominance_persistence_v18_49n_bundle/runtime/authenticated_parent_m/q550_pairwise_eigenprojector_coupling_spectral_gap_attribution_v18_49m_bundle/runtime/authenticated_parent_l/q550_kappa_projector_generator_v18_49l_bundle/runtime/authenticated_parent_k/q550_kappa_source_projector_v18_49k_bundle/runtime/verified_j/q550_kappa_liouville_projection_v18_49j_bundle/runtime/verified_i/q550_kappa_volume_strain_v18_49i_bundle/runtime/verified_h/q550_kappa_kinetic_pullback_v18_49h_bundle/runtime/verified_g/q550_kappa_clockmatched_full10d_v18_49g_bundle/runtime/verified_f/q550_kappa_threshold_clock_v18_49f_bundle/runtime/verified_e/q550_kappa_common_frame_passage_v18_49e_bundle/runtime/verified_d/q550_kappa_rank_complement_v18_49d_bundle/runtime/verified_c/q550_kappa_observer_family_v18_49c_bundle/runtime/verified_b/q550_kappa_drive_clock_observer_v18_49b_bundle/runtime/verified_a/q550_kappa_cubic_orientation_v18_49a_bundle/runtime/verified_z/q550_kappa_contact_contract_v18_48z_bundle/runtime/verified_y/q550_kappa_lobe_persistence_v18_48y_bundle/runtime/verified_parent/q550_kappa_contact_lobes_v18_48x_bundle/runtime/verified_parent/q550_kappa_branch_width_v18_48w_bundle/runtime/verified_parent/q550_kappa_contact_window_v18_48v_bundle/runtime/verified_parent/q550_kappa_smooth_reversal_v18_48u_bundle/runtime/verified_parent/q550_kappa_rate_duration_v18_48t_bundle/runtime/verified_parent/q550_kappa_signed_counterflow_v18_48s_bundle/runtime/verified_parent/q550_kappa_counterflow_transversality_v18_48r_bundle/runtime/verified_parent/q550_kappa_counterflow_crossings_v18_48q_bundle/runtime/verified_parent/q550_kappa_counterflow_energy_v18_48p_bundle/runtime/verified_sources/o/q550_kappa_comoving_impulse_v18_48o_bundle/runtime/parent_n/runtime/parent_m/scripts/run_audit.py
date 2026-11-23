#!/usr/bin/env python3
"""Q550 v18.48m: principal-angle subspace transport / apparent vs shared directions.

Input original 328 states inherited SHA-pinned from v18.48l. No Q550 rerun.
Source-active and cancellation planes are numerical cutoff-dependent constructs.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,math,platform,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'reference')]
from verify_parent import verify
from principal_geometry import (principal,principal_candidates,source_active_subspaces,
 evaluate_shared_direction,projected_line_angle)
from structural_jet import structural_jet,coupling_jet
from observer_geometry_v18_48k import matrices
from test_support_mobius_monodromy_audit import ModelParameters

def save_csv(p,rows):
    if not rows:raise ValueError(f'Empty output {p}')
    cols=list(rows[0]);
    if any(list(row)!=cols for row in rows):raise ValueError('Inconsistent CSV schema')
    with open(p,'w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(rows)

def maps_at(y,k,p,speed,scale):
    f=structural_jet(y,k,p,speed)[0]
    hb=structural_jet(y,0,p,speed)[2]
    hc=speed*k*coupling_jet(y,p)[2]
    return matrices(hb,hc,f,scale)

def choose_projection(g0,g1):
    axes=[(0,2),(0,5),(1,5),(2,6),(3,7),(8,9)]
    out=[]
    for ab in axes:
        phi,n0,n1=projected_line_angle(g0,g1,ab)
        if phi is not None:out.append((phi,n0,n1,ab))
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source-cutoffs',default='1e-4,1e-6,1e-8,1e-10,1e-12')
    ap.add_argument('--cancel-cutoffs',default='1e-3,1e-2,5e-2')
    ap.add_argument('--near-angle-deg',type=float,default=0.01)
    ap.add_argument('--output-dir',type=Path,default=ROOT/'results')
    args=ap.parse_args()
    source_cutoffs=[float(s) for s in args.source_cutoffs.split(',')]
    cancel_cutoffs=[float(s) for s in args.cancel_cutoffs.split(',')]
    if not source_cutoffs or not cancel_cutoffs or any(not 0<s<1 for s in source_cutoffs+cancel_cutoffs):raise ValueError('Invalid cutoffs')
    if source_cutoffs!=sorted(source_cutoffs,reverse=True) or cancel_cutoffs!=sorted(cancel_cutoffs):raise ValueError('Sort cutoffs')
    out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=True)
    provenance=verify()
    f=ROOT/'runtime/parent_k/runtime/parent_j/runtime/physical_paths.npz'
    pdata=np.load(f,allow_pickle=False)
    par=ModelParameters(gamma_rho=.3)
    hist=json.loads((ROOT/'runtime/parent_k/runtime/parent_j/runtime/report_v18_48h.json').read_text())
    kap={'original':float(hist['kappa_original']),'autonomous':float(hist['kappa_autonomous'])}
    sc=np.asarray(pdata['chart_scale'],float);speed=float(pdata['clock_speed'])/(2*math.pi)
    n=len(pdata['xi']);assert n==328
    groups=defaultdict(list)
    for i in range(n):
        fam=str(pdata['families'][i]);branch=int(pdata['seed_branches'][i]);kind=str(pdata['kappa_kind'][i]);xi=float(pdata['xi'][i]);k=kap[kind]
        b,c=maps_at(np.asarray(pdata['y'][i],float),k,par,speed,sc)
        groups[(fam,branch,kind)].append(dict(xi=xi,B=b,C=c,index=i))
    for rows in groups.values():rows.sort(key=lambda x:x['xi'])
    assert len(groups)==8 and all(len(v)==41 for v in groups.values())
    atlas=[];steps=[];checks=[];projection=[]
    for (family,branch,kappa),rows in sorted(groups.items()):
        # Crossings are evaluated only within a single original physical trajectory.
        for cutoff in source_cutoffs:
          for cancel in cancel_cutoffs:
            prev=None
            for record in rows:
                B,C=record['B'],record['C'];xi=record['xi']
                s=source_active_subspaces(B,C,cutoff,cancel)
                atlas.append(dict(family=family,branch=branch,kappa=kappa,xi=xi,
                  source_cutoff=cutoff,cancel_cutoff=cancel,source_rank=s['source_rank'],
                  cancellation_rank=s['near_rank'],generalized_sigma_min=s['generalized_min'],
                  generalized_sigma_second=s['generalized_second'],
                  active_source_min=s['source_last'],source_max=s['source_sigma_max']))
                if prev is None:prev=(record,s);continue
                old,ps=prev;prev=(record,s)
                sg=principal(ps['src'],s['src']);cg=principal(ps['near'],s['near'])
                a0=ps['near_rank'];a1=s['near_rank']
                pairs=principal_candidates(ps['near'],s['near'])
                overlap=next((pair for pair in pairs[:1]),None) if pairs else None
                best=overlap[2] if overlap else None
                vals=(evaluate_shared_direction(old['B'],old['C'],B,C,best)
                  if best is not None else dict(source_a=None,source_b=None,resultant_a=None,resultant_b=None,
                    source_relative_a=None,source_relative_b=None,residual_over_source_a=None,residual_over_source_b=None))
                principal_angles=cg['angles_deg']
                src_angles=sg['angles_deg']
                steps.append(dict(family=family,branch=branch,kappa=kappa,xi_a=old['xi'],xi_b=xi,
                  source_cutoff=cutoff,cancel_cutoff=cancel,
                  source_rank_a=ps['source_rank'],source_rank_b=s['source_rank'],
                  cancellation_rank_a=a0,cancellation_rank_b=a1,
                  source_projector_frobenius=sg['frobenius_gap'],
                  source_projector_spectral=sg['spectral_gap'],
                  source_max_principal_deg=max(src_angles) if src_angles else None,
                  source_min_principal_deg=min(src_angles) if src_angles else None,
                  source_numerical_shared_below_0p01deg=int(sum(x<args.near_angle_deg for x in src_angles)),
                  source_mandatory_intersection_dimension=sg['mandatory_intersection_dimension'],
                  near_projector_frobenius=cg['frobenius_gap'],
                  near_projector_spectral=cg['spectral_gap'],
                  near_max_principal_deg=max(principal_angles) if principal_angles else None,
                  near_min_principal_deg=min(principal_angles) if principal_angles else None,
                  numerical_shared_below_0p01deg=int(sum(x<args.near_angle_deg for x in principal_angles)),
                  mathematically_mandatory_min_intersection=cg['mandatory_intersection_dimension'],
                  candidate_source_a=vals['source_a'],candidate_source_b=vals['source_b'],
                  candidate_resultant_a=vals['resultant_a'],candidate_resultant_b=vals['resultant_b'],
                  candidate_source_relative_a=vals['source_relative_a'],candidate_source_relative_b=vals['source_relative_b'],
                  candidate_residual_over_source_a=vals['residual_over_source_a'],
                  candidate_residual_over_source_b=vals['residual_over_source_b'],
                  cutoff_defined_not_certified=True))
                # Projection controls use selected principal pair and compare their actual angle in 10D
                if overlap is not None:
                  u,v,g,c0=overlap
                  true_angle=float(np.rad2deg(np.arccos(np.clip(abs(float(u@v)),0,1))))
                  for ph,n0,n1,axes in choose_projection(u,v):
                    projection.append(dict(family=family,branch=branch,kappa=kappa,
                      xi_a=old['xi'],xi_b=xi,source_cutoff=cutoff,cancel_cutoff=cancel,
                      coordinate_pair=str(axes),projection_angle_deg=ph,
                      full_10D_angle_deg=true_angle,
                      projection_norm_a=n0,projection_norm_b=n1,
                      projection_artifact_candidate=bool(ph<1 and true_angle>10 and min(n0,n1)>1e-4)))
                if cutoff in (1e-6,1e-10) and cancel==1e-2 and overlap is not None:
                  checks.append(dict(family=family,branch=branch,kappa=kappa,xi_a=old['xi'],xi_b=xi,
                    source_cutoff=cutoff,cancel_cutoff=cancel,
                    min_principal_angle_deg=min(principal_angles),
                    candidate_shared_source_detectable_both=bool(vals['source_relative_a']>cutoff and vals['source_relative_b']>cutoff),
                    candidate_near_cancel_both=bool(vals['residual_over_source_a']<cancel and vals['residual_over_source_b']<cancel),
                    interpretation='CANDIDATE_ONLY_NO_EXACT_INTERSECTION_PROOF'))
            print(f'v18.48m {family[:10]} b{branch} {kappa} source={cutoff:g} cancel={cancel:g}',flush=True)
    save_csv(out/'subspace_atlas.csv',atlas)
    save_csv(out/'adjacent_principal_angles.csv',steps)
    save_csv(out/'shared_direction_checks.csv',checks)
    save_csv(out/'projection_false_crossings.csv',projection)
    a=np.array([float(q['near_projector_spectral']) for q in steps if q['near_projector_spectral'] is not None])
    flagged=[q for q in projection if q['projection_artifact_candidate']]
    rchanges=[q for q in steps if q['cancellation_rank_a']!=q['cancellation_rank_b']]
    fixed=[q for q in steps if q['source_cutoff']==1e-6 and q['cancel_cutoff']==1e-2]
    summary=dict(version='v18.48m',classification='AUTHENTICATED_NUMERICAL_SUBSPACE_INTERSECTION_DIAGNOSTIC',
      original_states=n,original_physical_trajectories=len(groups),new_integrations=0,
      source_cutoffs=source_cutoffs,cancellation_cutoffs=cancel_cutoffs,
      input_sha256=hashlib.sha256(f.read_bytes()).hexdigest(),provenance=provenance,
      rows_atlas=len(atlas),rows_steps=len(steps),rows_projection=len(projection),
      adjacent_max_projector_gap=float(np.max(a)) if len(a) else None,
      rank_changes_total=len(rchanges),projection_artifact_candidates=len(flagged),
      reference_fixed_source_1e_6_cancel_1e_2=dict(
        comparisons=len(fixed),rank_changes=sum(q['cancellation_rank_a']!=q['cancellation_rank_b'] for q in fixed),
        active_intersection_candidates=sum(q['numerical_shared_below_0p01deg']>0 for q in fixed),
        median_projector_gap=float(np.median([q['near_projector_spectral'] for q in fixed]))),
      warnings=['All subspaces defined by numerical relative cutoffs, not exact ranks.',
        'A principal angle near zero is a numerical proximity signal, not a proof of exact shared vectors.',
        'Projected 2D overlaps can be false intersections in 10D.',
        'Dimension-forced intersection is distinguished from near cancellation and requires source activity.',
        'Frozen normalized ten-dimensional covector chart: no physical observer adjoint transport performed.',
        'Input physical paths come from v18.48h and are float64 Q550 states; no new Q550 integrations.'])
    (out/'report.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:summary[k] for k in ('version','original_states','rows_atlas','rows_steps','rank_changes_total','projection_artifact_candidates','reference_fixed_source_1e_6_cancel_1e_2')},indent=2))
if __name__=='__main__':main()
