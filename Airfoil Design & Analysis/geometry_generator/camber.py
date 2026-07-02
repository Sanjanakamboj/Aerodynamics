"""
camber.py

Camber-line definitions shared by the NACA 4-digit and 5-digit generators.
"""

import numpy as np


# --------------------------------------------------------
# NACA 4-digit camber line
# --------------------------------------------------------

def camber_line_4digit(x, m, p):
    """
    NACA 4-digit camber line and slope.

    Parameters
    ----------
    x : ndarray
    m : float
        Maximum camber (e.g. 0.02 for a "2" first digit).
    p : float
        Location of maximum camber (e.g. 0.4 for a "4" second digit).

    Returns
    -------
    yc, dyc_dx : ndarray, ndarray
    """

    yc = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)

    if m == 0 or p == 0:
        return yc, dyc_dx

    front = x < p
    back = ~front

    yc[front] = (m / p**2) * (2 * p * x[front] - x[front]**2)
    dyc_dx[front] = (2 * m / p**2) * (p - x[front])

    yc[back] = (m / (1 - p)**2) * ((1 - 2 * p) + 2 * p * x[back] - x[back]**2)
    dyc_dx[back] = (2 * m / (1 - p)**2) * (p - x[back])

    return yc, dyc_dx


# --------------------------------------------------------
# NACA 5-digit camber line
# --------------------------------------------------------
# Standard tabulated (m, k1) pairs from Abbott & von Doenhoff, "Theory of
# Wing Sections". Valid for the camber-position digit P = 1..5 (p = P/20),
# normal (non-reflexed, Q=0) camber line. k1 is tabulated for a design lift
# coefficient of 0.3 (L=2, e.g. the 230XX family) and scales linearly with
# the actual design cl for other L digits.
_NORMAL_TABLE = {
    1: (0.0580, 361.4),
    2: (0.1260, 51.64),
    3: (0.2025, 15.957),
    4: (0.2900, 6.643),
    5: (0.3910, 3.230),
}

# Tabulated (m, k1, k2/k1) for the reflexed (Q=1) camber line. P=1 has no
# standard reflexed variant.
_REFLEX_TABLE = {
    2: (0.1300, 51.99, 0.000764),
    3: (0.2170, 15.793, 0.00677),
    4: (0.3180, 6.520, 0.0303),
    5: (0.4410, 3.191, 0.1355),
}


def camber_line_5digit(x, l_digit, p_digit, q_digit):
    """
    NACA 5-digit camber line and slope.

    Parameters
    ----------
    x : ndarray
    l_digit : int
        First digit. Design lift coefficient = 0.15 * l_digit.
    p_digit : int
        Second digit. Camber position p = p_digit / 20. Must be one of the
        standard tabulated positions (1-5 normal, 2-5 reflexed).
    q_digit : int
        Third digit. 0 = normal camber line, 1 = reflexed.

    Returns
    -------
    yc, dyc_dx : ndarray, ndarray
    """

    cl_design = 0.15 * l_digit
    table = _NORMAL_TABLE if q_digit == 0 else _REFLEX_TABLE

    if p_digit not in table:
        raise ValueError(
            f"NACA 5-digit camber position digit P={p_digit} is not a "
            f"standard tabulated value (expected one of {sorted(table)})."
        )

    if q_digit == 0:
        m, k1_ref = table[p_digit]
        k1 = k1_ref * (cl_design / 0.3)

        yc = np.where(
            x < m,
            (k1 / 6) * (x**3 - 3 * m * x**2 + m**2 * (3 - m) * x),
            (k1 * m**3 / 6) * (1 - x),
        )
        dyc_dx = np.where(
            x < m,
            (k1 / 6) * (3 * x**2 - 6 * m * x + m**2 * (3 - m)),
            -(k1 * m**3 / 6) * np.ones_like(x),
        )
        return yc, dyc_dx

    elif q_digit == 1:
        m, k1_ref, k2_k1 = table[p_digit]
        k1 = k1_ref * (cl_design / 0.3)

        yc = np.where(
            x < m,
            (k1 / 6) * ((x - m)**3 - k2_k1 * (1 - m)**3 * x - m**3 * x + m**3),
            (k1 / 6) * (k2_k1 * (x - m)**3 - k2_k1 * (1 - m)**3 * x - m**3 * x + m**3),
        )
        dyc_dx = np.where(
            x < m,
            (k1 / 6) * (3 * (x - m)**2 - k2_k1 * (1 - m)**3 - m**3),
            (k1 / 6) * (3 * k2_k1 * (x - m)**2 - k2_k1 * (1 - m)**3 - m**3),
        )
        return yc, dyc_dx

    else:
        raise ValueError("q_digit (reflex flag) must be 0 or 1.")
