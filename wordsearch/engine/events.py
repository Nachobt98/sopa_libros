"""Structured run events emitted by generation pipelines."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from typing import Any

RunEventCallback = Callable[["RunEvent"], None]


@dataclass(frozen=True)
class RunEvent:
    """Machine-readable pipeline event for GUI progress and logs."""

    type: str
    stage: str
    message: str
    current: int | None = None
    total: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def emit_run_event(
    callback: RunEventCallback | None,
    event_type: str,
    stage: str,
    message: str,
    *,
    current: int | None = None,
    total: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Emit a structured event when a caller provided a callback."""
    if callback is None:
        return
    callback(
        RunEvent(
            type=event_type,
            stage=stage,
            message=message,
            current=current,
            total=total,
            metadata=metadata or {},
        )
    )
