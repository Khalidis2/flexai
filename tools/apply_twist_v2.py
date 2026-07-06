# tools/apply_twist_v2.py

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from rich.console import Console
from rich.table import Table

from flexai.analyzer.mesh_analyzer import analyze_model
from flexai.cutters.twist_generator import generate_twist_cutter
from flexai.executor.boolean_executor_v2 import subtract_cutter_with_blender_v2
from flexai.importer.mesh_loader import load_mesh
from flexai.operations.twist_operation import twist_parameters_from_recommendation
from flexai.planner.recommender import recommend_cutter
from flexai.plugins.registry import load_plugins
from flexai.validation.mesh_comparison import compare_mesh_files
from flexai.validation.operation_score import score_operation

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Apply Twist cutter using Blender 5 compatible execution.")
    parser.add_argument("input", help="Input STL, OBJ, or 3MF path")
    parser.add_argument("output", help="Output STL path")
    parser.add_argument("--blender", default=None, help="Optional explicit Blender executable path")
    parser.add_argument("--keep-cutter", action="store_true", help="Keep generated cutter STL beside output")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    asset = load_mesh(input_path)
    report = analyze_model(asset, input_path)
    recommendation = recommend_cutter(report, load_plugins())

    twist_plugin = next(plugin for plugin in load_plugins() if plugin.plugin_id == "twist")
    if recommendation.plugin_id != "twist":
        console.print(f"[bold yellow]Warning:[/bold yellow] planner recommended {recommendation.plugin_name}; forcing Twist for this tool.")
        plugin_score = twist_plugin.score(report)
        from flexai.models import CutterRecommendation

        recommendation = CutterRecommendation(
            plugin_id=plugin_score.plugin_id,
            plugin_name=plugin_score.plugin_name,
            score=plugin_score.score,
            reason=plugin_score.reason,
            parameters=plugin_score.parameters,
        )

    with tempfile.TemporaryDirectory(prefix="flexai_twist_v2_") as tmpdir:
        tmpdir_path = Path(tmpdir)
        target_stl = tmpdir_path / "target.stl"
        cutter_stl = output_path.with_name(output_path.stem + "_cutter.stl") if args.keep_cutter else tmpdir_path / "cutter.stl"

        asset.mesh.export(target_stl)
        cutter = generate_twist_cutter(twist_parameters_from_recommendation(recommendation))
        cutter.export(cutter_stl)

        blender_result = subtract_cutter_with_blender_v2(
            target_path=target_stl,
            cutter_path=cutter_stl,
            output_path=output_path,
            blender_path=args.blender,
        )

        comparison = compare_mesh_files(target_stl, output_path)
        score = score_operation(comparison)

    table = Table(title="FlexAI Twist V2")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Input", str(input_path))
    table.add_row("Output", str(output_path))
    table.add_row("Cutter", str(cutter_stl))
    table.add_row("Blender Return Code", str(blender_result.return_code))
    table.add_row("Watertight", str(comparison.output_report.watertight))
    table.add_row("Removed Volume", f"{comparison.volume_removed_percent:.2f}%")
    table.add_row("Score", f"{score.score:.1f}/100")
    table.add_row("Grade", score.grade)
    table.add_row("Passed", str(score.passed))
    table.add_row("Warnings", "\n".join(score.warnings) if score.warnings else "None")
    console.print(table)
    return 0 if score.passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
