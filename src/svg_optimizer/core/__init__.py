"""SVG Optimizer Core Package."""

from .engine import (
    OptimizationContext,
    PassResult,
    PassRegistry,
    PassManager,
    SVGSerializer,
)

__all__ = [
    'OptimizationContext',
    'PassResult',
    'PassRegistry',
    'PassManager',
    'SVGSerializer',
]
