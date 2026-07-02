"""
compare_airfoils.py

Compare multiple airfoils side by side: overlaid geometry, and (if a
Reynolds number is given) overlaid lift curves, drag polars, and a
side-by-side performance-metrics table -- using the same get_airfoil()
and aerodynamic_analysis machinery as the rest of this project.

Usage: python compare_airfoils.py <code1> <code2> [<code3> ...] [--re REYNOLDS]
"""

import argparse
from pathlib import Path

from comparison_dashboard import save_geometry_comparison
from get_airfoil import display_code, get_airfoil

COMPARISONS_ROOT = Path(__file__).parent / "Comparisons"


def compare_airfoils(codes, reynolds=None):
    airfoils = [get_airfoil(code) for code in codes]

    name = "_vs_".join(display_code(c).replace(" ", "") for c in codes)
    out_dir = COMPARISONS_ROOT / name

    geometry_path = save_geometry_comparison(airfoils, out_dir)
    print(f"Saved {geometry_path}")

    if reynolds is not None:
        # Imported lazily: aerodynamic_analysis.xfoil_runner imports
        # get_airfoil at module load time, so importing it up front here
        # would be circular.
        from aerodynamic_analysis import (
            PolarRequest,
            run_polar,
            save_metrics_table,
            save_polar_analysis,
            summarize_polar,
        )

        polars = []
        reports = []
        for code, airfoil in zip(codes, airfoils):
            df = run_polar(PolarRequest(airfoil=code, reynolds=reynolds))
            polars.append((airfoil.name, df))
            reports.append((airfoil.name, summarize_polar(df)))

        prefix = f"polar_Re{reynolds:.0f}"
        polar_path = save_polar_analysis(polars, out_dir, prefix=prefix, name=name)
        print(f"Saved {polar_path}")

        table_path = save_metrics_table(reports, out_dir, prefix=f"{prefix}_metrics", name=name)
        print(f"Saved {table_path}")

    return out_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare multiple airfoils side by side.")
    parser.add_argument("codes", nargs="+", help="Airfoil codes, e.g. 0012 2412 sc20714")
    parser.add_argument("--re", type=float, default=None, dest="reynolds", help="Reynolds number for polar comparison")
    args = parser.parse_args()

    compare_airfoils(args.codes, reynolds=args.reynolds)
