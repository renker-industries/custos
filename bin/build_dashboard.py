#!/usr/bin/env python3
"""CUSTOS dashboard generator (concept section 18).

Reads the CUSTOS runtime reports (custos_findings.json, custos/fleet.yaml,
custos_suppressions.json) and renders a single self-contained dark-terminal
dashboard HTML with the data inlined - so it opens from disk without a server.

Views (concept section 18):
  1. Fleet overview   - repos with status, last scan, open findings
  2. Gates / findings - per-detector rows with status, latest blocked/ok
  3. Security log      - chronological passive-security runs
  4. Council cases     - recorded decisions and active suppressions

Colors/typography follow CUSTOS_BRANDING.md (section 2). The linked Claude Design
mockup is the binding visual reference for further refinement.

Usage:
  python bin/build_dashboard.py [--findings custos_findings.json]
      [--fleet custos/fleet.yaml] [--out interface/custos-dashboard.html]
"""
from __future__ import annotations

import argparse
import html
import json
import os
import sys
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    yaml = None


def load_json(path: str) -> dict:
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, json.JSONDecodeError):
            return {}
    return {}


def load_fleet(path: str) -> dict:
    if yaml and os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                return yaml.safe_load(fh) or {}
        except (OSError, yaml.YAMLError):
            return {}
    return {}


def build_model(findings: dict, fleet: dict, supp: dict,
                fleet_findings: dict | None = None) -> dict:
    runs = findings.get("runs", []) if isinstance(findings, dict) else []
    # per detector aggregation
    detectors: dict[str, dict] = {}
    security_runs = []
    council = []
    for r in runs:
        det = r.get("detector", "unknown")
        if det == "security_passive":
            security_runs.append(r)
            continue
        if det == "council":
            council.append(r)
            continue
        d = detectors.setdefault(det, {"runs": 0, "blocked": 0, "findings": 0,
                                       "last": None})
        d["runs"] += 1
        if r.get("blocked"):
            d["blocked"] += 1
        d["findings"] += len(r.get("findings", []) or [])
        d["last"] = r.get("timestamp")

    # Merge the fleet-wide content scan (fleet_findings.json) into each repo by
    # path (fallback name), so the fleet view shows real findings, not "0".
    ff = fleet_findings if isinstance(fleet_findings, dict) else {}
    scan_by_path: dict[str, dict] = {}
    scan_by_name: dict[str, dict] = {}
    for sr in ff.get("repos", []):
        if sr.get("path"):
            scan_by_path[os.path.abspath(sr["path"])] = sr
        scan_by_name.setdefault(sr.get("repo"), sr)
    repos = []
    for entry in fleet.get("repos", []):
        e = dict(entry)
        sr = None
        if entry.get("path"):
            sr = scan_by_path.get(os.path.abspath(os.path.expanduser(entry["path"])))
        sr = sr or scan_by_name.get(entry.get("name"))
        if sr and sr.get("status") == "scanned":
            fnd = sr.get("findings", {})
            e["scan"] = {
                "severity": sr.get("severity", "none"),
                "secrets": len(fnd.get("secrets", [])),
                "lint": fnd.get("lintIssues", 0),
                "slop": fnd.get("aiSlop", 0),
                "skipped": len(sr.get("skipped", [])),
                "timestamp": sr.get("timestamp"),
            }
        repos.append(e)

    return {
        "generated": datetime.now(timezone.utc).isoformat(),
        "repos": repos,
        "detectors": detectors,
        "security": security_runs[-20:],
        "council": council,
        "suppressions": supp.get("suppressions", []) if isinstance(supp, dict) else [],
        "totalRuns": len(runs),
        "fleetTotals": ff.get("totals", {}),
        "fleetGenerated": ff.get("generated"),
    }


TEMPLATE = """<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CUSTOS Dashboard</title>
<style>
:root {
  --bg: #0b0e11; --panel: #12161b; --text: #d8dee9; --muted: #5c6370;
  --green: #2ecc71; --yellow: #f1c40f; --red: #e74c3c; --grey: #5c6370;
  --border: #1e242c;
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
  font-family: "JetBrains Mono","Cascadia Code",ui-monospace,SFMono-Regular,
  Menlo,Consolas,monospace; font-size: 13px; line-height: 1.5;
  padding: 16px; }
h1 { font-size: 18px; margin: 0 0 2px; letter-spacing: 2px; }
h2 { font-size: 13px; text-transform: uppercase; letter-spacing: 1px;
  color: var(--muted); margin: 24px 0 8px; border-bottom: 1px solid var(--border);
  padding-bottom: 4px; }
.sub { color: var(--muted); margin-bottom: 8px; }
.grid { display: grid; gap: 8px; }
.card { background: var(--panel); border: 1px solid var(--border);
  border-radius: 6px; padding: 10px 12px; }
.row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.row .name { flex: 1 1 240px; min-width: 180px; }
.dot { width: 9px; height: 9px; border-radius: 50%; display: inline-block;
  flex: 0 0 auto; }
.g { background: var(--green); } .y { background: var(--yellow); }
.r { background: var(--red); } .x { background: var(--grey); }
.badge { font-size: 11px; padding: 1px 7px; border-radius: 10px;
  border: 1px solid var(--border); color: var(--muted); }
.badge.active { color: var(--green); border-color: var(--green); }
.badge.inv { color: var(--muted); }
.num { color: var(--text); }
.num.bad { color: var(--red); }
.empty { color: var(--muted); font-style: italic; }
pre { white-space: pre-wrap; word-break: break-word; margin: 6px 0 0;
  color: var(--muted); font-size: 12px; max-height: 160px; overflow: auto; }
.foot { margin-top: 28px; color: var(--muted); font-size: 11px; }
code { color: var(--yellow); }
</style>
</head>
<body>
<h1>CUSTOS</h1>
<div class="sub">Beweis statt Behauptung — dashboard generated <span id="gen"></span></div>
<div id="app"></div>
<div class="foot">Data source: custos_findings.json · custos/fleet.yaml ·
custos_suppressions.json. Visual reference: CUSTOS Dashboard (Claude Design).</div>
<script id="data" type="application/json">__DATA__</script>
<script>
const M = JSON.parse(document.getElementById("data").textContent);
document.getElementById("gen").textContent = M.generated;
const esc = s => (s==null?"":String(s));
const app = document.getElementById("app");
function h(html){ const d=document.createElement("div"); d.innerHTML=html; return d; }

// 1. Fleet overview (with real scan findings from fleet_findings.json)
const sevCls = {high:"r", medium:"y", low:"g", none:"x"};
const ft = M.fleetTotals || {};
let ftLine = "";
if(Object.keys(ft).length){
  ftLine = '<div class="sub">Fleet scan: '+esc(ft.reposScanned)+' scanned · '+
    '<span class="num'+(ft.secrets?" bad":"")+'">'+esc(ft.secrets)+'</span> secrets · '+
    esc(ft.lintIssues)+' lint · '+esc(ft.aiSlop)+' slop · '+
    esc(ft.skippedChecks)+' checks skipped'+
    (M.fleetGenerated?' · '+esc(M.fleetGenerated):'')+'</div>';
}
let s = '<h2>Fleet — '+M.repos.length+' repo(s)</h2>'+ftLine+'<div class="grid">';
if(!M.repos.length) s += '<div class="empty">No repos. Run fleet_discover.py.</div>';
for(const r of M.repos){
  const active = r.status==="aktiv-ueberwacht";
  const sc = r.scan;
  const dot = sc ? (sevCls[sc.severity]||"x") : (active?"g":"x");
  let metrics = '';
  if(sc){
    metrics = '<span class="badge'+(sc.secrets?" ":"")+'">secrets '+
      '<span class="num'+(sc.secrets?" bad":"")+'">'+sc.secrets+'</span></span>'+
      '<span class="badge">lint '+sc.lint+'</span>'+
      '<span class="badge">slop '+sc.slop+'</span>'+
      (sc.skipped?'<span class="badge">skipped '+sc.skipped+'</span>':'');
  } else if(active){
    metrics = '<span class="badge">not scanned</span>';
  }
  s += '<div class="card row"><span class="dot '+dot+'"></span>'+
    '<span class="name">'+esc(r.name)+'</span>'+
    '<span class="badge '+(active?"active":"inv")+'">'+esc(r.status)+'</span>'+
    metrics+'</div>';
}
s += '</div>';

// 2. Gates / findings
s += '<h2>Gates — '+M.totalRuns+' run(s) logged</h2><div class="grid">';
const dets = Object.entries(M.detectors);
if(!dets.length) s += '<div class="empty">No gate runs logged yet.</div>';
for(const [name,d] of dets){
  const cls = d.blocked>0 ? "r" : (d.findings>0 ? "y" : "g");
  s += '<div class="card row"><span class="dot '+cls+'"></span>'+
    '<span class="name">'+esc(name)+'</span>'+
    '<span class="badge">runs '+d.runs+'</span>'+
    '<span class="badge">findings <span class="num'+(d.findings?" bad":"")+'">'+d.findings+'</span></span>'+
    '<span class="badge">blocked <span class="num'+(d.blocked?" bad":"")+'">'+d.blocked+'</span></span></div>';
}
s += '</div>';

// 3. Security log
s += '<h2>Security log — passive</h2><div class="grid">';
if(!M.security.length) s += '<div class="empty">No passive security scans yet.</div>';
for(const run of M.security.slice().reverse()){
  const checks = run.checks||[];
  const bad = checks.filter(c=>c.status==="review"||c.status==="error").length;
  const cls = bad>0?"y":"g";
  s += '<div class="card"><div class="row"><span class="dot '+cls+'"></span>'+
    '<span class="name">'+esc(run.platform)+' · '+esc(run.timestamp)+'</span>'+
    '<span class="badge">'+checks.length+' checks</span></div>';
  s += '<pre>'+checks.map(c=>'['+esc(c.status)+'] '+esc(c.id)).join("\\n")+'</pre></div>';
}
s += '</div>';

// 4. Council cases
s += '<h2>Council — decisions &amp; suppressions</h2><div class="grid">';
if(!M.council.length && !M.suppressions.length)
  s += '<div class="empty">No council cases.</div>';
for(const c of M.council){
  const cls = c.decision==="uphold"?"r":(c.decision==="suppress"?"y":"x");
  s += '<div class="card"><div class="row"><span class="dot '+cls+'"></span>'+
    '<span class="name">'+esc(c.finding)+'</span>'+
    '<span class="badge">'+esc(c.decision)+(c.expiry?" until "+esc(c.expiry):"")+'</span></div>'+
    (c.rationale?'<pre>'+esc(c.votes)+' — '+esc(c.rationale)+'</pre>':'')+'</div>';
}
for(const sp of M.suppressions){
  s += '<div class="card row"><span class="dot y"></span>'+
    '<span class="name">SUPPRESSED: '+esc(sp.finding)+'</span>'+
    '<span class="badge">until '+esc(sp.expiry)+'</span></div>';
}
s += '</div>';

app.appendChild(h(s));
</script>
</body>
</html>
"""


def render(model: dict) -> str:
    data = json.dumps(model, ensure_ascii=False).replace("</", "<\\/")
    return TEMPLATE.replace("__DATA__", data)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--findings", default="custos_findings.json")
    ap.add_argument("--fleet", default=os.path.join("custos", "fleet.yaml"))
    ap.add_argument("--suppressions", default="custos_suppressions.json")
    ap.add_argument("--fleet-findings",
                    default=os.path.join("custos", "fleet_findings.json"))
    ap.add_argument("--out", default=os.path.join("interface", "custos-dashboard.html"))
    args = ap.parse_args()

    model = build_model(load_json(args.findings), load_fleet(args.fleet),
                        load_json(args.suppressions),
                        load_json(args.fleet_findings))
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(render(model))
    print(f"CUSTOS dashboard: wrote {args.out} "
          f"({len(model['repos'])} repos, {len(model['detectors'])} detectors, "
          f"{model['totalRuns']} runs).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
