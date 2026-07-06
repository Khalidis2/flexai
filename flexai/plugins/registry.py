# flexai/plugins/registry.py

from __future__ import annotations

from flexai.plugins.base import CutterPlugin
from flexai.plugins.honeycomb.plugin import HoneycombPlugin
from flexai.plugins.living_hinge.plugin import LivingHingePlugin
from flexai.plugins.twist.plugin import TwistPlugin
from flexai.plugins.zigzag.plugin import ZigzagPlugin


def load_plugins() -> list[CutterPlugin]:
    return [
        TwistPlugin(),
        LivingHingePlugin(),
        ZigzagPlugin(),
        HoneycombPlugin(),
    ]
