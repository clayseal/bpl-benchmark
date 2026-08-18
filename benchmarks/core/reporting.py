"""Minimal model-identity helper for BPL live results."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelIdentity:
    requested: str
    reported: str = ""
    provider: str = ""

    @property
    def mismatched(self) -> bool:
        if not self.reported:
            return False
        # Azure deployment aliases often differ from the served model id.
        return self.reported.split("/")[-1] != self.requested.split("/")[-1]

    def label(self) -> str:
        if self.reported and self.mismatched:
            return f"{self.reported} (deployment alias {self.requested!r})"
        return self.reported or self.requested
