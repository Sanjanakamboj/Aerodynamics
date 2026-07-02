"""
import_dat.py

Load an airfoil coordinate file (.dat) into the canonical Airfoil
representation.

Supports the two coordinate-file conventions in general circulation:

- Selig format: a single closed loop, starting at the trailing edge,
  running over the upper surface to the leading edge, then back along the
  lower surface to the trailing edge. No point-count header.
- Lednicer format: a header line giving (n_upper, n_lower) point counts,
  then the upper surface listed leading-edge to trailing-edge, a blank
  line, then the lower surface leading-edge to trailing-edge.
"""

from pathlib import Path

import numpy as np

from .airfoil import Airfoil


def _read_numeric_lines(lines):
    pts = []
    for line in lines:
        parts = line.split()
        if len(parts) != 2:
            continue
        try:
            pts.append((float(parts[0]), float(parts[1])))
        except ValueError:
            continue
    return pts


def _looks_like_lednicer_header(line):
    parts = line.split()
    if len(parts) != 2:
        return False
    try:
        a, b = float(parts[0]), float(parts[1])
    except ValueError:
        return False
    # Point counts are whole numbers well outside airfoil coordinate range
    # (roughly [-1, 1]); airfoil x/y pairs never look like this.
    return a > 1.5 and b > 1.5 and a == int(a) and b == int(b)


def load_dat(filepath, name=None, source="database"):
    """
    Load a .dat airfoil coordinate file into an Airfoil.

    Parameters
    ----------
    filepath : str or Path
    name : str, optional
        Overrides the airfoil name (defaults to the file's title line, or
        its filename stem).
    source : str
        Tag describing where this airfoil came from, e.g. "database:NASA".

    Returns
    -------
    Airfoil
    """

    filepath = Path(filepath)
    lines = [l for l in filepath.read_text().splitlines() if l.strip()]

    if not lines:
        raise ValueError(f"{filepath} is empty.")

    header = None
    body = lines
    if len(lines[0].split()) != 2:
        header = lines[0].strip()
        body = lines[1:]

    if body and _looks_like_lednicer_header(body[0]):
        n_upper, n_lower = (int(float(v)) for v in body[0].split())
        pts = _read_numeric_lines(body[1:])
        upper = pts[:n_upper]
        lower = pts[n_upper:n_upper + n_lower]
    else:
        pts = _read_numeric_lines(body)
        if not pts:
            raise ValueError(f"Could not find any coordinate pairs in {filepath}.")
        le_idx = int(np.argmin([p[0] for p in pts]))
        upper = pts[:le_idx + 1][::-1]  # reverse so it runs LE -> TE
        lower = pts[le_idx:]

    xu, yu = (np.array(v) for v in zip(*upper))
    xl, yl = (np.array(v) for v in zip(*lower))

    return Airfoil(
        name=name or header or filepath.stem,
        source=source,
        xu=xu,
        yu=yu,
        xl=xl,
        yl=yl,
        meta={"filepath": str(filepath)},
    )
