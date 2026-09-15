"""CUSTOS self-qualification test suite (concept section 12).

Reference testbed: runs the CUSTOS gates/detectors against known-good and
known-bad fixtures and asserts the expected block/allow behaviour. This is CUSTOS
proving itself - the same proof obligation it imposes on others, applied to it.

Stdlib only (unittest + subprocess), so it always runs without extra deps; it is
also collectible by pytest for CI. Each gate is invoked as a real subprocess with
a JSON hook payload on stdin, exactly as Claude Code would call it.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def run(script: str, payload: dict, args: list[str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PY, os.path.join(ROOT, script), *(args or [])],
        input=json.dumps(payload), capture_output=True, text=True, timeout=120,
    )


class AiSlopTests(unittest.TestCase):
    S = "detectors/ai_slop_detector.py"

    def test_clean_passes(self):
        p = {"cwd": ".", "tool_input": {"file_path": "c.py",
             "content": "def add(a, b):\n    return a + b\n"}}
        self.assertEqual(run(self.S, p).returncode, 0)

    def test_slop_blocks(self):
        content = ("// increment the counter by one\nlet data = 1;\nlet temp = 2;\n"
                   "// loop through the array\nconst foo = getStuff();\n"
                   "// return the result\n")
        p = {"cwd": ".", "tool_input": {"file_path": "d.js", "content": content}}
        self.assertEqual(run(self.S, p).returncode, 2)


class LintTests(unittest.TestCase):
    S = "detectors/lint_dispatch.py"

    def test_valid_python_passes(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "ok.py")
            with open(f, "w", encoding="utf-8") as fh:
                fh.write("def f(x):\n    return x + 1\n")
            p = {"cwd": d, "tool_input": {"file_path": f}}
            self.assertEqual(run(self.S, p).returncode, 0)

    def test_broken_python_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            f = os.path.join(d, "bad.py")
            with open(f, "w", encoding="utf-8") as fh:
                fh.write("def f(x)\n    return x\n")
            p = {"cwd": d, "tool_input": {"file_path": f}}
            self.assertEqual(run(self.S, p).returncode, 2)


class A11yTests(unittest.TestCase):
    S = "detectors/a11y_frontend_check.py"

    def test_inaccessible_blocks(self):
        content = ("<html><img src=a><img src=b><input type=text>"
                   "<button></button><a></a></html>")
        p = {"cwd": ".", "tool_input": {"file_path": "p.html", "content": content}}
        self.assertEqual(run(self.S, p).returncode, 2)

    def test_accessible_passes(self):
        content = '<html lang="en"><img src=a alt="a"></html>'
        p = {"cwd": ".", "tool_input": {"file_path": "p.html", "content": content}}
        self.assertEqual(run(self.S, p).returncode, 0)


class DbSchemaTests(unittest.TestCase):
    S = "detectors/db_schema_guard.py"

    @staticmethod
    def _snapshot(d):
        os.makedirs(os.path.join(d, "custos"))
        with open(os.path.join(d, "custos", "db_schema.json"), "w",
                  encoding="utf-8") as fh:
            json.dump({"tables": {"users": ["id"]}}, fh)

    def test_unknown_table_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            self._snapshot(d)
            p = {"cwd": d, "tool_input": {"file_path": "m/1.sql",
                 "content": "UPDATE ghost SET x=1;"}}
            self.assertEqual(run(self.S, p).returncode, 2)

    def test_known_table_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self._snapshot(d)
            p = {"cwd": d, "tool_input": {"file_path": "m/1.sql",
                 "content": "UPDATE users SET id=1;"}}
            self.assertEqual(run(self.S, p).returncode, 0)


class PlanScopeTests(unittest.TestCase):
    def test_plan_gate_blocks_without_approval(self):
        with tempfile.TemporaryDirectory() as d:
            p = {"cwd": d, "tool_name": "ExitPlanMode", "tool_input": {}}
            self.assertEqual(run("bin/plan_gate.py", p).returncode, 2)

    def test_plan_gate_opens_after_approval(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run([PY, os.path.join(ROOT, "bin/custos_approve_plan.py"),
                            "--cwd", d, "--scope", "src/**"], check=True,
                           capture_output=True)
            p = {"cwd": d, "tool_name": "ExitPlanMode", "tool_input": {}}
            self.assertEqual(run("bin/plan_gate.py", p).returncode, 0)

    def test_scope_guard_blocks_out_of_scope(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run([PY, os.path.join(ROOT, "bin/custos_approve_plan.py"),
                            "--cwd", d, "--scope", "src/**"], check=True,
                           capture_output=True)
            p = {"cwd": d, "tool_input": {"file_path": "other/b.py"}}
            self.assertEqual(run("bin/scope_guard.py", p).returncode, 2)


class StopGateTests(unittest.TestCase):
    def test_no_proof_fresh_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            p = {"cwd": d, "stop_hook_active": False}
            self.assertEqual(run("bin/custos_stop_gate.py", p).returncode, 2)

    def test_no_proof_loop_allows(self):
        with tempfile.TemporaryDirectory() as d:
            p = {"cwd": d, "stop_hook_active": True}
            self.assertEqual(run("bin/custos_stop_gate.py", p).returncode, 0)


class CouncilTests(unittest.TestCase):
    def test_suppression_requires_future_expiry(self):
        with tempfile.TemporaryDirectory() as d:
            r = subprocess.run(
                [PY, os.path.join(ROOT, "bin/council_log.py"), "--cwd", d,
                 "--finding", "x", "--decision", "suppress"],
                capture_output=True, text=True)
            self.assertEqual(r.returncode, 2)


class TaskQueueTests(unittest.TestCase):
    Q = "bin/task_queue.py"

    def test_claim_conflict_and_proof_required(self):
        with tempfile.TemporaryDirectory() as d:
            def q(*a):
                return subprocess.run([PY, os.path.join(ROOT, self.Q), *a,
                                       "--cwd", d], capture_output=True, text=True)
            q("add", "--title", "t")
            self.assertEqual(q("claim", "--id", "T1", "--session", "a").returncode, 0)
            self.assertEqual(q("claim", "--id", "T1", "--session", "b").returncode, 1)
            self.assertEqual(q("complete", "--id", "T1").returncode, 2)
            self.assertEqual(
                q("complete", "--id", "T1", "--proof", "run#1").returncode, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
