# flexai/cli.py

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from flexai.analyzer.mesh_analyzer import analyze_model
from flexai.importer.mesh_loader import load_mesh
from flexai.operations.twist_operation import apply_twist_operation
from flexai.planner.recommender import recommend_cutter
from flexai.plugins.registry import load_plugins

console = Console()


def analyze_command(path: str) -> int:
    model_path = Path(path).expanduser().resolve()
    mesh = load_mesh(model_path)
    report = analyze_model(mesh, model_path)
    recommendation = recommend_cutter(report, load_plugins())

    payload = {
        "model": report.to_dict(),
        "recommendation": recommendation.to_dict(),
    }

    table = Table(title="FlexAI Model Analysis")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("File", str(model_path))
    table.add_row("Format", report.file_type.upper())
    table.add_row("Dimensions", f"{report.dimensions_mm[0]:.2f} x {report.dimensions_mm[1]:.2f} x {report.dimensions_mm[2]:.2f} mm")
    table.add_row("Shape", report.shape)
    table.add_row("Watertight", str(report.watertight))
    table.add_row("Volume", f"{report.volume_mm3:.2f} mm³")
    table.add_row("Surface Area", f"{report.surface_area_mm2:.2f} mm²")
    table.add_row("Recommended Cutter", recommendation.plugin_name)
    table.add_row("Confidence", f"{recommendation.score:.1f}/100")
    table.add_row("Reason", recommendation.reason)
    console.print(table)
    console.print_json(json.dumps(payload, indent=2))
    return 0


def apply_twist_command(
    input_path: str,
    output_path: str,
    blender_path: str | None,
    keep_cutter: bool,
) -> int:
    model_path = Path(input_path).expanduser().resolve()
    result_path = Path(output_path).expanduser().resolve()

    mesh = load_mesh(model_path)
    report = analyze_model(mesh, model_path)
    recommendation = recommend_cutter(report, load_plugins())

    if recommendation.plugin_id != "twist":
        console.print(f"[bold yellow]Warning:[/bold yellow] planner recommended {recommendation.plugin_name}, but apply-twist was requested.")
        console.print("Continuing with Twist because the command is explicit.")

    twist_recommendation = recommendation
    if recommendation.plugin_id != "twist":
        twist_plugin = next(plugin for plugin in load_plugins() if plugin.plugin_id == "twist")
        plugin_score = twist_plugin.score(report)
        from flexai.models import CutterRecommendation

        twist_recommendation = CutterRecommendation(
            plugin_id=plugin_score.plugin_id,
            plugin_name=plugin_score.plugin_name,
            score=plugin_score.score,
            reason=plugin_score.reason,
            parameters=plugin_score.parameters,
        )

    operation_result = apply_twist_operation(
        input_path=model_path,
        output_path=result_path,
        recommendation=twist_recommendation,
        blender_path=blender_path,
        keep_cutter=keep_cutter,
    )

    table = Table(title="FlexAI Twist Operation")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Input", str(operation_result.input_path))
    table.add_row("Output", str(operation_result.output_path))
    table.add_row("Cutter", str(operation_result.cutter_path))
    table.add_row("Blender Return Code", str(operation_result.blender_result.return_code))
    console.print(table)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="flexai")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze an STL, OBJ, or 3MF file")
    analyze_parser.add_argument("path", help="Path to model file")

    twist_parser = subparsers.add_parser("apply-twist", help="Apply a generated Twist cutter using Blender")
    twist_parser.add_argument("input", help="Input STL or OBJ path")
    twist_parser.add_argument("output", help="Output STL path")
    twist_parser.add_argument("--blender", default=None, help="Optional explicit Blender executable path")
    twist_parser.add_argument("--keep-cutter", action="store_true", help="Keep generated cutter STL beside the output file")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "analyze":
        return analyze_command(args.path)
    if args.command == "apply-twist":
        return apply_twist_command(args.input, args.output, args.blender, args.keep_cutter)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
