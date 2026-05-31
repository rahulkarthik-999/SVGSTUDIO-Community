"""
API Blueprint — /api/* routes.
"""
from __future__ import annotations

import time
from flask import Blueprint, request, jsonify, Response

from ..services import (
    OptimizationService,
    UploadService,
    ReportService,
    DownloadService,
)
from ..utils import get_logger

logger = get_logger(__name__)
api_bp = Blueprint("api", __name__, url_prefix="/api")

_start_time = time.time()


# ── /api/health ──────────────────────────────────────────────────────────────

@api_bp.get("/health")
def health() -> Response:
    """Health check for container probes and uptime monitoring."""
    return jsonify({
        "status": "ok",
        "uptime_seconds": round(time.time() - _start_time, 1),
    })


# ── /api/version ─────────────────────────────────────────────────────────────

@api_bp.get("/version")
def version() -> Response:
    """Return version and available passes."""
    return jsonify(OptimizationService.list_passes())


# ── /api/optimize (JSON body) ────────────────────────────────────────────────

@api_bp.post("/optimize")
def optimize() -> Response:
    """
    Optimize SVG supplied as JSON.

    Body::

        { "svg": "<svg>…</svg>", "passes": ["remove_comments", …] }

    Response::

        { "success": true, "optimized": "…", "stats": {…} }
    """
    data = request.get_json(silent=True) or {}
    upload = UploadService.from_json(data)
    if not upload["ok"]:
        return jsonify({"error": upload["error"]}), 400

    passes = data.get("passes") or None
    result = OptimizationService.run(upload["content"], passes=passes)

    if not result["success"]:
        return jsonify({"error": result["error"]}), 500

    report = ReportService.build(
        result["stats"],
        result["duration_ms"],
        len(passes or []),
    )
    download = DownloadService.prepare(result["optimized"])
    return jsonify({
        "success": True,
        "optimized": result["optimized"],
        "stats": report,
        "download_name": download["download_name"],
    })


# ── /api/upload (multipart) ───────────────────────────────────────────────────

@api_bp.post("/upload")
def upload() -> Response:
    """
    Optimize SVG supplied as a multipart file upload.

    Form fields:
        file   – SVG file (required)
        passes – comma-separated pass names (optional)
    """
    if "file" not in request.files:
        return jsonify({"error": "No file field in request."}), 400

    upload = UploadService.from_file(request.files["file"])
    if not upload["ok"]:
        return jsonify({"error": upload["error"]}), 400

    passes_raw = request.form.get("passes", "")
    passes = [p.strip() for p in passes_raw.split(",") if p.strip()] or None

    result = OptimizationService.run(upload["content"], passes=passes)
    if not result["success"]:
        return jsonify({"error": result["error"]}), 500

    report = ReportService.build(
        result["stats"],
        result["duration_ms"],
        len(passes or []),
    )
    return jsonify({
        "success":  True,
        "filename": upload["filename"],
        "optimized": result["optimized"],
        "stats": report,
    })
