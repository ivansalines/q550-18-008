# Q550 v18.48z — Contact-Contract Invariance & Barrier Normal-Form Audit

**Status:** 14 fresh authentic 11D IVPs + 46 previously authenticated Y 11D phase-distance profiles + 8 historical-W cross-branch screens. Floating-point diagnostics, **not** a new exact mechanical conservation law, material merger, constitutive hysteresis theorem or interval topology certificate.

## The question

When two strict sublevel contact intervals become one, what remains structurally recognizable? We look at the *inter-lobe local maximum* of the **reduced 3D geometric gap** (the full 11D states do **not** meet) and quantify the local normal form using the independently authenticated Y data.

For a fixed smooth-reversal duration `r`, parameter choice `kappa_kind`, and equal external-drive phase `q`, the observed distance is

`d(q; r) = || (logrho1,logrho2,x)_return(q) - (logrho1,logrho2,x)_forward(q) ||`.

At an interior smooth local maximum `q_b`, let `B=d(q_b)`, `C=d''(q_b)<0`. For `epsilon=B-delta` (with `delta>0`), the *excluded* phase gap `G` between the two connected components of `{q: d(q) < epsilon}` has the normal form

`G = 2 sqrt(2 delta/|C|) [1 + O(delta)]`,

and the diagnostic contract ratio

`I = |C| G^2 / (8 delta) -> 1`.

**This limit comes from Taylor expansion at any nondegenerate maximum.** It does not identify a special physical constant. The numerical question is how accurately this normal form describes the real Q550 model, which higher-order terms are needed, how the corrections change with ramp/kappa, and whether the physical 11D state remains nonrecurrent.

## Authentic source and provenance

- `inputs/v18_48y_original_server_sendback.zip` is the *byte-identical* Y server sendback `sendback(20261027-110331).zip`, SHA-256 `7134cbc160e07f3383151e02fecccb53fcdb3549a61cf4b5f11ea38b102846ec`.
- `scripts/verify_parent.py` checks the original 34-manifest-file Y archive and invokes the original Y historical verifier to authenticate the recursively nested `Y -> X -> W -> V -> U -> T -> S -> R -> Q -> P -> O -> J` sources and physical histories.
- Four `reference/*.py` physics/drive/lobe modules and `reference/y_original_run_audit.py` are exact historical sources; SHA pins cover all input data and these copies. The fresh 11D integration calls the unchanged historical `integrate()` function and physical right-hand side, not a new toy surrogate.
- `inputs/v18_48y_*.csv` are byte-exact from the authenticated Y archive. `results/historical_W_cross_branch_screen.csv` is read from the *original authenticated W report*, not synthesized trajectories.
- All program documentation/comments are English. `scripts/*.py`, tests, CSV, plots and `SHA256SUMS_OUTPUT.json` ship with the reproducible sendback.

## What actually ran

1. Original **46** Y continuous-IVP-generated contact profiles (`23` smooth ramps for `original` and `autonomous` kappa) were examined, with **276** independent polynomial-jet fits (quartic/sextic, three local window radii) and **184** screening gap/root comparisons on their sampled grid.
2. **14 fresh original 11D IVPs:** two original forward 11D histories (`phaseblind` branch0, both kappas) and six genuine reverse smoothstep protocols per kappa, ramps `r = [0.285, 0.292, 0.296333, 0.300, 0.305, 0.309]`. Historical state continuation matches all 41 source sections to within the report's maximum replay error.
3. At each new physical reverse IVP, evaluate **both nearest level roots directly through the DOP853 continuous solution**, for `delta = [1e-5,3e-5,1e-4,3e-4]`, giving **48 independent direct full-physics root pairs**. The first root away from the barrier is used in each direction; bracketing the far endpoints would fail because lobe profiles are not monotone globally.
4. Compare observed gaps with the quadratic Taylor formula, a quartic local polynomial and a sixth-order polynomial. Higher derivatives come from local fits (`q-q_b` within `0.012`; additional fit radii 0.008 and 0.016 for sensitivity), **not symbolic or validated interval derivatives**. The cubic term shifts the individual left and right roots; the leading correction to the *total gap width* involves the quartic and the square of the cubic.
5. Compare how these properties differ between original and autonomous `kappa0`; inherited parent Y already authenticated the critical merger curve at seven geometric thresholds.
6. Screen all **eight** original W branch/kappa summaries separately. **Do not** infer that a two-lobe barrier or the same local normal form was detected on all four families/branches. Only `phaseblind branch0` was directly tested for the inter-lobe maximum in Y/Z. This is an explicit scientific limit, not missing data concealed by a median.

## Numerical results from the local preflight

- **14/14** genuine new 11D integrations completed, **48** continuous-IVP root pairs.
- Maximum absolute relative width error: **quadratic 0.0868%**, **quartic polynomial 0.00310%**, **sixth-order polynomial 0.000129%**. These are measured maximum discrepancies, **not** validated error bounds.
- Directly measured `I` lies between approximately `1.000016` and `1.001738` for the tested offsets. It approaches `1` as `delta` decreases.
- Minimum full **11D** distance at the inter-lobe barrier is **1.88768**, so the reduced-contact connection is not full material recurrence.
- Max historical source-state replay norm about `3.43e-13`; maximum normalized mechanical balance residual about `1.65e-11` (solver/ledger, not independent theorem).
- Independent affine phase-reparameterization check of `I`: max numerical discrepancy `4.45e-16`. This is a **coordinate identity** for affine phase rescaling, not general coordinate invariance under nonlinear reparameterizations.
- The archived Y sampled-grid roots are deliberately labeled **GRID SCREEN ONLY**. At very small offsets they can be biased by interpolating values at q increments of 0.0005. They are **not** substituted for the genuine dense-IVP threshold roots.

## Run on the server

```bash
cd /root/elab1/hysteresis
unzip q550_kappa_contact_contract_v18_48z_bundle.zip
cd q550_kappa_contact_contract_v18_48z_bundle
bash run_on_server.sh 2>&1 | tee v18_48z_server.log
```

The extraction root is precisely `q550_kappa_contact_contract_v18_48z_bundle/`. Default `python3.13`; override with `Q550_PYTHON`. The runner checks source authenticity, runs unit tests, regenerates every 11D comparison and all plots, checks scientific gates, and writes `sendback.zip`. No cache, orbit file, manual symlink or external path is required. Tested from clean extraction.

For a cheap authenticated historical screen without new IVPs:

```bash
python3.13 scripts/run_audit.py --parent-only
```

Do not run `check_outputs.py` after `--parent-only`: full scientific gates require the 14 fresh IVPs.

## Results

- `results/report.json`: scope, all numerical maxima, provenance, limitations.
- `results/continuous_11D_root_validation.csv`: all **48** actual IVP left/right roots, gap widths, comparative prediction errors, source energies and 11D separation.
- `results/normal_form_jets.csv`: **276** window/ramp/kappa polynomial fits; derivatives 2–6 and local fit quality.
- `results/parent_grid_gap_screen.csv`: **184** source-Y sampled-grid root checks, explicitly separate from continuous-IVP validation.
- `results/historical_W_cross_branch_screen.csv`: eight authentic W cases, **not** barrier-normal-form certification.
- Five PNGs: direct `I` convergence, errors by normal-form order, predicted/observed gaps, original Y critical curve, cubic-term variation.
- `results/SOURCE_PROVENANCE.json`, `README.md`, `SCIENTIFIC_DECISION_RULES.md`, math scripts, tests, `inputs/SOURCE_PINS.json`, manifest SHA-256 and original user sendback ZIP.

## Boundaries

**Not proved:** uniqueness of the central maximum outside the screened interval; global lobe topology; existence of a global invariant under nonlinear phase charts; two-lobe structure on every branch; universal constitutive response, torsion, entropy production or a material state merger. The scalar contract ratio has a *generic mathematical* limit. In the authentic local experiments the curvature remains negative and source full-state separation stays nonzero, but neither inequality is an interval certificate over all model parameters.
