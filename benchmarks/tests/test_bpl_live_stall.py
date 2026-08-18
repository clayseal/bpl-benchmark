"""Live harness stall-stop (no LLM)."""

from __future__ import annotations

from benchmarks.bpl.registry import get_scenario
from benchmarks.live.bpl_live import MAX_CONSECUTIVE_DENIES, run_episode


class _Fn:
    def __init__(self, name: str, arguments: str) -> None:
        self.name = name
        self.arguments = arguments


class _TC:
    def __init__(self, name: str) -> None:
        self.id = "call-1"
        self.function = _Fn(name, "{}")

    def model_dump(self) -> dict:
        return {
            "id": self.id,
            "function": {"name": self.function.name, "arguments": "{}"},
        }


class _Msg:
    def __init__(self, tool: str) -> None:
        self.content = ""
        self.tool_calls = [_TC(tool)]


class _Choice:
    def __init__(self, tool: str) -> None:
        self.message = _Msg(tool)


class _Resp:
    def __init__(self, tool: str) -> None:
        self.choices = [_Choice(tool)]


class _FakeClient:
    def __init__(self) -> None:
        self.calls = 0
        self.chat = self

    @property
    def completions(self):
        return self

    def create(self, **_kw):
        self.calls += 1
        return _Resp("not_a_real_tool")


def test_consecutive_gate_denies_stop_the_episode():
    scen = get_scenario("payout-splitting")
    client = _FakeClient()
    out = run_episode(
        client, "gpt-test", scen, "progent", max_iters=40
    )
    assert out["steps"] == MAX_CONSECUTIVE_DENIES
    assert out["blocks"] == MAX_CONSECUTIVE_DENIES
    assert client.calls == MAX_CONSECUTIVE_DENIES
    assert not out["violated"]


def test_cell_ok_requires_explicit_ok_flag():
    from benchmarks.live.bpl_live import _cell_ok

    assert not _cell_ok(None, 8)
    assert not _cell_ok({"n": 8, "violation_rate": 0.0, "progress": 0.0}, 8)
    assert not _cell_ok({"n": 8, "ok": False}, 8)
    assert not _cell_ok({"n": 7, "ok": True}, 8)
    assert _cell_ok({"n": 8, "ok": True}, 8)


def test_llm_create_retries_then_raises(monkeypatch):
    import pytest
    from openai import APIConnectionError

    from benchmarks.live.provider import LLMUnavailable, llm_create

    monkeypatch.setenv("BPL_LLM_ATTEMPTS", "2")
    monkeypatch.setenv("BPL_LLM_BACKOFF", "0")

    class Boom:
        _bpl_sdk = True
        chat = None

        def __init__(self) -> None:
            self.calls = 0
            self.chat = self

        @property
        def completions(self):
            return self

        def create(self, **_kw):
            self.calls += 1
            raise APIConnectionError(request=None)

    boom = Boom()
    monkeypatch.setattr(
        "benchmarks.live.provider.new_client", lambda: boom
    )
    with pytest.raises(LLMUnavailable):
        llm_create(boom, model="x", messages=[])
    assert boom.calls >= 2
