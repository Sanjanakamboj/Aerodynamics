# Skills

A breakdown of the aerodynamics theory, numerical methods, and software
engineering practices demonstrated across the projects in this repo.

## Aerodynamics & Numerical Methods

- **Thin airfoil theory** — Fourier-series camber-line solution, zero-lift
  angle and quarter-chord moment, validated against textbook values.
  ([Thin Airfoil Theory](Thin%20Airfoil%20Theory/))
- **Vortex panel methods** — linear-strength (Kuethe & Chow) panel
  method with the Kutta condition; diagnosed and fixed a checkerboard
  node-to-node instability present in a naive constant-strength
  formulation.
  ([Thin Airfoil Theory](Thin%20Airfoil%20Theory/))
- **Prandtl lifting-line theory** — Fourier-coefficient solution of the
  compatibility equation for circulation, span loading, induced drag,
  and Oswald efficiency; extended to a non-uniform upwash field (wake
  interaction between two aircraft) and rolling-moment trim via
  aileron deflection.
  ([Formation Flight](Formation%20Flight/))
- **Vortex core modeling** — Burnham-Hallock model for a rolled-up
  wake's two-vortex system, derived from impulse and energy
  conservation.
  ([Formation Flight](Formation%20Flight/))
- **Potential flow theory** — uniform flow, doublet, and point-vortex
  superposition; d'Alembert's paradox and the Kutta-Joukowski theorem,
  both validated by direct numerical force integration rather than
  assumed.
  ([Flow around Cylinder](Flow%20around%20Cylinder/))
- **NACA airfoil geometry** — 4- and 5-digit series (including the
  reflexed camber-line family) from first-principles camber/thickness
  formulas, plus `.dat` coordinate import with automatic Selig/Lednicer
  format detection.
  ([Airfoil Design & Analysis](Airfoil%20Design%20%26%20Analysis/))
- **Viscous/inviscid coupled panel analysis (XFOIL)** — polar sweeps,
  single-alpha Cp distributions, stall capture, and cross-validation
  against a second Reynolds number and thin-airfoil-theory lift-curve
  slope.
  ([Airfoil Design & Analysis](Airfoil%20Design%20%26%20Analysis/))

## Software Engineering

- **Package architecture** — decomposed a multi-stage pipeline (geometry
  generation → geometry analysis → aerodynamic analysis → comparison)
  into independent, composable Python packages sharing one canonical
  data type (`Airfoil`), so downstream code never needs to know whether
  a given airfoil's geometry was generated or looked up from a database.
  ([Airfoil Design & Analysis](Airfoil%20Design%20%26%20Analysis/))
- **Driving an interactive Fortran CLI from Python** — XFOIL has no
  Python API; built a subprocess-based wrapper (command scripting,
  output parsing) around it, including diagnosing and fixing a
  filename-truncation bug (XFOIL's fixed 48-character buffer) and a
  panel-count/repaneling bug, both found by testing against a live
  binary rather than assumed correct.
  ([Airfoil Design & Analysis](Airfoil%20Design%20%26%20Analysis/))
- **Numerical debugging** — root-caused and fixed a boundary-artifact
  bug in a finite-difference curvature calculation (via arc-length
  reparametrization), confirmed with before/after numerical evidence
  rather than visual inspection alone.
  ([Airfoil Design & Analysis](Airfoil%20Design%20%26%20Analysis/))
- **Verification-first development** — every derived physical quantity
  in this repo (lift-curve slope, stagnation points, force coefficients,
  panel convergence, thin-airfoil-theory limits) is checked against a
  closed-form or textbook reference in code, not just plotted.
- **Git workflow** — feature branching, isolated worktrees to avoid
  disturbing unrelated local state, and pull-request-based delivery.

## Tools & Technologies

Python, NumPy, SciPy, pandas, Matplotlib, Jupyter, XFOIL, openpyxl,
Git/GitHub, LaTeX.
