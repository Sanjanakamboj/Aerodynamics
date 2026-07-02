"""
naca5.py
---------

Generate NACA 5-digit airfoils.
"""

from .airfoil import Airfoil
from .camber import camber_line_5digit
from .spacing import cosine_spacing, uniform_spacing
from .thickness import thickness_distribution
from .utils import surface_coordinates


def generate_naca5(code, n_points=200, spacing="cosine"):
    """
    Generate NACA 5-digit airfoil.

    Parameters
    ----------
    code : str
        Example: "23012" (230XX family, non-reflexed) or "23112" (reflexed).

    n_points : int

    spacing : str
        "cosine" or "uniform"

    Returns
    -------
    Airfoil
    """

    code = code.upper().replace("NACA", "").strip()

    if len(code) != 5 or not code.isdigit():
        raise ValueError("NACA 5-digit code must contain exactly 5 digits, e.g. '23012'.")

    l_digit = int(code[0])
    p_digit = int(code[1])
    q_digit = int(code[2])
    t = int(code[3:]) / 100

    if spacing.lower() == "cosine":
        x = cosine_spacing(n_points)
    elif spacing.lower() == "uniform":
        x = uniform_spacing(n_points)
    else:
        raise ValueError("Spacing must be 'cosine' or 'uniform'.")

    yt = thickness_distribution(x, t)
    yc, dyc_dx = camber_line_5digit(x, l_digit, p_digit, q_digit)
    xu, yu, xl, yl = surface_coordinates(x, yc, yt, dyc_dx)

    return Airfoil(
        name=f"NACA {code}",
        source="generated:naca5",
        xu=xu,
        yu=yu,
        xl=xl,
        yl=yl,
        meta={"l": l_digit, "p": p_digit, "q": q_digit, "t": t, "camber_x": x, "camber_y": yc},
    )
