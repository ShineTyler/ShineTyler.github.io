"""Static-site build package for Tyler's Corner.

All third-party code lives under src/vendor/ and is committed to the
repository, so building the site still requires nothing but Python 3.
"""
import sys
from pathlib import Path

VENDOR = Path(__file__).resolve().parents[2] / "vendor"
if VENDOR.is_dir() and str(VENDOR) not in sys.path:
    sys.path.insert(0, str(VENDOR))

__all__ = ["VENDOR"]
