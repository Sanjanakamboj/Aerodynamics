"""
plots.py

Plotting for geometry analysis: airfoil shape as a standard NACA
nomenclature diagram (chord line, mean camber line, nose circle, max
thickness/camber with location, all labeled with actual computed values),
thickness distribution, and surface curvature.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from .metrics import analyze_airfoil, thickness_distribution


def _dimension_line(ax, x1, x2, y, label):
    """Horizontal double-headed dimension line with a centered value label above it."""
    ax.annotate("", xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="<->", color="black", lw=1))
    ax.text(
        (x1 + x2) / 2, y, label, ha="center", va="bottom", fontsize=8.5,
        bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"),
    )


def _leader_line(ax, x, y_from, y_to):
    """Thin dotted vertical leader connecting a dimension line up to the geometry above it."""
    ax.plot([x, x], [y_from, y_to], color="gray", lw=0.6, ls=":")


def _plot_shape(airfoil, report):
    """NACA-style nomenclature diagram: chord line, mean camber line, nose
    circle, max thickness/camber, and their locations, each labeled with
    the actual value from `report` (not just generic labels)."""

    chord = report["chord"]
    t_max, t_loc = report["max_thickness"], report["max_thickness_location"]
    c_max, c_loc = report["max_camber"], report["max_camber_location"]
    le_radius = report["leading_edge_radius"]
    mean_x, mean_y = report["mean_line_x"], report["mean_line_y"]

    y_top = float(np.max(airfoil.yu))
    y_bot = float(np.min(airfoil.yl))
    span = y_top - y_bot  # airfoil's own thickness scale -- annotation offsets scale off this,
    # not chord, since a thin airfoil (chord=1, span~0.1) would otherwise leave huge blank gaps.

    fig, ax = plt.subplots(figsize=(12, 8))

    # --- Airfoil body ---
    ax.fill(
        np.concatenate([airfoil.xu, airfoil.xl[::-1]]),
        np.concatenate([airfoil.yu, airfoil.yl[::-1]]),
        color="lightgray", zorder=1,
    )
    ax.plot(airfoil.xu, airfoil.yu, color="mediumblue", lw=1.8, zorder=3)
    ax.plot(airfoil.xl, airfoil.yl, color="mediumblue", lw=1.8, zorder=3)

    # --- Chord line ---
    ax.plot([0, chord], [0, 0], color="red", lw=1, zorder=2)

    # --- Mean camber line ---
    ax.plot(mean_x, mean_y, "--", color="green", lw=1.6, zorder=3)
    mid = len(mean_x) * 3 // 4
    ax.annotate(
        "Mean camber line", xy=(mean_x[mid], mean_y[mid]), xytext=(chord * 0.80, y_top + 0.8 * span),
        fontsize=9, ha="left", arrowprops=dict(arrowstyle="->", color="black", lw=0.8),
    )

    # --- Upper / lower surface ---
    xu_ref = chord * 0.30
    ax.annotate(
        "Upper surface", xy=(xu_ref, float(np.interp(xu_ref, airfoil.xu, airfoil.yu))),
        xytext=(chord * 0.30, y_top + 1.6 * span),
        fontsize=9, ha="center", arrowprops=dict(arrowstyle="->", color="black", lw=0.8),
    )
    xl_ref = chord * 0.55
    ax.annotate(
        "Lower surface", xy=(xl_ref, float(np.interp(xl_ref, airfoil.xl, airfoil.yl))),
        xytext=(chord * 0.55, y_bot - 1.3 * span),
        fontsize=9, ha="center", arrowprops=dict(arrowstyle="->", color="black", lw=0.8),
    )

    # --- Leading / trailing edge ---
    ax.annotate(
        "Leading edge", xy=(0, 0), xytext=(-chord * 0.16, y_top + 0.5 * span),
        fontsize=9, ha="right", arrowprops=dict(arrowstyle="->", color="black", lw=0.8),
    )
    ax.annotate(
        "Trailing edge", xy=(chord, 0), xytext=(chord * 1.02, y_top + 0.5 * span),
        fontsize=9, ha="left", arrowprops=dict(arrowstyle="->", color="black", lw=0.8),
    )

    # --- Nose circle (leading-edge radius) ---
    nose_center = (le_radius, float(np.interp(le_radius, mean_x, mean_y)))
    ax.add_patch(plt.Circle(nose_center, le_radius, fill=False, color="gray", lw=1, ls="--", zorder=4))
    ax.annotate(
        f"Nose circle, r = {le_radius:.4f}", xy=nose_center, xytext=(-chord * 0.16, y_bot - 0.5 * span),
        fontsize=9, ha="right", arrowprops=dict(arrowstyle="->", color="black", lw=0.8),
    )

    # --- Maximum thickness: vertical double arrow through the airfoil,
    # label above it (well clear of the airfoil body) ---
    yu_at_tmax = float(np.interp(t_loc, airfoil.xu, airfoil.yu))
    yl_at_tmax = float(np.interp(t_loc, airfoil.xl, airfoil.yl))
    ax.annotate("", xy=(t_loc, yu_at_tmax), xytext=(t_loc, yl_at_tmax), arrowprops=dict(arrowstyle="<->", lw=1))
    _leader_line(ax, t_loc, yu_at_tmax, y_top + 0.35 * span)
    ax.text(t_loc, y_top + 0.4 * span, f"Max thickness\n= {t_max:.4f}", fontsize=8.5, ha="center", va="bottom")

    # --- Maximum camber: vertical double arrow from chord line to camber
    # line, label below the chord line (clear of the thickness label above) ---
    ax.annotate("", xy=(c_loc, c_max), xytext=(c_loc, 0), arrowprops=dict(arrowstyle="<->", lw=1))
    _leader_line(ax, c_loc, 0, y_bot - 0.35 * span)
    ax.text(c_loc, y_bot - 0.4 * span, f"Max camber\n= {c_max:.4f}", fontsize=8.5, ha="center", va="top")

    # --- Dimension lines below the airfoil: location of max thickness,
    # location of max camber, and overall chord ---
    dim0_y = y_bot - 1.0 * span
    dim1_y = y_bot - 1.9 * span
    dim2_y = y_bot - 2.6 * span
    dim3_y = y_bot - 3.3 * span

    _leader_line(ax, t_loc, dim0_y, dim1_y)
    _leader_line(ax, c_loc, 0, dim2_y)
    _leader_line(ax, 0, dim0_y, dim3_y)
    _leader_line(ax, chord, 0, dim3_y)

    _dimension_line(ax, 0, t_loc, dim1_y, f"Location of max thickness = {t_loc:.4f}")
    _dimension_line(ax, 0, c_loc, dim2_y, f"Location of max camber = {c_loc:.4f}")
    _dimension_line(ax, 0, chord, dim3_y, f"Chord = {chord:.4f}")

    ax.set_xlim(-chord * 0.22, chord * 1.22)
    ax.set_ylim(dim3_y - 0.5 * span, y_top + 2.0 * span)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(f"{airfoil.name} -- Geometry", fontsize=12, pad=10)
    fig.tight_layout()

    return fig


def plot_geometry_analysis(airfoil, report=None, show=True):
    """
    Build the geometry-analysis figure set for an Airfoil: shape
    (NACA-style nomenclature diagram), thickness distribution, and
    surface curvature.

    Returns
    -------
    dict[str, matplotlib.figure.Figure]
    """

    if report is None:
        report = analyze_airfoil(airfoil)

    figures = {"shape": _plot_shape(airfoil, report)}

    # --- Thickness distribution ---
    x, t = thickness_distribution(airfoil)
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(x, t)
    ax.grid(True)
    ax.set_xlabel("x/c")
    ax.set_ylabel("thickness, t(x)/c")
    ax.set_title(f"{airfoil.name} -- Thickness Distribution")
    fig.tight_layout()
    figures["thickness_distribution"] = fig

    # --- Surface curvature ---
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(airfoil.xu, report["curvature_upper"], label="Upper Surface")
    ax.plot(airfoil.xl, report["curvature_lower"], label="Lower Surface")
    ax.grid(True)
    ax.set_xlabel("x/c")
    ax.set_ylabel("curvature")
    ax.set_title(f"{airfoil.name} -- Surface Curvature")
    ax.legend()
    fig.tight_layout()
    figures["curvature"] = fig

    if show:
        plt.show()

    return figures


def save_geometry_analysis(airfoil, out_dir, report=None):
    """
    Build the geometry-analysis figures and save each as a PNG into
    out_dir.

    Returns
    -------
    dict[str, Path]
    """

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    figures = plot_geometry_analysis(airfoil, report=report, show=False)

    paths = {}
    for name, fig in figures.items():
        path = out_dir / f"{name}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close(fig)
        paths[name] = path

    return paths
