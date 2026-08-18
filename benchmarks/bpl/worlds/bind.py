"""Attach the Acme world journal to every scenario episode.

Core-12 worlds are native (tools mutate tables). Everything else keeps its
existing handler and gains a durable tool log plus JSON state snapshots so
an episode is inspectable after the fact.
"""

from __future__ import annotations

from benchmarks.bpl.schema import Scenario
from benchmarks.bpl.worlds.world import World


def attach_journal(scen: Scenario) -> Scenario:
    orig_make = scen.make_env
    orig_handler = scen.handler

    def make_env():
        env = orig_make()
        if getattr(env, "world", None) is None:
            env.world = World.journal_only(scen.name)
        return env

    def handler(env, name, args):
        world = getattr(env, "world", None)
        if world is not None and world.native:
            return orig_handler(env, name, args)
        result = orig_handler(env, name, args)
        if world is not None:
            world.log(name, args, result)
            try:
                world.snapshot_state(env.state)
            except (TypeError, ValueError):
                pass
        return result

    scen.make_env = make_env
    scen.handler = handler
    return scen
