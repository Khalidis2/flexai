# app.py

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from flexai.analyzer.mesh_analyzer import analyze_model
from flexai.importer.mesh_loader import load_mesh
from flexai.planner.recommender import recommend_cutter
from flexai.plugins.registry import load_plugins

console = Console()


def analyze_command(path: str) -> int:
    model_path = Path(path).expanduser().resolve()
    mesh = load_mesh(model_path)
    report = analyze_model(mesh, model_path)
    plugins = load_plugins()
    recommendation = recommend_cutter(report, plugins)

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


def main() -> int:
    parser = argparse.ArgumentParser(prog="flexai")
    subparsers = parser.add_subparsers(dest="command", required=True)

    analyze_parser = subparsers.add_parser("analyze", help="Analyze an STL, OBJ, or 3MF file")
    analyze_parser.add_argument("path", help="Path to model file")

    args = parser.parse_args()
    if args.command == "analyze":
        return analyze_command(args.path)

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
