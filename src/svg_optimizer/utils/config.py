"""
Centralised environment-based configuration.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List


@dataclass
class AppConfig:
    # Server
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "10000")))
    debug: bool = field(default_factory=lambda: os.getenv("FLASK_DEBUG", "0") == "1")
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", "dev-insecure-key"))

    # Upload limits
    max_file_bytes: int = field(default_factory=lambda: int(os.getenv("MAX_FILE_MB", "16")) * 1024 * 1024)
    allowed_extensions: frozenset = field(default_factory=lambda: frozenset({"svg"}))

    # Optimisation
    default_passes: List[str] = field(default_factory=lambda: [
        "remove_xml_declaration",
        "remove_comments",
        "remove_editor_namespaces",
        "remove_metadata",
        "remove_hidden_elements",
        "remove_empty_attributes",
        "trim_trailing_zeros",
        "round_decimals",
        "collapse_whitespace",
        "collapse_groups",
        "remove_unused_ids",
        "merge_paths",
        "collapse_transforms",
        "cleanup_styles",
        "remove_empty_groups",
        "convert_colors",
        "minify_css",
        "optimize_path_data",
        "remove_scripts",
        "remove_event_handlers",
        "sanitize_urls",
    ])

    # CORS
    cors_origins: str = field(default_factory=lambda: os.getenv("CORS_ORIGINS", "*"))


# Module-level singleton
config = AppConfig()
