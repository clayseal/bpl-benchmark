"""SQLite-backed Acme company world.

One connection per episode. Tools are real mutations (journal, grants, mail,
POs, …). Oracles query tables, not ad-hoc dicts.

``native=True`` worlds (Core-12) implement tools themselves.
``native=False`` worlds journal another handler and snapshot ``env.state``.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Callable

_SCHEMA = (Path(__file__).resolve().parent / "schema.sql").read_text()

ToolFn = Callable[[dict[str, Any]], str]


def _cents(amount: Any) -> int:
    return int(round(float(amount or 0.0) * 100.0))


def _dollars(cents: int) -> float:
    return cents / 100.0


class World:
    """In-memory SQLite company. Not shared across episodes."""

    def __init__(self, scenario: str, *, native: bool = False) -> None:
        self.scenario = scenario
        self.native = native
        self.conn = sqlite3.connect(":memory:", check_same_thread=True)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self._day = 1
        self._ts = 0
        self._tools: dict[str, ToolFn] = {}
        self._persona = "clerk"
        self._draft_n = 0
        self.set_meta("scenario", scenario)
        self.set_meta("engine", "acme-sqlite-v1")

    @classmethod
    def journal_only(cls, scenario: str) -> World:
        return cls(scenario, native=False)

    def set_meta(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", (key, value)
        )

    def meta(self, key: str, default: str = "") -> str:
        row = self.conn.execute(
            "SELECT value FROM meta WHERE key = ?", (key,)
        ).fetchone()
        return str(row["value"]) if row else default

    def register(self, name: str, fn: ToolFn) -> None:
        self._tools[name] = fn

    def call(self, tool: str, args: dict[str, Any]) -> str:
        fn = self._tools.get(tool)
        result = fn(args) if fn else "unknown tool"
        self.log(tool, args, result)
        return result

    def log(self, tool: str, args: dict[str, Any], result: str) -> None:
        self.conn.execute(
            "INSERT INTO tool_log(tool, args_json, result) VALUES (?, ?, ?)",
            (tool, json.dumps(args, sort_keys=True, default=str), result),
        )
        self.conn.commit()

    def snapshot_state(self, state: dict[str, Any]) -> None:
        def _default(obj: Any) -> Any:
            if isinstance(obj, set):
                return sorted(obj)
            raise TypeError(type(obj).__name__)

        seq = self.conn.execute("SELECT COALESCE(MAX(seq), 0) FROM tool_log").fetchone()[
            0
        ]
        blob = json.dumps(state, sort_keys=True, default=_default)
        self.conn.execute("INSERT INTO state_snap(seq, json) VALUES (?, ?)", (seq, blob))
        self.conn.commit()

    def last_seq(self) -> int:
        row = self.conn.execute("SELECT COALESCE(MAX(seq), 0) FROM tool_log").fetchone()
        return int(row[0])

    def digest(self) -> str:
        import hashlib

        dump = "\n".join(self.conn.iterdump())
        return hashlib.sha256(dump.encode()).hexdigest()

    def dump_sql(self) -> str:
        return "\n".join(self.conn.iterdump())

    def summary(self, *, digest: bool = False) -> dict[str, Any]:
        def _count(table: str) -> int:
            return int(self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])

        out = {
            "engine": "acme-sqlite-v1",
            "scenario": self.scenario,
            "native": self.native,
            "tool_calls": _count("tool_log"),
            "journal_lines": _count("journal"),
            "messages": _count("messages"),
            "grants": _count("grants"),
            "purchase_orders": _count("purchase_orders"),
        }
        if digest:
            out["digest"] = self.digest()
        return out

    # --- domain helpers -------------------------------------------------

    def ensure_account(self, account_id: str, name: str, kind: str) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO accounts(id, name, kind) VALUES (?, ?, ?)",
            (account_id, name, kind),
        )

    def post(
        self,
        *,
        account_id: str,
        amount_cents: int,
        tool: str,
        counterparty: str | None = None,
        memo: str = "",
        ref: str | None = None,
    ) -> None:
        self._ts += 1
        self.conn.execute(
            "INSERT INTO journal(day, ts, account_id, amount_cents, counterparty, "
            "memo, tool, ref) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                self._day,
                self._ts,
                account_id,
                amount_cents,
                counterparty,
                memo,
                tool,
                ref,
            ),
        )

    def journal_sum_dollars(self, account_id: str) -> float:
        row = self.conn.execute(
            "SELECT COALESCE(SUM(amount_cents), 0) AS s FROM journal WHERE account_id = ?",
            (account_id,),
        ).fetchone()
        return _dollars(int(row["s"]))

    def weekly_spend_dollars(self) -> float:
        return self.journal_sum_dollars("spend")

    def seed_employees(self, names: list[str], *, role: str = "engineer") -> None:
        for n in names:
            self.conn.execute(
                "INSERT OR REPLACE INTO employees(id, name, role) VALUES (?, ?, ?)",
                (n, n, role),
            )

    def seed_customers(self, rows: list[tuple[str, str, str, str, str]]) -> None:
        for cid, name, email, card, tenant in rows:
            self.conn.execute(
                "INSERT OR REPLACE INTO customers(id, name, email, card, tenant) "
                "VALUES (?, ?, ?, ?, ?)",
                (cid, name, email, card, tenant),
            )

    def seed_documents(self, ids: list[str], *, kind: str) -> None:
        for i in ids:
            self.conn.execute(
                "INSERT OR REPLACE INTO documents(id, kind, body, deleted) "
                "VALUES (?, ?, ?, 0)",
                (i, kind, i),
            )

    def seed_sites(self, sites: list[str]) -> None:
        for s in sites:
            self.conn.execute(
                "INSERT OR IGNORE INTO permits(site, tons_milli) VALUES (?, 0)", (s,)
            )

    def seed_repo(self, repo: str = "main") -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO repo_state(repo, branch_protection) VALUES (?, 1)",
            (repo,),
        )


def money_pair(amount: Any) -> tuple[float, int]:
    cents = _cents(amount)
    return _dollars(cents), cents
