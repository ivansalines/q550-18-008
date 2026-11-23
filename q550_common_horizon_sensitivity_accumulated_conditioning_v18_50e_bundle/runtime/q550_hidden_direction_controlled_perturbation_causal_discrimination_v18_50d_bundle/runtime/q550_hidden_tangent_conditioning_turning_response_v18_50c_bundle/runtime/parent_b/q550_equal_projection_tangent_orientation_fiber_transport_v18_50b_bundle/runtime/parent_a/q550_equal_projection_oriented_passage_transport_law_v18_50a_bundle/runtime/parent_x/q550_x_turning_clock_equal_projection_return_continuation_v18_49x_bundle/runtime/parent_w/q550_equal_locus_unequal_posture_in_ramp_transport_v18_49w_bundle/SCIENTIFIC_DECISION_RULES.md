# v18.49w — Scientific decision rules

1. Use the **genuine 11D** Q550 return trajectory under the original cubic drive, not a synthetic interpolation of CSV summaries. Authenticate the exact v18.49v sendback and upstream source genealogy before computation.
2. Select pairs of **different** instants with `delta_sigma >= 0.20`; reject adjacent-grid trivial proximity.
3. Locus lenses: `x=logistic(z)` alone; and the **strict coordinate projection** `(logrho1, logrho2, x)` normalized by each coordinate's span within that ramp. These are not Euclidean physical distances.
4. `near_x` means `|Δx|/span_x <= 0.10`; `near_3D` means the Euclidean norm of three span-normalized gaps `<= 0.20`. These are explicitly user-adjustable diagnostic thresholds, not intrinsic physical bounds.
5. Posture: differences of wrapped `(theta1,theta2)`, full first-ten-state norm, kinetic-frame spectral rank-three projector `P6+P7+P8`, and SO(3) rotation relative to a fixed first valid reference at `sigma=0.10`. The Frobenius projector distance is **invariant under eigenvector sign changes**, unlike naked eigenaxis signs.
6. If a rank-three spectral projector cannot be reliably defined, retain the pair but mark its projector and angle quantities *undefined*, never zero.
7. The cubic sign reversal has `Theta(sigma)=Theta(1-sigma)` exactly in its integrated clock. This identity is a **negative interpretive control**, not a discovered material return.
8. Even if a near-x pair has large posture discrepancy, do not claim full equal-locus, physical torsion, eight-state cubical packing, material memory, or dynamic closure unless separately certified.
9. A failed full-locus near-pair search is only a **finite-grid / finite-duration negative finding**, not a no-go theorem.
