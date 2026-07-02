"""
utils.py
"""

import numpy as np


def surface_coordinates(x, yc, yt, dyc_dx):
    """
    Compute upper and lower surfaces.
    """

    theta = np.arctan(dyc_dx)

    xu = x - yt * np.sin(theta)
    yu = yc + yt * np.cos(theta)

    xl = x + yt * np.sin(theta)
    yl = yc - yt * np.cos(theta)

    return xu, yu, xl, yl


def export_dat(filename, xu, yu, xl, yl, name="Airfoil"):
    """
    Export to DAT.
    """

    with open(filename, "w") as f:

        f.write(name + "\n")

        for X, Y in zip(xu[::-1], yu[::-1]):
            f.write(f"{X:.6f} {Y:.6f}\n")

        for X, Y in zip(xl[1:], yl[1:]):
            f.write(f"{X:.6f} {Y:.6f}\n")


def chord_length(x):
    return np.max(x) - np.min(x)


def max_thickness(yt):
    return 2 * np.max(yt)