# Q550 v18.49j — Liouville Source-Cancellation & Directional Strain Projection Audit

**Status:** authentic Q550 numerical audit, not a proof of a universal invariant or a new physical conservation law.

## Scientific target

Reintegrate genuine 11D return trajectories and their 10D material fundamental matrices, using the independent v18.49i **server sendback** exactly as uploaded. Verify the lineage recursively through H, G, F, E, D, C, B, A, Z, Y and J. Inspect the observed near-cancellation between κ₀-induced changes in integrated solver divergence and kinetic metric density, and separate two ways strain-axis occupation can evolve.

## Exact material density and source

The authenticated kinetic embedding is `H(y)=(Q(y),tau_ref V(y))`. For material coordinates `y=(l1,v1,theta1,w1,l2,v2,theta2,w2,z,vz)` and `x=sigmoid(z)`, its Jacobian determinant satisfies

```
log |det DH| = 5 log(tau_ref) + log(m_x)
             + 4*l1 + 4*l2 + 2*log(x*(1-x)).
grad_y log |det DH| = (4,0,0,0, 4,0,0,0, 2*(1-2*x),0).
```

On the actual 11D solution with a prescribed clock protocol, let `A(t)=dF_material/dy`. The declared kinetic material volume source is

```
s_kinetic(t)=tr(A(t)) + f_material(t) dot grad_y log |det DH(y(t))|.

log J_kinetic(t)= integral_0^t s_kinetic(s) ds
                = log|det Phi(t)| + log |det DH_end/det DH_start|.
```

All three are compared. The original analytic coupling `coupling_jet` has zero 10D trace at fixed state: the explicit κ derivative of the material divergence vanishes. κ nonetheless changes **the physical state history** and hence the evaluated trace and volume density; no absence of κ dependence is inferred.

## Geometric occupation derivative

For genuine kinetic-frame Cauchy–Green principal axes `a_i(t)`, define **sign-invariant** projectors `P_i=a_i a_i^T`. Let `u(t)` be the unit vector of the finite forward–return difference pulled to the initial kinetic frame by the genuine 10D tangent matrix. The occupation fractions are `p_i=u^T P_i u`, with exact differential identity

```
p_i' = 2 u'^T P_i u + u^T P_i' u.
       [moving direction] [rotating eigenprojector]
```

Finite differences on a 61-sample clock grid `q=0.35..0.65` measure the terms. The occupation sums to one for a complete orthonormal eigenbasis. These are **geometric projections, not energy flow between modes**. The finite gap itself is not an exact Jacobi field. Individual rank axes are meaningful only where eigenvalue gaps resolve their directions. The parent I has already measured the top spectral gap, but this J does not prove all lower gaps remain isolated; interpretations of rank 8 and 10 are restricted to the resolved samples.

## Independent checks and controls

1. Exact kinetic Jacobian determinant and finite-difference gradient, plus direct parent I regression of all ten squared occupations at `q=0.50`.
2. Analytic `kappa` coupling-trace audit at every source sample.
3. Independent Liouville volume and metric-density rate integrations, split at the command ramp boundary, against the independently integrated tangent-matrix determinant.
4. Clock-matched local κ source differences at 61 phases for each of six reversal ramps.
5. A **counterfactual different volume form** `exp(alpha*(l1-l2)) * physical_kinetic_volume`, for `alpha = -2,-1,0,1,2`. This is NOT an ordinary coordinate change of the *same* volume form; its changing κ contrast tests how strong the near-cancellation claim really is.
6. Occupation rate split using sign-free projector differentiation, with finite difference residual check and metric/clock conventions explicitly stated.
7. Source SHA-256, all nested ancestors, tests, row-count gates and output manifest.

## Server

```bash
cd /root/elab1/hysteresis
unzip Q550_v18_49j_COMPLETO.zip
cd q550_kappa_liouville_projection_v18_49j_bundle
bash run_on_server.sh 2>&1 | tee v18_49j_server.log
```

Python 3.13 recommended; `Q550_PYTHON` can override it. Requires numpy, scipy, matplotlib and pandas. `run_on_server.sh` creates `sendback.zip` containing the complete scripts, original I sendback, minimum inputs, results, report, figures, test code, manifest and SHA-256. Root ZIP directory is **`q550_kappa_liouville_projection_v18_49j_bundle/`**, exactly matching the server commands.

Optional `python3.13 scripts/run_audit.py --smoke` tests one physical history; it **overwrites full result CSVs** and therefore is not a valid release run. Use the full runner to regenerate all data.

## Outputs

- `scripts/run_audit.py`, `scripts/source_math.py`, `scripts/verify_parent.py` — actual computational code
- `scripts/frame_math.py`, `scripts/kinetic_metric.py`, `scripts/strain_math.py` — functionally preserved genuine ancestry
- `results/liouville_source_integrals.csv` — integrated independent source and volume identities
- `results/instantaneous_volume_sources.csv` — local divergence and metric-density rates
- `results/clockmatched_kappa_cancellation.csv` — κ-contrast with independent integrated parts
- `results/ten_axis_occupation_and_split.csv` — ten occupation fractions plus both rate terms across 61 clocks
- `results/occupation_rate_and_local_kappa_comparison.csv` — selected rank rates and local κ source differences
- `results/counterfactual_volume_forms.csv` — alternate volume-form family
- `results/report.json` and four generated figures
- `SHA256SUMS_OUTPUT.json` and `sendback.zip`

## Interpretation boundaries

- The strong original/autonomous cancellation is an empirical model result **for the kinetic volume form** on `phaseblind`, branch 0. It is **not** a coordinate-independent numeric statement across *all* volume forms.
- Exact Liouville formula in a specified smooth volume form is a differential-geometric identity. Agreement of independent numerical integrations validates implementation; it does not establish new fundamental physics.
- The clock is prescribed, so material trace is 10×10; the external command direction is not a tangent variable.
- Finite-gap pullback and eigenprojector occupation are diagnostics, not a proof of physical energy transfer, flip, holonomy or an exact nonlinear transport invariant.
- Only one finite κ change and six ramp timings were sampled. A zero coupling trace at fixed state is a structural derivative fact; it does not mean response to κ is zero.
