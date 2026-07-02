"""
airfoil.py

Canonical Airfoil representation, shared by generated airfoils (NACA 4/5-
digit) and airfoils loaded from the database or a .dat file, so downstream
code (plotting, export, XFOIL hand-off) doesn't care where the geometry
came from.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from .utils import chord_length, export_dat


@dataclass
class Airfoil:
    name: str
    source: str  # e.g. "generated:naca4", "database:NASA", "database:UIUC"
    xu: np.ndarray
    yu: np.ndarray
    xl: np.ndarray
    yl: np.ndarray
    meta: dict = field(default_factory=dict)

    def export_dat(self, filename: str | Path) -> None:
        export_dat(filename, self.xu, self.yu, self.xl, self.yl, name=self.name)

    @property
    def chord(self) -> float:
        return chord_length(np.concatenate([self.xu, self.xl]))

    @property
    def thickness_max(self) -> float:
        """Max vertical gap between upper and lower surface, sampled at the upper surface's x stations."""
        yl_interp = np.interp(self.xu, self.xl, self.yl)
        return float(np.max(self.yu - yl_interp))
