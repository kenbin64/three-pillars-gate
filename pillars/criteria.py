# Software pillar, deterministic: check the code itself against the direction the human gave, not just that it runs.
# The human writes criteria as exact, checkable rules (forbid a pattern, require a pattern, require a minimum number
# of tests). This is how "complies with the direction" becomes something software can prove, token-free.
import ast
import re


def _forbid(sources, pattern, reason):
    out = []
    rx = re.compile(pattern)
    for path in sources:
        for i, line in enumerate(open(path, encoding='utf-8').read().split('\n')):
            if line.lstrip().startswith('#'):
                continue
            if rx.search(line):
                out.append(f'{path.rsplit("/", 1)[-1]} line {i + 1}: forbidden by direction ({reason}): {line.strip()}')
    return out


def _require(sources, pattern, reason):
    rx = re.compile(pattern)
    found = any(rx.search(open(p, encoding='utf-8').read()) for p in sources)
    return [] if found else [f'direction not met ({reason}): nothing matches {pattern!r}']


def _min_tests(test_files, minimum, reason):
    count = 0
    for path in test_files:
        tree = ast.parse(open(path, encoding='utf-8').read())
        count += sum(1 for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith('test'))
    return [] if count >= minimum else [f'direction not met ({reason}): {count} tests, at least {minimum} required']


def check(source_paths, test_paths, criteria):
    # criteria is the human's list of exact rules. Return the violations; empty means the code follows the direction.
    out = []
    for rule in criteria:
        kind = rule['rule']
        if kind == 'forbid':
            out += _forbid(source_paths, rule['pattern'], rule['reason'])
        elif kind == 'require':
            out += _require(source_paths, rule['pattern'], rule['reason'])
        elif kind == 'min_tests':
            out += _min_tests(test_paths, rule['count'], rule['reason'])
        else:
            out.append(f'unknown criterion {kind!r}')
    return out
