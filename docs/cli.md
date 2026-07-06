# FlexAI CLI

The current recommended entry point is:

```bash
python -m flexai
```

## Analyze a model

```bash
python -m flexai analyze model.stl
```

This prints:

- file type
- dimensions
- detected shape
- watertight status
- volume
- surface area
- recommended cutter
- confidence score
- JSON report

Supported analysis inputs:

- `.stl`
- `.obj`
- `.3mf`

## Apply Twist cutter

```bash
python -m flexai apply-twist input.stl output.stl
```

This command:

1. Loads the input model.
2. Analyzes the geometry.
3. Generates Twist cutter parameters.
4. Generates a temporary cutter STL.
5. Runs Blender in headless mode.
6. Exports the modified STL.

Supported boolean inputs for the current Blender executor:

- `.stl`
- `.obj`

3MF analysis is supported, but 3MF boolean execution is not wired into Blender yet.

## Keep generated cutter file

```bash
python -m flexai apply-twist input.stl output.stl --keep-cutter
```

This writes the generated cutter beside the output file for debugging.

## Explicit Blender path

macOS example:

```bash
python -m flexai apply-twist input.stl output.stl --blender "/Applications/Blender.app/Contents/MacOS/Blender"
```

Windows example:

```powershell
python -m flexai apply-twist input.stl output.stl --blender "C:\Program Files\Blender Foundation\Blender 4.3\blender.exe"
```

## Current limitation

The Twist cutter generator is still an early procedural approximation. It exists to validate the pipeline before the cutter geometry is refined to match production flex-cut behavior.
