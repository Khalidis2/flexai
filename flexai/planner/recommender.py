# flexai/planner/recommender.py

from __future__ import annotations

from flexai.models import CutterRecommendation, ModelReport
from flexai.plugins.base import CutterPlugin


def recommend_cutter(report: ModelReport, plugins: list[CutterPlugin]) -> CutterRecommendation:
    if not plugins:
        raise ValueError("No cutter plugins are available")

    scored = [plugin.score(report) for plugin in plugins]
    best = max(scored, key=lambda item: item.score)
    return CutterRecommendation(
        plugin_id=best.plugin_id,
        plugin_name=best.plugin_name,
        score=best.score,
        reason=best.reason,
        parameters=best.parameters,
    )
