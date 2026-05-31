"""
SVG Optimizer — Flask Application Factory

Architecture
────────────
  routes/api.py          Blueprint: /api/*
  services/              OptimizationService, UploadService, ReportService, DownloadService
  utils/                 config, logging, validation

Run
───
  python -m svg_optimizer.web_app          # direct
  flask run --app svg_optimizer.web_app    # flask CLI
  PORT=8080 python -m svg_optimizer.web_app
"""
from __future__ import annotations

import os
import sys
from flask import Flask, send_from_directory, jsonify

if __name__ == "__main__" and __package__ is None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(script_dir))
    __package__ = "svg_optimizer"

from .routes import api_bp
from .utils import get_logger, config

logger = get_logger(__name__)


def create_app() -> Flask:
    """Application factory — use with gunicorn or flask run."""
    # Resolve frontend directory - try multiple locations for flexibility
    # When installed via pip, frontend is at /app/frontend
    # When running from source, frontend is relative to this file
    possible_frontend_dirs = [
        "/app/frontend",  # Docker/Render deployment path
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend")),  # Source path
    ]
    
    frontend_dir = None
    for candidate in possible_frontend_dirs:
        if os.path.exists(candidate):
            frontend_dir = candidate
            break
    
    if frontend_dir is None:
        frontend_dir = possible_frontend_dirs[0]  # Default to Docker path

    app = Flask(
        __name__,
        static_folder=frontend_dir,
        static_url_path="",
    )
    app.config["MAX_CONTENT_LENGTH"] = config.max_file_bytes
    app.config["SECRET_KEY"] = config.secret_key

    # ── Blueprints ────────────────────────────────────────────
    app.register_blueprint(api_bp)

    # ── Security headers ──────────────────────────────────────
    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: blob:; "
            "media-src 'self' blob:; "
            "connect-src 'self'; "
            "object-src 'none';"
        )
        return response

    # ── Frontend routes ───────────────────────────────────────
    @app.route("/")
    def index():
        return send_from_directory(frontend_dir, "index.html")

    # ── Health check endpoint for Render ──────────────────────
    @app.route("/healthz")
    def healthz():
        return jsonify({"status": "ok"}), 200

    # SPA fallthrough — anything not /api/* serves index.html
    @app.route("/<path:path>")
    def catch_all(path: str):
        if path.startswith("api/"):
            return jsonify({"error": "Not found."}), 404
        # Try serving a static asset first, fall back to index.html
        try:
            return send_from_directory(frontend_dir, path)
        except Exception:
            return send_from_directory(frontend_dir, "index.html")

    # ── Error handlers ────────────────────────────────────────
    @app.errorhandler(413)
    def too_large(_e):
        return jsonify({"error": f"File too large. Maximum is {config.max_file_bytes // (1024*1024)} MB."}), 413

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "Not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(_e):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def server_error(_e):
        return jsonify({"error": "Internal server error."}), 500

    logger.info("SVG Optimizer app created | frontend=%s", frontend_dir)
    return app


# Module-level app instance for `flask run --app svg_optimizer.web_app`
app = create_app()

if __name__ == "__main__":
    app.run(
        debug=config.debug,
        host=config.host,
        port=config.port,
    )


# ── Backwards-compat shim (used by test_web_app.py) ──────────────────────────
def allowed_file(filename: str) -> bool:
    """Check whether a filename has an allowed extension. Kept for test compatibility."""
    from .utils.validation import validate_filename
    return validate_filename(filename) is None
