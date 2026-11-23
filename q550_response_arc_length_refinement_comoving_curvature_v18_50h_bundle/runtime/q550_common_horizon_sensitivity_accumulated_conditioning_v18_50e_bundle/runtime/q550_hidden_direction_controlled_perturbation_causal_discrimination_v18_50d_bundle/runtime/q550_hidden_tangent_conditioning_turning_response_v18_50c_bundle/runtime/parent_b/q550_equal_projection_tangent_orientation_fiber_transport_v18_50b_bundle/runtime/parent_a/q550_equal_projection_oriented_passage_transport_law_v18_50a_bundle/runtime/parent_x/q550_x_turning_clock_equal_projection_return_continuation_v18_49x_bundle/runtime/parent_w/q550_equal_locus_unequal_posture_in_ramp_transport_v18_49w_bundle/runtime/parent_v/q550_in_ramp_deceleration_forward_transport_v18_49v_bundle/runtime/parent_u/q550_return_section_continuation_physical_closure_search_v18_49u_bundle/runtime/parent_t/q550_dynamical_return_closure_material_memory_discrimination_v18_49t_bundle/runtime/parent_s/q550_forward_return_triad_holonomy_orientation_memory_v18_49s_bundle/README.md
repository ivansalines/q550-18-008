# Q550 v18.49s — Forward–Return Triad Holonomy & Orientation Memory Audit

**Authentic-source executable audit; not a certified physical memory law.**

## Question and careful terminology

We ask whether the rank-three spectral projector `S=P6+P7+P8` has a nonzero geometric return residual when comparing **two distinct authentic post-kick return evolutions**. Leg A is traversed forward in registered phase `q` and leg B is traced backwards **as a geometric path**. This is not the physical equation with time-reversed forcing and must not be presented as a second physical return experiment. Their initial and final projectors are generally different; we join them via specified canonical minimal direct rotations. We explicitly report those endpoint differences.

This is **closed projector-space holonomy** dependent on the endpoint connector. Nonzero results are geometric path sensitivity, not by themselves irreversible material memory, temporal hysteresis, or a physical Dzhanibekov flip.

## Mathematics

From authenticated v18.49r 11D/10D replay, `S(q)` and `K(q)` in a fixed inherited kinetic observer chart are calculated. `T=I-S`, `K_cross=SKT+TKS`. The ordered exponential of `K_cross` gives `U_A`, `U_B`, and reconstructs `S`.

For rank-three projectors `P,Q`, the canonical direct rotation is the orthogonal polar factor of `QP+(I-Q)(I-P)` (only permitted with a well-conditioned polar factor). Let `C0` map A-start to B-start, and `C1` map A-end to B-end. The loop is:

`H10 = C0.T @ UB.T @ C1 @ UA`.

Restricting to the oriented A-start eigenframe, the **conjugacy angle** of the resulting `SO(3)` holonomy is retained; it is invariant under sign-gauge changes of individual eigenvectors. The signed rotation axis is NOT independently gauge invariant.

## Mandatory controls

1. The exact same path traversed forward and backwards has zero holonomy within tolerance.
2. Each Kato cross transport reconstructs the aggregate triad projector endpoint.
3. Parent v18.49r relative rotation is reproduced numerically.
4. Explicit endpoint connector rank/conditioning, loop projector closure and inverse-loop reciprocity.
5. Random independent eigenvector sign flips and constant 10D orthogonal basis rotation leave the angle unchanged.
6. Subwindow comparison establishes dependence on the chosen phase extent.

## Commands

```bash
cd /root/elab1/hysteresis
unzip q550_forward_return_triad_holonomy_orientation_memory_v18_49s_bundle.zip
cd q550_forward_return_triad_holonomy_orientation_memory_v18_49s_bundle
bash run_on_server.sh --smoke 2>&1 | tee v18_49s_smoke.log
bash run_on_server.sh 2>&1 | tee v18_49s_full.log
```

Arguments: `--smoke` (2 cases), `--focus` (4 cases), or default (5 cases); `--q-start`, `--q-end`, `--phase-samples`, `--transport-steps`, `--no-subwindows`, numerical tolerances. The `run_on_server.sh` script regenerates CSV, plots, scientific report, manifests, and `*_sendback.zip` outside the root folder. Prefer Python 3.13 or fall back to python3 with NumPy/SciPy/Matplotlib.

Root directory inside the ZIP **exactly matches the complete descriptive filename**. The parent v18.49r sendback is embedded unchanged and authenticated recursively; no upstream script is replaced. The full executable lineage is included as zipped archive ancestry.
