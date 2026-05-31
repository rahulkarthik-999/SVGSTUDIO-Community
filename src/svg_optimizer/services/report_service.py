"""
ReportService — builds structured optimisation reports.
DownloadService — prepares download responses.
"""
from __future__ import annotations

from typing import Dict, Any, Optional


class ReportService:
    """Enriches raw optimisation stats with human-readable fields."""

    @staticmethod
    def build(stats: Dict[str, Any], duration_ms: float, passes_applied: int) -> Dict[str, Any]:
        orig = stats.get("original_size", 0)
        opt  = stats.get("optimized_size", 0)
        gzip_size = stats.get("gzip_size", 0)
        saved = orig - opt
        gzip_saved = orig - gzip_size

        def fmt_bytes(n: int) -> str:
            if n < 1024:
                return f"{n} B"
            if n < 1024 * 1024:
                return f"{n/1024:.1f} KB"
            return f"{n/(1024*1024):.2f} MB"

        return {
            **stats,
            "original_size_human":  fmt_bytes(orig),
            "optimized_size_human": fmt_bytes(opt),
            "bytes_saved":          saved,
            "bytes_saved_human":    fmt_bytes(saved),
            "gzip_size_human":      fmt_bytes(gzip_size),
            "gzip_bytes_saved":     gzip_saved,
            "gzip_bytes_saved_human": fmt_bytes(gzip_saved),
            "duration_ms":          round(duration_ms, 2),
            "passes_applied":       passes_applied,
        }


class DownloadService:
    """Prepares the optimised SVG content for download."""

    @staticmethod
    def prepare(
        optimized: str,
        original_filename: Optional[str] = None,
    ) -> Dict[str, str]:
        """Return content + suggested download filename."""
        base = (original_filename or "file").rsplit(".", 1)[0]
        download_name = f"{base}_optimized.svg"
        return {
            "content":       optimized,
            "download_name": download_name,
            "content_type":  "image/svg+xml",
        }
