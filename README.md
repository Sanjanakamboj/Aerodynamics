# Aerodynamics

A collection of aerodynamics projects spanning classical potential-flow
theory, lifting-line theory, and a full airfoil geometry/analysis
pipeline built around XFOIL.

## Projects

### [Formation Flight](Formation%20Flight/)
Prandtl Lifting-Line Theory study of two-aircraft formation flight — an
Airbus A320 leader and a trailer surfing its rolled-up wake —
quantifying the induced-drag benefit before and after trimming out the
induced rolling moment. Course project, LMECA2323 (UCLouvain).

### [Thin Airfoil Theory](Thin%20Airfoil%20Theory/)
Glauert's thin airfoil theory (Fourier-series camber-line solution) and
a linear-strength vortex panel method, applied to the NACA 2412 airfoil
and validated against textbook zero-lift angle and quarter-chord moment.

### [Airfoil Design & Analysis](Airfoil%20Design%20%26%20Analysis/)
A Python pipeline for generating airfoil geometry (NACA 4/5-digit,
`.dat` import), analyzing it geometrically and aerodynamically (via a
custom XFOIL wrapper), and comparing multiple airfoils side by side.
Verified end-to-end against a live XFOIL binary, including captured
stall, for NACA 0012, NACA 2412, and NASA SC(2)-0714.

### [Flow around Cylinder](Flow%20around%20Cylinder/)
Classical potential flow past a circular cylinder: uniform flow +
doublet, then a point vortex for circulation and lift (Magnus effect).
Validated against d'Alembert's paradox and the Kutta-Joukowski theorem.

## Skills

See [SKILLS.md](SKILLS.md) for a breakdown of the aerodynamics theory,
numerical methods, and software engineering demonstrated across these
projects.
