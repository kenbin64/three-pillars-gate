# The config is the law, so the law itself is tested first. Before any code is checked, the gate validates the config:
# it must be well-formed, complete, and sane. A broken or half-written law is caught here, before anything else runs.
# And because the certificate's fingerprint covers the config, any change to it invalidates the old certificate and
# the product must be certified again. Changing the law re-opens the loop.
RULES = {'forbid', 'require', 'min_tests'}
SEVERITIES = {'low', 'medium', 'medium-high', 'high', 'critical'}


def _need(man, path):
    cur = man
    for key in path.split('.'):
        if not isinstance(cur, dict) or key not in cur:
            return f'missing {path}'
        cur = cur[key]
    return None


def validate(man):
    # Return the problems with the config itself. Empty means the law is well-formed and ready to govern.
    out = []
    for path in ('name', 'language', 'source', 'test_cmd', 'thresholds.mutation_min_score',
                 'human.style', 'human.bloat', 'human.libraries', 'human.criteria', 'human.signoff', 'ai'):
        miss = _need(man, path)
        if miss:
            out.append(miss)

    if isinstance(man.get('source'), list) and not man['source']:
        out.append('source is empty: name at least one file to check')
    if man.get('language') == 'python' and not str(man.get('test_cmd', '')).strip():
        out.append('test_cmd is empty: the gate needs a way to run the tests')

    bar = man.get('thresholds', {}).get('mutation_min_score')
    if isinstance(bar, (int, float)) and not (0 <= bar <= 100):
        out.append(f'mutation_min_score {bar} is not between 0 and 100')

    for i, c in enumerate(man.get('human', {}).get('criteria', [])):
        if c.get('rule') not in RULES:
            out.append(f'criterion {i + 1}: rule {c.get("rule")!r} is not one of {sorted(RULES)}')
        elif c['rule'] == 'min_tests' and not isinstance(c.get('count'), int):
            out.append(f'criterion {i + 1}: min_tests needs an integer count')
        elif c['rule'] in ('forbid', 'require') and not str(c.get('pattern', '')).strip():
            out.append(f'criterion {i + 1}: {c["rule"]} needs a pattern')
        if not str(c.get('reason', '')).strip():
            out.append(f'criterion {i + 1}: every rule needs a reason')

    sev = man.get('human', {}).get('libraries', {}).get('min_severity')
    if sev is not None and sev not in SEVERITIES:
        out.append(f'libraries.min_severity {sev!r} is not one of {sorted(SEVERITIES)}')

    return out


def validate_access(access):
    # Check an access policy, if the system has moved past a single all-roles user to a real users list. The one hard
    # rule: at least one admin must be able to both add and remove admins, so the org can never lock itself out.
    users = access.get('users', [])
    if not users:
        return []  # single user holds all roles, which satisfies the invariant
    admins = [u for u in users if 'admin' in (u.get('roles') or [])]
    if not admins:
        return ['no admin: the system needs at least one admin']
    full = [u for u in admins if u.get('can_add_admins') and u.get('can_remove_admins')]
    if not full:
        return ['no admin can both add and remove admins: keep at least one, or you lock yourself out']
    return []

