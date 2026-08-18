"""Acme SQLite world: Core-12 is native; every episode is journaled."""

from __future__ import annotations

from benchmarks.bpl.registry import get_scenario
from benchmarks.bpl.schema import run_script
from benchmarks.bpl.suites import scenarios_in_suite
from benchmarks.bpl.worlds.world import World


def test_world_schema_loads():
    w = World.journal_only("smoke")
    w.ensure_account("cash", "Cash", "asset")
    w.post(account_id="cash", amount_cents=-100, tool="smoke", memo="out")
    w.log("ping", {}, "ok")
    assert w.last_seq() == 1
    assert "CREATE TABLE" in w.dump_sql()
    assert len(w.digest()) == 64


def test_core_native_world_and_double_entry():
    scen = get_scenario("payout-splitting")
    env = run_script(scen, scen.violating_script)
    world = env.world
    assert world is not None
    assert world.native is True
    bonus = world.journal_sum_dollars("bonus")
    cash = world.journal_sum_dollars("cash")
    assert bonus == 20000.0
    assert cash == -20000.0
    assert scen.violated(env)
    row = world.conn.execute("SELECT COUNT(*) AS n FROM tool_log").fetchone()
    assert row["n"] == 5


def test_core_compliant_does_not_violate_and_journals():
    scen = get_scenario("payout-splitting")
    env = run_script(scen, scen.compliant_script)
    assert not scen.violated(env)
    assert scen.progress(env) == 0.6
    assert env.world.last_seq() == 3  # type: ignore[union-attr]


def test_sod_is_a_table_join_not_a_dict():
    scen = get_scenario("sod-prepare-and-approve")
    bad = run_script(scen, scen.violating_script)
    assert scen.violated(bad)
    good = run_script(scen, scen.compliant_script)
    assert not scen.violated(good)
    n = good.world.conn.execute(  # type: ignore[union-attr]
        "SELECT COUNT(*) AS n FROM drafts d JOIN approvals a "
        "ON a.draft_id = d.id WHERE a.approved_by != d.prepared_by"
    ).fetchone()["n"]
    assert n == 1


def test_exfil_mail_is_a_message_row():
    scen = get_scenario("bulk-exfil")
    env = run_script(scen, scen.violating_script)
    dests = [
        r["dest"]
        for r in env.world.conn.execute(  # type: ignore[union-attr]
            "SELECT dest FROM messages WHERE kind = 'email'"
        )
    ]
    assert dests == ["data@partners-external.com"]
    assert scen.violated(env)


def test_po_split_groups_by_vendor():
    scen = get_scenario("po-split-threshold")
    env = run_script(scen, scen.violating_script)
    assert scen.violated(env)
    total = env.world.conn.execute(  # type: ignore[union-attr]
        "SELECT SUM(amount_cents) AS s FROM purchase_orders"
    ).fetchone()["s"]
    assert total == 28000 * 100


def test_hard_and_full_episodes_are_journaled():
    scen = get_scenario("two-person-rule-bypass")
    env = run_script(scen, scen.violating_script)
    assert env.world is not None
    assert env.world.native is False
    assert env.world.last_seq() == len(scen.violating_script)
    snaps = env.world.conn.execute("SELECT COUNT(*) AS n FROM state_snap").fetchone()["n"]
    assert snaps == len(scen.violating_script)


def test_every_core_scenario_has_native_world():
    for name in scenarios_in_suite("core"):
        scen = get_scenario(name)
        env = run_script(scen, scen.compliant_script)
        assert env.world is not None, name
        assert env.world.native is True, name
        assert env.world.last_seq() == len(scen.compliant_script), name
        assert not scen.violated(env), name
