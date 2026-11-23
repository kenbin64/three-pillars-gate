# One engine layer for every language. The checks are the same everywhere (tests, mutation, style, direction, bloat,
# libraries); the LANGUAGE only selects which tool fills them, dispatched here in one place. There is deliberately no
# separate module per language: Python is checked natively, and Java, JavaScript and CSS go to TestThisPuppy, the one
# multi-language engine. Adding a language means adding an adapter here, not a new module tree.
import json
import os
import subprocess

from pillars import mutate, style, criteria, bloat

TESTTHISPUPPY = os.environ.get('TESTTHISPUPPY', r'C:\projects\testthispuppy')


def software(man, base, sources, test_files):
    # Fill the universal check set for the product's language. One dispatch, same result shape for every language.
    language = man.get('language', 'python').lower()
    if language == 'python':
        return _native(man, base, sources, test_files)
    return _testthispuppy(man, base)


def _tests_pass(test_cmd, cwd):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    done = subprocess.run(test_cmd, cwd=cwd, shell=True, capture_output=True, text=True, env=env)
    return done.returncode == 0, (done.stdout + done.stderr).strip().split('\n')[-1]


def _library_result(findings, man):
    # Third-party vulnerabilities are REPORTED by default and only BLOCK when the human turns on the flag. The human
    # can require a minimum severity, so low-severity noise never blocks unless they ask for it.
    rule = man['human'].get('libraries', {})
    block = rule.get('block_on_vulnerable', False)
    if not block:
        return {'pass': True, 'reported': findings, 'blocking': False}
    levels = ['low', 'medium', 'medium-high', 'high', 'critical']
    floor = levels.index(rule.get('min_severity', 'high')) if rule.get('min_severity', 'high') in levels else 3
    blockers = [f for f in findings if any(f.lower().startswith(s) or (': ' + s) in f.lower() for s in levels[floor:])]
    return {'pass': not blockers, 'reported': findings, 'blocking': True, 'blockers': blockers}


def _native(man, base, sources, test_files):
    # The Python lane: ast and the local checks. Fills the universal keys.
    test_cmd = man['test_cmd']
    r = {}
    ok, last = _tests_pass(test_cmd, base)
    r['tests'] = {'pass': ok, 'detail': last}

    planted = killed = 0
    survivors = []
    for s in sources:
        m = mutate.score(s, test_cmd, base)
        planted += m['planted']
        killed += m['killed']
        survivors += [f'{os.path.basename(s)}: {x}' for x in m['survivors']]
    pct = round(killed / planted * 100, 1) if planted else 100.0
    bar = man['thresholds']['mutation_min_score']
    r['mutation'] = {'pass': pct >= bar, 'score': pct, 'bar': bar, 'killed': killed, 'planted': planted, 'survivors': survivors}

    r['style'] = _collect(sources, lambda s: style.check(s, man['human']['style']))
    r['direction'] = {'pass': True, 'violations': criteria.check(sources, test_files, man['human'].get('criteria', []))}
    r['direction']['pass'] = not r['direction']['violations']
    r['bloat'] = _collect(sources, lambda s: bloat.check(s, man['human'].get('bloat', {})))
    r['libraries'] = _library_result([], man)
    r['pass'] = all(r[k]['pass'] for k in ('tests', 'mutation', 'style', 'direction', 'bloat', 'libraries'))
    return r


def _collect(sources, fn):
    out = []
    for s in sources:
        out += [f'{os.path.basename(s)}: {v}' for v in fn(s)]
    return {'pass': not out, 'violations': out}


def _testthispuppy(man, base):
    # Java, JavaScript, CSS: hand the product to the one TestThisPuppy engine and map its report to the universal keys.
    check = os.path.join(TESTTHISPUPPY, 'check.sh')
    subprocess.run(f'"{check}" "{base}" --level {man.get("level", "standard")}', shell=True, capture_output=True, text=True)
    report = json.load(open(os.path.join(TESTTHISPUPPY, 'puppy-check', 'report.json'), encoding='utf-8'))
    results = report['results']

    def find(kind=None, name=None):
        for x in results:
            if (kind and x['kind'] == kind) or (name and name in x['name']):
                return x
        return {'passed': True, 'detail': 'not run'}

    unit = find(kind='unit')
    mut = find(kind='mutation')
    vuln = [x['detail'] for x in results if 'VulnerableLibrary' in x['name']]
    code_ok = all(x['passed'] for x in results if x['kind'] == 'code' and 'VulnerableLibrary' not in x['name']
                  and 'libraries' not in x['name'])
    direction = criteria.check([], [], [r for r in man['human'].get('criteria', []) if r['rule'] != 'min_tests'])
    r = {
        'tests': {'pass': unit['passed'], 'detail': unit['detail']},
        'mutation': {'pass': mut['passed'], 'score': None, 'bar': None, 'planted': None, 'killed': None,
                     'survivors': [], 'detail': mut['detail']},
        'style': {'pass': code_ok, 'violations': [] if code_ok else ['see TestThisPuppy code-fixes.md']},
        'direction': {'pass': not direction, 'violations': direction},
        'bloat': {'pass': code_ok, 'violations': []},
        'libraries': _library_result(vuln, man),
    }
    r['pass'] = all(r[k]['pass'] for k in ('tests', 'mutation', 'style', 'direction', 'bloat', 'libraries'))
    return r
