# Thin Airfoil Theory — NACA 2412

Glauert's thin airfoil theory (Fourier-series camber-line solution) and a linear-strength vortex panel method, applied to the NACA 2412 airfoil and validated against a symmetric NACA 0012 baseline.

## Contents

- **Geometry** — imports digitized NACA 2412 coordinates from `Geometry.xlsx` and extracts the mean camber line; also generates arbitrary NACA 4-digit sections analytically.
- **Thin Airfoil Theory** — Fourier coefficients of the camber-line slope, zero-lift angle $\alpha_{L0}$, quarter-chord moment $C_{m,c/4}$, and $C_L(\alpha) = 2\pi(\alpha-\alpha_{L0})$.
- **Vortex Panel Method** — linear-strength (Kuethe & Chow) formulation: vortex sheet strength varies linearly along each panel and is continuous at panel nodes, closed by the Kutta condition. This avoids the checkerboard node-to-node oscillation that a naive constant-strength panel produces on thin, closed bodies.
- **Validation** — panel-count convergence study, and a thickness sweep confirming the panel method recovers thin airfoil theory exactly in the zero-thickness limit.
- **Camber sensitivity** — $\alpha_{L0}$ and $C_{m,c/4}$ vs. max camber for the NACA m412 family.

## Key results (NACA 2412)

| Quantity | Value | Reference |
|---|---|---|
| Zero-lift angle $\alpha_{L0}$ | −2.06° | ≈ −2.08° (textbook) |
| Quarter-chord moment $C_{m,c/4}$ | −0.053 | ≈ −0.05 (textbook) |
| $C_L$ at $\alpha=5°$, thin airfoil theory | 0.775 | — |
| $C_L$ at $\alpha=5°$, panel method | 0.851 | ~10% above TAT (thickness effect) |

## Repository structure

```
.
├── Thin Airfoil Theory.ipynb   # Full analysis, runs top-to-bottom
└── Geometry.xlsx                # Digitized NACA 2412 surface coordinates
```

## Requirements

```
numpy
pandas
scipy
matplotlib
openpyxl
```

Run with Jupyter (`jupyter notebook "Thin Airfoil Theory.ipynb"`) or any compatible IDE.
