"""
spacing.py

Generate x-coordinate distributions.
"""

import numpy as np


def cosine_spacing(n_points=200):
    """
    Cosine spacing.

    Parameters
    ----------
    n_points : int

    Returns
    -------
    ndarray
    """

    beta = np.linspace(0.0, np.pi, n_points)

    x = 0.5 * (1 - np.cos(beta))

    return x


def uniform_spacing(n_points=200):
    """
    Uniform spacing.
    """

    return np.linspace(0.0, 1.0, n_points)


def half_cosine_spacing(n_points=200):
    """
    Slightly denser leading edge spacing.
    """

    beta = np.linspace(0, np.pi / 2, n_points)

    x = np.sin(beta)

    return x