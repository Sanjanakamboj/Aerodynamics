"""
polar_analysis.py

Performance metrics from a single XFoil polar sweep: CLmax, CDmin, max
L/D, best glide angle, stall angle, zero-lift angle, lift-curve slope,
and moment coefficient.
"""

import numpy as np


def cl_at_alpha(df, alpha):
    """Interpolated CL at a given angle of attack."""
    return float(np.interp(alpha, df["alpha"], df["CL"]))


def cd_at_alpha(df, alpha):
    """Interpolated CD at a given angle of attack."""
    return float(np.interp(alpha, df["alpha"], df["CD"]))


def cm_at_alpha(df, alpha):
    """Interpolated CM at a given angle of attack."""
    return float(np.interp(alpha, df["alpha"], df["CM"]))


def lift_curve_slope(df, n_points=2):
    """
    Lift-curve slope (dCL/dalpha), in per-radian, estimated by a linear
    fit over the first `n_points`+1 rows of the sweep (the pre-stall
    linear region).
    """
    alpha = np.radians(df["alpha"].iloc[: n_points + 1].to_numpy())
    cl = df["CL"].iloc[: n_points + 1].to_numpy()
    slope, _ = np.polyfit(alpha, cl, 1)
    return float(slope)


def max_lift_to_drag(df):
    """Returns (alpha, CL, CD, L_over_D) at the best lift-to-drag ratio."""
    l_over_d = df["CL"] / df["CD"]
    i = int(l_over_d.idxmax())
    row = df.loc[i]
    return float(row["alpha"]), float(row["CL"]), float(row["CD"]), float(l_over_d.loc[i])


def best_glide_angle(df):
    """
    Best (shallowest) unpowered glide angle, in degrees, at the max L/D
    condition: glide_angle = arctan(1 / (L/D)_max).
    """
    _, _, _, l_over_d_max = max_lift_to_drag(df)
    return float(np.degrees(np.arctan(1.0 / l_over_d_max)))


def stall_angle(df):
    """Returns (alpha, CL) at maximum CL (simple peak-CL heuristic)."""
    i = int(df["CL"].idxmax())
    return float(df.loc[i, "alpha"]), float(df.loc[i, "CL"])


def min_drag(df):
    """Returns (alpha, CD) at minimum drag."""
    i = int(df["CD"].idxmin())
    return float(df.loc[i, "alpha"]), float(df.loc[i, "CD"])


def zero_lift_angle(df):
    """Angle of attack (deg) where CL = 0, via interpolation on the CL-alpha curve."""
    return float(np.interp(0.0, df["CL"], df["alpha"]))


def moment_coefficient(df):
    """
    Pitching moment coefficient at zero lift (CM0) -- the standard
    single-value characterization of an airfoil's moment behavior, since
    CM is roughly constant with alpha away from stall.
    """
    return cm_at_alpha(df, zero_lift_angle(df))


def summarize_polar(df):
    """Compute the full performance-metrics report for a polar sweep DataFrame."""
    alpha_stall, cl_max = stall_angle(df)
    alpha_cd_min, cd_min = min_drag(df)
    alpha_ld, _, _, l_over_d_max = max_lift_to_drag(df)

    return {
        "cl_max": cl_max,
        "cd_min": cd_min,
        "alpha_at_cd_min": alpha_cd_min,
        "max_L_over_D": l_over_d_max,
        "alpha_at_max_L_over_D": alpha_ld,
        "best_glide_angle": best_glide_angle(df),
        "stall_angle": alpha_stall,
        "zero_lift_angle": zero_lift_angle(df),
        "lift_curve_slope": lift_curve_slope(df),
        "moment_coefficient": moment_coefficient(df),
    }


def save_polar_dat(df, filepath):
    """Save a polar sweep DataFrame as a simple space-delimited .dat file."""
    df.to_csv(filepath, sep=" ", index=False, float_format="%.6f")
