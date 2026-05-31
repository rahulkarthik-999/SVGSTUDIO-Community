# SVGSTUDIO Community

**Open-source SVG optimization platform for developers, designers, and teams.**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker)](Dockerfile)
[![REST API](https://img.shields.io/badge/REST-API-green.svg)](https://github.com/rahulkarthik-999/SVGSTUDIO-Community)
[![Community Edition](https://img.shields.io/badge/Edition-Community-orange.svg)](https://github.com/rahulkarthik-999/SVGSTUDIO-Community)

> **SVG Optimizer | SVG Compression | Web Performance | Developer Tools | Flask | Python | REST API | Open Source**

---

## Live Demo

Try SVGSTUDIO instantly:

**🔗 [https://svg-studio.onrender.com/](https://svg-studio.onrender.com/)**

No installation required.

---

## Why SVGSTUDIO?

- **Reduce SVG size** — Strip unnecessary markup and comments for lean files
- **Improve website performance** — Faster page loads with optimized assets
- **Automate optimization workflows** — REST API for CI/CD pipelines
- **Self-hosted and privacy-friendly** — No cloud dependency, runs entirely local

---

## Screenshots

### Optimizer

![Optimizer](docs/images/optimizer.png)

### Batch Processing (Pro)

![Batch Processing](docs/images/batch-processing.png)

### Security Scanner (Enterprise)

![Security Scanner](docs/images/security-scanner.png)

---

## Editions

### Community (Free)

| Feature | Description |
|---------|-------------|
| ✓ Single SVG Optimization | Optimize individual SVG files |
| ✓ REST API | Programmatic access via HTTP |
| ✓ Web UI | Browser-based interface |
| ✓ Docker Deployment | Self-hosted container |

### Pro

| Feature | Description |
|---------|-------------|
| ✓ Batch Processing | Process multiple files simultaneously |
| ✓ Watch Mode | Auto-optimize files on change |
| ✓ Advanced Analytics | Detailed optimization reports |
| ✓ Conversion Studio | Batch format conversion |

**Contact:** [rkytube999@gmail.com](mailto:rkytube999@gmail.com)

### Enterprise

| Feature | Description |
|---------|-------------|
| ✓ Security Scanner | Detect malicious SVG patterns |
| ✓ Compliance Reports | Audit and compliance documentation |
| ✓ Enterprise Licensing | Flexible licensing terms |
| ✓ Air-Gapped Validation | Offline security verification |
| ✓ Custom Passes | Define organization-specific rules |

**Contact:** [rkytube999@gmail.com](mailto:rkytube999@gmail.com)

---

## Features

- **Modular optimization engine** — Enable/disable individual optimization passes
- **Pass architecture** — Configurable optimization steps for fine-tuned results
- **REST API** — Full HTTP API for integration with any workflow
- **Local-first deployment** — Zero cloud dependency, runs on your infrastructure
- **Docker support** — One-command containerized deployment
- **Optimization statistics** — Detailed before/after size reports

---

## Included Optimization Passes

| Pass | Description | Default |
|------|-------------|---------|
| `remove_xml_declaration` | Remove `<?xml?>` declaration | ✅ |
| `remove_comments` | Strip HTML/XML comments | ✅ |
| `remove_metadata` | Remove `<metadata>`, `<desc>`, `<title>` | ✅ |
| `remove_editor_attributes` | Strip Inkscape/Figma/Sketch attributes | ✅ |
| `remove_empty_attributes` | Remove attributes with empty values | ✅ |
| `collapse_whitespace` | Collapse redundant whitespace | ✅ |
| `remove_unused_ids` | Remove IDs not referenced elsewhere | ✅ |
| `remove_default_attributes` | Remove attributes at their default value | ✅ |
| `remove_namespaces` | Remove unused XML namespace declarations | ✅ |

---

## Quick Start

### Clone the Repository

```bash
git clone https://github.com/rahulkarthik-999/SVGSTUDIO-Community.git
cd SVGSTUDIO-Community
```

### Install

```bash
pip install -e .
```

### Run Web App

```bash
python -m svg_optimizer.web_app
# Open http://localhost:5000
```

### Run with Docker

```bash
docker build -t svgstudio .
docker run -p 5000:10000 svgstudio
```

---

## API Reference

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "SVGSTUDIO",
  "version": "1.0.0"
}
```

### Optimize SVG (JSON)

```http
POST /api/optimize
Content-Type: application/json

{
  "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\"><!-- comment --><rect/></svg>",
  "passes": ["remove_comments", "remove_metadata"]
}
```

**Response:**
```json
{
  "success": true,
  "original_size": 124,
  "optimized_size": 67,
  "reduction": "45.97%",
  "svg": "<svg xmlns=\"http://www.w3.org/2000/svg\"><rect/></svg>"
}
```

### Upload SVG File

```http
POST /api/upload
Content-Type: multipart/form-data

file=@icon.svg&passes=remove_comments,collapse_whitespace
```

**Response:**
```json
{
  "success": true,
  "filename": "icon.svg",
  "original_size": 512,
  "optimized_size": 298,
  "reduction": "41.80%"
}
```

---

## Architecture

```
src/svg_optimizer/
├── core/
│   └── engine.py          # PassRegistry, PassManager, OptimizationContext
├── passes/
│   └── basic.py           # All built-in optimization passes
├── routes/
│   └── api.py             # Flask Blueprint: /api/*
├── services/
│   ├── optimization_service.py
│   └── upload_service.py
└── web_app.py             # Flask application factory
```

---

## Roadmap

- 🔄 **Conversion Studio** — Batch format conversion and optimization
- 🔄 **Team Workspaces** — Collaborative SVG management
- 🔄 **Security Scanner** — Detect malicious SVG patterns (Enterprise)
- 🔄 **Enterprise Reports** — Compliance and audit documentation
- 🔄 **Plugin System** — Custom optimization passes

---

## Support

**Community support:**
Open an issue on [GitHub Issues](https://github.com/rahulkarthik-999/SVGSTUDIO-Community/issues)

**Pro / Enterprise unlocks:**
[rkytube999@gmail.com](mailto:rkytube999@gmail.com)

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
