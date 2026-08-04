from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class PluginPayload:
    data: dict


class PipelinePlugin(Protocol):
    name: str

    def pre_geometry(self, payload: PluginPayload) -> PluginPayload: ...

    def post_geometry(self, payload: PluginPayload) -> PluginPayload: ...

    def pre_architecture(self, payload: PluginPayload) -> PluginPayload: ...

    def post_architecture(self, payload: PluginPayload) -> PluginPayload: ...

    def post_core(self, payload: PluginPayload) -> PluginPayload: ...


class NoOpPlugin:
    name = "noop"

    def pre_geometry(self, payload: PluginPayload) -> PluginPayload:
        return PluginPayload(data={**payload.data})

    def post_geometry(self, payload: PluginPayload) -> PluginPayload:
        return PluginPayload(data={**payload.data})

    def pre_architecture(self, payload: PluginPayload) -> PluginPayload:
        return PluginPayload(data={**payload.data})

    def post_architecture(self, payload: PluginPayload) -> PluginPayload:
        return PluginPayload(data={**payload.data})

    def post_core(self, payload: PluginPayload) -> PluginPayload:
        return PluginPayload(data={**payload.data})
