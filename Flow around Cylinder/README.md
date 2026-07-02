# Flow Around a Circular Cylinder — Potential Flow Theory

Classical inviscid, incompressible potential flow past a circular cylinder: uniform flow superposed with a doublet (non-lifting case), then a point vortex added to model circulation and lift (the Magnus effect). Validated against two textbook results: d'Alembert's paradox (zero drag) and the Kutta-Joukowski theorem ($L' = \rho U_\infty \Gamma$).

## Contents

- **Non-lifting flow** — uniform flow + doublet superposition, closed-form streamlines and surface velocity.
- **Surface pressure distribution** — $C_p = 1 - 4\sin^2\theta$, verified numerically against the closed form.
- **Lifting flow** — a point vortex adds circulation $\Gamma$ (clockwise-positive, so positive $\Gamma$ gives positive lift); streamlines for the subcritical, critical, and supercritical circulation regimes, showing the stagnation point migrate along the surface and eventually lift off entirely.
- **Force integration** — numerical $C_d$/$C_l$ from surface $C_p$ integration, validated against d'Alembert's paradox and Kutta-Joukowski.
- **Circulation sensitivity** — $C_l$ vs. $\Gamma$ across both regimes, confirming the theory holds past the critical circulation.
- **Reality check** — where the inviscid theory breaks down (boundary-layer separation, wake drag), with a pointer to the companion viscous CFD notebook for the real, computed comparison.

## Key results

| Quantity | Computed | Theory |
|---|---|---|
| Min surface $C_p$ (non-lifting) | -3.0000 | -3 |
| $C_d$, all $\Gamma$ (d'Alembert's paradox) | ~0 (< 1e-10) | 0 |
| $C_l$ at $\Gamma=5$ | matches $\Gamma/(RU_\infty)$ to numerical precision | Kutta-Joukowski |
| Stagnation points, subcritical $\Gamma$ | $\sin\theta = -\Gamma/(4\pi RU_\infty)$ | closed-form |

## Repository structure

```
.
└── Flow around Cylinder.ipynb   # Full analysis, runs top-to-bottom
```

## Requirements

```
numpy
matplotlib
```

Run with Jupyter (`jupyter notebook "Flow around Cylinder.ipynb"`) or any compatible IDE.

## Related work

For the viscous counterpart — boundary-layer separation, wake formation, vortex shedding, and the real (nonzero) drag this potential-flow treatment cannot predict — see `CFD/CFD Basics/cylinder_cfd/main.ipynb`, a from-scratch unsteady Navier-Stokes solver for the same geometry.
