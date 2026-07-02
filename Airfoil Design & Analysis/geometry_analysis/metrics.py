"""
metrics.py

Geometric analysis of an Airfoil, computed purely from its surface
coordinates (xu, yu, xl, yl). Works the same way whether the Airfoil came
from the generator (which already knows its camber line analytically) or
from the database/import path (which only ever has raw points) -- these
functions never rely on `meta`.
"""

import numpy as np


def _common_grid(airfoil, n=200):
    """Resample upper and lower surfaces onto a shared x grid, LE -> TE."""
    x_max = min(airfoil.xu.max(), airfoil.xl.max())
    x = np.linspace(0.0, x_max, n)
    yu = np.interp(x, airfoil.xu, airfoil.yu)
    yl = np.interp(x, airfoil.xl, airfoil.yl)
    return x, yu, yl


def thickness_distribution(airfoil, n=200):
    """Thickness t(x) = yu(x) - yl(x) on a common grid."""
    x, yu, yl = _common_grid(airfoil, n)
    return x, yu - yl


def camber_line(airfoil, n=200):
    """Mean line yc(x) = (yu(x) + yl(x)) / 2 on a common grid."""
    x, yu, yl = _common_grid(airfoil, n)
    return x, 0.5 * (yu + yl)


def max_thickness(airfoil, n=200):
    """Returns (value, x_location) of the maximum thickness."""
    x, t = thickness_distribution(airfoil, n)
    i = int(np.argmax(t))
    return float(t[i]), float(x[i])


def max_camber(airfoil, n=200):
    """Returns (value, x_location) of the maximum camber."""
    x, yc = camber_line(airfoil, n)
    i = int(np.argmax(np.abs(yc)))
    return float(yc[i]), float(x[i])


def leading_edge_radius(airfoil, n_fit=6):
    """
    Estimate leading-edge radius by algebraically fitting a circle through
    the first `n_fit` points on both the upper and lower surface.
    """
    pts_u = np.column_stack([airfoil.xu[:n_fit], airfoil.yu[:n_fit]])
    pts_l = np.column_stack([airfoil.xl[1:n_fit], airfoil.yl[1:n_fit]])  # skip duplicate LE point
    pts = np.vstack([pts_u, pts_l])

    x, y = pts[:, 0], pts[:, 1]
    A = np.column_stack([2 * x, 2 * y, np.ones_like(x)])
    b = x**2 + y**2
    (a, b_center, c), *_ = np.linalg.lstsq(A, b, rcond=None)

    r_squared = c + a**2 + b_center**2
    return float(np.sqrt(max(r_squared, 0.0)))


def trailing_edge_angle(airfoil, n_fit=6):
    """
    Included wedge angle (degrees) between the upper and lower surface
    tangents at the trailing edge, estimated from the last `n_fit` points
    on each surface.
    """
    dx_u = airfoil.xu[-1] - airfoil.xu[-n_fit]
    dy_u = airfoil.yu[-1] - airfoil.yu[-n_fit]
    dx_l = airfoil.xl[-1] - airfoil.xl[-n_fit]
    dy_l = airfoil.yl[-1] - airfoil.yl[-n_fit]

    angle_u = np.arctan2(dy_u, dx_u)
    angle_l = np.arctan2(dy_l, dx_l)

    return float(abs(np.degrees(angle_u - angle_l)))


def cross_sectional_area(airfoil):
    """Enclosed area of the airfoil's closed surface loop (shoelace formula)."""
    x = np.concatenate([airfoil.xu, airfoil.xl[::-1]])
    y = np.concatenate([airfoil.yu, airfoil.yl[::-1]])
    return float(0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def surface_curvature(x, y):
    """
    Curvature kappa(i) along a parametric curve (x[i], y[i]), aligned to
    the input points.

    Finite-difference curvature needs roughly evenly-spaced points to be
    numerically stable, but the airfoil's cosine-spaced grid bunches
    points hard at the leading and trailing edges. Differentiating
    directly against that raw spacing makes the second-derivative
    estimate blow up right at those edges (a boundary artifact, not real
    geometry -- e.g. curvature 240 at the very last trailing-edge point
    vs. ~16 a few points earlier). So this reparametrizes onto a uniform
    arc-length grid to compute derivatives, then interpolates back onto
    the original points.
    """
    ds = np.hypot(np.diff(x), np.diff(y))
    s = np.concatenate([[0.0], np.cumsum(ds)])

    s_uniform = np.linspace(s[0], s[-1], len(x))
    x_u = np.interp(s_uniform, s, x)
    y_u = np.interp(s_uniform, s, y)

    dx = np.gradient(x_u, s_uniform)
    dy = np.gradient(y_u, s_uniform)
    ddx = np.gradient(dx, s_uniform)
    ddy = np.gradient(dy, s_uniform)

    denom = (dx**2 + dy**2) ** 1.5
    with np.errstate(divide="ignore", invalid="ignore"):
        kappa_uniform = (dx * ddy - dy * ddx) / denom

    return np.interp(s, s_uniform, kappa_uniform)


def analyze_airfoil(airfoil, n=200):
    """
    Compute the full geometry report for an Airfoil: thickness, camber,
    chord, leading-edge radius, trailing-edge angle, cross-sectional area,
    mean line, and surface curvature.
    """

    t_max, t_loc = max_thickness(airfoil, n)
    c_max, c_loc = max_camber(airfoil, n)
    x_grid, yc = camber_line(airfoil, n)

    return {
        "chord": airfoil.chord,
        "max_thickness": t_max,
        "max_thickness_location": t_loc,
        "max_camber": c_max,
        "max_camber_location": c_loc,
        "leading_edge_radius": leading_edge_radius(airfoil),
        "trailing_edge_angle": trailing_edge_angle(airfoil),
        "cross_sectional_area": cross_sectional_area(airfoil),
        "mean_line_x": x_grid,
        "mean_line_y": yc,
        "curvature_upper": surface_curvature(airfoil.xu, airfoil.yu),
        "curvature_lower": surface_curvature(airfoil.xl, airfoil.yl),
    }
