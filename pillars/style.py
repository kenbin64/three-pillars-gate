# Software pillar, deterministic: verify the code meets the human's criteria and coding style. Every rule here is
# exact and token-free, the kind of repetitive checking the allocation rule sends to Software, not the AI.
# The rules are Ken's standing coding style, checkable without judgment; the human turns each on or off per product.
import ast
import re

BARE_EXCEPT = re.compile(r'except\s*:')


def _functions(tree):
    return [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def _return_count(fn):
    return sum(1 for n in ast.walk(fn) if isinstance(n, ast.Return))


def _statement_count(fn):
    return sum(1 for n in ast.walk(fn) if isinstance(n, ast.stmt)) - 1


def check(source_path, rules):
    # Return a list of violations. An empty list means the code meets the style the human laid out.
    src = open(source_path, encoding='utf-8').read()
    lines = src.split('\n')
    out = []

    for i, line in enumerate(lines):
        n = i + 1
        if rules.get('no_em_dash', True) and ('—' in line or '–' in line):
            out.append(f'line {n}: em-dash or en-dash (Ken: never, reads as AI-written)')
        limit = rules.get('max_line_length', 120)
        if len(line) > limit:
            out.append(f'line {n}: {len(line)} chars over the {limit} limit')
        if rules.get('no_bare_except', True) and BARE_EXCEPT.search(line):
            out.append(f'line {n}: bare "except:" (name the exception)')
        if rules.get('no_todo', True) and ('TODO' in line or 'FIXME' in line):
            out.append(f'line {n}: unfinished marker left in shipped code')

    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        out.append(f'does not parse: {e}')
        return out

    for fn in _functions(tree):
        if rules.get('single_return', True) and _return_count(fn) > 1:
            out.append(f'function {fn.name!r}: {_return_count(fn)} returns (Ken: one return at the end)')
        cap = rules.get('max_function_statements', 0)
        if cap and _statement_count(fn) > cap:
            out.append(f'function {fn.name!r}: {_statement_count(fn)} statements over the {cap} limit')

    return out
