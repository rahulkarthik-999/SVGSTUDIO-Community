"""
SVG Optimizer - A Python package to optimize SVG files.

Provides:
- Core optimization passes (remove comments, metadata, unused IDs, etc.)
- Web API via Flask for browser-based optimization
"""

from .optimizer import optimize_svg, SVGOptimizer

__version__ = "1.0.0"
__all__ = ["optimize_svg", "SVGOptimizer"]


def get_version():
    """Return the version of the SVG Optimizer package."""
    return __version__
