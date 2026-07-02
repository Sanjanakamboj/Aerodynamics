"""
xfoil_runner.py

Minimal, reusable Python wrapper around the XFoil CLI to run airfoil polar
sweeps (Cl, Cd, Cm vs alpha) and return the results as a pandas DataFrame.

XFoil itself has no Python API -- it's an interactive Fortran console program.
This wrapper drives it the way you'd drive it by hand: it writes a sequence
of XFoil commands to a script file, feeds that to the xfoil binary via stdin,
and parses the polar dump file XFoil writes to disk.

Design note: this function signature (airfoil in, polar dataframe out) is
deliberately the same shape an MCP tool would expose -- "given an airfoil and
flow conditions, return a polar" -- so this is reusable almost as-is later.

Geometry source: PolarRequest.airfoil is resolved through this project's
get_airfoil() (database lookup, else NACA 4/5-digit generation) rather
than XFoil's own internal NACA generator, so XFoil always analyzes the
exact geometry shown in the geometry/curvature plots. A literal existing
file path is still accepted as-is (bypassing get_airfoil) for one-off
coordinate files that aren't in the database.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# Path to a self-compiled double-precision XFoil binary. The Ubuntu/Debian
# "xfoil" apt package (6.99.dfsg+1-3) is built in single precision and
# reliably crashes with SIGFPE partway through a multi-point OPER sweep
# (confirmed: divergence inside the boundary-layer Newton solve in xbl.f).
# Rebuilding from the same Debian source tree with -fdefault-real-8
# (double precision) eliminates the crash entirely. See README for build steps.
XFOIL_BIN = "/Users/sanju/xfoil/build/src/xfoil"

# get_airfoil.py lives at the project root, one level up from this package.
# Add it to sys.path so this module is importable regardless of the
# caller's own working directory.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from get_airfoil import get_airfoil  # noqa: E402


@dataclass
class PolarRequest:
    airfoil: str          # NACA code ("2412"), database code ("sc20714"), or path to a .dat file
    reynolds: float        # Reynolds number
    mach: float = 0.0
    alpha_start: float = -4.0
    alpha_end: float = 20.0  # wide enough to see stall (CLmax then dropoff), not just the linear region
    alpha_step: float = 1.0
    n_panels: int = 200    # paneling refinement (PPAR N)
    max_iter: int = 100    # viscous solver iterations per point


@dataclass
class CpRequest:
    airfoil: str          # NACA code ("2412"), database code ("sc20714"), or path to a .dat file
    reynolds: float        # Reynolds number
    alpha: float           # single angle of attack, not a sweep
    mach: float = 0.0
    n_panels: int = 200
    max_iter: int = 100


def _resolve_airfoil_dat(airfoil_spec: str, tmp_path: Path) -> Path:
    """
    Resolve PolarRequest.airfoil to a short-named .dat file inside
    tmp_path, ready for XFoil's LOAD command (short name because of the
    48-char filename truncation -- see run_polar()).

    If airfoil_spec is an existing file path, it's copied in as-is.
    Otherwise it's resolved through get_airfoil(): database lookup, else
    NACA 4/5-digit generation.
    """
    dat_path = tmp_path / "airfoil.dat"

    if Path(airfoil_spec).is_file():
        shutil.copyfile(airfoil_spec, dat_path)
    else:
        airfoil = get_airfoil(airfoil_spec)
        airfoil.export_dat(dat_path)

    return dat_path


def _build_script(req: PolarRequest, polar_name: str, airfoil_name: str) -> str:
    """Construct the sequence of XFoil console commands for a polar sweep.

    All filenames passed to XFoil here (polar_name, airfoil_name) must be
    *bare relative names*, not absolute paths. XFoil stores filenames in a
    fixed CHARACTER*48 Fortran buffer and silently truncates anything longer;
    on macOS the $TMPDIR prefix alone is ~49 chars, so an absolute temp path
    gets chopped and the polar is written to the wrong place. run_polar()
    invokes XFoil with cwd set to the temp dir so these short names resolve
    correctly. See run_polar() for the full explanation.

    Other notes from getting this to run reliably:
    - PLOP / G F must come first to disable the X11 plot window; otherwise
      XFoil tries to open a display and aborts in a headless environment.
    - No QUIT at the end. Sending QUIT from inside the top-level menu after
      a PACC session is closed has triggered a clean-exit crash on some
      builds; simply letting stdin hit EOF terminates the process just as
      well once the polar file has been flushed by the second PACC.
    """
    lines: list[str] = []

    lines.append("PLOP")
    lines.append("G F")
    lines.append("")  # exit PLOP submenu

    lines.append(f"LOAD {airfoil_name}")

    # Repanel to the requested node count. Also required for correctness,
    # not just refinement: some XFoil builds have a lower max-panel-node
    # limit than our exported .dat point count (~399, from a 200-point-
    # per-surface airfoil), and LOAD alone then fails to promote the
    # loaded points to the "current" airfoil ("Current airfoil cannot be
    # set. Try executing PANE at Top Level instead.") -- every subsequent
    # OPER/VISC/etc. command then errors with "No airfoil available".
    lines.append("PPAR")
    lines.append(f"N {req.n_panels}")
    # Two blank lines: PPAR's "Change what?" prompt needs one blank to
    # accept "N <count>" and trigger the actual repanel (confirmed by
    # testing against a real XFoil binary -- one blank alone re-displays
    # the same submenu prompt instead of exiting it), then a second blank
    # to exit the submenu back to the top level.
    lines.append("")
    lines.append("")

    # Enter viscous operating-point mode
    lines.append("OPER")
    lines.append(f"VISC {req.reynolds:.0f}")
    lines.append(f"MACH {req.mach:.4f}")
    lines.append(f"ITER {req.max_iter}")

    # Set up polar accumulation file (blank line = skip optional dump file)
    lines.append("PACC")
    lines.append(polar_name)
    lines.append("")

    # Sweep angle of attack in one shot
    lines.append(f"ASEQ {req.alpha_start:.2f} {req.alpha_end:.2f} {req.alpha_step:.2f}")

    lines.append("PACC")  # close polar accumulation, flush file

    return "\n".join(lines) + "\n"


def _build_cp_script(req: CpRequest, cp_name: str, airfoil_name: str) -> str:
    """
    Construct the XFoil command sequence for a single-alpha Cp(x/c)
    distribution: converge one operating point, then dump the surface
    pressure distribution. See _build_script() for the filename-length,
    PLOP/no-QUIT, and PPAR/repanel notes -- identical reasoning applies
    here.
    """
    lines: list[str] = []

    lines.append("PLOP")
    lines.append("G F")
    lines.append("")  # exit PLOP submenu

    lines.append(f"LOAD {airfoil_name}")

    lines.append("PPAR")
    lines.append(f"N {req.n_panels}")
    # Two blank lines: PPAR's "Change what?" prompt needs one blank to
    # accept "N <count>" and trigger the actual repanel (confirmed by
    # testing against a real XFoil binary -- one blank alone re-displays
    # the same submenu prompt instead of exiting it), then a second blank
    # to exit the submenu back to the top level.
    lines.append("")
    lines.append("")

    lines.append("OPER")
    lines.append(f"VISC {req.reynolds:.0f}")
    lines.append(f"MACH {req.mach:.4f}")
    lines.append(f"ITER {req.max_iter}")
    lines.append(f"ALFA {req.alpha:.2f}")
    lines.append(f"CPWR {cp_name}")

    return "\n".join(lines) + "\n"


def _parse_cp_file(cp_file: Path) -> pd.DataFrame:
    """Parse XFoil's CPWR output (x, Cp columns, one row per panel node)."""
    rows = []
    for line in cp_file.read_text().splitlines():
        parts = line.split()
        if len(parts) != 2:
            continue
        try:
            rows.append([float(parts[0]), float(parts[1])])
        except ValueError:
            continue

    return pd.DataFrame(rows, columns=["x", "Cp"])


def split_cp_surfaces(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split a Cp(x) DataFrame into (upper, lower) surface branches, both
    ordered LE -> TE.

    CPWR dumps points in the same order XFoil paneled the airfoil, which
    follows our own .dat export convention (see geometry_generator/utils.py
    export_dat): upper surface TE -> LE, then lower surface LE -> TE. The
    leading edge is the point of minimum x, marking the split.
    """
    le_idx = int(df["x"].idxmin())
    upper = df.iloc[: le_idx + 1].iloc[::-1].reset_index(drop=True)  # TE->LE reversed to LE->TE
    lower = df.iloc[le_idx:].reset_index(drop=True)  # already LE->TE
    return upper, lower


def run_cp(req: CpRequest, timeout: float = 60.0) -> pd.DataFrame:
    """
    Run XFoil at a single angle of attack and return the surface Cp
    distribution as a DataFrame with columns: x, Cp (one row per panel
    node, upper-then-lower order -- see split_cp_surfaces()).
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        cp_file = tmp_path / "cp.txt"

        airfoil_path = _resolve_airfoil_dat(req.airfoil, tmp_path)
        script = _build_cp_script(req, cp_file.name, airfoil_path.name)

        result = subprocess.run(
            [XFOIL_BIN],
            input=script,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tmp_path,
        )

        if not cp_file.exists():
            raise RuntimeError(
                f"XFoil did not produce a Cp file. stdout tail:\n{result.stdout[-2000:]}"
            )

        df = _parse_cp_file(cp_file)
        if df.empty:
            raise RuntimeError(
                f"Cp file was empty -- likely non-convergence at alpha={req.alpha}. "
                f"stdout tail:\n{result.stdout[-2000:]}"
            )
        return df


def _parse_polar_file(polar_file: Path) -> pd.DataFrame:
    """Parse XFoil's fixed-width polar dump format into a DataFrame."""
    lines = polar_file.read_text().splitlines()

    header_idx = next(
        i for i, l in enumerate(lines) if l.strip().startswith("alpha")
    )
    data_lines = lines[header_idx + 2:]  # skip header + dashed separator

    rows = []
    for line in data_lines:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) < 7:
            continue
        rows.append([float(p) for p in parts[:7]])

    cols = ["alpha", "CL", "CD", "CDp", "CM", "Top_Xtr", "Bot_Xtr"]
    return pd.DataFrame(rows, columns=cols)


def run_polar(req: PolarRequest, timeout: float = 60.0) -> pd.DataFrame:
    """
    Run an XFoil polar sweep and return results as a DataFrame with columns:
    alpha, CL, CD, CDp, CM, Top_Xtr, Bot_Xtr
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        polar_file = tmp_path / "polar.txt"

        # XFoil truncates filenames to 48 chars (fixed Fortran buffer), and a
        # macOS temp path is far longer than that. So we run XFoil *inside* the
        # temp dir (cwd=tmp_path) and only ever hand it short relative names.
        airfoil_path = _resolve_airfoil_dat(req.airfoil, tmp_path)

        script = _build_script(req, polar_file.name, airfoil_path.name)

        result = subprocess.run(
            [XFOIL_BIN],
            input=script,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=tmp_path,
        )
        # Note: XFoil's exit code is not a reliable success signal here --
        # because we don't send QUIT (see _build_script docstring), the
        # process exits via EOF-on-stdin, which some builds report as a
        # non-zero code even when the polar file was written correctly.
        # The real success check is whether the polar file has data rows.

        if not polar_file.exists():
            raise RuntimeError(
                f"XFoil did not produce a polar file. stdout tail:\n"
                f"{result.stdout[-2000:]}"
            )

        df = _parse_polar_file(polar_file)
        if df.empty:
            raise RuntimeError(
                f"Polar file was empty -- likely non-convergence. "
                f"stdout tail:\n{result.stdout[-2000:]}"
            )
        return df
