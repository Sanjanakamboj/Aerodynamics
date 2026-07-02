# Airfoil Design & Analysis

A Python pipeline for generating airfoil geometry, analyzing it (both
geometrically and aerodynamically via XFOIL), and comparing multiple
airfoils side by side.

## Overview

`get_airfoil("2412")` is the core entry point. It checks the local
airfoil database first, and only falls back to generating a NACA
4/5-digit airfoil analytically if the code isn't found there. Either
way, every airfoil comes back as the same `Airfoil` object, so nothing
downstream needs to know whether the geometry was generated or looked
up.

Run everything at once:

```bash
python get_airfoil.py 2412 1000000
```

This fetches/generates NACA 2412, runs geometry analysis, runs an XFOIL
polar sweep at Re=1,000,000, sanity-checks the wrapper against a second
Reynolds number, and computes a Cp distribution at the best-L/D angle --
saving everything into `Airfoils/NACA 2412/`.

## Structure

- **`get_airfoil.py`** -- main entry point (see above)
- **`geometry_generator/`** -- NACA 4- and 5-digit generation, and
  `.dat` coordinate file import (Selig/Lednicer format auto-detected)
  - `naca4.py`, `naca5.py`, `camber.py`, `thickness.py`, `spacing.py` --
    the generators and their shared building blocks
  - `airfoil.py` -- the canonical `Airfoil` type every code path returns
  - `import_dat.py`, `utils.py`
- **`airfoil_database/`** -- local database of `.dat` files, searched
  before falling back to generation
  - `NACA/`, `UIUC/`, `Selig/` -- currently empty, ready to populate
  - `NASA/` -- seeded with SC(2)-0714
  - `User Library/` -- airfoils you generate get auto-saved here, so
    the next lookup finds them instead of regenerating
- **`geometry_analysis/`** -- geometric metrics (max thickness/camber +
  location, leading-edge radius, trailing-edge angle, cross-sectional
  area, curvature) and the shape/thickness/curvature plots
- **`aerodynamic_analysis/`** -- the XFOIL wrapper and everything built
  on it
  - `xfoil_runner.py` -- `PolarRequest`/`run_polar()` for an alpha
    sweep, `CpRequest`/`run_cp()` for a single-alpha pressure
    distribution. Geometry is always resolved through `get_airfoil()`
    first, so XFOIL analyzes the exact same shape shown in the geometry
    plots -- never XFOIL's own internal NACA generator.
  - `polar_analysis.py` -- performance metrics from a polar: CLmax,
    CDmin, max L/D, best glide angle, stall angle, zero-lift angle,
    lift-curve slope, moment coefficient (CM0)
  - `plots.py` -- lift curve + drag polar, Cp distribution, and a
    metrics table. All three accept either one airfoil or several
    overlaid (used for comparisons and Reynolds-number validation)
  - `validate.py` -- sanity-checks the wrapper for a given airfoil
    across two Reynolds numbers (symmetric-airfoil CL check, higher-Re
    lower-drag check)
- **`comparison_dashboard/`** -- overlay multiple airfoils' geometry
- **`compare_airfoils.py`** -- comparison entry point
- **`Airfoils/<code>/`** -- generated output per airfoil (geometry
  plots, polar `.dat` + plots + metrics table, Cp plot)
- **`Comparisons/<names>/`** -- generated output per comparison

## Usage

Geometry only:

```bash
python get_airfoil.py 2412
```

Also run aerodynamic analysis at a given Reynolds number (angle of
attack for the Cp plot is optional -- defaults to the best-L/D angle
from the polar just computed):

```bash
python get_airfoil.py 2412 1000000
python get_airfoil.py 2412 1000000 6      # Cp distribution at alpha=6 deg instead
```

Compare multiple airfoils (geometry, and polars/metrics if `--re` is given):

```bash
python compare_airfoils.py 0012 2412 sc20714 --re 1000000
```

Sanity-check the XFOIL wrapper on any airfoil:

```bash
python aerodynamic_analysis/validate.py 0012
```

## Requirements

- Python 3, numpy, pandas, matplotlib
- A compiled XFOIL binary for anything touching `aerodynamic_analysis`
  -- path is set in `aerodynamic_analysis/xfoil_runner.py`
  (`XFOIL_BIN`). Geometry generation and analysis (`geometry_generator`,
  `geometry_analysis`, `airfoil_database`) don't need XFOIL at all.

## Notes

- Folder/file names are snake_case throughout (`geometry_generator`,
  not `Geometry Generator`) specifically so everything is importable as
  normal Python packages -- a space in the path breaks `import`.
- `NACA`, `UIUC`, and `Selig` database folders are empty placeholders
  today; only `NASA/` and whatever you've generated into
  `User Library/` are populated.
