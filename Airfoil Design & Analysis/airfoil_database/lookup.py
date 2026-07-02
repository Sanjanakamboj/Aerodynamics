"""
lookup.py

Search the local Airfoil Database for a coordinate file matching a code or
name, before falling back to generating the airfoil analytically.
"""

import re
from pathlib import Path

DATABASE_ROOT = Path(__file__).parent
SOURCES = ["NACA", "UIUC", "NASA", "Selig", "User Library"]


def _normalize(name):
    name = re.sub(r"[^a-z0-9]", "", name.lower())
    if name.startswith("naca"):
        name = name[len("naca"):]
    return name


def find_in_database(code):
    """
    Search each database source, in priority order, for a .dat file whose
    name matches `code`. Returns the matching Path, or None.
    """

    target = _normalize(code)

    for source in SOURCES:
        folder = DATABASE_ROOT / source
        if not folder.is_dir():
            continue
        for f in folder.glob("*.dat"):
            if _normalize(f.stem) == target:
                return f

    return None


def list_database():
    """Returns {source_name: [dat files]} for every populated database source."""

    return {
        source: sorted((DATABASE_ROOT / source).glob("*.dat"))
        for source in SOURCES
        if (DATABASE_ROOT / source).is_dir()
    }


def save_to_library(airfoil, name=None):
    """
    Save a generated/imported airfoil into the User Library so
    find_in_database() can find it next time instead of regenerating it.
    Filed under its display name (e.g. "NACA 2412.dat") -- lookups still
    match regardless of spacing/prefix, since _normalize() strips both.

    Returns the path it was written to.
    """

    folder = DATABASE_ROOT / "User Library"
    folder.mkdir(parents=True, exist_ok=True)

    filepath = folder / f"{(name or airfoil.name).strip()}.dat"
    airfoil.export_dat(filepath)
    return filepath
