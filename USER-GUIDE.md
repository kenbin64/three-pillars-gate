# Three Pillars: User Guide

Comprehensive guide to using the Three Pillars gate: what it is, how to run it, every check it makes, the config
that drives it, the reports it writes, the roles and access model, and the honest limits. For the design and the
reasoning behind it, see `FRAMEWORK.md`.

## 1. What it is

A gate that certifies software built with AI. Three roles do the work: the **human** directs and gives the final
word, the **AI** writes the code, and **deterministic software** proves it is correct. Nothing ships until every
check is green and the human signs. The software does the verifying, so there is no AI reviewing AI, no tokens
spent on the checks, and the same verdict every time.

It works on AI-generated code and human-written code alike, at any scope: a single function, a whole app, or a
workflow. It runs with no login, no server, and no AI (the AI is optional and off by default).

## 2. Requirements and install

- Python 3.9 or newer. No third-party Python packages are needed for the native (Python) lane.
- For the Java, JavaScript and CSS lanes, the engine is TestThisPuppy (a separate tool), which brings PIT, PMD,
  SpotBugs, ESLint, Stylelint and an OSV library scan. The Python lane needs none of that.

Clone the repository and you are ready. There is nothing to install for the example.

## 3. Quick start

```
python -m pillars.gate example/manifest.json            # certify the example
python -m pillars.gate example/manifest.json --detail   # the full breakdown
bash run-proof.sh                                        # watch the loop: weak tests blocked, then certified
```

Open `ui/index.html` in any browser to build or edit a config visually. Open `example/report.html` after a run to
see the color-coded report.

## 4. The config file (the law)

The config is a JSON file (the "manifest"). It is the law the code must follow, and it is checked first: a broken
config blocks before any code is examined. The certificate's fingerprint covers the config, so changing it
invalidates the old certificate and re-opens the loop. Start from `default.manifest.json` and add to it, or build
it in the UI.

Fields:

- `name`, `version`: what the product is.
- `language`: `python`, `java`, `javascript`, or `css`. The checks are the same; the engine behind them changes.
- `dir`: the folder the code lives in, relative to the config.
- `source`: the source files to check (a list).
- `test_files`: the test files (a list).
- `test_cmd`: the command that runs the tests; it must exit non-zero if a test fails.
- `thresholds.mutation_min_score`: the least percent of planted bugs the tests must catch (0 to 100).
- `human.criteria`: your own checks (see section 5, Direction).
- `human.style`: coding-style rules (see section 5).
- `human.bloat`: bloat limits (see section 5).
- `human.security`: security toggles (see section 5).
- `human.libraries`: `block_on_vulnerable` (default false) and `min_severity` (see section 5).
- `human.signoff`: `approved`, `by`, `date`. The human's final word.
- `ai`: `authored` and `self_check`. The AI's record of its part.
- `engine`: for Java, JavaScript and CSS, which TestThisPuppy features to run.

## 5. The checks

The gate runs these in order and certifies only when all pass (plus the AI's part and the human's sign-off). Each
check has a severity, shown as a color-coded dot in the report (section 6).

1. **Config** (show-stopper). The law itself: the config must be well-formed and complete. A bad law stops
   everything before any code is read.
2. **Tests** (show-stopper). Every test must pass, 100 percent, no skips counted as passes.
3. **Tests of the tests / mutation** (critical). The gate changes the code in small, meaning-changing ways and
   checks the tests notice. Weak tests that pass but catch nothing are blocked. It also captures exceptions, reads
   stack traces, and can invoke error paths, so the failure cases are tested, not just the happy path.
4. **Coding style** (minor). Your style rules: line length, one return per function, no bare `except`, no leftover
   TODOs, function size, and more. It also tests for modularity: it flags spaghetti, deeply nested or sprawling
   functions, and functions that are hard to test, and suggests breaking them up.
5. **Direction** (major). Your own criteria: `forbid` a pattern, `require` a pattern, or require a minimum number
   of tests. This is how "it runs" becomes "it is the code I asked for."
6. **Bloat** (minor). Unused imports, values assigned and never read, duplicated blocks, oversized functions and
   files.
7. **Security** (critical). Vulnerabilities, brittle code, and anything exploitable: code built at runtime,
   unsafe deserialization, shell injection, hardcoded secrets, and checks that vanish in production. In the Java,
   JavaScript and CSS lanes the deep scan is TestThisPuppy's.
8. **Libraries** (info by default, major if you flag it). Third-party vulnerabilities are reported so you see them,
   and they block only if you set `block_on_vulnerable`, optionally at a `min_severity`. A dependency's CVE may not
   touch your product, so you decide.

## 6. The reports

Every run writes three reports, so each reader gets what they need:

- **`report.md`** and the terminal: for the human. Concise but complete, one plain line per check, and the one thing
  to do next. Add `--detail` for the full breakdown with line numbers.
- **`report.json`**: for the AI. The machine-readable version it corrects from.
- **`report.html`**: the visual report. Color-coded dots by severity: a green verdict dot for certified, a testing
  status strip, and a dot per check. The legend: show-stopper and critical are red, major orange, minor yellow,
  info blue, pass green. Open it in a browser.

When everything is green and the human has signed, the gate also writes **`certificate.json`**, the final report,
with the fingerprint that ties it to this exact code and config.

## 7. The loop

1. The human writes the config (the law) and directs the work.
2. The AI writes the code and the tests.
3. The gate runs every check and reports to the human and the AI.
4. The AI fixes what software flagged; the human decides on the AI's recommendations and the software's verdicts.
5. Repeat until every check is green, then the human gives the final word and it certifies.

The `run-proof.sh` script walks this: happy-path tests are blocked (weak tests, too few), edge tests turn the
software green, and the human's sign-off certifies.

## 8. Roles and access

The system is secured with a login and four roles, each able to act only within its domain:

- **Admin** runs the system, manages users and roles, and sets policy. Managing other admins is its own pair of
  permissions, add and remove are separate, and the system always keeps at least one admin who can do both.
- **Dev** is the development team: writes code, writes the law for their products, runs the gate, creates their own
  tests and checks, and iterates.
- **Test** is the tester or QA: independent verification within its scope. It does not ship.
- **User** is the end user: views reports and runs production checks on their own instance, read-mostly.

Out of the box, a single user holds all roles automatically, so a solo developer has the whole system with no setup.
Roles only separate when an admin adds more people. The login is pluggable: a simple internal login by default, or
plug in SSO (OIDC, SAML, LDAP), cloud, social (Google, GitHub, Microsoft), or a custom handler, configured in
`default.access.json`.

Checks and tests are added two ways and by anyone within their domain: each standard check is a toggle in the UI
that writes to the config, or you write the JSON directly, same result. Devs create their own tests and checks for
the products they own.

## 9. The config UI

`ui/index.html` is a single self-contained page, no install and no login. Fill in the product, check the common
things, add your own checks, and it builds the JSON live. Copy it, download it, or paste an existing config to edit
it. The output is one file you can share on any workstation or a server.

## 10. AI is optional, and the directives

The gate is deterministic and spends no tokens, so it runs with or without AI. An AI model is added only to assist
(read a failure, propose a fix), configured in the access policy, and the verdict never depends on it. How the AI
writes is set by the directives in the `directives/` folder, which you extend; a pristine copy of the default is
kept in `directives/_default-backup/` and restored with `directives/restore-default.sh` if the working one is ever
corrupted.

## 11. What it does not do

- It checks what you specify, so a missing requirement passes green. The hard thinking moves to writing the spec.
- Tests passing and mutation high means the tests are strong and the code passes them, not that the spec is right.
- Not everything is deterministically checkable: real-world performance, novel security, and whether the product is
  good need human judgment, not a checkmark.
- The gate itself must be trusted, and the efficient-form freedom trades against maintainability. See `FRAMEWORK.md`
  for the full list.

## 12. Coming

Comprehensive professional video tutorials (no on-screen characters) covering setup, the config, each check, the
reports, and the roles, to go with this guide.
