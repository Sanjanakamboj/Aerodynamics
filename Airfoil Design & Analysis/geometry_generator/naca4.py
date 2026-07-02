"""
naca4.py
---------

Generate NACA 4-digit airfoils.

Author: Sanjana
"""

from .airfoil import Airfoil
from .camber import camber_line_4digit
from .spacing import cosine_spacing, uniform_spacing
from .thickness import thickness_distribution
from .utils import surface_coordinates


def generate_naca4(code, n_points=200, spacing="cosine"):
    """
    Generate NACA 4-digit airfoil.

    Parameters
    ----------
    code : str
        Example: "2412"

    n_points : int

    spacing : str
        "cosine" or "uniform"

    Returns
    -------
    Airfoil
    """

    code = code.upper().replace("NACA", "").strip()

    if len(code) != 4 or not code.isdigit():
        raise ValueError("NACA 4-digit code must contain exactly 4 digits, e.g. '2412'.")

    m = int(code[0]) / 100
    p = int(code[1]) / 10
    t = int(code[2:]) / 100

    if spacing.lower() == "cosine":
        x = cosine_spacing(n_points)
    elif spacing.lower() == "uniform":
        x = uniform_spacing(n_points)
    else:
        raise ValueError("Spacing must be 'cosine' or 'uniform'.")

    yt = thickness_distribution(x, t)
    yc, dyc_dx = camber_line_4digit(x, m, p)
    xu, yu, xl, yl = surface_coordinates(x, yc, yt, dyc_dx)

    return Airfoil(
        name=f"NACA {code}",
        source="generated:naca4",
        xu=xu,
        yu=yu,
        xl=xl,
        yl=yl,
        meta={"m": m, "p": p, "t": t, "camber_x": x, "camber_y": yc},
    )
