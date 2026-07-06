# flexai/plugins/honeycomb/plugin.py

from __future__ import annotations

from flexai.models import ModelReport
from flexai.plugins.base import CutterPlugin, PluginScore


class HoneycombPlugin(CutterPlugin):
    plugin_id = "honeycomb"
    name = "Honeycomb"
    description = "Hexagonal cut pattern for lightweight panels and decorative flexible surfaces."

    def score(self, report: ModelReport) -> PluginScore:
        dimensions = report.dimensions_mm
        longest = max(dimensions)
        shortest = min(dimensions)
        middle = sorted(dimensions)[1]

        if report.shape == "flat_panel":
            score = 88.0
            reason = "Flat panel geometry is a strong match for honeycomb lightening and decorative flex."
        elif report.shape == "compact":
            score = 55.0
            reason = "Compact body may accept honeycomb cuts on a selected face, but automatic placement needs review."
        elif report.shape == "organic_or_complex":
            score = 38.0
            reason = "Complex geometry may support honeycomb only with manual region selection."
        else:
            score = 28.0
            reason = "Honeycomb is most useful on broad flat or gently curved panels."

        if not report.watertight:
            score -= 15.0
            reason += " Mesh is not watertight, so cutter execution should be conservative."

        cell_size = max(3.0, min(longest, middle) * 0.12)
        parameters = {
            "cell_size_mm": round(float(cell_size), 3),
            "wall_width_mm": 0.8,
            "margin_mm": max(2.0, round(float(shortest * 0.15), 3)),
            "cut_through": True,
        }

        return PluginScore(
            plugin_id=self.plugin_id,
            plugin_name=self.name,
            score=max(0.0, min(100.0, score)),
            reason=reason,
            parameters=parameters,
        )
