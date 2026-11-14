"""Tennis Abstract career match data and results with age-difference plots."""

from .data import get_career_data
from .plot import plot_career

__version__ = "0.1.0"

__all__ = ["get_career_data", "plot_career"]