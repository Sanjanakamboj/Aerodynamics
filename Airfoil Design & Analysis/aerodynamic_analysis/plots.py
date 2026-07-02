"""
plots.py

Plotting for aerodynamic analysis: lift curve (CL vs alpha) and drag polar
(CD vs CL) from an XFoil polar sweep, side by side in one figure. Accepts
either a single polar (the common case) or several labeled polars overlaid
on the same axes (e.g. comparing Reynolds numbers).
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .xfoil_runner import split_cp_surfaces


def _as_series(df_or_series, reynolds):
    if isinstance(df_or_series, pd.DataFrame):
        label = f"Re = {reynolds:.0f}" if reynolds is not None else "XFoil"
        return [(label, df_or_series)]
    return df_or_series


def plot_polar_analysis(df_or_series, name="Airfoil", reynolds=None, show=True):
    """
    Build the polar-analysis figure: lift curve and drag polar side by side.

    Parameters
    ----------
    df_or_series : DataFrame, or list of (label, DataFrame) pairs to
        overlay multiple polars on the same axes (e.g. comparing Reynolds
        numbers). A single DataFrame is labeled from `reynolds`.

    Returns
    -------
    matplotlib.figure.Figure
    """

    series = _as_series(df_or_series, reynolds)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    for label, df in series:
        axes[0].plot(df["alpha"], df["CL"], "o-", label=label)
        axes[1].plot(df["CD"], df["CL"], "o-", label=label)

    axes[0].axhline(0, color="black", lw=0.8)
    axes[0].set_xlabel("Angle of attack, α (deg)")
    axes[0].set_ylabel("$C_L$")
    axes[0].set_title(f"{name} Lift Curve")
    axes[0].legend()
    axes[0].grid(alpha=0.3)
    axes[0].margins(x=0.08, y=0.1)

    axes[1].set_xlabel("$C_D$")
    axes[1].set_ylabel("$C_L$")
    axes[1].set_title(f"{name} Drag Polar")
    axes[1].legend()
    axes[1].grid(alpha=0.3)
    axes[1].margins(x=0.08, y=0.1)

    fig.tight_layout()

    if show:
        plt.show()

    return fig


def save_polar_analysis(df_or_series, out_dir, prefix, name="Airfoil", reynolds=None):
    """
    Build the polar-analysis figure and save it as <prefix>.png into
    out_dir.

    Returns
    -------
    Path
    """

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fig = plot_polar_analysis(df_or_series, name=name, reynolds=reynolds, show=False)

    path = out_dir / f"{prefix}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return path


def plot_cp_distribution(df, name="Airfoil", alpha=None, show=True):
    """
    Build the Cp(x/c) distribution figure: upper and lower surface,
    y-axis inverted (aerodynamics convention -- suction/negative Cp
    plotted upward).

    Parameters
    ----------
    df : DataFrame with columns x, Cp (as returned by run_cp())

    Returns
    -------
    matplotlib.figure.Figure
    """
    upper, lower = split_cp_surfaces(df)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(upper["x"], upper["Cp"], "o-", ms=3, label="Upper Surface")
    ax.plot(lower["x"], lower["Cp"], "o-", ms=3, label="Lower Surface")
    ax.invert_yaxis()
    ax.set_xlabel("x/c")
    ax.set_ylabel("$C_p$")
    title = f"{name} Cp Distribution"
    if alpha is not None:
        title += f" (α = {alpha:.1f}°)"
    ax.set_title(title)
    ax.legend()
    ax.grid(alpha=0.3)
    ax.margins(x=0.05, y=0.1)
    fig.tight_layout()

    if show:
        plt.show()

    return fig


def save_cp_distribution(df, out_dir, prefix, name="Airfoil", alpha=None):
    """
    Build the Cp distribution figure and save it as <prefix>.png into
    out_dir.

    Returns
    -------
    Path
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fig = plot_cp_distribution(df, name=name, alpha=alpha, show=False)

    path = out_dir / f"{prefix}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return path


# (label, format string) for each summarize_polar() key, in display order.
_METRIC_LABELS = {
    "cl_max": ("CLmax", "{:.4f}"),
    "cd_min": ("CDmin", "{:.5f}"),
    "alpha_at_cd_min": ("alpha @ CDmin (deg)", "{:.2f}"),
    "max_L_over_D": ("Max L/D", "{:.2f}"),
    "alpha_at_max_L_over_D": ("alpha @ Max L/D (deg)", "{:.2f}"),
    "best_glide_angle": ("Best Glide Angle (deg)", "{:.2f}"),
    "stall_angle": ("Stall Angle (deg)", "{:.2f}"),
    "zero_lift_angle": ("Zero Lift Angle (deg)", "{:.2f}"),
    "lift_curve_slope": ("Lift Curve Slope (/rad)", "{:.3f}"),
    "moment_coefficient": ("Moment Coefficient, CM0", "{:.4f}"),
}


def plot_metrics_table(report_or_series, name="Airfoil", show=True):
    """
    Render summarize_polar()'s performance-metrics report as a table
    figure.

    Parameters
    ----------
    report_or_series : dict, or list of (label, dict) pairs to compare
        several reports side by side (e.g. across Reynolds numbers).

    Returns
    -------
    matplotlib.figure.Figure
    """

    series = [("Value", report_or_series)] if isinstance(report_or_series, dict) else report_or_series

    rows = [
        [metric_label] + [fmt.format(report[key]) for _, report in series]
        for key, (metric_label, fmt) in _METRIC_LABELS.items()
        if all(key in report for _, report in series)
    ]
    col_labels = ["Metric"] + [label for label, _ in series]

    fig, ax = plt.subplots(figsize=(2.5 + 2 * len(series), 0.35 * len(rows) + 0.6))
    ax.axis("off")

    table = ax.table(cellText=rows, colLabels=col_labels, cellLoc="left", bbox=[0, 0, 1, 1])
    table.auto_set_font_size(False)
    table.set_fontsize(10)

    ax.set_title(f"{name} Performance Metrics", pad=12)
    fig.tight_layout()

    if show:
        plt.show()

    return fig


def save_metrics_table(report_or_series, out_dir, prefix, name="Airfoil"):
    """
    Build the metrics-table figure and save it as <prefix>.png into
    out_dir.

    Returns
    -------
    Path
    """

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fig = plot_metrics_table(report_or_series, name=name, show=False)

    path = out_dir / f"{prefix}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return path
