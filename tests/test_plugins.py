# tests/test_plugins.py

from __future__ import annotations

from flexai.plugins.registry import load_plugins


def test_loads_four_v1_plugins() -> None:
    plugins = load_plugins()
    plugin_ids = {plugin.plugin_id for plugin in plugins}

    assert plugin_ids == {"twist", "living_hinge", "zigzag", "honeycomb"}
    assert len(plugins) == 4
