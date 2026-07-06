# FlexAI

FlexAI is a local, cross-platform STL/3MF assistant for analyzing 3D-print models and recommending flex-cutting operations.

Milestone 1 focuses on the foundation:

- Load STL, OBJ, and basic 3MF mesh files
- Analyze mesh dimensions, volume, surface area, watertightness, and shape
- Discover cutter plugins
- Recommend one of the V1 cutters
- Output a structured JSON report

V1 cutter plugins:

- Twist
- Living Hinge
- Zigzag / Offset Slots
- Honeycomb

## Requirements

- Python 3.11+
- macOS or Windows

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run analysis

```bash
python app.py analyze path/to/model.stl
```

For your uploaded 3MF test file, copy it into the repo and run:

```bash
python app.py analyze LLK4_0.3mf
```

## Project status

This is the first foundation milestone. It does not modify geometry yet. The next milestone will add the first end-to-end Twist cutter execution using Blender headless.
