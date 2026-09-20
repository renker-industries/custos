# Concept: CUSTOS – a proof-based guardrail system for Claude Code

> Formerly the working title "Guardian". Inspired by the basic idea from the video (Code Guardian, Profimedia/Promptgeflüster), but technically independent, broken down to real Claude Code building blocks (skills, hooks, subagents, plugins) and developed further under its own name as part of the Renker Industries product family. Business aspects of the model (sales, community, prices) are deliberately excluded – this is about the technical architecture and about a standalone, publishable project.

## 1. Core idea in one sentence

An AI coding agent likes to claim that something is done, correct, or secure. CUSTOS ensures that it must **prove** this at every relevant point in the flow – with an executed command (linter, test run, static check, schema comparison), not with a sentence in the answer.

Everything else in the system is only the answer to the question: *At which point in the flow is which proof required, from whom, and what happens if it is missing?*

## 2. Branding & identity

**Name:** CUSTOS – Latin for "guardian, keeper, overseer". Short, pronounceable, free as a repo name on GitHub, no collision with a well-known developer brand.

**One-sentence pitch:** *CUSTOS is the guardian that turns every claim of your AI agent into a proof – before code, repo, or server may call themselves "done".*

**Tone:** sober, technical, no marketing speak. CUSTOS "sells" nothing, it proves. This should also be reflected in docs, README, and commit messages – short, factual sentences instead of superlatives.

**Naming conventions within the project** (so that it feels consistent when more people look in later):
- Core components in lowercase, technically named: `senior-dev`, `plan-reviewer`, `scope-guard` (see section 6) – no fancy names for individual building blocks.
- CUSTOS itself always written in caps (like a proper name/acronym character), never "Custos" or "custos" in prose – only lowercase in the file path/code (`custos/`, `custos.config.yaml`).
- Log and report files carry the prefix `custos_` (e.g. `custos_findings.json`), so that they remain uniquely identifiable in a repo with many other tools.

**Visual identity (basis for the interface, section 18, and a later logo):**

| Element | Definition |
|---|---|
| Base tone | Dark terminal theme: near-black background (`#0b0e11`), no pure white in text (`#d8dee9`) |
| Status colors | Green `#2ecc71` = proof provided/gate open, yellow `#f1c40f` = warning/council case, red `#e74c3c` = gate blocked/finding open, gray `#5c6370` = inactive/skipped |
| Typography | Monospace throughout (e.g. JetBrains Mono / Cascadia Code) – fits the "terminal, not a dashboard toy" character |
| Logo idea | A simple, geometric shield or seal symbol (no mascot, no animal) with a checkmark or exclamation mark as a status indicator that colors green/red – legible even as a 16×16 favicon |
| Acronym reading | C.U.S.T.O.S. can internally stand as a backronym for the four levels from section 4 (**C**heck, **U**nblock only on proof, **S**tatic, **T**est, **O**bserve, **S**top on finding) – optional, only if needed later for marketing/README, technically irrelevant |

## 3. Placement in the Renker infrastructure

CUSTOS is not an island project, but the **cross-cutting quality and security layer** placed over all Renker Industries projects (RenkerNet, RENCORA/LOKARA, BASI2, and everything else that comes along). Instead of maintaining separate lint/security rules for each project, you install CUSTOS once, and it applies to every repo registered in fleet mode (section 10).

Practical consequences for the structure:
- **A central configuration repo** (e.g. `renker-industries/custos-config`) contains the target standards (linter rules, thresholds, scope file) that all other repos reference – changes to the rules happen in one place, not in each project individually.
- **A GitHub organization instead of individual repos under the private account**, if not yet present: `renker-industries` as the org, CUSTOS as one of the first publicly visible repos in it – this makes clear on GitHub immediately that it is part of a coherent product family, not a loose individual project.
- **Shared README building blocks** (badge style, license note, contact/imprint) across all Renker repos, so that a visitor clicking from RenkerNet to CUSTOS sees a recognizable signature.

## 4. The four levels

Each of the four conceptual levels maps 1:1 to a Claude Code building block:

| Level | Question | Claude Code building block |
|---|---|---|
| **Stance** | How is a task approached at all? | A default subagent (`settings.json: "agent"`) with a senior-dev system prompt that opens every session |
| **Reflexes** | What must be checked at this point? | `UserPromptSubmit` and `PreToolUse` hooks that feed in context or enforce follow-up questions |
| **Mechanics** | What is technically prevented? | `PreToolUse`/`PostToolUse` hooks that run linters/static tools and block on exit code 2 |
| **Proofs** | Is it demonstrably correct? | `Stop`/`SubagentStop` hooks that enforce measurement scripts (tests, linter, typecheck) before the session may end |

This mapping is the common thread for the entire rest of the concept.

## 5. Packaging: a Claude Code plugin

CUSTOS is built as a single plugin, installed via a marketplace or `--plugin-dir`:

```
custos/
├── .claude-plugin/
│   └── plugin.json            # name: "custos"
├── settings.json              # sets the senior-dev agent as the default agent
├── agents/
│   ├── senior-dev.md          # default main agent ("Stance")
│   ├── plan-reviewer.md
│   ├── scope-guard.md
│   ├── root-cause.md          # "root-cause analysis" for debug mode
│   ├── council-advisor.md     # instantiated 5× for the LLM council
│   ├── council-chair.md
│   └── plain-text-translator.md  # "decision plain text"
├── skills/
│   ├── grill-me/SKILL.md      # asks follow-up questions before planning
│   ├── plan-mode/SKILL.md
│   ├── build-mode/SKILL.md
│   ├── debug-mode/SKILL.md
│   ├── cleanup-mode/SKILL.md
│   ├── data-analytics-mode/SKILL.md
│   └── fleet-mode/SKILL.md    # see section 10
├── hooks/
│   └── hooks.json             # all gates, see section 8
├── detectors/                 # static-analysis scripts, language-specific
│   ├── ai_slop_detector.py
│   ├── impact_analysis.py
│   ├── db_schema_guard.py
│   └── a11y_frontend_check.py
├── bin/                       # CLI wrappers that call the hooks
└── monitors/
    └── monitors.json          # multi-session and fleet orchestrator
```

`plugin.json` also references that there are **two variants**: one for Claude Code (this concept) and, separately, a functionally equivalent one for Codex (there via its own extension format, not a 1:1 port of the files, but the same logic).

## 6. Core roles (subagents)

| Subagent | Task | Model/effort |
|---|---|---|
| **Senior Developer** (default agent) | Opens every session, decides: trivial or requires planning, delegates onward | Standard |
| **Plan Reviewer** | Checks every finished plan against scope, security standards, completeness, before `ExitPlanMode` is allowed | High |
| **Scope Guard** | Runs alongside build mode, detects scope drift (the task grows larger than commissioned) | Standard |
| **Root-Cause Agent** | Debug mode: does not immediately discard the first plausible cause of an error, actively checks for alternative causes | High (X-High) |
| **Council Advisor ×5** | Consulted in parallel when static analysis and the model decision disagree | Medium |
| **Council Chair** | Summarizes the five advisor opinions and makes the binding decision | High |
| **Plain-Text Translator** | Translates technical follow-up questions/prompts into simple language understandable by non-developers | Low |

Each of these agents is a `.claude/agents/*.md` file with its own `description` field, via which the senior-dev main agent delegates to it automatically (via the `Agent` tool) – no manual switching needed.

## 7. Modes as skills, transitions as gates

The modes from the model (plan, build, debug, cleanup, data-analytics, plus the new fleet, see section 10) are implemented as skills whose *transitions* – not their content – are enforced by hooks. That is the decisive point: the modes themselves are only system prompts, the **gates between them** are the actual mechanism.

**Flow of a task:**

1. The `UserPromptSubmit` hook checks: is the task trivial (a one-line fix) or does it need a plan? If unclear, it loads the `grill-me` skill, which asks targeted follow-up questions before any planning.
2. The plan-mode skill creates the plan; the **plan-reviewer** subagent assesses it against a checklist (security, scope, DB impact, affected modules).
3. Only after approval may `ExitPlanMode` be called – a `PreToolUse` hook on exactly this tool is the technical gate for it.
4. Build mode: the **scope-guard** compares every file change against the approved plan scope. For DB changes, `db_schema_guard.py` (via `PreToolUse` on `Write`/`Edit` of migration files) enforces a comparison against the real, current database schema – no invented fields.
5. After every code change, `PostToolUse` runs → `ai_slop_detector.py` (patterns such as unnecessary abstractions, duplicate code, generic variable names, superfluous comments) as well as language-specific static tools (e.g. ESLint/TypeScript, Ruff/mypy, PHPStan).
6. At the end of a work step, the `Stop` hook demands a **proof**: test run, linter result, typecheck – without a green exit code, no session end. Additionally, the internal to-do is reconciled with the plan again.

Debug mode is a special case: the root-cause agent does not stop at the first cause found, but actively checks via checklist whether a more plausible second cause exists before a fix is proposed.

Data-analytics mode adds an additional proof obligation: before any statement about data, it is checked how a value was computed and whether it is consistent from multiple angles – analogous to the code proof, only for numbers instead of functions.

## 8. Gates in detail (hook mapping)

| Gate | Hook event | Matcher | Action on violation |
|---|---|---|---|
| Trivial barrier | `UserPromptSubmit` | – | Injects `additionalContext`: "Plan needed? [yes/no]" |
| Plan approval | `PreToolUse` | `ExitPlanMode` | Exit 2 as long as the plan reviewer has not agreed |
| Scope guard | `PreToolUse` | `Write\|Edit` | Warning/block if the file is outside the plan scope |
| DB schema guard | `PreToolUse` | `Write\|Edit` on migration/schema files | Block if referenced fields do not exist in the real schema |
| AI-slop detector | `PostToolUse` | `Write\|Edit` | `additionalContext` with findings; exit 2 above a threshold |
| Static analysis | `PostToolUse` | `Write\|Edit` | Linter/typecheck per language, exit 2 on errors |
| Impact analysis | `PostToolUse` | `Write\|Edit` | Searches callers of the changed function, warns about unadjusted spots |
| A11y/frontend check | `PostToolUse` | `*.tsx\|*.jsx\|*.vue\|*.html` | Contrast, focus order, ARIA basics |
| Proof obligation | `Stop` | – | Exit 2 until a test run/linter is documented as successful |
| Regression guard | `SubagentStop` | – | Compares before/after test results, blocks on new failures |

All detectors are standalone scripts under `detectors/`; the hooks only call them – so they stay independently testable and swappable per language.

## 9. Static analysis as a second, independent authority

Important about the model: the check does not only run "the AI looks at the code again", but via real static-analysis libraries that judge independently of the language model:

- TypeScript/JavaScript: ESLint + `tsc --noEmit`
- Python: Ruff + mypy (also for CUSTOS's own scripts – self-application)
- PHP: PHPStan
- Frontend/accessibility: axe-core or a comparable CLI tool, contrast check against WCAG values

On a contradiction between a static finding and the model's assessment, static analysis does not automatically decide – this is where the **code council** (section 6) comes in: five advisor instances assess the case independently, the chair agent makes the decision and documents the rationale in the log.

## 10. Fleet mode: check and edit other local repos & GitHub

CUSTOS should not be limited to the project it is currently running in, but on request cover **the entire own software fleet**: other Git repos on the PC, all repos in the GitHub account/org, and in perspective also servers/Pis (their config repos or deployed code).

**10.1 Build a repo inventory**
- Local: a discovery run searches configured root directories (e.g. `~/Projects`, `~/Documents`, everything under defined folders) for `.git` directories and enters findings in `custos/fleet.yaml`.
- GitHub: `gh repo list <account-or-org> --json name,visibility,defaultBranch` builds the list of all remote repos; private and public are captured, but marked separately.
- Each entry gets a status: `actively monitored`, `inventoried only` (not yet released), `ignored` (deliberately excluded, e.g. forks of others' projects).

**10.2 Check per repo**
For each repo marked "actively monitored", CUSTOS applies the same gates as in its own project (static analysis, AI-slop detector, secret scan from section 15), but **read-only by default**: first only a findings report is generated, no automatic change. Automatic editing (auto-fix commits, dependency updates) is an explicit opt-in per repo in `fleet.yaml` – never a global switch, so that nothing is accidentally written into a sensitive/foreign repo.

**10.3 Editing, when released**
For released repos, CUSTOS can propose fixes on its own: small, clearly delimited changes (e.g. an outdated dependency, a missing linter fix) directly as a branch + pull request instead of a direct push to the main branch – so every automatic change stays reviewable and reversible, even if no one looks promptly.

**10.4 Central dashboard**
The results of all repos converge into a shared report (the basis for the interface, section 18): an overview of "repo → last scan → open findings → zero-tolerance status" instead of a separate report per repo.

**10.5 Security barrier**
Fleet mode uses the same scope-file logic as section 15.1: only repos explicitly listed are touched. No automatic "everything I find on GitHub" without this allowlist – otherwise a misconfigured access token is enough to accidentally write into foreign or public third-party repos.

## 11. Multi-session orchestration

Goal: when several Claude Code sessions are open on the same project (or in several fleet repos in parallel), tasks should be distributed in a coordinated rather than colliding way. Technically realistic via:

1. **Isolation**: every session/subagent writing in parallel runs in its own Git worktree (`Agent` tool with `isolation:worktree`) – no file collisions.
2. **Coordination**: a `monitors/monitors.json` process of the plugin keeps a shared task-queue file (or a small local MCP server) up to date, which all sessions read/write.
3. **Assignment**: the senior-dev agent checks the queue at session start (`SessionStart` hook) and takes only free tasks; completed tasks are marked with a proof reference (test-run ID).
4. **Merging**: merges run via normal Git workflows (a branch per worktree, PR/merge after the proof gate passes).

This is not a magical built-in orchestrator, but a deliberate combination of existing Claude Code primitives (worktree isolation, hooks, a lean coordination process).

## 12. Self-qualification of the system

So that CUSTOS not only claims to be good but also proves it for itself:

- **Reference codebases**: a set of real, differently sized projects serves as a regression test bed. Every new CUSTOS version runs test-wise against these projects (a multi-hour run) before it is released.
- **Session log**: after every session a central log is created that evaluates whether CUSTOS itself made mistakes or improved – the basis for daily/weekly releases.
- **Metrics**: error rate per release, share of detected vs. missed regressions, time to the first valid proof per task.

## 13. Effort management

Not every module needs the same depth of thought. Proposal for model/effort assignment via the `model` field of the respective subagent file:

| Module | Effort |
|---|---|
| Root-Cause Agent (debug) | High |
| Plan Reviewer | High |
| Council Chair | High |
| Senior Developer (triage) | Standard |
| Scope Guard, static wrapper | Low/Standard |
| Plain-Text Translator | Low |

This keeps token costs in everyday operation in check, without saving on the truly difficult decisions (root cause, plan approval, council decision).

## 14. Compatibility

- **Claude Code**: as above, a native plugin.
- **Codex**: a separate, functionally equivalent implementation via its own extension/config format – same gate logic, different technical shell.
- **Windows**: write hooks/detector scripts platform-independently in Python/Node instead of Bash-only, so that no WSL requirement arises.

## 15. Security & pentest module (GitHub, servers, Raspberry Pis, PC)

Short version: yes, this can be cleanly integrated into CUSTOS – as its own **security mode** that follows the same proof logic as the rest of the system (not "is secure" as a statement, but a scan report with a timestamp in the same findings log) and that is applied automatically to all registered repos via fleet mode (section 10). One ground rule is non-negotiable, see 15.1.

### 15.1 Scope file as a prerequisite for everything active

Before any active scan runs, CUSTOS needs a fixed **asset allowlist** (`custos/scope.yaml`) with exactly the IPs/hostnames/repos that may be checked – the same list that fleet mode uses for repo release. Every active check (port scan, web scan) validates against this list first and otherwise aborts. Reason: even in your own home network, without this barrier, foreign devices quickly end up in the scan range (others' routers/IoT devices, cloud IPs where the provider requires prior notice of active scans) – that is the difference between "hardening your own systems" and a real incident.

### 15.2 GitHub hygiene

| Check | Tool |
|---|---|
| Secrets in commits/history | gitleaks or trufflehog, additionally enable GitHub secret scanning + push protection |
| Dependency vulnerabilities | Dependabot / OSV scanner |
| Code vulnerabilities (SAST) | CodeQL or Semgrep |
| Branch protection, repo visibility, member rights | Query via the GitHub API (`gh` CLI) against a target configuration |

For the Claude-Code-specific part of this, there is already a finished plugin in the catalog that fits CUSTOS directly: **"Security Guidance"** – automatically checks every code change via hook (incl. `PostToolUse`, `Stop`) for injection, XSS, SSRF, hardcoded secrets, and more than 20 other vulnerability classes. This can be included as an additional component instead of building this part entirely yourself.

### 15.3 Servers, Raspberry Pis, PC – passive hardening (uncritical, arbitrarily automatable)

| Check | Tool/approach |
|---|---|
| Hardening score, misconfigurations | Lynis |
| Rootkits/known malware signatures | rkhunter, chkrootkit |
| Open services, unnecessarily running processes | `systemctl list-units`, `ss -tulpn` |
| SSH configuration (password login disabled? key-only? Fail2ban active?) | Comparison against target values |
| Firewall rules | ufw/iptables comparison |
| Patch level | unattended-upgrades status, `apt list --upgradable` |
| Windows PC | Defender status, `netstat`, autostart entries, `winget upgrade --all` as a dry run |

This runs entirely locally and is pure observation, not an attack – it can be automated regularly without concern, e.g. via `monitors/monitors.json` or a cron job on each Pi/server that writes its result into the same log/findings system as the code checks.

### 15.4 Active checking from outside – only within the scope list

| Check | Tool |
|---|---|
| Which ports are actually reachable from outside | Nmap against your own, listed IPs |
| Typical web vulnerabilities of your own services | OWASP ZAP or Nikto |
| DAST against your own web applications with prioritized fix suggestions | For this too there is already a fitting plugin in the catalog: **StackHawk HawkScan** – automatically generates a scan configuration, runs the scan, and turns findings directly into prioritized tasks for the coding agent |

Two points to clarify beforehand: some cloud providers (Hetzner, AWS, Azure, …) require prior notice for active scans, even against your own instances. And a low-powered Raspberry Pi can actually buckle under a too-aggressive scan – hence a defined maintenance window and a "safe mode" (moderate scan intensity, no brute-forcing) instead of continuous operation.

## 16. Zero-tolerance policy: how strictly "0 vulnerabilities" is enforceable

An honest framing first: **"0 known vulnerabilities detectable by the deployed checks"** is technically enforceable and exactly the goal of this section. **"0 vulnerabilities at all"** cannot be promised by any system – a zero-day is by definition a gap no one knows yet, and no scanner finds what does not yet exist as a pattern/CVE/signature. CUSTOS should therefore consistently enforce the first, honest goal instead of claiming the second, untenable one.

So that the first goal does not become lip service but actually takes effect:

| Lever | Without zero-tolerance (default) | With zero-tolerance |
|---|---|---|
| Gate threshold | Blocks only from "high"/"critical" | Blocks from any finding, including "low"/"info" |
| Behavior on finding | Warning, work continues | Fail-closed: exit 2, session/deploy stops |
| Number of scanners per category | One tool per category | Several independent tools in parallel (each tool has its own blind spots – defense in depth) |
| Rescan trigger | Only on code change | Additionally time-triggered (e.g. daily), because new CVEs become known for already-merged code over time |
| Exceptions/suppressions | Can be set by the model itself | Only via the code council (section 6), with a rationale and an expiry date – never a silent self-approval |
| Existing code | "It's always been this way" is accepted | New findings in old code count just like in new code, no grandfathering |

The price for this is more friction: builds break even on small findings, and more cases land at the council instead of passing automatically. That is the deliberate trade-off that turns a "mostly clean" system into an "as bare as technically possible" system.

## 17. GitHub publication: repo setup

So that the repo looks serious from the start and not like a half-finished side hack:

- **Repo name:** `custos` under the newly created `renker-industries` org (section 3), not under the private account. **Decided.**
- **README skeleton:** the one-sentence pitch at the top (section 2), below it a brief "What it does" (the four levels from section 4 as a concise list), an installation step, a screenshot/GIF of the interface (section 18), a license section.
- **Badges:** build status (own CI that applies the CUSTOS gates to itself – dogfooding), MIT license badge, optionally a "0 open findings" badge fed from the latest `custos_findings.json` instead of a claim.
- **License: MIT.** **Decided** – maximally open, the simplest choice for visibility/reputation. The `LICENSE` placeholder in the repo is replaced by the standard MIT text (copyright line: year + Renker Industries or the author's name).
- **CI dogfooding:** a GitHub Actions workflow that on every push runs the same gates CUSTOS enforces for other projects – the best advertising is a repo that visibly follows its own rules.
- **.github/ folder:** issue templates, possibly CONTRIBUTING.md, if the community idea from the model video is picked up later after all (optional, not part of the MVP).

## 18. Interface

Fixed style: a dark terminal dashboard (colors/typography see section 2). Core views:

1. **Overview/fleet dashboard**: a list of all monitored repos (section 10) with a status light, last scan time, number of open findings.
2. **Repo detail**: the gates in detail (section 8) as rows with status; a click opens the associated proof (test output/linter log).
3. **Security log**: a chronological list of all security scans (section 15) with a severity filter.
4. **Council cases**: open or decided disputes between static analysis and the model assessment, incl. the chair agent's rationale.

**Design reference:** [CUSTOS Dashboard](https://claude.ai/design/p/e5676802-f116-4b7a-bd09-06dc8c891cc8?file=CUSTOS+Dashboard.dc.html&via=share) – a professionally worked-out version of the four views in Claude Design, the binding basis for the later interface implementation (roadmap phase 10, section 19).

## 19. Implementation roadmap

1. **MVP**: senior-dev default agent + plan reviewer + a `Stop` hook that enforces a test run. With this, the core statement ("proof instead of claim") is already tangible.
2. **Static level**: add the AI-slop detector + language-specific linter/typecheck hooks.
3. **Branding & repo skeleton**: create `renker-industries/custos`, README/license/CI dogfooding (section 17) – before more functionality is added, so that the repo is in good shape from the start.
4. **Special modes**: debug mode with the root-cause agent, data-analytics mode.
5. **Fleet mode**: repo discovery locally + GitHub, initially read-only (section 10.1–10.2).
6. **Security mode**: scope file + passive hardening checks first (uncritical), active scans only afterwards and only against the scope list.
7. **Fleet editing**: auto-fix PRs for released repos (section 10.3).
8. **Council**: the five-advisor mechanism for disputed cases.
9. **Multi-session**: worktree isolation + task-queue coordination.
10. **Interface**: the dashboard from section 18 as a standalone application, fed from the `custos_findings.json` reports.
11. **Self-qualification**: reference test suite, session logs, release metrics.

## 20. Open points

Decided (2026-09-15): license = MIT (section 17), the GitHub org `renker-industries` is created new (section 3), fleet mode starts with **only `custos` itself** as "actively monitored" (section 10.2) – all other repos remain inventoried only for now, until released individually.

Decided (2026-09-15): fleet discovery searches `CascadeProjects` and `Documents` as root directories (section 10.1).

Still open:

- `scope.yaml` deliberately stays empty (no active scan) until real hosts/IPs are entered – no deadline for it.
- When and which second repo (presumably RenkerNet or RENCORA/LOKARA) is released next for fleet mode?
- How large should the reference test suite for regression runs be initially, and from which of your own projects is it fed?
- Should the task-queue mechanism run via a file in the repo or a local MCP server?
- Which IPs/hostnames/repos concretely belong in the scope file (section 15.1) before any active scan is enabled?

---

*Note on the technical details:* The mapping to hook events, skill/agent format, and plugin structure is based on the current Claude Code documentation (as of September 2026, code.claude.com/docs). Before building, a brief comparison with `/docs/en/hooks`, `/docs/en/plugins`, and `/docs/en/permissions` is worthwhile, since field names can change in newer versions.
