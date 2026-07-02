"""
thickness.py

Thickness distributions for NACA airfoils.
"""

import numpy as np


def thickness_distribution(x, t, closed_te=False):
    """
    NACA thickness distribution.

    Parameters
    ----------
    x : ndarray
    t : float
        Maximum thickness ratio

    closed_te : bool
        Closed trailing edge if True

    Returns
    -------
    yt : ndarray
    """

    if closed_te:
        a4 = -0.1036
    else:
        a4 = -0.1015

    yt = (
        5 * t * (
            0.2969 * np.sqrt(x)
            - 0.1260 * x
            - 0.3516 * x**2
            + 0.2843 * x**3
            + a4 * x**4
        )
    )

    return yt