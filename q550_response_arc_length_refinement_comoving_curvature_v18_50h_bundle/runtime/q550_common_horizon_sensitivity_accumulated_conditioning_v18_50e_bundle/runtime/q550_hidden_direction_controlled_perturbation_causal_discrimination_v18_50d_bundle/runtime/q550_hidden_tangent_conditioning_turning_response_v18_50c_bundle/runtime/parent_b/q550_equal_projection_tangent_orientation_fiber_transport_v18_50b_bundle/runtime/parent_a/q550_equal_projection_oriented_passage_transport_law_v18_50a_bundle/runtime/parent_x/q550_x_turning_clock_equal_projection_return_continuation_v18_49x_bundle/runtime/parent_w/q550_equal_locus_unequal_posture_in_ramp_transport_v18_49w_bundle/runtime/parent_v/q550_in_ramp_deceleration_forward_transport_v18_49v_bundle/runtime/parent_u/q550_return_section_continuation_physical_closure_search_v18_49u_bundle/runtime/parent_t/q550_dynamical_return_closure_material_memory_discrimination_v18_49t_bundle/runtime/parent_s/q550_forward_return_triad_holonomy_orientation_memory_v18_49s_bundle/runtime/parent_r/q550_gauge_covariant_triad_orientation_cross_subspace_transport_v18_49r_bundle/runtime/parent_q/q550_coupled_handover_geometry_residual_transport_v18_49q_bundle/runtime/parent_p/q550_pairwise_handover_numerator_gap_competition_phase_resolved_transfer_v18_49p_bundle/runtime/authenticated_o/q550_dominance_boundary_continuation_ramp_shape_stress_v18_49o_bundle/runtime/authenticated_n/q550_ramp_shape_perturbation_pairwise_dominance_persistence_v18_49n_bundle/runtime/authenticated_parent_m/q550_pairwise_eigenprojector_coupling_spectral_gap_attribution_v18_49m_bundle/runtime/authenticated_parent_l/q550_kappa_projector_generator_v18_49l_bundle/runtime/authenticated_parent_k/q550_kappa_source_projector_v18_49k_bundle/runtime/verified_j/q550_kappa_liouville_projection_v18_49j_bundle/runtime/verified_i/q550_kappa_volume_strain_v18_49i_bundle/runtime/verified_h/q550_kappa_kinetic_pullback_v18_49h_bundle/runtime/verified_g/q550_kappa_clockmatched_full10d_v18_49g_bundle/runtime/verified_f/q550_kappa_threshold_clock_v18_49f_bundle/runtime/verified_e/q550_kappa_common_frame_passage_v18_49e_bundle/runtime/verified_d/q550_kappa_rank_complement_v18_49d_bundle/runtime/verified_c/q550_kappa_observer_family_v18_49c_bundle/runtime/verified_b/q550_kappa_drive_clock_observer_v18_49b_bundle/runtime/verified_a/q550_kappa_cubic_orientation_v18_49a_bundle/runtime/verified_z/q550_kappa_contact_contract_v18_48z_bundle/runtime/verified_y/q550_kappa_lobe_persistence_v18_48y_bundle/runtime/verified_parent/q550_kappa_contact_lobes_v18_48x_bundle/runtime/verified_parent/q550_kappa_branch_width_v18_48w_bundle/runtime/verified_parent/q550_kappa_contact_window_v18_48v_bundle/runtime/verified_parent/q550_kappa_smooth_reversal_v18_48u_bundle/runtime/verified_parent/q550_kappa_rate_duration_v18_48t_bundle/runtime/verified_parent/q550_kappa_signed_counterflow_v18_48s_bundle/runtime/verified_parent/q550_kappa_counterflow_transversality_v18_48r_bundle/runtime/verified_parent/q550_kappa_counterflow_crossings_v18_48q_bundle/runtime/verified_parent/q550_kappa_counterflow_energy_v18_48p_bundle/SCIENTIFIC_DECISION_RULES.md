# Scientific decision rules for v18.48p

1. **Physical inverse versus external reversal:** Solving `dY/dxi=F(Y)` with decreasing `xi` mathematically inverts a deterministic ODE. Running with increasing `xi` and `dTheta/dxi` switched to `-2*pi*slope` is a *distinct driven IVP*. Never identify these protocols.
2. **A third, explicit counterflow protocol** flips `v1,omega1,v2,omega2,vz` at the turnaround, then reverses only the Theta clock. It is a controlled intervention, not a proven physical time reversal or a true action minimizer.
3. **Mechanical energy** is *defined*, not assumed to be an invariant, by

   `E= (rho1^2*(v1^2+omega1^2)+rho2^2*(v2^2+omega2^2)+m_x*x_dot^2)/2 + U(rho1)+U(rho2) - B*log[x(1-x)] + kappa0*x*rho1*rho2*cos(delta)`

   where `U(rho)=rho^2 - 0.8*rho^3 + 0.2*rho^4 +e_reserve^2/(2*rho^2)`,
   `x_dot=x(1-x)*v_z`, and `delta=theta1+theta2-phi0-Theta`.
4. **Derived exact ODE balance (in original tau time)**:

   `dE/dtau = kappa0*x*rho1*rho2*sin(delta)*Theta_dot
        - gamma_rho*((rho1*v1)^2+(rho2*v2)^2)
        - gamma_x*x_dot^2
        + x_dot*rho1*rho2*(mu_x*sin(delta)+kappa0*cos(delta))`.

   Here `d/dxi=(2*pi*slope/x)d/dtau`, `Theta_dot = {+x,-x}` for drive signs `{+1,-1}` respectively. For the backward solve, integrate with **decreasing xi**, which reverses the signs of the resulting integrals; positive signed damping integral on that solve is not energy production.
5. **Energy identity is checked three ways**: symbolic derivation from the historical material ODE, finite-difference directional derivative at three representative 11D states with both kappa values and drive signs -1/0/+1, and direct augmented-IVP quadrature against endpoints. No claim is made about a unique externally calibrated thermodynamic energy.
6. **Geometry-only return measure**: Euclidean distance of `[log(rho1), log(rho2), x]` from the actual historical return location at mirrored progress. This metric is explicitly not energy, spatial body distance, or observer-invariant Riemannian length.
7. **Numerical reversibility cannot prove thermodynamic reversibility**. A nonzero return gap under changed control demonstrates non-retracing for that control, not a universal hysteresis law.
8. **Provenance**: the original v18.48o server sendback and original v18.48j server sendback are immutable nested archives. Verify both full SHA manifests, run both original ancestry scripts, recover the v18.48h full 11D trajectories, compare recomputed forward trajectories at all 41 sections, and check the direct original RHS against its authenticated analytic RHS. Do not replace the original equations with a surrogate.
9. **Validation gates**: all unit tests pass; eight original paths, 41 sections each; 8 forward integrations, 8 backward inverses, 8 drive reversals, 8 drive+velocity reversals and 8 unchanged-drive continuation controls; forward regression <5e-6 absolute 11D; analytic-RHS relative error <1e-11; energy balance relative error <2e-7. The preflight performs much better but floating point is not a validated interval guarantee.
10. **Scope**: no causality or entropy theorem, no statistical generalization to other Q, no reconstruction of an exact physical observer connection, no definitive physical law of anti-flow. Distinct histories and explicit mechanical source terms are measured for one frozen Q550 11D system.
