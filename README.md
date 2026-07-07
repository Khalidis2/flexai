# FlexAI

FlexAI is a local, cross-platform STL/3MF assistant for analyzing 3D-print models and applying validated flex-cutting operations.

Milestone 1 foundation:

- Load STL, OBJ, and basic 3MF mesh files
- Analyze mesh dimensions, volume, surface area, watertightness, and shape
- Discover cutter plugins
- Recommend one of the V1 cutters
- Output a structured JSON report

Current Twist workflow:

- Generate a Twist cutter from planner parameters
- Convert non-Blender execution inputs, such as 3MF, to temporary STL internally
- Run Blender headless boolean subtraction
- Validate the output mesh
- Score the operation and report warnings
- Optionally export the cutter STL for inspection

V1 cutter plugins:

- Twist
- Living Hinge
- Zigzag / Offset Slots
- Honeycomb

## Requirements

- Python 3.11+
- macOS or Windows
- Blender installed locally for cutter execution

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

For a 3MF test file, copy it into the repo and run:

```bash
python app.py analyze path/to/model.3mf
```

## Apply Twist cutter

Use the main CLI workflow:

```bash
python app.py twist path/to/model.stl path/to/output.stl --keep-cutter
```

For 3MF inputs, FlexAI keeps the original input path in reports and creates a temporary STL only for Blender execution:

```bash
python app.py twist path/to/model.3mf path/to/output.stl --keep-cutter
```

If Blender is not on PATH, pass the executable explicitly:

macOS:

```bash
python app.py twist path/to/model.stl path/to/output.stl --blender /Applications/Blender.app/Contents/MacOS/Blender --keep-cutter
```

Windows PowerShell:

```powershell
python app.py twist path\to\model.stl path\to\output.stl --blender "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe" --keep-cutter
```

Use strict recommendation mode when you want the command to fail unless the planner recommends Twist:

```bash
python app.py twist path/to/model.stl path/to/output.stl --strict-recommendation
```

## Project status

The first end-to-end Twist workflow is being integrated into the primary CLI. Blender execution still exports STL output first; 3MF export can be added later if needed.