# Formation Flight — Aerodynamics of External Flow (LMECA2323, Homework 2)

Prandtl Lifting-Line Theory (PLLT) study of two-aircraft formation flight: a **leader** flying in free-stream conditions and a **trailer** surfing the leader's rolled-up wake. The study quantifies the induced-drag benefit the trailer gains from the leader's wake, both before and after trimming out the resulting rolling moment with ailerons.

Course: LMECA2323 - Aerodynamics of External Flow, UCLouvain (EPL).
Teachers: G. Winckelmans, J.-B. Crismer. Student: Sanjana Rani.

## Problem

Two identical aircraft (Airbus A320, cruise at 11,000 m) are modeled as straight, untwisted, linearly-tapered lifting lines (2D lift-curve slope $a_0 = 2\pi$). The leader's wake rolls up far downstream into a two-vortex system (2VS) of circulation $\pm\Gamma_0$ and spacing $b_0$, represented with the Burnham-Hallock vortex core model. The trailer flies at the vortex-center altitude, offset from the port vortex, and experiences the resulting non-uniform upwash.

The analysis is split into three parts:

1. **Leader aircraft** — circulation, span loading, effective angle of attack, induced drag, Oswald efficiency, and far-wake (2VS) characteristics.
2. **Untrimmed trailer** — circulation, span loading, effective angle of attack, induced drag, and rolling moment under the leader's upwash.
3. **Trimmed trailer** — antisymmetric aileron deflection $\delta_a$ that zeroes the rolling moment, and the resulting drag benefit of formation flight.

## Key results

| Quantity | Leader | Trailer (untrimmed) | Trailer (trimmed) |
|---|---|---|---|
| Wing angle of attack $\alpha_w$ | 7.09° | 7.28° | 7.28° |
| Induced drag $C_{D_i}$ | 0.01327 | 0.01191 | 0.01191 |
| Rolling moment $C_M$ | — | $1.2\times10^{-4}$ | ≈ 0 (trimmed) |

- Oswald efficiency of the leader: $e = 0.979$.
- Far wake: $b_0/b = 0.740$, $r_c/b = 0.048$ ($b_0 \approx 26.5$ m, $r_c \approx 1.72$ m).
- Trim aileron deflection: $\delta_a = -0.54^\circ$.
- Total drag reduction for the trimmed trailer vs. the leader: **≈ 5.1%**.

Full derivations, assumptions, and discussion are in the [report](Report/Formation%20Flight%20Report.pdf).

## Repository structure

```
.
├── Formation Flight.ipynb   # Main analysis notebook (PLLT implementation, all 3 parts)
├── Report/
│   ├── Formation Flight Report.tex   # LaTeX source of the report
│   └── Formation Flight Report.pdf   # Compiled report
├── Figures/
│   ├── Study Case.png         # Leader/trailer/2VS geometry schematic
│   ├── UCLouvain_logo.svg.png, epl.png   # Title-page logos
│   └── extracted/             # Plots exported from the notebook, used in the report
└── Chapters/                  # (reserved for split-out report sections; currently empty)
```

## Notebook contents

`Formation Flight.ipynb` runs top-to-bottom and reproduces every number and plot in the report:

- **Aircraft data & chord distribution** — Airbus A320 cruise parameters, aspect ratio, taper.
- **Part I (Leader)** — solves Prandtl's compatibility equation for the Fourier coefficients $b_n$; computes circulation $\Gamma(\theta)$, span loading $K(\xi)$, induced/effective angle of attack, induced drag $C_{D_i}$, and Oswald efficiency $e$.
- **Far wake** — derives the 2VS spacing $b_0$ (impulse conservation) and core radius $r_c$ (Burnham-Hallock energy conservation), and the induced vertical velocity profile.
- **Part II (Untrimmed trailer)** — interpolates the leader's far-wake upwash onto the trailer's span, solves the extended compatibility equation (adds $C_n$ coefficients), and computes the trailer's circulation, span loading, effective angle of attack, induced drag, and rolling moment $C_M$.
- **Part III (Trimmed trailer)** — builds a smoothed antisymmetric aileron effectiveness function $f(\xi)$ (regularized Heaviside, avoids Gibbs oscillations), solves for the $d_n$ coefficients, finds the trim deflection $\delta_a$ that zeroes $C_M$, and evaluates the trimmed trailer's drag and the overall fuel-saving potential of formation flight.
- **Combined figures** — leader vs. untrimmed vs. trimmed trailer, circulation and span loading overlays used in the report.

### Requirements

```
numpy
matplotlib
```

Run with Jupyter (`jupyter notebook "Formation Flight.ipynb"`) or any compatible IDE (e.g. VS Code, Spyder).

## Report

The full writeup — problem statement, assumptions, aircraft data, and section-by-section discussion of results — is in [`Report/Formation Flight Report.tex`](Report/Formation%20Flight%20Report.tex) / [`.pdf`](Report/Formation%20Flight%20Report.pdf).
