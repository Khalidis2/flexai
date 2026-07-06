# flexai/plugins/base.py

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from flexai.models import ModelReport


@dataclass(frozen=True)
class PluginScore:
    plugin_id: str
    plugin_name: str
    score: float
    reason: str
    parameters: dict[str, Any]


class CutterPlugin(ABC):
    plugin_id: str
    name: str
    description: str

    @abstractmethod
    def score(self, report: ModelReport) -> PluginScore:
        raise NotImplementedError
