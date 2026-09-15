#!/usr/bin/env python3
"""CUSTOS multi-session task queue (concept section 11).

A small file-based coordination queue so several Claude Code sessions / subagents
working the same project (or several fleet repos) pick up distinct tasks instead of
colliding. Combined with git-worktree isolation per session, this is the coordinated
distribution the concept describes - built from existing primitives, not a magic
orchestrator.

Queue file: custos_tasks.json in the repo root (shared, gitignored runtime state).
A lock file makes the read-modify-write atomic across concurrent sessions.

Completed tasks must carry a proof reference (e.g. a test-run id) - a task is not
done on a claim, same rule as everywhere in CUSTOS.

Usage:
  python bin/task_queue.py add --title "Fix login" [--desc "..."]
  python bin/task_queue.py list [--status open|claimed|done]
  python bin/task_queue.py claim --id T1 --session sess-abc
  python bin/task_queue.py complete --id T1 --proof "pytest run #42 green"
  python bin/task_queue.py release --id T1
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone

QUEUE = "custos_tasks.json"
LOCK = "custos_tasks.lock"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Lock:
    def __init__(self, path: str, timeout: float = 10.0):
        self.path = path
        self.timeout = timeout
        self.fd = None

    def __enter__(self):
        start = time.time()
        while True:
            try:
                self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                return self
            except FileExistsError:
                if time.time() - start > self.timeout:
                    # Stale lock breaker: assume crash after timeout.
                    try:
                        os.remove(self.path)
                    except OSError:
                        pass
                time.sleep(0.05)

    def __exit__(self, *exc):
        if self.fd is not None:
            os.close(self.fd)
        try:
            os.remove(self.path)
        except OSError:
            pass


def load(cwd: str) -> dict:
    path = os.path.join(cwd, QUEUE)
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict) and isinstance(data.get("tasks"), list):
                return data
        except (OSError, json.JSONDecodeError):
            pass
    return {"schema": 1, "seq": 0, "tasks": []}


def save(cwd: str, data: dict) -> None:
    path = os.path.join(cwd, QUEUE)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


def find(data: dict, tid: str) -> dict | None:
    return next((t for t in data["tasks"] if t["id"] == tid), None)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["add", "list", "claim", "complete", "release"])
    ap.add_argument("--title")
    ap.add_argument("--desc", default="")
    ap.add_argument("--id")
    ap.add_argument("--session", default="")
    ap.add_argument("--proof", default="")
    ap.add_argument("--status")
    ap.add_argument("--cwd", default=os.getcwd())
    args = ap.parse_args()

    if args.cmd == "list":
        data = load(args.cwd)
        tasks = [t for t in data["tasks"]
                 if not args.status or t["status"] == args.status]
        if not tasks:
            print("CUSTOS queue: no tasks.")
            return 0
        for t in tasks:
            extra = ""
            if t["status"] == "claimed":
                extra = f" by {t.get('session', '?')}"
            elif t["status"] == "done":
                extra = f" proof={t.get('proof', '?')}"
            print(f"  {t['id']} [{t['status']}{extra}] {t['title']}")
        return 0

    with Lock(os.path.join(args.cwd, LOCK)):
        data = load(args.cwd)

        if args.cmd == "add":
            if not args.title:
                print("add requires --title", file=sys.stderr)
                return 2
            data["seq"] += 1
            tid = f"T{data['seq']}"
            data["tasks"].append({
                "id": tid, "title": args.title, "desc": args.desc,
                "status": "open", "session": None, "proof": None,
                "created": now(), "updated": now(),
            })
            save(args.cwd, data)
            print(f"CUSTOS queue: added {tid}.")
            return 0

        task = find(data, args.id) if args.id else None
        if args.cmd in ("claim", "complete", "release") and not task:
            print(f"CUSTOS queue: task {args.id} not found.", file=sys.stderr)
            return 2

        if args.cmd == "claim":
            if task["status"] == "claimed" and task["session"] != args.session:
                print(f"CUSTOS queue: {args.id} already claimed by "
                      f"{task['session']}.", file=sys.stderr)
                return 1
            if task["status"] == "done":
                print(f"CUSTOS queue: {args.id} already done.", file=sys.stderr)
                return 1
            task.update(status="claimed", session=args.session, updated=now())
            save(args.cwd, data)
            print(f"CUSTOS queue: {args.id} claimed by {args.session}.")
            return 0

        if args.cmd == "complete":
            if not args.proof:
                print("CUSTOS queue: complete requires --proof (a task is not done "
                      "on a claim).", file=sys.stderr)
                return 2
            task.update(status="done", proof=args.proof, updated=now())
            save(args.cwd, data)
            print(f"CUSTOS queue: {args.id} done (proof: {args.proof}).")
            return 0

        if args.cmd == "release":
            task.update(status="open", session=None, updated=now())
            save(args.cwd, data)
            print(f"CUSTOS queue: {args.id} released.")
            return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
