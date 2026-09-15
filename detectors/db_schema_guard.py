#!/usr/bin/env python3
"""CUSTOS DB schema guard (PreToolUse on Write|Edit of migration/schema files).

Concept section 8: when a migration or schema file references columns/tables, they
must exist in the real, current schema - no invented fields. This gate compares
identifiers referenced in the edited migration against a schema snapshot
(custos/db_schema.json) and blocks (exit 2) on references that are not in the
snapshot.

Only migration/schema-looking files are inspected. If no snapshot exists, it emits
a non-blocking notice (it cannot verify against a schema it does not have) rather
than blocking, and tells you how to provide one.

Snapshot format (custos/db_schema.json):
  { "tables": { "users": ["id", "email", "created_at"], "orders": ["id", ...] } }
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import custos_lib as cl  # noqa: E402

SNAPSHOT = os.path.join("custos", "db_schema.json")

MIGRATION_HINTS = ("migration", "migrate", "schema", "alembic")


def is_migration(path: str) -> bool:
    p = path.replace(os.sep, "/").lower()
    if p.endswith(".sql"):
        return True
    return any(h in p for h in MIGRATION_HINTS)


def load_snapshot(cwd: str) -> dict | None:
    path = os.path.join(cwd, SNAPSHOT)
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict) and isinstance(data.get("tables"), dict):
            return data
    except (OSError, json.JSONDecodeError):
        return None
    return None


# ALTER TABLE x / column references in common SQL / ORM forms.
_TABLE_REF = re.compile(r"\b(?:table|from|into|update|alter\s+table)\s+[\"'`]?(\w+)",
                        re.IGNORECASE)
_COL_REF = re.compile(r"\bcolumn\s+[\"'`]?(\w+)", re.IGNORECASE)


def referenced(text: str) -> tuple[set[str], set[str]]:
    tables = {m.group(1).lower() for m in _TABLE_REF.finditer(text)}
    cols = {m.group(1).lower() for m in _COL_REF.finditer(text)}
    return tables, cols


def main() -> int:
    payload = cl.read_payload()
    path = cl.target_path(payload)
    text = cl.changed_text(payload)
    if not path or not text or not is_migration(path):
        return 0
    cwd = payload.get("cwd") or os.getcwd()

    snap = load_snapshot(cwd)
    if snap is None:
        cl.record(payload, "db_schema_guard",
                  [{"kind": "no-snapshot", "text": SNAPSHOT + " missing"}],
                  blocked=False)
        cl.emit_context(
            f"CUSTOS db-schema guard: no schema snapshot at {SNAPSHOT}; cannot "
            f"verify referenced tables/columns against the real schema. Add one to "
            f"enforce this gate."
        )
        return 0

    tables = {t.lower() for t in snap.get("tables", {})}
    known_cols = {c.lower() for cols in snap.get("tables", {}).values() for c in cols}
    ref_tables, ref_cols = referenced(text)

    unknown = []
    for t in sorted(ref_tables):
        if t not in tables:
            unknown.append({"kind": "unknown-table", "name": t})
    for c in sorted(ref_cols):
        if c not in known_cols:
            unknown.append({"kind": "unknown-column", "name": c})

    if unknown:
        cl.record(payload, "db_schema_guard", unknown, blocked=True)
        names = ", ".join(f"{u['kind']}:{u['name']}" for u in unknown)
        cl.block(
            f"CUSTOS db-schema guard BLOCKED {path}: references not found in the "
            f"real schema snapshot ({names}). Do not invent fields - reconcile "
            f"with the actual schema first."
        )
        return 2  # not reached

    cl.record(payload, "db_schema_guard", [], blocked=False)
    return 0


if __name__ == "__main__":
    sys.exit(main())
