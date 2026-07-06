# flexai/plugins/zigzag/plugin.py

from __future__ import annotations

from flexai.models import ModelReport
from flexai.plugins.base import CutterPlugin, PluginScore


class ZigzagPlugin(CutterPlugin):
    plugin_id = "zigzag"
    name = "Zigzag / Offset Slots"
    description = "Alternating slot cutter for straps, bracelets, handles, and flexible bands."

    def score(self, report: ModelReport) -> PluginScore:
        dimensions = report.dimensions_mm
        longest = max(dimensions)
        shortest = min(dimensions)
        aspect = longest / max(shortest, 0.001)

        if report.shape == "long_strip":
            score = 94.0
            reason = "Long narrow geometry is a strong match for zigzag flexibility cuts."
        elif report.shape == "flat_panel" and aspect > 2.0:
            score = 78.0
            reason = "Flat elongated region can use offset zigzag slots for controlled bending."
        elif report.shape == "cylinder_or_rod":
            score = 52.0
            reason = "Axial body may support zigzag cuts, but placement should be reviewed."
        else:
            score = 24.0
            reason = "Zigzag cuts work best on straps, strips, and elongated regions."

        if not report.watertight:
            score -= 15.0
            reason += " Mesh is not watertight, so cutter execution should be conservative."

        parameters = {
            "slot_width_mm": 0.8,
            "slot_spacing_mm": 2.5,
            "row_offset_mm": 1.25,
            "amplitude_mm": round(float(max(2.0, shortest * 0.35)), 3),
            "margin_mm": 2.0,
        }

        return PluginScore(
            plugin_id=self.plugin_id,
            plugin_name=self.name,
            score=max(0.0, min(100.0, score)),
            reason=reason,
            parameters=parameters,
        )
