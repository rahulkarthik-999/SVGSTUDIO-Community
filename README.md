# SVGO — SVG Optimizer

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

A modular, local-first SVG optimization engine. Strips unnecessary markup and reduces file sizes without altering visual output.

## Features

- **Single SVG optimization** via JSON body or file upload
- **Modular pass architecture** — enable/disable individual optimization steps
- **REST API** with health endpoint
- **Basic dashboard** — browser-based interface
- **Zero cloud dependency** — runs entirely on your machine

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

## Installation

```bash
git clone https://github.com/your-org/svgo.git
cd svgo
pip install -e .
```

### With Web UI

```bash
pip install -e ".[dev]"
```

## Usage

### Web App

```bash
python -m svg_optimizer.web_app
# Open http://localhost:5000
```

### API

**Optimize (JSON)**
```http
POST /api/optimize
Content-Type: application/json

{ "svg": "<svg>…</svg>", "passes": ["remove_comments"] }
```

**Optimize (file upload)**
```http
POST /api/upload
Content-Type: multipart/form-data

file=@icon.svg&passes=remove_comments,collapse_whitespace
```

**Health check**
```http
GET /api/health
```

**List available passes**
```http
GET /api/version
```

### Docker

```bash
docker build -t svgo .
docker run -p 5000:10000 svgo
```

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

## License

Apache 2.0 — see [LICENSE](LICENSE).
