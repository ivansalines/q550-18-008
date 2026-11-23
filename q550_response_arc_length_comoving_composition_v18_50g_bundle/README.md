# Q550 v18.50g — Response Arc-Length & Co-Moving Composition Audit

**Goal:** Follow the response-vector composition as it evolves, using the accumulated sampled chord length instead of assigning special meaning to any prescribed time.

**Reproduction:** Extract this archive in `/root/elab1/hysteresis`, `cd q550_response_arc_length_comoving_composition_v18_50g_bundle`, then run `bash run_on_server.sh 2>&1 | tee v18_50g_server.log`. Uses Python3 with NumPy and Matplotlib (`pip install -r requirements.txt` if necessary).

**Authentic immutable ancestry:** The complete server sendback from v18.50f is included under `inputs/`, byte-for-byte. A verifier checks its archive SHA-256 and all manifested contents, then recursively verifies the embedded v18.50e input and reopens the original measured 4D vectors.

**What is actually measured:** Twenty trajectories/protocols × 5 *existing* horizon observations. We form `R=L+T` in the inherited metric-whitened 4D chart and compute (i) the polygonal response length from 5 points, (ii) coarser 3-point length and endpoint chord, (iii) the cancellation ratio as a function of normalized response path, (iv) signed projections of increments of L and T onto the moving resultant-chord tangent, (v) chord turning and direction changes, and (vi) an explicit alternate diagonal metric stress test. The segment time labels are retained for audit and orientation only.

**Hard scientific limitation:** **No new Q550 IVP is solved here.** Five samples cannot determine the *continuous* 4D response curve, its exact arc length, curvature, or physical times of any turning. The polygonal length is a **lower bound** on the continuous Euclidean length through the same measured points. No interpolation is silently promoted to a measurement. No material memory, physical fiber, threshold, causal decomposition, or volume claim is made.

**Files:** `scripts/run_audit.py` (generates all new numerical outputs), `scripts/geometry_math.py`, `scripts/verify_ancestry.py`, `scripts/plot_results.py`, `scripts/pack_sendback.py`, `tests/test_geometry.py`, `results/*.csv/png/json`, `SCIENTIFIC_REPORT.md`, `SCIENTIFIC_DECISION_RULES.md`, manifest `SHA256SUMS.json`.
