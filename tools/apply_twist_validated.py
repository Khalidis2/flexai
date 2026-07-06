# tools/apply_twist_validated.py

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.table import Table

from flexai.analyzer.mesh_analyzer import analyze_model
from flexai.importer.mesh_loader import load_mesh
from flexai.models import CutterRecommendation
from flexai.operations.validated_twist_operation import apply_validated_twist_operation
from flexai.planner.recommender import recommend_cutter
from flexai.plugins.registry import load_plugins

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apply Twist cutter and validate exported mesh.")
    parser.add_argument("input", help="Input STL or OBJ path")
    parser.add_argument("output", help="Output STL path")
    parser.add_argument("--blender", default=None, help="Optional explicit Blender executable path")
    parser.add_argument("--keep-cutter", action="store_true", help="Keep generated cutter STL beside the output file")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    asset = load_mesh(input_path)
    report = analyze_model(asset, input_path)
    recommendation = recommend_cutter(report, load_plugins())

    if recommendation.plugin_id != "twist":
        twist_plugin = next(plugin for plugin in load_plugins() if plugin.plugin_id == "twist")
        plugin_score = twist_plugin.score(report)
        recommendation = CutterRecommendation(
            plugin_id=plugin_score.plugin_id,
            plugin_name=plugin_score.plugin_name,
            score=plugin_score.score,
            reason=plugin_score.reason,
            parameters=plugin_score.parameters,
        )
        console.print("[bold yellow]Warning:[/bold yellow] planner did not prefer Twist; forcing Twist because this tool is explicit.")

    result = apply_validated_twist_operation(
        input_path=input_path,
        output_path=output_path,
        recommendation=recommendation,
        blender_path=args.blender,
        keep_cutter=args.keep_cutter,
    )

    table = Table(title="FlexAI Validated Twist Operation")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Input", str(result.operation.input_path))
    table.add_row("Output", str(result.operation.output_path))
    table.add_row("Cutter", str(result.operation.cutter_path))
    table.add_row("Validation Passed", str(result.validation.passed))
    table.add_row("Watertight", str(result.validation.watertight))
    table.add_row("Faces", str(result.validation.face_count))
    table.add_row("Vertices", str(result.validation.vertex_count))
    table.add_row("Volume", f"{result.validation.volume_mm3:.2f} mm³")
    table.add_row("Surface Area", f"{result.validation.surface_area_mm2:.2f} mm²")
    table.add_row("Warnings", "\n".join(result.validation.warnings) if result.validation.warnings else "None")
    console.print(table)

    return 0 if result.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
