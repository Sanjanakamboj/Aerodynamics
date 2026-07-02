# Aerodynamics — Analytical & Numerical Methods

Coursework projects for **LMECA2323 – Aerodynamics of External Flow** (UCLouvain, EPL), building up classical aerodynamic theory from a single 2D airfoil section to a 3D finite wing to interacting multi-aircraft wakes. Each project is a self-contained Jupyter notebook that derives the theory, implements it from scratch (NumPy/SciPy, no black-box solvers), and validates the results against textbook/reference values.

Teachers: G. Winckelmans, J.-B. Crismer. Student: Sanjana Rani.

## Goal

Model lift and drag generation at increasing levels of complexity:

1. **2D section aerodynamics** — how camber and thickness set the lift, moment, and pressure distribution of a single airfoil.
2. **3D finite-wing aerodynamics** — how a finite span redistributes that section lift and generates induced drag.
3. **Multi-aircraft interaction** — how one aircraft's rolled-up wake perturbs a second aircraft's finite-wing solution, and how that can be exploited (formation flight drag reduction).

## Projects

| # | Project | Theory | Question answered |
|---|---|---|---|
| 1 | [Thin Airfoil Theory](Thin%20Airfoil%20Theory/) | Glauert thin-airfoil (Fourier camber-line) + linear-strength vortex panel method | Given a NACA 2412 section, what are $\alpha_{L0}$, $C_{m,c/4}$, and $C_L(\alpha)$ — analytically and with a full-geometry panel solver? |
| 2 | [Formation Flight](Formation%20Flight/) | Prandtl Lifting-Line Theory + Burnham-Hallock 2-vortex far-wake model | Given a finite-span leader aircraft, how much induced drag does a trailer save by flying in the leader's wake, once trimmed for the induced rolling moment? |

Project 1 establishes the 2D section behavior (lift-curve slope, zero-lift angle) that feeds the finite-wing model in Project 2 (`a_0 = 2π` per unit span). See each project's own README for full derivations, notebook contents, and key results.

## Repository structure

```
.
├── Thin Airfoil Theory/       # Project 1 — 2D section aerodynamics
│   ├── Thin Airfoil Theory.ipynb
│   └── Geometry.xlsx
└── Formation Flight/          # Project 2 — 3D finite-wing + wake interaction
    ├── Formation Flight.ipynb
    ├── Report/                # LaTeX + PDF writeup
    └── Figures/                # Schematics + exported plots
```

## Running the notebooks

```
pip install numpy scipy pandas matplotlib openpyxl
jupyter notebook
```

Each notebook runs top-to-bottom and reproduces every number and figure referenced in its README/report.
