# Q550 v18.49r — Gauge-Covariant Triad Orientation & Cross-Subspace Transport Audit

**Reproducible study, numerical not interval-certified.**

## Input genealogy

Immutable v18.49q user-server sendback, SHA-256 pinned in `inputs/SOURCE_PINS.json`, contains the v18.49p sendback and upstream verified code / authentic Q550 physical state. The script verifies all archive members and the nested genealogy before importing historical physical equations. No new physical model is introduced.

## Numerical question

Does the 6–7–8 eigenspace remain an oriented, coherently transported subspace through the 6–7 → 7–8 power handover? Separate local internal rotations from motion of the triad subspace against the remaining seven modes. Reject gauge-dependent sign flips of individual `eigh` eigenvectors.

Let `S = P6 + P7 + P8`, `T = I − S`; decompose the skew projector generator into `K_internal = S K S`, `K_cross = S K T + T K S`, `K_external = T K T`. Then `Sdot = [K_cross,S]`. Integrate `K_cross` alone to obtain the canonical path-following subspace transport. Compare the endpoint frame after continuous sign alignment to this subspace-transported initial frame, extracting the relative `SO(3)` angle.

The gauge-invariant `chi = <[K67,K78],K68>_F / (||[K67,K78]||_F ||K68||_F)` is diagnostic only: for nonzero factors its magnitude is necessarily exactly one by the Lie algebra structure. The sign is the relative orientation of two observable skew operators, not a claimed intrinsic chirality of three *unoriented* eigenlines.

## Commands on server

```bash
cd /root/elab1/hysteresis
unzip q550_gauge_covariant_triad_orientation_cross_subspace_transport_v18_49r_bundle.zip
cd q550_gauge_covariant_triad_orientation_cross_subspace_transport_v18_49r_bundle
bash run_on_server.sh 2>&1 | tee v18_49r_server.log
```

Use `bash run_on_server.sh --smoke` for one case, `--focus` for both kappa values at r=0.327375, and default for five authenticated cases. CLI knobs include `--phase-samples`, `--transport-steps`, and tolerances. Results, plots, reports, hashes and execution environment are packed as descriptive sendback ZIP alongside this directory. Python 3.13 preferred, Python 3 compatible with stated requirements.

## Scientific guardrails

Rank-ordered eigenspaces are not material components. A signed coefficient in the instantaneous spectral eigenbasis has arbitrary sign. A relative SO(3) angle depends on the choice of reference and path; only specified gauge invariances are tested. Neither a material wake nor a universal torsional flip follows from these measurements.
