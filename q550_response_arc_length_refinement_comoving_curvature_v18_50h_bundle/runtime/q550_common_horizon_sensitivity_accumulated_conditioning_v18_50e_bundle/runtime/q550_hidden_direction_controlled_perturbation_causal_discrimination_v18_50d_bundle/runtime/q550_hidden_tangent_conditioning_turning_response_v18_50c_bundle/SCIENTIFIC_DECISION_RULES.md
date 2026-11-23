# v18.50c — Scientific decision rules

1. Use authenticated v18.50b events, unchanged. Re-integrate the actual Q550 11D return using the inherited solver, RHS and structural Jacobian. Never assign quadrants or eight-state labels to the data.
2. The source turning clock is the zero of `dx/dxi` from v18.49x, not `r/2`, not a fixed number near 0.09. Verify the derivative at the sourced event.
3. Hidden state `h=(theta1,theta2,theta1_rate,theta2_rate)` has hidden tangent `dh/dxi=(theta1_rate,theta2_rate,theta1_accel,theta2_accel)`.
4. Use a **single fixed diagonal metric** based on the max authenticated v18.50b trajectory span in each hidden coordinate across all cases. Contrast with the native metric and declared theta-reweightings; do not interpret metric angles as physical body rotations.
5. Measure the **pathwise turning of the normalized hidden tangent** `||d(h'/||h'||)/dxi||`; its six-component wedge is retained as signed directional information. Derivatives of the normalized tangent use a sampled finite-difference grid; report refinement.
6. The direction-turning peak in a window around the measured `x` turning is a *windowed* peak. Flag window-edge peaks. Do not treat a peak at an arbitrary boundary as a new clock law.
7. Demonstrating a curvature value, angular change, or lag is **correlation** in a co-driven system, not a causal conditioning certificate. A causal claim needs a controlled counterfactual of the dynamical equations and source term.
8. Same `x` does **not** imply same radial locus, kinetic state, physical fiber, cubical volume or material memory. The 34 pairs are correlated within 10 trajectories.

**Decision label**: `NUMERICAL_HIDDEN_DIRECTION_RESPONSE_ASSOCIATION_NOT_CAUSAL_CONDITIONING_OR_MATERIAL_MEMORY_CERTIFICATE`.
