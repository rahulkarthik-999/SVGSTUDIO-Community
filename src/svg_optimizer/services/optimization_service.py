"""
OptimizationService — wraps the core SVGOptimizer with
timing, logging, error handling, and report building.
"""
from __future__ import annotations

import gzip
import time
from typing import Dict, Any, List, Optional, Tuple

from ..optimizer import optimize_svg, SVGOptimizer, get_version
from ..utils import get_logger, config

logger = get_logger(__name__)


class OptimizationService:
    """
    High-level service for running SVG optimisation.

    Usage::

        result = OptimizationService.run(svg_content, passes=["remove_comments"])
        # result["success"] / result["optimized"] / result["stats"]
    """

    @staticmethod
    def run(
        svg_content: str,
        passes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Optimise *svg_content* and return a result dict.

        Returns:
            {
              "success": bool,
              "optimized": str,          # only on success
              "stats": { ... },          # only on success
              "error": str,              # only on failure
              "duration_ms": float,
            }
        """
        effective_passes = passes if passes is not None else config.default_passes
        t0 = time.perf_counter()

        try:
            optimized, stats = optimize_svg(
                svg_content,
                passes=effective_passes,
                return_stats=True,
            )
            gzip_size = len(gzip.compress(optimized.encode("utf-8")))
            original_size = stats.get("original_size", 0)
            stats["gzip_size"] = gzip_size
            stats["gzip_reduction_percent"] = round(
                ((original_size - gzip_size) / original_size * 100) if original_size else 0,
                2,
            )
            duration_ms = (time.perf_counter() - t0) * 1000

            logger.info(
                "Optimised %.1f KB → %.1f KB (%.0f%% reduction) in %.0f ms | passes=%d",
                stats.get("original_size", 0) / 1024,
                stats.get("optimized_size", 0) / 1024,
                stats.get("reduction_percent", 0),
                duration_ms,
                len(effective_passes),
            )

            return {
                "success": True,
                "optimized": optimized,
                "stats": stats,
                "duration_ms": round(duration_ms, 2),
            }

        except Exception as exc:
            duration_ms = (time.perf_counter() - t0) * 1000
            logger.exception("Optimisation failed after %.0f ms: %s", duration_ms, exc)
            return {
                "success": False,
                "error": str(exc),
                "duration_ms": round(duration_ms, 2),
            }

    @staticmethod
    def run_batch(
        inputs: List[Dict[str, Any]],
        default_passes: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """Run optimization across a batch of SVG inputs."""
        results = []
        for item in inputs:
            content = item.get('content', '')
            passes = item.get('passes', default_passes)
            filename = item.get('filename')
            result = OptimizationService.run(content, passes=passes)
            record = {
                'filename': filename,
                'success': result['success'],
                'optimized': result.get('optimized'),
                'stats': result.get('stats'),
                'error': result.get('error'),
                'duration_ms': result.get('duration_ms'),
                'passes': passes if passes is not None else [],
            }
            results.append(record)
        return results

    @staticmethod
    def list_passes() -> Dict[str, Any]:
        """Return all available passes + defaults."""
        all_passes = SVGOptimizer.get_all_passes()
        return {
            "version": get_version(),
            "passes": all_passes,
            "default_passes": [p for p in config.default_passes if p in all_passes],
        }
