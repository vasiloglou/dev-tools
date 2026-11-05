# Acceptance test examples

These examples show the target style. `myapp`, its commands, modules, field names and error codes are placeholders: a real test follows the project's public contract (`references/project.md` beside the process-phase skill) and the phase's LOCKED decisions. When Discuss fixes a different name, the test follows the CONTEXT. Each example gives its red reason at the time of Specify.

## Shared helper module

Once an earlier phase has helpers, copy them from its `pNN_helpers.py` into the new phase's `pNN_helpers.py` rather than rewriting them. Typical helpers:
- `cli(*args, cwd=None, env=None, timeout=120.0) -> (exit_code, stdout, stderr)`: runs the project's CLI in a subprocess. `env=` is how a test reaches the subprocess environment.
- `fixture_path(name)`, `sha256_of(path)` and fixtures such as `sample_orders`.

## A command's output, exit codes and unchanged input

```python
# tests/acceptance/p02_reports/test_report_cli.py (style)
import json
from pathlib import Path

from p02_helpers import cli, sha256_of


def test_report_prints_totals_as_json(sample_orders):
    code, out, err = cli("report", "--input", str(sample_orders), "--format", "json")
    assert code == 0, err
    assert {"total", "count", "warnings"} <= json.loads(out).keys()


def test_unknown_column_is_a_domain_error_and_input_is_unchanged(sample_orders):
    before = sha256_of(Path(sample_orders))
    code, out, err = cli("report", "--input", str(sample_orders), "--group-by", "no_such_column")
    assert code == 1, err                                   # a domain error, not a crash or a usage error
    assert json.loads(out)["error"]["code"] == "UNKNOWN_COLUMN"
    assert sha256_of(Path(sample_orders)) == before         # the command never writes its input
```

**Red reason:** the CLI exits 2 (usage error) because `report` does not exist yet, and each `assert code == …, err` prints stderr.

## Expected values come from construction

```python
# tests/acceptance/p02_reports/test_report_totals.py
import pytest

from p02_helpers import gold_cases


@pytest.mark.parametrize("gold", gold_cases("orders"), ids=lambda g: g.id)
def test_report_totals_match(gold):
    from myapp.reports import totals                 # ImportError until the phase lands
    assert totals(gold.orders) == gold.expected      # expected is fixed by how the case was built


@pytest.mark.parametrize("gold", gold_cases("orders"), ids=lambda g: g.id)
def test_removing_one_order_changes_the_total(gold):
    from myapp.reports import totals
    for removed in gold.orders:
        rest = [order for order in gold.orders if order is not removed]
        assert totals(rest) == gold.expected - removed.amount, removed.id   # a constant answer cannot pass
```

**Red reason:** `ModuleNotFoundError: myapp.reports`, raised inside each test, so every test fails on its own and nothing fails at collection.

## A spike-dependent provider (never live; passes under Go and Kill)

The spike verdict is known before Specify: it is a LOCKED CX item backed by a DEC. **Branch on that recorded verdict, not on the tool's output**; otherwise a broken Go implementation that returns `PROVIDER_UNAVAILABLE` passes. How replay mode is selected and where the opt-in lives are decided in Discuss, so the helpers `spike_verdict`, `with_opt_in` and `replay_env` below stand for whatever the CONTEXT fixes.

```python
# tests/acceptance/p02_reports/test_summary_provider.py
import json

from p02_helpers import cli, no_network_env, read_all, replay_env, spike_verdict, with_opt_in

SENTINEL = "sentinel-key-never-printed"


def test_summary_follows_the_locked_verdict(sample_orders, summary_cassettes, tmp_path):
    env = replay_env(no_network_env(tmp_path), summary_cassettes, {"PROVIDER_API_KEY": SENTINEL})
    code, out, err = cli("summarize", "--input", str(sample_orders), *with_opt_in(tmp_path), env=env)
    if spike_verdict() == "go":                    # read from the LOCKED CX / DEC, not from the output
        assert code == 0, err
        assert json.loads(out)["summary"]["order_count"] == 3
    else:
        error = json.loads(out)["error"]
        assert error["code"] == "PROVIDER_UNAVAILABLE" and "DEC-" in error["message"]
    assert SENTINEL not in out + err + read_all(summary_cassettes) + read_all(tmp_path)


def test_no_opt_in_fails_before_any_network(sample_orders, tmp_path):
    code, out, err = cli("summarize", "--input", str(sample_orders), env=no_network_env(tmp_path))
    assert json.loads(out)["error"]["code"] == "OPT_IN_REQUIRED", err
    assert "socket blocked" not in err             # the guard fired first, no connect attempted
```

Also cover: a missing optional dependency → `PROVIDER_UNAVAILABLE` with an install hint (simulate with a `sitecustomize.py` that sets `sys.modules["<provider_sdk>"] = None`, or `monkeypatch.setitem(sys.modules, "<provider_sdk>", None)` in process); a cassette miss → `REPLAY_MISS`.

**Blocking sockets for subprocesses.** `monkeypatch` does not reach a CLI subprocess. `no_network_env(tmp_path)` writes a `sitecustomize.py` into `tmp_path` that replaces `socket.socket.connect` with a function raising `OSError("socket blocked")`, and returns `os.environ` plus `PYTHONPATH=tmp_path`. Assert the error text never appears when the tool should stop before the network.

## Seeded sampling (set-level assertions on two fixtures)

```python
# tests/acceptance/p03_samples/test_sample_orders.py
import json

import pytest

from p03_helpers import cli, fixture_path

FIXTURES = ("orders_small", "orders_wide")   # two fixtures, so one cannot hide a special case


@pytest.mark.parametrize("name", FIXTURES)
def test_sampler_yields_20_distinct_valid_orders(name):
    code, out, err = cli("sample", "--input", str(fixture_path(name)), "--n", "20", "--seed", "7")
    assert code == 0, err                                    # no early return: these must generate
    samples = json.loads(out)["samples"]
    assert len({s["fingerprint"] for s in samples}) >= 20    # a set-level property, not one exact sample
    assert all(s["valid"] for s in samples)
```

**Red reason:** the CLI exits 2 (usage error) for `sample`, which `assert code == 0, err` reports with stderr.

## Anti-examples

| Bad test | Problem |
|---|---|
| `from myapp.reports import totals` at module top | Collection error at red; hides the other tests |
| Asserting on the text a live provider returns | Nondeterministic, costs money, and needs a network |
| `assert samples[0] == {...}` without a golden file | Pins one sample of a random process |
| Asserting `myapp.reports._group_rows` internals | Couples the contract to private code |
| `pytest.skip` when a case is infeasible | Hides the result; report infeasibility and assert that a reason is given |
