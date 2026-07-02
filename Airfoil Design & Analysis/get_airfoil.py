"""
get_airfoil.py

Main entry point for Airfoil Design & Analysis.

get_airfoil("2412") first checks the local Airfoil Database (NACA, UIUC,
NASA, Selig, User Library) for a matching coordinate file; if none is
found, it falls back to generating the airfoil analytically -- NACA
4-digit or 5-digit, detected from the code itself -- and saves the result
into the User Library so the next lookup finds it instead of regenerating.
"""

from pathlib import Path

from airfoil_database import find_in_database, save_to_library
from geometry_analysis import analyze_airfoil, save_geometry_analysis
from geometry_generator import Airfoil, generate_naca4, generate_naca5, load_dat

AIRFOILS_ROOT = Path(__file__).parent / "Airfoils"


def display_code(code):
    """'2412' / 'naca2412' -> 'NACA 2412'; anything else (e.g. 'sc20714') -> 'SC20714'."""
    digits = code.upper().replace("NACA", "").strip()
    if digits.isdigit() and len(digits) in (4, 5):
        return f"NACA {digits}"
    return code.upper().strip()


def get_airfoil(code, n_points=200, spacing="cosine") -> Airfoil:
    match = find_in_database(code)
    if match is not None:
        return load_dat(match, name=display_code(code), source=f"database:{match.parent.name}")

    digits = code.upper().replace("NACA", "").strip()

    if len(digits) == 4 and digits.isdigit():
        airfoil = generate_naca4(digits, n_points=n_points, spacing=spacing)
    elif len(digits) == 5 and digits.isdigit():
        airfoil = generate_naca5(digits, n_points=n_points, spacing=spacing)
    else:
        raise ValueError(
            f"'{code}' was not found in the Airfoil Database and is not a "
            f"recognized NACA 4- or 5-digit code."
        )

    save_to_library(airfoil)
    return airfoil


if __name__ == "__main__":
    import sys

    code = sys.argv[1] if len(sys.argv) > 1 else "2412"
    reynolds = float(sys.argv[2]) if len(sys.argv) > 2 else None
    alpha_deg = float(sys.argv[3]) if len(sys.argv) > 3 else None

    airfoil = get_airfoil(code)
    print(f"{airfoil.name}  (source: {airfoil.source})")

    report = analyze_airfoil(airfoil)
    print(f"chord={report['chord']:.4f}  max thickness={report['max_thickness']:.4f}")

    dat_path = save_to_library(airfoil)
    print(f"Saved {dat_path}")

    plot_dir = AIRFOILS_ROOT / display_code(code)
    saved = save_geometry_analysis(airfoil, plot_dir, report=report)
    print(f"Saved {len(saved)} plots to {plot_dir}")

    if reynolds is not None:
        # Imported lazily: aerodynamic_analysis.xfoil_runner imports
        # get_airfoil at module load time, so importing it up front here
        # would be circular.
        from aerodynamic_analysis import (
            PolarRequest,
            run_polar,
            save_metrics_table,
            save_polar_analysis,
            save_polar_dat,
            summarize_polar,
        )

        polar_req = PolarRequest(airfoil=code, reynolds=reynolds)
        polar_df = run_polar(polar_req)

        polar_report = summarize_polar(polar_df)
        print(
            f"CLmax={polar_report['cl_max']:.3f} @ alpha={polar_report['stall_angle']:.2f}  "
            f"CDmin={polar_report['cd_min']:.5f} @ alpha={polar_report['alpha_at_cd_min']:.2f}"
        )
        print(
            f"max L/D={polar_report['max_L_over_D']:.2f} @ alpha={polar_report['alpha_at_max_L_over_D']:.2f}  "
            f"best glide angle={polar_report['best_glide_angle']:.2f} deg"
        )
        print(
            f"zero-lift angle={polar_report['zero_lift_angle']:.2f} deg  "
            f"lift-curve slope={polar_report['lift_curve_slope']:.3f}/rad  "
            f"CM0={polar_report['moment_coefficient']:.4f}"
        )

        prefix = f"polar_Re{reynolds:.0f}"
        save_polar_dat(polar_df, plot_dir / f"{prefix}.dat")
        polar_plot_path = save_polar_analysis(polar_df, plot_dir, prefix=prefix, name=airfoil.name, reynolds=reynolds)
        table_path = save_metrics_table(polar_report, plot_dir, prefix=f"{prefix}_metrics", name=airfoil.name)
        print(f"Saved {prefix}.dat, {polar_plot_path.name}, and {table_path.name} to {plot_dir}")

        # Sanity-check the wrapper for this same airfoil across a second
        # Reynolds number, reusing polar_df instead of re-running XFoil at
        # `reynolds` a second time.
        from aerodynamic_analysis.validate import validate

        print()
        validate(code, re1=reynolds, re2=reynolds * 3, df1=polar_df)

        # Cp distribution at a single operating point -- defaults to the
        # best-L/D angle from the polar just computed, unless overridden.
        from aerodynamic_analysis import CpRequest, run_cp, save_cp_distribution

        cp_alpha = alpha_deg if alpha_deg is not None else polar_report["alpha_at_max_L_over_D"]
        cp_df = run_cp(CpRequest(airfoil=code, reynolds=reynolds, alpha=cp_alpha))

        cp_prefix = f"cp_alpha{cp_alpha:g}"
        cp_plot_path = save_cp_distribution(cp_df, plot_dir, prefix=cp_prefix, name=airfoil.name, alpha=cp_alpha)
        print()
        print(f"Saved {cp_plot_path.name} to {plot_dir}")
