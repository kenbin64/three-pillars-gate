# Three Pillars: a deterministic gate for AI-assisted development

A small, runnable framework for shipping software built with AI, where **software, not another AI, proves the code is
correct**. Three roles do the work: the human directs and gives the final word, the AI writes the code, and
deterministic software verifies it. Nothing ships until every check is green and the human signs.

This repository is the deterministic core, and it is deliberately simple to try:

- **No login, no server, no cloud.** Clone it and run it.
- **Deterministic only, zero AI, zero tokens.** The gate is pure software. It spends no tokens and gives the same
  verdict every time.
- **Tests AI-generated code and human-written code alike.** The gate does not care who wrote it; it checks what the
  code does.
- **Any scope: a single function, a whole app, or a workflow.** Point it at what you want certified.

## What the gate checks

The config is the law, and the law is checked first. Then, for the code:

1. **Tests pass**, 100 percent, no skips counted as passes.
2. **The tests are tested** (mutation): weak tests that pass but catch nothing are blocked.
3. **Style**: the code meets the rules you set.
4. **Direction**: the code obeys your own criteria (forbid a pattern, require a pattern, require a minimum number of
   tests), so "it runs" is not enough; it has to be the code you asked for.
5. **Bloat**: unused imports, dead assignments, duplicated blocks, oversized functions and files.
6. **Libraries**: third-party vulnerabilities are reported, and block only if you flag that you care.

Only when all of that is green, the AI's part is recorded, and the human has signed, does the gate issue a
certificate. It is reproducible: a fingerprint covers the code and the config, so any change re-opens the loop.

## Try it

```
python -m pillars.gate example/manifest.json          # certify the example
python -m pillars.gate example/manifest.json --detail # the full breakdown
bash run-proof.sh                                      # watch the loop: weak tests blocked, then certified
```

Open `ui/index.html` in a browser to build or edit a config visually: check the common things, or write the JSON
directly. No install, no login. The output is one JSON file you can share on any workstation or a server.

## The run-proof, in words

The example is a small money library whose tricky part is splitting a bill so the cents sum exactly. With
happy-path-only tests the gate **blocks**: the tests pass but mutation shows they are weak, and the direction check
flags too few tests. After the edge tests are added the software goes green, but the gate still **waits** for the
human. When the human signs, it **certifies**, and writes the final report.

## Measured (full version, on real code)

The deterministic engine was run on a real Java project through TestThisPuppy, the multi-language engine behind the
gate: **19 of 19 tests passed, and mutation caught 41 of 41 planted bugs, 100 percent, for zero AI tokens.** On the
verification work, the software gate spent **0 tokens** where a single AI-reviews-AI pass spent about **1,475** and
still could not prove coverage. The point: deterministic verification is exact, free, and repeatable.

## What this does not do

It checks what you specify, so a missing requirement passes green; strong tests mean the tests are strong, not that
the spec is right; and some qualities (real-world performance, novel security, whether the product is good) need
human judgment, not a checkmark. The honest limits travel with the framework. See `FRAMEWORK.md`.

## The fuller design

`FRAMEWORK.md` lays out the whole thing: the allocation rule (deterministic work to software, cognition to AI,
direction to the human), the lifecycle sides (development, deployment, production), and the design for roles, access,
pluggable login and optional AI assist. This runnable demo is the deterministic core and needs none of them.

## Layout

```
pillars/      the gate: config, engines (one dispatch, many languages), mutate, style, criteria, bloat, report
example/      a small product, its tests, and its config
ui/           the browser config builder (no login, no server)
directives/   how the AI writes, with a pristine default kept for restore
FRAMEWORK.md  the full design
```
