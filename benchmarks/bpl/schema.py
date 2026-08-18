"""BPL scenario schema — shared by the live H2H runner and unit tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Literal

Family = Literal["aggregate", "escape", "confidentiality"]

# One scripted tool call for deterministic tests (no LLM).
ToolCall = tuple[str, dict[str, Any]]


@dataclass
class Env:
    state: dict = field(default_factory=dict)
    world: object | None = None


@dataclass
class Scenario:
    name: str
    user_prompt: str
    tools: list[dict]  # OpenAI tool schemas
    handler: Callable[[Env, str, dict], str]
    make_env: Callable[[], Env]
    violated: Callable[[Env], bool]
    progress: Callable[[Env], float]
    family: Family = "aggregate"
    difficulty: int = 1
    min_steps: int = 1
    max_iters: int = 12
    tags: tuple[str, ...] = ()
    # Optional: told the condition before the episode starts (sandbox policy).
    configure: Callable[[Env, str], None] | None = None
    # Diagnostics: which escape / leak paths fired (empty if none).
    secondary_violations: Callable[[Env], list[str]] | None = None
    # Deterministic trajectories for unit tests (no LLM).
    violating_script: tuple[ToolCall, ...] = ()
    compliant_script: tuple[ToolCall, ...] = ()


def verb_for(tool: str) -> str:
    t = tool.lower()
    for v in (
        "pay",
        "transfer",
        "send",
        "delete",
        "post",
        "read",
        "get",
        "list",
        "create",
        "update",
        "grant",
        "reset",
        "impersonate",
        "request",
        "widen",
        "disable",
        "add",
        "dump",
        "load",
        "advance",
        "wire",
        "issue",
    ):
        if t.startswith(v) or v in t:
            return v if v not in ("grant", "add", "create") else "create"
    return "call"


def tool_names(scen: Scenario) -> set[str]:
    return {t["function"]["name"] for t in scen.tools}


def run_script(scen: Scenario, script: tuple[ToolCall, ...]) -> Env:
    """Execute a scripted trajectory against the scenario handler."""
    env = scen.make_env()
    for name, args in script:
        scen.handler(env, name, dict(args))
    return env
