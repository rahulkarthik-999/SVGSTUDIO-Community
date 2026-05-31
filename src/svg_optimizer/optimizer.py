"""
SVG Optimizer - Main Module

Provides the primary interface for SVG optimization.
"""

from typing import List, Dict, Any, Optional, Tuple
from .core.engine import (
    OptimizationContext,
    PassManager,
    PassRegistry,
)


class SVGOptimizer:
    """
    SVG Optimizer that applies configurable optimization passes.
    
    Uses a pass-based architecture where each optimization is a 
    registered function that transforms the SVG content.
    """
    
    def __init__(self, passes: Optional[List[str]] = None):
        """
        Initialize the optimizer.
        
        Args:
            passes: List of pass names to apply. If None, uses defaults.
        """
        if passes is None:
            self.passes = PassRegistry.get_default_passes()
        else:
            self.passes = passes
        
        self.stats: Dict[str, Any] = {
            "original_size": 0,
            "optimized_size": 0,
            "removed_elements": 0,
            "removed_attributes": 0,
            "removed_comments": 0,
            "removed_ids": 0,
            "removed_namespaces": 0,
        }
    
    @staticmethod
    def get_all_passes() -> List[str]:
        """Return list of all available optimization passes."""
        return PassRegistry.get_all_passes()
    
    @staticmethod
    def get_pass_metadata(pass_name: str) -> Dict[str, Any]:
        """Get metadata for a specific pass."""
        return PassRegistry.get_metadata(pass_name)
    
    def optimize(self, svg_content: str) -> str:
        """
        Apply all configured optimization passes to SVG content.
        
        Args:
            svg_content: The SVG content as a string.
            
        Returns:
            The optimized SVG content.
        """
        # Create context
        context = OptimizationContext(original_content=svg_content)
        
        # Execute passes
        manager = PassManager(passes=self.passes)
        context = manager.execute(context)
        
        # Update stats
        self.stats = context.stats
        
        return context.current_content
    
    def get_stats(self) -> Dict[str, Any]:
        """Return optimization statistics."""
        original = self.stats.get("original_size", 0)
        optimized = self.stats.get("optimized_size", 0)
        reduction = ((original - optimized) / original * 100) if original > 0 else 0
        
        return {
            **self.stats,
            "reduction_percent": round(reduction, 2),
        }


def optimize_svg(
    svg_content: str,
    passes: Optional[List[str]] = None,
    return_stats: bool = False
) -> str | Tuple[str, Dict[str, Any]]:
    """
    Optimize SVG content with specified passes.
    
    Args:
        svg_content: The SVG content as a string.
        passes: List of optimization passes to apply. If None, uses defaults.
        return_stats: If True, returns a tuple of (optimized_content, stats).
    
    Returns:
        The optimized SVG content, or tuple of (content, stats) if return_stats is True.
    """
    optimizer = SVGOptimizer(passes=passes)
    result = optimizer.optimize(svg_content)
    
    if return_stats:
        return result, optimizer.get_stats()
    return result


def get_version() -> str:
    """Return the version of the optimizer module."""
    return "1.0.0"
