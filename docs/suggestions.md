# FlexAI Suggestions

This document captures practical suggestions for turning FlexAI from a working prototype into a useful local 3D-printing tool.

## 1. Keep V1 narrow

V1 should not try to support every cutter or every model type.

Recommended V1 goal:

```text
Upload STL/OBJ
Analyze model
Recommend cutter
Apply Twist cutter
Validate output
Export STL
```

Reason:

A narrow end-to-end workflow is more valuable than many incomplete cutters.

## 2. Prioritize Twist quality before adding more cutters

The current Twist generator is an approximation. The next major engineering work should improve it until it creates a cutter closer to the manual workflow shown in reference videos.

Recommended improvements:

- cleaner blade geometry
- controllable twist pitch
- stronger core clearance
- smooth cutter body
- better cutter intersection with spherical and cylindrical models
- preview/export of cutter mesh for debugging

## 3. Add a real preview before full desktop UI

Before building a polished desktop app, add a simple preview/export workflow.

Suggested path:

```text
CLI generates:
  model_report.json
  cutter.stl
  output.stl
  validation_report.json
```

Then the user can inspect files in Blender, Bambu Studio, or PrusaSlicer.

This is faster than building a GUI too early.

## 4. Use a benchmark model folder

Create a local non-committed folder:

```text
benchmarks/
  spheres/
  panels/
  strips/
  complex/
  failed/
```

Do not commit downloaded STL files unless licensing allows it.

Use the benchmark set to check every new cutter change.

## 5. Add protected-region detection gradually

Do not try to detect everything at once.

Recommended order:

1. Holes
2. Thin walls
3. Text/logo relief
4. Screw bosses
5. Snap tabs
6. Threads

Each protected feature should produce a region with:

- feature type
- center
- size
- confidence
- reason

## 6. Add output scoring

After every operation, FlexAI should score the result.

Suggested score components:

- output loads successfully
- output is watertight
- reasonable material removed
- no tiny floating shells
- volume change is within expected range
- cutter changed the intended region

The operation should return:

```json
{
  "passed": true,
  "score": 87,
  "warnings": []
}
```

## 7. Keep Blender as an executor, not the brain

Do not put planning logic inside Blender scripts.

Correct separation:

```text
FlexAI Python chooses operation and parameters
Cutter generator creates cutter mesh
Blender performs boolean difference only
Validation checks the result
```

This keeps the project maintainable.

## 8. Add 3MF execution later

3MF analysis currently works through trimesh, but Blender boolean execution is wired for STL/OBJ.

Recommended path:

1. Keep STL as the main execution format for now.
2. Convert 3MF input to temporary STL internally.
3. Run boolean on STL.
4. Export STL first.
5. Add 3MF export later only if needed.

## 9. Avoid GUI too early

A desktop GUI is useful, but only after the backend is reliable.

Suggested order:

1. CLI
2. Generated reports
3. Cutter preview STL
4. Validated output STL
5. Simple desktop wrapper
6. Full interactive region selection

## 10. Add a plugin manifest later

The current plugin registry is simple and fine for now.

Later, each cutter should have:

```text
plugin.json
plugin.py
generator.py
validator.py
```

Example manifest fields:

```json
{
  "id": "twist",
  "name": "Twist",
  "version": "0.1.0",
  "supported_shapes": ["sphere", "cylinder_or_rod"],
  "minimum_nozzle_mm": 0.4,
  "minimum_wall_mm": 0.8
}
```

## 11. Use printer constraints early

FlexAI should know the practical limits of common FDM printing.

Recommended default profile:

```text
Nozzle: 0.4 mm
Minimum slot width: 0.8 mm
Minimum wall: 0.8 mm
Minimum embossed detail: 0.6 mm
Recommended layer height: 0.16-0.20 mm
Material: PLA/PETG
```

These values should influence cutter spacing and validation.

## 12. Suggested near-term roadmap

### Milestone A: Stabilize current backend

- run CI cleanly
- fix test failures
- expose smoke pipeline in docs
- generate JSON report files

### Milestone B: Improve Twist cutter

- improve twist geometry
- add cutter debug export
- validate generated cutter mesh
- test on sphere and cylinder fixtures

### Milestone C: Add operation scoring

- combine output validation and input/output comparison
- return a single operation score
- fail safely when volume removed is unreasonable

### Milestone D: Add simple preview workflow

- export cutter STL
- export modified STL
- export reports
- optionally generate screenshots through Blender later

### Milestone E: Add second cutter

Recommended second cutter: Living Hinge.

Reason:

It is simpler than Honeycomb and easier to validate.

## 13. Product direction

The long-term product should feel like:

```text
Drop model
Choose intent: Make flexible
Review recommendation
Apply
Inspect validation
Export
```

Not like CAD software.

The user should not need to understand Blender, booleans, or mesh repair.
