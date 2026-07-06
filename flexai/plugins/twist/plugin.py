# flexai/plugins/twist/plugin.py

from __future__ import annotations

from flexai.models import ModelReport
from flexai.plugins.base import CutterPlugin, PluginScore


class TwistPlugin(CutterPlugin):
    plugin_id = "twist"
    name = "Twist"
    description = "Centered twist-style cutter for rounded or axial fidget-like models."

    def score(self, report: ModelReport) -> PluginScore:
        dimensions = report.dimensions_mm
        shortest = min(dimensions)
        longest = max(dimensions)
        diameter = min(dimensions[0], dimensions[1])
        height = dimensions[2]

        if report.shape == "sphere":
            score = 96.0
            reason = "Round, radially symmetric body is a strong match for a centered Twist cutter."
        elif report.shape == "cylinder_or_rod":
            score = 84.0
            reason = "Axial shape can support twist cuts if centered along the main body."
        elif report.shape == "compact" and shortest / longest > 0.7:
            score = 62.0
            reason = "Compact body may support twist cutting, but shape confidence is lower."
        else:
            score = 20.0
            reason = "Twist cutter is usually unsafe or low-value for this shape."

        if not report.watertight:
            score -= 25.0
            reason += " Mesh is not watertight, so boolean cutting risk is higher."

        parameters = {
            "center_mm": [0.0, 0.0, 0.0],
            "diameter_mm": round(float(diameter * 1.05), 3),
            "height_mm": round(float(height * 1.10), 3),
            "core_hole_mm": round(float(max(6.0, diameter * 0.22)), 3),
            "turns": 1.0,
            "clearance_mm": 0.25,
        }

        return PluginScore(
            plugin_id=self.plugin_id,
            plugin_name=self.name,
            score=max(0.0, min(100.0, score)),
            reason=reason,
            parameters=parameters,
        )
