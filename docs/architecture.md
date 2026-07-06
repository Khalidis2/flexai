# FlexAI Architecture

FlexAI is designed as a local geometry-modification assistant for 3D-print models.

The core rule is simple:

> Planning, geometry generation, and execution must stay separate.

## Layers

```text
Importer
  -> Analyzer / Perception
  -> Planner
  -> Cutter Generator
  -> Executor
  -> Validator
```

## Importer

Responsible only for loading mesh files into a normalized internal mesh asset.

Current support:

- STL
- OBJ
- basic 3MF through trimesh

The importer does not make recommendations and does not modify geometry.

## Analyzer / Perception

Responsible for measurable facts:

- bounding box
- volume
- surface area
- watertightness
- face count
- vertex count
- primary shape
- symmetry
- candidate regions
- protected regions, later

The analyzer does not generate cutters and does not run Blender.

## Planner

Responsible for selecting the best cutter plugin based on the model report.

The planner asks each plugin for a score and chooses the highest-scoring plugin.

The planner does not edit meshes.

## Cutter Generator

Responsible for generating cutter mesh geometry from explicit parameters.

Example:

```python
TwistCutterParameters(
    diameter_mm=44.0,
    height_mm=44.0,
    core_hole_mm=9.0,
)
```

The generator does not know why the cutter is being used and does not call Blender.

## Executor

Responsible for external geometry operations.

Current executor:

- Blender headless Boolean Difference

The executor does not choose cutters and does not infer model meaning.

## Validator

Future responsibility:

- output exists
- output is watertight
- output has no obvious floating shells
- minimum thickness checks
- printability warnings

## Design principle

Every new cutter should be added as a plugin and generator, not as planner-specific hardcoded logic.

Good:

```text
Plugin scores model -> Planner chooses plugin -> Generator creates cutter -> Executor applies boolean
```

Bad:

```text
Planner directly creates Blender objects
```
