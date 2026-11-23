# Software pillar, deterministic: test the tests. Change the code in small, meaning-changing ways (mutations) and
# check that the tests notice. A test suite that stays green while the code is broken is a weak suite, and weak
# tests must not count as passing tests. This is the Python stand-in for TestThisPuppy's mutation engine (PIT);
# in the Java, JavaScript and CSS lanes the engine is TestThisPuppy itself.
#
# No tokens are spent here: it is pure, repeatable software, exactly the work the allocation rule sends to Software.
import os
import re
import subprocess
import sys

# Each mutation is a pair of opposite operators; we swap one occurrence at a time and see if a test dies.
SWAPS = [
    (' + ', ' - '), (' - ', ' + '), (' * ', ' / '), (' // ', ' * '),
    (' < ', ' <= '), (' > ', ' >= '), (' <= ', ' < '), (' >= ', ' > '),
    (' == ', ' != '), (' != ', ' == '), (' and ', ' or '), (' or ', ' and '),
    ('True', 'False'), ('False', 'True'), (' + 1', ' + 0'), (' - 1', ' - 0'),
]


def _mutants(line):
    # Yield every (column, old, new) mutation that applies on one source line. Comments are skipped by the caller.
    out = []
    for old, new in SWAPS:
        start = 0
        while True:
            at = line.find(old, start)
            if at == -1:
                break
            out.append((at, old, new))
            start = at + 1
    return out


def _run(test_cmd, cwd):
    # Run the test command; a non-zero exit means a test failed, which means the mutant was killed.
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    done = subprocess.run(test_cmd, cwd=cwd, shell=True, capture_output=True, env=env)
    return done.returncode != 0


def score(target_path, test_cmd, cwd):
    # Apply every mutation to the target file one at a time, restoring after each, and count how many the tests kill.
    original = open(target_path, encoding='utf-8').read()
    lines = original.split('\n')
    planted = 0
    killed = 0
    survivors = []
    try:
        for i, line in enumerate(lines):
            if line.lstrip().startswith('#'):
                continue
            for at, old, new in _mutants(line):
                mutated = lines[:]
                mutated[i] = line[:at] + new + line[at + len(old):]
                open(target_path, 'w', encoding='utf-8').write('\n'.join(mutated))
                planted += 1
                if _run(test_cmd, cwd):
                    killed += 1
                else:
                    survivors.append(f'line {i + 1}: {old.strip()!r} -> {new.strip()!r}  ({line.strip()})')
    finally:
        open(target_path, 'w', encoding='utf-8').write(original)
    pct = (killed / planted * 100) if planted else 100.0
    return {'planted': planted, 'killed': killed, 'score': round(pct, 1), 'survivors': survivors}


if __name__ == '__main__':
    target, cmd, cwd = sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else '.'
    r = score(target, cmd, cwd)
    print(f"mutation: {r['killed']}/{r['planted']} killed = {r['score']}%")
    for s in r['survivors']:
        print('  survived', s)
