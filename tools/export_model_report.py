# tools/export_model_report.py

from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console

from flexai.analyzer.mesh_analyzer import analyze_model
from flexai.importer.mesh_loader import load_mesh
from flexai.perception.candidate_regions import find_candidate_regions
from flexai.perception.model_interpreter import interpret_model
from flexai.perception.protected_regions import detect_protected_regions
from flexai.planner.recommender import recommend_cutter
from flexai.plugins.registry import load_plugins

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Export a full FlexAI model report as JSON.")
    parser.add_argument("input", help="Input STL, OBJ, or 3MF path")
    parser.add_argument("output", help="Output JSON report path")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    asset = load_mesh(input_path)
    model_report = analyze_model(asset, input_path)
    perception = interpret_model(model_report)
    candidate_regions = find_candidate_regions(model_report)
    protected_regions = detect_protected_regions(model_report)
    recommendation = recommend_cutter(model_report, load_plugins())

    payload = {
        "model": model_report.to_dict(),
        "perception": perception.to_dict(),
        "candidate_regions": [region.to_dict() for region in candidate_regions],
        "protected_regions": [region.to_dict() for region in protected_regions],
        "recommendation": recommendation.to_dict(),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    console.print(f"[bold green]Report written:[/bold green] {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
