# app.py

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from flexai.analyzer.mesh_analyzer import analyze_model
from flexai.importer.mesh_loader import load_mesh
from flexai.models import CutterRecommendation, ModelReport
from flexai.operations.scored_twist_operation import ScoredTwistOperationResult, apply_scored_twist_operation
from flexai.planner.recommender import recommend_cutter
from flexai.plugins.base import CutterPlugin
from flexai.plugins.registry import load_plugins

console = Console()


def analyze_command(path: str, report_path: str | None = None) -> int:
    model_path = Path(path).expanduser().resolve()
    mesh = load_mesh(model_path)
    report = analyze_model(mesh, model_path)
    plugins = load_plugins()
    recommendation = recommend_cutter(report, plugins)

    payload = {
        "model": report.to_dict(),
        "recommendation": recommendation.to_dict(),
    }

    if report_path:
        _write_json_report(Path(report_path), payload)

    table = _analysis_table(model_path, report, recommendation)
    console.print(table)
    console.print_json(json.dumps(payload, indent=2))
    return 0


def twist_command(
    input_path: str,
    output_path: str,
    blender_path: str | None,
    keep_cutter: bool,
    strict_recommendation: bool,
    report_path: str | None = None,
) -> int:
    model_path = Path(input_path).expanduser().resolve()
    output_model_path = Path(output_path).expanduser().resolve()
    asset = load_mesh(model_path)
    report = analyze_model(asset, model_path)
    plugins = load_plugins()
    recommendation = recommend_cutter(report, plugins)

    if recommendation.plugin_id != "twist":
        if strict_recommendation:
            console.print(
                f"[bold red]Refusing Twist:[/bold red] planner recommended {recommendation.plugin_name} "
                f"with score {recommendation.score:.1f}/100."
            )
            return 2
        console.print(
            f"[bold yellow]Warning:[/bold yellow] planner recommended {recommendation.plugin_name}; "
            "forcing Twist because the twist command was requested."
        )
        recommendation = _force_twist_recommendation(report, plugins)

    result = apply_scored_twist_operation(
        input_path=model_path,
        output_path=output_model_path,
        recommendation=recommendation,
        blender_path=blender_path,
        keep_cutter=keep_cutter,
    )

    payload = {
        "model": report.to_dict(),
        "recommendation": recommendation.to_dict(),
        "operation": _twist_result_to_dict(result),
    }

    if report_path:
        _write_json_report(Path(report_path), payload)

    console.print(_twist_table(model_path, output_model_path, result))
    console.print_json(json.dumps(payload, indent=2))
    return 0 if result.passed else 2


def _write_json_report(path: Path, payload: dict[str, Any]) -> Path:
    report_path = path.expanduser().resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return report_path


def _analysis_table(model_path: Path, report: ModelReport, recommendation: CutterRecommendation) -> Table:
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
    return table


def _twist_table(input_path: Path, output_path: Path, result: ScoredTwistOperationResult) -> Table:
    comparison = result.compared_result.comparison
    operation = result.compared_result.operation
    table = Table(title="FlexAI Twist Operation")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Input", str(input_path))
    table.add_row("Output", str(output_path))
    table.add_row("Cutter", str(operation.cutter_path))
    if operation.blender_input_path and operation.blender_input_path != operation.input_path:
        table.add_row("Blender Input", str(operation.blender_input_path))
    table.add_row("Blender Return Code", str(operation.blender_result.return_code))
    table.add_row("Watertight", str(comparison.output_report.watertight))
    table.add_row("Removed Volume", f"{comparison.volume_removed_percent:.2f}%")
    table.add_row("Score", f"{result.score.score:.1f}/100")
    table.add_row("Grade", result.score.grade)
    table.add_row("Passed", str(result.passed))
    table.add_row("Warnings", "\n".join(result.score.warnings) if result.score.warnings else "None")
    return table


def _force_twist_recommendation(report: ModelReport, plugins: list[CutterPlugin]) -> CutterRecommendation:
    for plugin in plugins:
        if plugin.plugin_id == "twist":
            score = plugin.score(report)
            return CutterRecommendation(
                plugin_id=score.plugin_id,
                plugin_name=score.plugin_name,
                score=score.score,
                reason=score.reason,
                parameters=score.parameters,
            )
    raise ValueError("Twist plugin is not available")


def _twist_result_to_dict(result: ScoredTwistOperationResult) -> dict[str, object]:
    operation = result.compared_result.operation
    return {
        "passed": result.passed,
        "score": result.score.to_dict(),
        "comparison": result.compared_result.comparison.to_dict(),
        "input_path": str(operation.input_path),
        "blender_input_path": str(operation.blender_input_path) if operation.blender_input_path else None,
        "cutter_path": str(operation.cutter_path),
        "output_path": str(operation.output_path),
        "blender": {
            "return_code": operation.blender_result.return_code,
            "stdout": operation.blender_result.stdout,
            "stderr": operation.blender_result.stderr,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="flexai")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze an STL, OBJ, or 3MF file")
    analyze_parser.add_argument("path", help="Path to model file")
    analyze_parser.add_argument("--report", default=None, help="Optional path to write the JSON analysis report")

    twist_parser = subparsers.add_parser("twist", help="Apply the Twist cutter and validate the output STL")
    twist_parser.add_argument("input", help="Input STL, OBJ, or 3MF path")
    twist_parser.add_argument("output", help="Output STL path")
    twist_parser.add_argument("--blender", default=None, help="Optional explicit Blender executable path")
    twist_parser.add_argument("--keep-cutter", action="store_true", help="Keep generated cutter STL beside output")
    twist_parser.add_argument("--report", default=None, help="Optional path to write the JSON operation report")
    twist_parser.add_argument(
        "--strict-recommendation",
        action="store_true",
        help="Fail if the planner does not recommend Twist for this model",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "analyze":
        return analyze_command(args.path, report_path=args.report)
    if args.command == "twist":
        return twist_command(
            input_path=args.input,
            output_path=args.output,
            blender_path=args.blender,
            keep_cutter=args.keep_cutter,
            strict_recommendation=args.strict_recommendation,
            report_path=args.report,
        )

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
