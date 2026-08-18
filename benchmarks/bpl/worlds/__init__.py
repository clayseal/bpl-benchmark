"""Acme operational environments for BPL.

Scored suites (Core-12, Hard-24) run against a SQLite company: double-entry
ledger, IAM grants, customer records, mail, procurement, permits, and a
complete tool journal. Freeze fields (prompts, tool schemas, scripts) are
unchanged; only the runtime is real.

See ENVS.md.
"""

from benchmarks.bpl.worlds.world import World

__all__ = ["World"]
