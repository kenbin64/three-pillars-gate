# Turn the gate result into a report a person can read. Concise but complete: it tells the human everything that
# matters in plain words, without a wall of numbers and without needing a team to decipher it. The full technical
# breakdown is there on request (detail), and the machine-readable version for the AI is the report.json.


def _tests_line(soft):
    t = soft['tests']
    return 'Every test passes.' if t['pass'] else 'A test is failing. The code does not do what the tests expect.'


def _mutation_line(soft):
    m = soft['mutation']
    if m.get('score') is None:
        return f"The tests were tested (mutation): {m.get('detail', 'see the engine report')}." if m['pass'] else \
               f"The tests are weak: {m.get('detail', 'see the engine report')}."
    if m['pass']:
        return f"The tests were tested and catch {m['score']}% of planted bugs (your bar is {m['bar']}%)."
    n = len(m['survivors'])
    return (f"The tests are weak: they catch only {m['score']}% of planted bugs, under your {m['bar']}% bar. "
            f"{n} change(s) to the code went unnoticed. The AI should add tests that cover them.")


def _style_line(soft):
    s = soft['style']
    return 'The code follows your coding style.' if s['pass'] else f"The code breaks your style in {len(s['violations'])} place(s)."


def _direction_line(soft):
    d = soft['direction']
    return 'The code follows your direction.' if d['pass'] else f"The code breaks your direction in {len(d['violations'])} place(s)."


def _bloat_line(soft):
    b = soft['bloat']
    return 'The code is lean, no bloat found.' if b['pass'] else f"The code carries bloat in {len(b['violations'])} place(s) (unused, duplicated, or oversized)."


def _libraries_line(soft):
    lib = soft.get('libraries', {})
    n = len(lib.get('reported', []))
    if n == 0:
        return 'Third-party libraries: none flagged.'
    if not lib.get('blocking'):
        return f"Third-party libraries: {n} with known vulnerabilities, reported for your awareness (not blocking, you have not flagged it)."
    bad = len(lib.get('blockers', []))
    return f"Third-party libraries: {n} reported, {bad} at or above your severity flag, which blocks."


def summary(report):
    # The default report for the human: the verdict, one plain line per pillar, and the one thing to do next.
    verdict = 'CERTIFIED TO SHIP' if report['certified'] else 'NOT YET: something still needs doing'
    cfg = report.get('config', {'pass': True, 'problems': []})
    out = [f"# {report['product']} {report['version']}  ({verdict})",
           f"_fingerprint {report['fingerprint']} (covers the code and the config); reproducible_", '',
           '## Config (the law itself, checked first)',
           '- ' + ('The config is well-formed.' if cfg['pass'] else
                   f"The config does not pass: {len(cfg['problems'])} problem(s). Fix the config before anything else.")]
    for p in (cfg['problems'][:6] if not cfg['pass'] else []):
        out.append(f'   - {p}')
    if report.get('software') is None:
        out += ['', '## What to do next', '- Fix the config above, then run the gate again.',
                '', '_The config is the law; it is checked before any code._']
        return '\n'.join(out)
    soft, ai, human = report['software'], report['ai'], report['human']
    out += ['', '## Software (the deterministic checks)',
           '- ' + _tests_line(soft),
           '- ' + _mutation_line(soft),
           '- ' + _style_line(soft),
           '- ' + _direction_line(soft),
           '- ' + _bloat_line(soft),
           '- ' + _libraries_line(soft),
           '', '## AI',
           '- ' + ('Has done its part: ' + ai['self_check'] if ai['pass'] else 'Has not recorded its part yet.'),
           '', '## Human (the final word)',
           '- ' + (f"Certified by {human['by']} on {human['date']}." if human['pass'] else 'Waiting on your final word.'),
           '', '## What to do next']
    if report['certified']:
        out.append('- Nothing. Every pillar is green and you have signed. It is cleared to ship.')
    elif not soft['pass']:
        out.append('- Send the report to the AI to fix what software flagged above, then run the gate again.')
    elif not human['pass']:
        out.append('- Software and the AI are green. Read it, and if you are satisfied, give the final word to certify.')
    out += ['', '_Ask for the full breakdown with: gate --detail_']
    return '\n'.join(out)


def detail(report):
    # The verbose drill-down, on request: the exact survivors, style breaks and direction breaches, with line numbers.
    if report.get('software') is None:
        return summary(report)
    soft = report['software']
    out = [summary(report), '', '## Full breakdown']
    m = soft['mutation']
    if m.get('score') is None:
        out.append(f"\n### Mutation (test the tests): {m.get('detail', 'see the engine report')}")
    else:
        out.append(f"\n### Mutation: {m['killed']}/{m['planted']} killed = {m['score']}%")
        for s in m['survivors']:
            out.append(f"- survived: {s}")
    out.append('\n### Style')
    out += [f"- {v}" for v in soft['style']['violations']] or ['- none']
    out.append('\n### Direction (your criteria)')
    out += [f"- {v}" for v in soft['direction']['violations']] or ['- none']
    out.append('\n### Bloat')
    out += [f"- {v}" for v in soft['bloat']['violations']] or ['- none']
    out.append('\n### Third-party libraries (reported)')
    out += [f"- {v}" for v in soft.get('libraries', {}).get('reported', [])] or ['- none flagged']
    return '\n'.join(out)
