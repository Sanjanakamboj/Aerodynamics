"""
geometry_compare.py

Overlay multiple airfoils' shapes on one plot, for visual comparison.
"""

from pathlib import Path

import matplotlib.pyplot as plt


def plot_geometry_comparison(airfoils, show=True):
    """
    Build a shape-comparison figure: each airfoil's upper/lower surface
    overlaid on the same axes.

    Parameters
    ----------
    airfoils : list of Airfoil

    Returns
    -------
    matplotlib.figure.Figure
    """

    fig, ax = plt.subplots(figsize=(10, 4.5))

    for airfoil in airfoils:
        line = ax.plot(airfoil.xu, airfoil.yu, label=airfoil.name)[0]
        ax.plot(airfoil.xl, airfoil.yl, color=line.get_color())

    ax.set_aspect("equal")
    ax.grid(True)
    ax.set_xlabel("x/c")
    ax.set_ylabel("y/c")
    ax.set_title("Airfoil Shape Comparison")
    ax.legend()
    fig.tight_layout()

    if show:
        plt.show()

    return fig


def save_geometry_comparison(airfoils, out_dir, prefix="geometry_comparison"):
    """
    Build the shape-comparison figure and save it as <prefix>.png into
    out_dir.

    Returns
    -------
    Path
    """

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    fig = plot_geometry_comparison(airfoils, show=False)

    path = out_dir / f"{prefix}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return path
