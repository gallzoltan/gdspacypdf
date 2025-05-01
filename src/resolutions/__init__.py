"""
Kormányhatározatok kinyerésére és elemzésére szolgáló modul.
"""

from .extractor import extract_resolutions
from .analyzer import analyze_resolutions

__all__ = ['extract_resolutions', 'analyze_resolutions']