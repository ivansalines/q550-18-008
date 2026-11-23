# Q550 v18.50f — Vector Cancellation Geometry & Response-Composition Continuation Audit

**Purpose.** Analyze the *composition* of the v18.50e hidden-direction response while preserving the difference between a coordinate ledger and independent physical causes.

**Authentic parent.** The embedded `inputs/q550_common_horizon_sensitivity_accumulated_conditioning_v18_50e_authenticated_server_sendback.zip` is pinned byte-for-byte by SHA-256 (`21d9f910c14148746853bd211c873a77ae965ec8cf386baff2ec2b8f0cdb8a2f`). The verifier checks its internal manifest before reading the 100 v18.50e records. The parent ZIP includes its own executable scripts and recursively pinned prior genealogy. No original file is altered.

**Reproduce on Linux server:**
```
cd /root/elab1/hysteresis
unzip q550_vector_cancellation_geometry_response_composition_continuation_v18_50f_bundle.zip
cd q550_vector_cancellation_geometry_response_composition_continuation_v18_50f_bundle
bash run_on_server.sh 2>&1 | tee v18_50f_server.log
```
`python3 -m pip install -r requirements.txt` if NumPy and Matplotlib are missing.

**Method.** In the fixed metric-whitened 4D chart inherited from v18.50e, compute the Gram ledger of endpoint vectors **L** (frozen-endpoint local x derivative), **T** (contribution from transported endpoint state tangent), and **R=L+T**. Measure vector closure, alignment, angle, cancellation fraction, parallel/transverse decomposition, and finite horizon-to-horizon reorientation. Compare natural turning seeds vs exactly matched initial seeds, both kappa rules and cubic/quintic ramp protocols. A negative L·T is a *counteralignment*, not a negative energy or a signed physical torsion.

**Measurement limits.** The 50f script performs **no new Q550 integration**: it reprocesses the 50e 100 observations and computes independent algebraic cross-checks and four figures. This is a genuine and reproducible numerical analysis, but its conclusions are conditional on the parent trajectory and inherited metric. It does not independently establish material memory, physical causality, chiral orientation, or a regime transition. To pursue those claims requires new interventions on the physical RHS and metric controls.
