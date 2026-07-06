# flexai/plugins/living_hinge/plugin.py

from __future__ import annotations

from flexai.models import ModelReport
from flexai.plugins.base import CutterPlugin, PluginScore


class LivingHingePlugin(CutterPlugin):
    plugin_id = "living_hinge"
    name = "Living Hinge"
    description = "Parallel slit cutter for flat panels, lids, boxes, and bendable strips."

    def score(self, report: ModelReport) -> PluginScore:
        dimensions = report.dimensions_mm
        longest = max(dimensions)
        shortest = min(dimensions)

        if report.shape == "flat_panel":
            score = 92.0
            reason = "Flat panel geometry is the ideal use case for living-hinge slit cuts."
        elif report.shape == "long_strip":
            score = 82.0
            reason = "Long strip geometry can bend predictably with repeated hinge slots."
        elif report.shape == "compact":
            score = 42.0
            reason = "Compact geometry may accept hinge cuts only if a flat region is selected manually."
        else:
            score = 18.0
            reason = "Living hinge cuts require a flat or strip-like region."

        if not report.watertight:
            score -= 15.0
            reason += " Mesh is not watertight, so cutter execution should be conservative."

        parameters = {
            "slot_width_mm": 0.8,
            "slot_spacing_mm": round(float(max(2.0, shortest * 0.35)), 3),
            "margin_mm": 2.0,
            "slot_length_mm": round(float(longest * 0.75), 3),
            "cut_through": True,
        }

        return PluginScore(
            plugin_id=self.plugin_id,
            plugin_name=self.name,
            score=max(0.0, min(100.0, score)),
            reason=reason,
            parameters=parameters,
        )
