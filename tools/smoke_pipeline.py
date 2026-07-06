# tools/smoke_pipeline.py

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import trimesh
from rich.console import Console
from rich.table import Table

from flexai.analyzer.mesh_analyzer import analyze_model
from flexai.cutters.twist_generator import generate_twist_cutter
from flexai.importer.mesh_loader import load_mesh
from flexai.operations.twist_operation import twist_parameters_from_recommendation
from flexai.planner.recommender import recommend_cutter
from flexai.plugins.registry import load_plugins
from flexai.validation.mesh_validator import validate_mesh_file

console = Console()


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="flexai_smoke_") as tmpdir:
        workdir = Path(tmpdir)
        model_path = workdir / "sphere.stl"
        cutter_path = workdir / "twist_cutter.stl"

        trimesh.creation.icosphere(subdivisions=3, radius=20.0).export(model_path)

        asset = load_mesh(model_path)
        report = analyze_model(asset, model_path)
        recommendation = recommend_cutter(report, load_plugins())

        if recommendation.plugin_id != "twist":
            console.print(f"[bold red]Expected Twist recommendation, got {recommendation.plugin_name}[/bold red]")
            return 1

        params = twist_parameters_from_recommendation(recommendation)
        cutter = generate_twist_cutter(params)
        cutter.export(cutter_path)
        cutter_validation = validate_mesh_file(cutter_path)

        table = Table(title="FlexAI Smoke Pipeline")
        table.add_column("Stage")
        table.add_column("Result")
        table.add_row("Generated input", str(model_path))
        table.add_row("Detected shape", report.shape)
        table.add_row("Recommendation", recommendation.plugin_name)
        table.add_row("Score", f"{recommendation.score:.1f}/100")
        table.add_row("Cutter file", str(cutter_path))
        table.add_row("Cutter loadable", str(cutter_validation.loadable))
        table.add_row("Cutter faces", str(cutter_validation.face_count))
        table.add_row("Cutter vertices", str(cutter_validation.vertex_count))
        console.print(table)

        console.print_json(
            json.dumps(
                {
                    "model": report.to_dict(),
                    "recommendation": recommendation.to_dict(),
                    "cutter_validation": cutter_validation.to_dict(),
                },
                indent=2,
            )
        )

        return 0 if cutter_validation.loadable else 2


if __name__ == "__main__":
    raise SystemExit(main())
