# Konzept: CUSTOS – ein Beweis-basiertes Guardrail-System für Claude Code

> Vormals Arbeitstitel "Guardian". Angelehnt an die Grundidee aus dem Video (Code Guardian, Profimedia/Promptgeflüster), aber technisch eigenständig auf reale Claude-Code-Bausteine (Skills, Hooks, Subagents, Plugins) heruntergebrochen und unter eigenem Namen als Teil der Renker-Industries-Produktfamilie weiterentwickelt. Business-Aspekte des Vorbilds (Verkauf, Community, Preise) sind bewusst ausgeklammert – es geht um die technische Architektur und um ein eigenständiges, veröffentlichungsfähiges Projekt.

## 1. Kernidee in einem Satz

Ein KI-Coding-Agent behauptet gerne, dass etwas fertig, korrekt oder sicher ist. CUSTOS sorgt dafür, dass er das an jeder relevanten Stelle im Ablauf **belegen muss** – mit einem ausgeführten Kommando (Linter, Testlauf, Statik-Check, Schema-Abgleich), nicht mit einem Satz in der Antwort.

Alles Weitere im System ist nur die Antwort auf die Frage: *An welcher Stelle im Ablauf wird welcher Beleg verlangt, von wem, und was passiert, wenn er fehlt?*

## 2. Branding & Identität

**Name:** CUSTOS – lateinisch für „Wächter, Hüter, Aufseher". Kurz, sprechbar, auf GitHub als Repo-Name frei, keine Kollision mit einer bekannten Entwickler-Marke.

**Ein-Satz-Pitch:** *CUSTOS ist der Wächter, der jede Behauptung deines KI-Agenten in einen Beweis verwandelt – bevor Code, Repo oder Server sich „fertig" nennen dürfen.*

**Tonalität:** nüchtern, technisch, kein Marketing-Sprech. CUSTOS "verkauft" nichts, es belegt. Das sollte sich auch in Doku, README und Commit-Messages widerspiegeln – kurze, faktische Sätze statt Superlative.

**Naming-Konventionen innerhalb des Projekts** (damit es sich konsistent anfühlt, wenn später mehr Leute reinschauen):
- Kernkomponenten in Kleinbuchstaben, technisch benannt: `senior-dev`, `plan-reviewer`, `scope-guard` (siehe Abschnitt 6) – keine Fantasienamen für einzelne Bausteine.
- CUSTOS selbst immer in Versalien geschrieben (wie ein Eigenname/Akronym-Charakter), nie „Custos" oder „custos" in Fließtext – nur im Dateipfad/Code klein (`custos/`, `custos.config.yaml`).
- Log- und Report-Dateien tragen das Präfix `custos_` (z. B. `custos_findings.json`), damit sie in einem Repo mit vielen anderen Tools eindeutig zuordenbar bleiben.

**Visuelle Identität (Basis für das Interface, Abschnitt 18, und ein späteres Logo):**

| Element | Festlegung |
|---|---|
| Grundton | Dunkles Terminal-Theme: nahezu schwarzer Hintergrund (`#0b0e11`), keine reinen Weißtöne im Text (`#d8dee9`) |
| Statusfarben | Grün `#2ecc71` = Beleg erbracht/Gate offen, Gelb `#f1c40f` = Warnung/Council-Fall, Rot `#e74c3c` = Gate blockiert/Fund offen, Grau `#5c6370` = inaktiv/übersprungen |
| Typografie | Monospace durchgehend (z. B. JetBrains Mono / Cascadia Code) – passt zum "Terminal, kein Dashboard-Spielzeug"-Charakter |
| Logo-Idee | Ein einfaches, geometrisches Schild- oder Siegel-Symbol (kein Maskottchen, kein Tier) mit einem Häkchen oder Ausrufezeichen als Statusindikator, das sich in Grün/Rot einfärbt – lesbar auch als 16×16-Favicon |
| Akronym-Lesart | C.U.S.T.O.S. kann intern als Backronym für die vier Ebenen aus Abschnitt 4 stehen (**C**heck, **U**nblock nur bei Beleg, **S**tatik, **T**est, **O**bservieren, **S**topp bei Fund) – optional, nur falls es später fürs Marketing/README gebraucht wird, technisch irrelevant

## 3. Einordnung in die Renker-Infrastruktur

CUSTOS ist kein Insel-Projekt, sondern die **querschnittliche Qualitäts- und Sicherheitsschicht**, die über alle Renker-Industries-Projekte gelegt wird (RenkerNet, RENCORA/LOKARA, BASI2 und alles, was noch dazukommt). Statt für jedes Projekt eigene Lint-/Security-Regeln zu pflegen, installiert man CUSTOS einmal, und es gilt für jedes Repo, das im Fleet-Modus (Abschnitt 10) registriert ist.

Praktische Konsequenzen für die Struktur:
- **Ein zentrales Konfigurations-Repo** (z. B. `renker-industries/custos-config`) enthält die Soll-Standards (Linter-Regeln, Schwellwerte, Scope-Datei), die alle anderen Repos referenzieren – Änderungen an den Regeln passieren an einer Stelle, nicht in jedem Projekt einzeln.
- **GitHub-Organisation statt Einzel-Repos unter dem privaten Account**, falls noch nicht vorhanden: `renker-industries` als Org, CUSTOS als eines der ersten öffentlich sichtbaren Repos darin – das macht auf GitHub sofort klar, dass es Teil einer zusammenhängenden Produktfamilie ist, nicht ein loses Einzelprojekt.
- **Gemeinsame README-Bausteine** (Badge-Stil, Lizenz-Hinweis, Kontakt/Impressum) über alle Renker-Repos hinweg, damit ein Besucher, der von RenkerNet zu CUSTOS klickt, eine wiedererkennbare Handschrift sieht.

## 4. Die vier Ebenen

Jede der vier gedanklichen Ebenen lässt sich 1:1 auf einen Claude-Code-Baustein abbilden:

| Ebene | Frage | Claude-Code-Baustein |
|---|---|---|
| **Haltung** | Wie wird eine Aufgabe überhaupt angefasst? | Ein Default-Subagent (`settings.json: "agent"`) mit Senior-Dev-Systemprompt, der jede Session eröffnet |
| **Reflexe** | Was muss an dieser Stelle geprüft werden? | `UserPromptSubmit`- und `PreToolUse`-Hooks, die Kontext einspeisen bzw. Rückfragen erzwingen |
| **Mechanik** | Was wird technisch verhindert? | `PreToolUse`/`PostToolUse`-Hooks, die Linter/Statik-Tools ausführen und bei Exit-Code 2 blocken |
| **Beweise** | Ist es nachweislich korrekt? | `Stop`/`SubagentStop`-Hooks, die Messskripte (Tests, Linter, Typecheck) erzwingen, bevor die Session enden darf |

Diese Zuordnung ist der rote Faden für das gesamte restliche Konzept.

## 5. Paketierung: ein Claude-Code-Plugin

CUSTOS wird als ein einziges Plugin gebaut, das per Marketplace oder `--plugin-dir` installiert wird:

```
custos/
├── .claude-plugin/
│   └── plugin.json            # name: "custos"
├── settings.json              # setzt den Senior-Dev-Agent als Default-Agent
├── agents/
│   ├── senior-dev.md          # Default-Hauptagent ("Haltung")
│   ├── plan-reviewer.md
│   ├── scope-guard.md
│   ├── root-cause.md          # "Kausalanalyse" für den Debug-Modus
│   ├── council-advisor.md     # 5x instanziiert für das LLM-Council
│   ├── council-chair.md
│   └── plain-text-translator.md  # "Entscheidungsklartext"
├── skills/
│   ├── grill-me/SKILL.md      # stellt Rückfragen vor der Planung
│   ├── plan-mode/SKILL.md
│   ├── build-mode/SKILL.md
│   ├── debug-mode/SKILL.md
│   ├── cleanup-mode/SKILL.md
│   ├── data-analytics-mode/SKILL.md
│   └── fleet-mode/SKILL.md    # siehe Abschnitt 10
├── hooks/
│   └── hooks.json             # alle Gates, siehe Abschnitt 8
├── detectors/                 # Statik-Analyse-Skripte, sprachspezifisch
│   ├── ai_slop_detector.py
│   ├── impact_analysis.py
│   ├── db_schema_guard.py
│   └── a11y_frontend_check.py
├── bin/                       # CLI-Wrapper, die die Hooks aufrufen
└── monitors/
    └── monitors.json          # Multi-Session- und Fleet-Orchestrator
```

`plugin.json` referenziert außerdem, dass es **zwei Varianten** gibt: eine für Claude Code (dieses Konzept) und separat eine funktional äquivalente für Codex (dort über dessen eigenes Extension-Format, keine 1:1-Portierung der Dateien, aber gleiche Logik).

## 6. Kernrollen (Subagents)

| Subagent | Aufgabe | Modell/Effort |
|---|---|---|
| **Senior Developer** (Default-Agent) | Öffnet jede Session, entscheidet: trivial oder planungspflichtig, delegiert weiter | Standard |
| **Plan Reviewer** | Prüft jeden fertigen Plan gegen Scope, Sicherheitsstandards, Vollständigkeit, bevor `ExitPlanMode` erlaubt wird | Hoch |
| **Scope Guard** | Läuft während Build-Mode mit, erkennt Scope Drift (Aufgabe wird größer als beauftragt) | Standard |
| **Root-Cause-Agent** | Debug-Modus: verwirft die erste plausible Fehlerursache nicht sofort, prüft aktiv nach Alternativursachen | Hoch (X-High) |
| **Council-Advisor ×5** | Werden bei Uneinigkeit zwischen Statik-Analyse und Modellentscheidung parallel befragt | Mittel |
| **Council-Chair** | Fasst die fünf Advisor-Meinungen zusammen und trifft die verbindliche Entscheidung | Hoch |
| **Plain-Text-Translator** | Übersetzt technische Rückfragen/Prompts in einfache, für Nicht-Entwickler verständliche Sprache | Niedrig |

Jeder dieser Agenten ist eine `.claude/agents/*.md`-Datei mit eigenem `description`-Feld, über das der Senior-Dev-Hauptagent automatisch dorthin delegiert (via `Agent`-Tool) – keine manuelle Umschaltung nötig.

## 7. Modi als Skills, Übergänge als Gates

Die Modi aus dem Vorbild (Plan, Build, Debug, Cleanup, Data-Analytics, plus neu Fleet, siehe Abschnitt 10) werden als Skills umgesetzt, deren *Übergänge* – nicht ihr Inhalt – von Hooks erzwungen werden. Das ist der entscheidende Punkt: die Modi selbst sind nur Systemprompts, die **Gates dazwischen** sind der eigentliche Mechanismus.

**Ablauf einer Aufgabe:**

1. `UserPromptSubmit`-Hook prüft: ist die Aufgabe trivial (Ein-Zeilen-Fix) oder braucht sie einen Plan? Bei Unklarheit lädt er die `grill-me`-Skill, die gezielte Rückfragen stellt, bevor überhaupt geplant wird.
2. Plan-Mode-Skill erstellt den Plan; der **Plan-Reviewer**-Subagent bewertet ihn gegen eine Checkliste (Sicherheit, Umfang, DB-Auswirkungen, betroffene Module).
3. Erst nach Freigabe darf `ExitPlanMode` aufgerufen werden – ein `PreToolUse`-Hook auf genau dieses Tool ist das technische Gate dafür.
4. Build-Mode: Der **Scope-Guard** vergleicht jede Dateiänderung gegen den freigegebenen Plan-Umfang. Bei DB-Änderungen erzwingt `db_schema_guard.py` (per `PreToolUse` auf `Write`/`Edit` an Migrationsdateien) einen Abgleich gegen das echte, aktuelle Datenbankschema – keine erfundenen Felder.
5. Nach jeder Code-Änderung läuft `PostToolUse` → `ai_slop_detector.py` (Muster wie unnötige Abstraktionen, Duplicate Code, generische Variablennamen, überflüssige Kommentare) sowie sprachspezifische Statik-Tools (z. B. ESLint/TypeScript, Ruff/mypy, PHPStan).
6. Am Ende eines Arbeitsschritts verlangt der `Stop`-Hook einen **Beleg**: Testlauf, Linter-Ergebnis, Typecheck – ohne grünen Exit-Code kein Sessionende. Zusätzlich wird das interne To-Do erneut mit dem Plan abgeglichen.

Debug-Mode ist ein Sonderfall: Der Root-Cause-Agent stoppt nicht bei der ersten gefundenen Fehlerursache, sondern prüft per Checkliste aktiv, ob eine plausiblere zweite Ursache existiert, bevor ein Fix vorgeschlagen wird.

Data-Analytics-Mode fügt eine zusätzliche Beweispflicht hinzu: Vor jeder Aussage über Daten wird geprüft, wie ein Wert berechnet wurde und ob er aus mehreren Blickwinkeln konsistent ist – analog zum Code-Beweis, nur für Zahlen statt für Funktionen.

## 8. Gates im Detail (Hook-Zuordnung)

| Gate | Hook-Event | Matcher | Aktion bei Verstoß |
|---|---|---|---|
| Trivial-Schranke | `UserPromptSubmit` | – | Injiziert `additionalContext`: "Plan nötig? [ja/nein]" |
| Plan-Freigabe | `PreToolUse` | `ExitPlanMode` | Exit 2, solange Plan-Reviewer nicht zugestimmt hat |
| Scope-Wächter | `PreToolUse` | `Write\|Edit` | Warnung/Block, wenn Datei außerhalb des Plan-Scopes liegt |
| DB-Schema-Guard | `PreToolUse` | `Write\|Edit` auf Migrations-/Schemadateien | Block, wenn referenzierte Felder nicht im echten Schema existieren |
| AI-Slop-Detektor | `PostToolUse` | `Write\|Edit` | `additionalContext` mit Fundstellen; ab Schwellwert Exit 2 |
| Statik-Analyse | `PostToolUse` | `Write\|Edit` | Linter/Typecheck pro Sprache, Exit 2 bei Fehlern |
| Impact-Analyse | `PostToolUse` | `Write\|Edit` | Sucht Aufrufer der geänderten Funktion, warnt bei nicht angepassten Stellen |
| A11y/Frontend-Check | `PostToolUse` | `*.tsx\|*.jsx\|*.vue\|*.html` | Kontrast, Fokus-Reihenfolge, ARIA-Basics |
| Beweis-Pflicht | `Stop` | – | Exit 2, bis Testlauf/Linter mit Erfolg dokumentiert ist |
| Regressions-Wächter | `SubagentStop` | – | Vergleicht Vorher/Nachher-Testergebnisse, blockt bei neuen Fehlschlägen |

Alle Detektoren sind eigenständige Skripte unter `detectors/`, die Hooks rufen sie nur auf – so bleiben sie unabhängig testbar und pro Sprache austauschbar.

## 9. Statische Analyse als zweite, unabhängige Instanz

Wichtig am Vorbild: die Prüfung läuft nicht nur "die KI schaut sich den Code nochmal an", sondern über echte statische Analyse-Bibliotheken, die unabhängig vom Sprachmodell urteilen:

- TypeScript/JavaScript: ESLint + `tsc --noEmit`
- Python: Ruff + mypy (auch für die CUSTOS-eigenen Skripte – Selbstanwendung)
- PHP: PHPStan
- Frontend/Accessibility: axe-core oder vergleichbares CLI-Tool, Kontrast-Check gegen WCAG-Werte

Bei Widerspruch zwischen Statik-Befund und Modell-Einschätzung entscheidet nicht automatisch die Statik – hier kommt das **Code-Council** (Abschnitt 6) ins Spiel: fünf Advisor-Instanzen bewerten den Fall unabhängig, der Chair-Agent trifft die Entscheidung und dokumentiert die Begründung im Log.

## 10. Fleet-Modus: andere lokale Repos & GitHub prüfen und bearbeiten

CUSTOS soll sich nicht auf das Projekt beschränken, in dem es gerade läuft, sondern auf Wunsch **die gesamte eigene Software-Flotte** abdecken: andere Git-Repos auf dem PC, alle Repos im GitHub-Account/der Org, perspektivisch auch Server/Pis (deren Konfigurationsrepos bzw. deployter Code).

**10.1 Repo-Inventar aufbauen**
- Lokal: ein Discovery-Lauf durchsucht konfigurierte Wurzelverzeichnisse (z. B. `~/Projects`, `~/Documents`, alles unter definierten Ordnern) nach `.git`-Verzeichnissen und trägt Fundstellen in `custos/fleet.yaml` ein.
- GitHub: `gh repo list <account-oder-org> --json name,visibility,defaultBranch` baut die Liste aller Remote-Repos; private wie öffentliche werden erfasst, aber getrennt markiert.
- Jeder Eintrag bekommt einen Status: `aktiv überwacht`, `nur inventarisiert` (noch nicht freigegeben), `ignoriert` (bewusst ausgeschlossen, z. B. Forks fremder Projekte).

**10.2 Prüfung pro Repo**
Für jedes als „aktiv überwacht" markierte Repo wendet CUSTOS dieselben Gates an wie im eigenen Projekt (Statik-Analyse, AI-Slop-Detektor, Secret-Scan aus Abschnitt 15), aber **read-only per Default**: es wird zuerst nur ein Befund-Report erzeugt, keine automatische Änderung. Automatisches Bearbeiten (Auto-Fix-Commits, Dependency-Updates) ist ein expliziter Opt-in pro Repo in `fleet.yaml` – nie ein globaler Schalter, damit nicht versehentlich in ein sensibles/fremdes Repo geschrieben wird.

**10.3 Bearbeitung, wenn freigegeben**
Bei freigegebenen Repos kann CUSTOS eigenständig Fixes vorschlagen: kleine, klar abgegrenzte Änderungen (z. B. veraltete Dependency, fehlender Linter-Fix) direkt als Branch + Pull Request statt als Direct-Push auf den Hauptbranch – so bleibt jede automatische Änderung überprüfbar und rückgängig machbar, auch wenn niemand zeitnah hinschaut.

**10.4 Zentrales Dashboard**
Die Ergebnisse aller Repos laufen in einem gemeinsamen Report zusammen (Basis für das Interface, Abschnitt 18): eine Übersicht „Repo → letzter Scan → offene Funde → Zero-Tolerance-Status" statt eines Reports pro Repo einzeln.

**10.5 Sicherheitsschranke**
Der Fleet-Modus nutzt dieselbe Scope-Datei-Logik wie Abschnitt 15.1: nur Repos, die explizit eingetragen sind, werden angefasst. Kein automatisches „alles was ich auf GitHub finde" ohne diese Freigabeliste – sonst reicht ein falsch konfigurierter Zugriffstoken, um versehentlich in fremden oder öffentlichen Repos Dritter zu schreiben.

## 11. Multi-Session-Orchestrierung

Ziel: Wenn mehrere Claude-Code-Sessions am selben Projekt (oder in mehreren Fleet-Repos parallel) offen sind, sollen Aufgaben koordiniert statt kollidierend verteilt werden. Technisch realistisch umsetzbar über:

1. **Isolation**: Jede Session/jeder Subagent, der parallel schreibt, läuft in einem eigenen Git-Worktree (`Agent`-Tool mit `isolation:worktree`) – keine Datei-Kollisionen.
2. **Koordination**: Ein `monitors/monitors.json`-Prozess des Plugins hält eine gemeinsame Task-Queue-Datei (oder einen kleinen lokalen MCP-Server) aktuell, den alle Sessions lesen/schreiben.
3. **Zuteilung**: Der Senior-Dev-Agent prüft beim Sessionstart (`SessionStart`-Hook) die Queue und übernimmt nur freie Aufgaben; erledigte Aufgaben werden mit Beweis-Verweis (Testlauf-ID) markiert.
4. **Zusammenführung**: Merges laufen über normale Git-Workflows (Branch pro Worktree, PR/Merge nach bestandenem Beweis-Gate).

Das ist kein magischer eingebauter Orchestrator, sondern eine bewusste Kombination aus vorhandenen Claude-Code-Primitiven (Worktree-Isolation, Hooks, ein schlanker Koordinationsprozess).

## 12. Selbstqualifizierung des Systems

Damit CUSTOS nicht nur behauptet, gut zu sein, sondern es auch für sich selbst beweist:

- **Referenz-Codebases**: Ein Satz realer, unterschiedlich großer Projekte dient als Regressionstestbett. Jede neue CUSTOS-Version läuft testweise gegen diese Projekte (mehrstündiger Lauf), bevor sie freigegeben wird.
- **Session-Log**: Nach jeder Session entsteht ein zentrales Log, das auswertet, ob CUSTOS selbst Fehler gemacht oder sich verbessert hat – Grundlage für tägliche/wöchentliche Releases.
- **Metriken**: Fehlerquote pro Release, Anteil erkannter vs. übersehener Regressionen, Zeit bis zum ersten validen Beweis pro Aufgabe.

## 13. Effort-Management

Nicht jedes Modul braucht die gleiche Denktiefe. Vorschlag zur Modell-/Effort-Zuordnung über das `model`-Feld der jeweiligen Subagent-Datei:

| Modul | Effort |
|---|---|
| Root-Cause-Agent (Debug) | Hoch |
| Plan-Reviewer | Hoch |
| Council-Chair | Hoch |
| Senior Developer (Triage) | Standard |
| Scope-Guard, Statik-Wrapper | Niedrig/Standard |
| Plain-Text-Translator | Niedrig |

Das hält die Token-Kosten im Alltagsbetrieb im Rahmen, ohne bei den wirklich schwierigen Entscheidungen (Root Cause, Plan-Freigabe, Council-Entscheid) zu sparen.

## 14. Kompatibilität

- **Claude Code**: wie oben, natives Plugin.
- **Codex**: separate, funktional äquivalente Umsetzung über dessen eigenes Extension-/Konfigurationsformat – gleiche Gate-Logik, andere technische Hülle.
- **Windows**: Hooks/Detektor-Skripte plattformunabhängig in Python/Node schreiben statt Bash-only, damit keine WSL-Pflicht entsteht.

## 15. Security- & Pentest-Modul (GitHub, Server, Raspberry Pis, PC)

Kurzfassung: ja, das lässt sich sauber in CUSTOS integrieren – als eigener **Security-Mode**, der derselben Beweislogik folgt wie der Rest des Systems (kein „ist sicher" als Aussage, sondern ein Scan-Report mit Zeitstempel im selben Befund-Log) und der über den Fleet-Modus (Abschnitt 10) automatisch auf alle registrierten Repos angewendet wird. Eine Grundregel ist dabei nicht verhandelbar, siehe 15.1.

### 15.1 Scope-Datei als Voraussetzung für alles Aktive

Bevor irgendein aktiver Scan läuft, braucht CUSTOS eine feste **Asset-Allowlist** (`custos/scope.yaml`) mit genau den IPs/Hostnamen/Repos, die geprüft werden dürfen – dieselbe Liste, die auch der Fleet-Modus für die Repo-Freigabe nutzt. Jeder aktive Check (Portscan, Web-Scan) validiert vorher gegen diese Liste und bricht sonst ab. Grund: Auch im eigenen Heimnetz landen ohne diese Schranke schnell fremde Geräte im Scanbereich (Router/IoT-Geräte anderer, Cloud-IPs, bei denen der Provider eine vorherige Ankündigung aktiver Scans verlangt) – das ist der Unterschied zwischen „eigene Systeme härten" und einem echten Zwischenfall.

### 15.2 GitHub-Hygiene

| Prüfung | Werkzeug |
|---|---|
| Secrets in Commits/Historie | gitleaks oder trufflehog, zusätzlich GitHub Secret Scanning + Push Protection aktivieren |
| Abhängigkeits-Schwachstellen | Dependabot / OSV-Scanner |
| Code-Schwachstellen (SAST) | CodeQL oder Semgrep |
| Branch-Schutz, Repo-Sichtbarkeit, Mitgliederrechte | Abfrage über die GitHub-API (`gh` CLI) gegen eine Soll-Konfiguration |

Für den Claude-Code-eigenen Teil davon gibt es bereits ein fertiges Plugin im Katalog, das direkt zu CUSTOS passt: **„Security Guidance"** – prüft jede Code-Änderung automatisch per Hook (u. a. `PostToolUse`, `Stop`) auf Injection, XSS, SSRF, hartcodierte Secrets und über 20 weitere Schwachstellenklassen. Das lässt sich als zusätzliche Komponente einbinden, statt diesen Teil komplett selbst zu bauen.

### 15.3 Server, Raspberry Pis, PC – passive Härtung (unkritisch, beliebig oft automatisierbar)

| Prüfung | Werkzeug/Ansatz |
|---|---|
| Hardening-Score, Fehlkonfigurationen | Lynis |
| Rootkits/bekannte Malware-Signaturen | rkhunter, chkrootkit |
| Offene Dienste, unnötig laufende Prozesse | `systemctl list-units`, `ss -tulpn` |
| SSH-Konfiguration (Passwort-Login deaktiviert? Key-only? Fail2ban aktiv?) | Abgleich gegen Soll-Werte |
| Firewall-Regeln | ufw/iptables-Abgleich |
| Patch-Stand | unattended-upgrades-Status, `apt list --upgradable` |
| Windows-PC | Defender-Status, `netstat`, Autostart-Einträge, `winget upgrade --all` als Trockenlauf |

Das läuft komplett lokal und ist reine Beobachtung, kein Angriff – lässt sich bedenkenlos regelmäßig automatisieren, z. B. über `monitors/monitors.json` oder einen Cronjob auf jedem Pi/Server, der sein Ergebnis in dasselbe Log-/Befund-System schreibt wie die Code-Checks.

### 15.4 Aktive Prüfung von außen – nur innerhalb der Scope-Liste

| Prüfung | Werkzeug |
|---|---|
| Welche Ports sind tatsächlich von außen erreichbar | Nmap gegen die eigenen, gelisteten IPs |
| Typische Web-Schwachstellen eigener Dienste | OWASP ZAP oder Nikto |
| DAST gegen eigene Webanwendungen mit priorisierten Fix-Vorschlägen | Auch hierfür gibt es bereits ein passendes Plugin im Katalog: **StackHawk HawkScan** – erzeugt automatisch eine Scan-Konfiguration, führt den Scan aus und wandelt Funde direkt in priorisierte Aufgaben für den Coding-Agenten um |

Zwei Punkte vorher klären: Manche Cloud-Provider (Hetzner, AWS, Azure, …) verlangen bei aktiven Scans eine vorherige Ankündigung, auch gegen die eigenen Instanzen. Und ein Raspberry Pi mit wenig Leistung kann durch einen zu aggressiven Scan tatsächlich in die Knie gehen – deshalb ein definiertes Wartungsfenster und ein „safe mode" (moderate Scan-Intensität, kein Brute-Forcing) statt Dauerbetrieb.

## 16. Zero-Tolerance-Policy: wie strikt „0 Schwachstellen" durchsetzbar ist

Ehrliche Einordnung zuerst: **„0 bekannte, von den eingesetzten Prüfungen erkennbare Schwachstellen"** ist technisch durchsetzbar und genau das Ziel dieses Abschnitts. **„0 Schwachstellen überhaupt"** kann kein System versprechen – ein Zero-Day ist per Definition eine Lücke, die noch niemand kennt, und kein Scanner findet, was noch nicht als Muster/CVE/Signatur existiert. CUSTOS sollte deshalb das erste, ehrliche Ziel konsequent durchsetzen, statt das zweite, unhaltbare zu behaupten.

Damit das erste Ziel nicht zur Lippenbekenntnis wird, sondern tatsächlich greift:

| Stellschraube | Ohne Zero-Tolerance (Standard) | Mit Zero-Tolerance |
|---|---|---|
| Schwellwert der Gates | Blockt erst ab „hoch"/„kritisch" | Blockt ab jedem Fund, auch „niedrig"/„info" |
| Verhalten bei Fund | Warnung, Arbeit geht weiter | Fail-closed: Exit 2, Session/Deploy stoppt |
| Scanner-Anzahl je Kategorie | Ein Tool pro Kategorie | Mehrere unabhängige Tools parallel (jedes Tool hat eigene blinde Flecken – Defense in Depth) |
| Rescan-Auslöser | Nur bei Code-Änderung | Zusätzlich zeitgesteuert (z. B. täglich), weil für bereits gemergten Code laufend neue CVEs bekannt werden |
| Ausnahmen/Suppressions | Können vom Modell selbst gesetzt werden | Nur über den Code-Council (Abschnitt 6), mit Begründung und Ablaufdatum – nie eine stille Selbst-Freigabe |
| Bestandscode | „War schon immer so" wird akzeptiert | Neue Funde in Altcode zählen genauso wie in neuem Code, kein Bestandsschutz |

Der Preis dafür ist mehr Reibung: Builds brechen auch bei kleinen Funden, und mehr Fälle landen beim Council statt automatisch durchzulaufen. Das ist der bewusste Trade-off, der aus einem „meistens sauber"-System ein „so blank wie technisch möglich"-System macht.

## 17. GitHub-Veröffentlichung: Repo-Setup

Damit das Repo von Anfang an seriös wirkt und nicht wie ein halbfertiger Side-Hack:

- **Repo-Name:** `custos` (unter der `renker-industries`-Org, siehe Abschnitt 3, statt unter dem privaten Account).
- **README-Grundgerüst:** Ein-Satz-Pitch oben (Abschnitt 2), darunter kurz „Was es tut" (die vier Ebenen aus Abschnitt 4 als knappe Liste), Installationsschritt, ein Screenshot/GIF des Interfaces (Abschnitt 18), Lizenzabschnitt.
- **Badges:** Build-Status (eigene CI, die die CUSTOS-Gates auf sich selbst anwendet – Dogfooding), Lizenz-Badge, optional „0 offene Funde"-Badge, der sich aus dem letzten `custos_findings.json` speist statt einer Behauptung.
- **Lizenzwahl:** Muss vor Veröffentlichung bewusst getroffen werden (MIT/Apache-2.0 für offene Weiterverwendung vs. restriktivere Lizenz, falls es kommerziell bleiben soll) – siehe offene Punkte.
- **CI-Dogfooding:** Ein GitHub-Actions-Workflow, der bei jedem Push dieselben Gates laufen lässt, die CUSTOS auch für fremde Projekte durchsetzt – die beste Werbung ist ein Repo, das die eigenen Regeln sichtbar einhält.
- **.github/-Ordner:** Issue-Templates, ggf. CONTRIBUTING.md, falls die Community-Idee aus dem Vorbild-Video später doch aufgegriffen werden soll (optional, nicht Teil des MVP).

## 18. Interface

Festgelegter Stil: dunkles Terminal-Dashboard (Farben/Typografie siehe Abschnitt 2). Kernansichten:

1. **Übersicht/Fleet-Dashboard**: Liste aller überwachten Repos (Abschnitt 10) mit Status-Ampel, letztem Scan-Zeitpunkt, Anzahl offener Funde.
2. **Repo-Detail**: Gates im Detail (Abschnitt 8) als Zeilen mit Status, Klick öffnet den zugehörigen Beleg (Testoutput/Linter-Log).
3. **Security-Log**: chronologische Liste aller Security-Scans (Abschnitt 15) mit Schweregrad-Filter.
4. **Council-Fälle**: offene bzw. entschiedene Streitfälle zwischen Statik-Analyse und Modell-Einschätzung, inkl. Begründung des Chair-Agents.

**Design-Referenz:** [CUSTOS Dashboard](https://claude.ai/design/p/e5676802-f116-4b7a-bd09-06dc8c891cc8?file=CUSTOS+Dashboard.dc.html&via=share) – professionell in Claude Design ausgearbeitete Fassung der vier Ansichten, verbindliche Grundlage für die spätere Interface-Umsetzung (Roadmap-Phase 10, Abschnitt 19).

## 19. Umsetzungs-Roadmap

1. **MVP**: Senior-Dev-Default-Agent + Plan-Reviewer + ein `Stop`-Hook, der einen Testlauf erzwingt. Damit ist die Kernaussage ("Beweis statt Behauptung") bereits spürbar.
2. **Statik-Ebene**: AI-Slop-Detektor + sprachspezifische Linter/Typecheck-Hooks ergänzen.
3. **Branding & Repo-Grundgerüst**: `renker-industries/custos` anlegen, README/Lizenz/CI-Dogfooding (Abschnitt 17) – bevor mehr Funktionsumfang dazukommt, damit das Repo von Anfang an in gutem Zustand ist.
4. **Spezialmodi**: Debug-Mode mit Root-Cause-Agent, Data-Analytics-Mode.
5. **Fleet-Modus**: Repo-Discovery lokal + GitHub, zunächst read-only (Abschnitt 10.1–10.2).
6. **Security-Mode**: Scope-Datei + passive Härtungs-Checks zuerst (unkritisch), aktive Scans erst danach und nur gegen die Scope-Liste.
7. **Fleet-Bearbeitung**: Auto-Fix-PRs für freigegebene Repos (Abschnitt 10.3).
8. **Council**: Fünf-Advisor-Mechanismus für strittige Fälle.
9. **Multi-Session**: Worktree-Isolation + Task-Queue-Koordination.
10. **Interface**: Dashboard aus Abschnitt 18 als eigenständige Anwendung, gespeist aus den `custos_findings.json`-Reports.
11. **Selbstqualifizierung**: Referenz-Testsuite, Session-Logs, Release-Metriken.

## 20. Offene Punkte

- Lizenzwahl für die Veröffentlichung (Abschnitt 17) – MIT/Apache-2.0 oder restriktiver?
- Existiert die GitHub-Org `renker-industries` schon, oder muss sie neu angelegt werden?
- Welche Wurzelverzeichnisse auf dem PC soll die lokale Repo-Discovery (Abschnitt 10.1) überhaupt durchsuchen?
- Welche der eigenen GitHub-Repos werden zum Start als „aktiv überwacht" freigegeben, welche bleiben erstmal nur inventarisiert?
- Wie groß soll die Referenz-Testsuite für Regressionsläufe initial sein, und aus welchen eigenen Projekten wird sie gespeist?
- Soll der Task-Queue-Mechanismus über eine Datei im Repo oder einen lokalen MCP-Server laufen?
- Welche IPs/Hostnamen/Repos gehören konkret in die Scope-Datei (Abschnitt 15.1), bevor irgendein aktiver Scan aktiviert wird?

---

*Hinweis zu den technischen Angaben:* Die Zuordnung auf Hook-Events, Skill-/Agent-Format und Plugin-Struktur basiert auf der aktuellen Claude-Code-Dokumentation (Stand September 2026, code.claude.com/docs). Vor dem Bau lohnt sich ein kurzer Abgleich mit `/docs/en/hooks`, `/docs/en/plugins` und `/docs/en/permissions`, da sich Feldnamen bei neueren Versionen ändern können.
