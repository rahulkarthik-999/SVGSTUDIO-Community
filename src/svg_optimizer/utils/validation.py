"""
Input validation helpers.
"""
from __future__ import annotations

import re
from typing import Optional

from .config import config


_SVG_OPEN = re.compile(r"<svg[\s>]", re.IGNORECASE)


def validate_svg_content(content: str) -> Optional[str]:
    """
    Return an error string if content is not valid SVG, else None.
    """
    if not content or not content.strip():
        return "SVG content is empty."
    if len(content.encode("utf-8")) > config.max_file_bytes:
        return f"SVG content exceeds {config.max_file_bytes // (1024*1024)} MB limit."
    if not _SVG_OPEN.search(content):
        return "Content does not appear to be an SVG file."
    return None


def validate_filename(filename: str) -> Optional[str]:
    """
    Return an error string if filename is not acceptable, else None.
    """
    if not filename:
        return "Filename is empty."
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in config.allowed_extensions:
        return f"File type '.{ext}' is not allowed. Upload an SVG file."
    return None
