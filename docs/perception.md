# FlexAI Perception

The perception layer turns raw mesh facts into useful design information.

It currently has three parts.

## Model interpreter

File:

```text
flexai/perception/model_interpreter.py
```

Purpose:

- classify model size
- estimate likely use
- estimate whether the model behaves like a shell
- list suitable operations
- provide warnings

Example interpretation:

```text
sphere -> toy_or_fidget -> twist
flat_panel -> panel_lid_or_cover -> living_hinge / honeycomb
long_strip -> strap_bracelet_or_handle -> zigzag / living_hinge
```

## Candidate regions

File:

```text
flexai/perception/candidate_regions.py
```

Purpose:

- identify areas that may accept cutters
- provide preferred operations per region
- assign confidence
- explain why the region is useful

Current examples:

```text
sphere -> centered radial body
flat panel -> broad flat face
long strip -> long flex strip
cylinder -> axial body
```

## Protected regions

File:

```text
flexai/perception/protected_regions.py
```

Purpose:

- flag risky areas or whole models before modification
- prevent blind geometry changes on unsafe models

Current checks:

- non-watertight mesh
- low-detail mesh
- complex or unknown shape
- extreme aspect ratio

## Next improvements

The next useful improvements are local feature detection:

- holes
- text relief
- logo relief
- screw bosses
- snap tabs
- thin edges

These features should become explicit protected regions so planners can avoid them.
