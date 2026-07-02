"""validate.py — sanity-check the wrapper: plot a polar, run a second
Reynolds number to confirm the wrapper isn't a one-shot fluke, and verify
basic physical expectations (CL=0 at alpha=0 for a symmetric airfoil,
higher Re means lower drag at a matched alpha, etc).

Usage: python validate.py <code> [re1] [re2]
`code` is required -- no implicit default -- so this always validates
whichever airfoil you're actually working on, e.g. the same code you just
ran through get_airfoil.py, rather than silently falling back to some
other airfoil if you forget to pass it.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

# get_airfoil.py lives at the project root, one level up from this package.
# Add it to sys.path so both get_airfoil and aerodynamic_analysis (this
# module's own package) are importable regardless of how this file was
# invoked -- run directly (python validate.py) or imported as
# aerodynamic_analysis.validate (e.g. from get_airfoil.py).
#
# Siblings are imported via the fully-qualified aerodynamic_analysis.*
# path rather than bare names -- bare imports would load e.g. plots.py a
# second time under the plain name "plots" instead of
# "aerodynamic_analysis.plots", and plots.py's own internal relative
# import (from .xfoil_runner import ...) only works when it's loaded as a
# proper package submodule.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from aerodynamic_analysis.xfoil_runner import PolarRequest, run_polar
from aerodynamic_analysis.polar_analysis import cd_at_alpha, cl_at_alpha, lift_curve_slope, summarize_polar
from aerodynamic_analysis.plots import save_metrics_table, save_polar_analysis
from get_airfoil import AIRFOILS_ROOT, display_code


def _is_symmetric_naca4(code):
    """NACA 4-digit codes 00XX (zero camber) are symmetric; nothing else is checkable this way."""
    digits = code.upper().replace("NACA", "").strip()
    return len(digits) == 4 and digits.isdigit() and digits[0] == "0"


def validate(code, re1=1e6, re2=3e6, alpha_start=-4, alpha_end=20, alpha_step=1.0, df1=None, df2=None):
    """
    df1/df2 : already-computed polars for re1/re2, if the caller already
        has them (e.g. get_airfoil.py reusing its own polar run instead
        of paying for a second identical XFoil call).
    """
    if df1 is None:
        req1 = PolarRequest(airfoil=code, reynolds=re1, alpha_start=alpha_start, alpha_end=alpha_end, alpha_step=alpha_step)
        df1 = run_polar(req1)

    if df2 is None:
        # Second Reynolds number, to confirm the wrapper generalizes and
        # isn't tuned to one specific input.
        req2 = PolarRequest(airfoil=code, reynolds=re2, alpha_start=alpha_start, alpha_end=alpha_end, alpha_step=alpha_step)
        df2 = run_polar(req2)

    if _is_symmetric_naca4(code):
        sym_cl_at_zero = cl_at_alpha(df1, 0.0)
        assert abs(sym_cl_at_zero) < 1e-3, f"Symmetric airfoil should have CL~0 at alpha=0, got {sym_cl_at_zero}"
        print(f"Symmetric airfoil check passed: CL(0)={sym_cl_at_zero:.5f}")
    else:
        print(f"CL(alpha=0)={cl_at_alpha(df1, 0.0):.4f} (not checked -- {code} isn't a symmetric NACA 4-digit airfoil)")

    slope = lift_curve_slope(df1)
    print(f"Lift slope ≈ {slope:.2f} /rad (thin airfoil theory predicts 2π ≈ 6.28)")

    check_alpha = 4.0
    cd1, cd2 = cd_at_alpha(df1, check_alpha), cd_at_alpha(df2, check_alpha)
    higher_re_drag_lower = cd2 < cd1
    print(f"Higher Re has lower drag at alpha={check_alpha}: {higher_re_drag_lower} "
          f"(Re={re1:.0f} CD={cd1:.5f}, Re={re2:.0f} CD={cd2:.5f})")
    assert higher_re_drag_lower, "Expected lower CD at higher Re (thinner boundary layer)"

    print("All sanity checks passed.")

    # Same Airfoils/<code>/ folder get_airfoil.py uses, so this lands
    # alongside that airfoil's geometry plots.
    out_dir = AIRFOILS_ROOT / display_code(code)
    out_path = save_polar_analysis(
        [(f"Re = {re1:.0f}", df1), (f"Re = {re2:.0f}", df2)],
        out_dir,
        prefix="polar_validation",
        name=display_code(code),
    )
    print(f"Saved {out_path}")

    table_path = save_metrics_table(
        [(f"Re = {re1:.0f}", summarize_polar(df1)), (f"Re = {re2:.0f}", summarize_polar(df2))],
        out_dir,
        prefix="metrics_validation",
        name=display_code(code),
    )
    print(f"Saved {table_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python validate.py <code> [re1] [re2]  (e.g. python validate.py 0012)")

    code = sys.argv[1]
    re1 = float(sys.argv[2]) if len(sys.argv) > 2 else 1e6
    re2 = float(sys.argv[3]) if len(sys.argv) > 3 else 3e6
    validate(code, re1, re2)
