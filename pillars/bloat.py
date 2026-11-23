# Software pillar, deterministic: check for bloat as part of quality. Bloat is code that earns nothing: things
# imported and never used, values assigned and never read, blocks copy-pasted instead of shared, functions and files
# that have grown past what one person should hold at once. All of it is exact and token-free to find.
import ast


def _names_used(tree):
    used = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            used.add(node.id)
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            used.add(node.value.id)
    return used


def _unused_imports(tree):
    used = _names_used(tree)
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                name = (alias.asname or alias.name).split('.')[0]
                if name != '*' and name not in used:
                    out.append(f'line {node.lineno}: import {name!r} never used')
    return out


def _unused_assignments(tree):
    out = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        assigned = {}
        read = set()
        for node in ast.walk(fn):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store):
                    assigned.setdefault(node.id, node.lineno)
                elif isinstance(node.ctx, ast.Load):
                    read.add(node.id)
        for name, line in assigned.items():
            if name != '_' and name not in read:
                out.append(f'line {line}: {name!r} assigned in {fn.name!r} but never read')
    return out


def _duplicate_blocks(lines, min_run):
    clean = [(i + 1, s.strip()) for i, s in enumerate(lines) if s.strip() and not s.lstrip().startswith('#')]
    seen = {}
    out = []
    for start in range(len(clean) - min_run + 1):
        window = tuple(s for _, s in clean[start:start + min_run])
        if window in seen:
            out.append(f'lines {clean[start][0]}+: a {min_run}-line block is duplicated (first seen at line {seen[window]})')
        else:
            seen[window] = clean[start][0]
    return out


def check(source_path, rules):
    # Return bloat findings. Empty means the code is lean by the human's limits.
    src = open(source_path, encoding='utf-8').read()
    lines = src.split('\n')
    out = []

    max_lines = rules.get('max_file_lines', 400)
    if len(lines) > max_lines:
        out.append(f'file is {len(lines)} lines over the {max_lines} limit (split it)')

    try:
        tree = ast.parse(src)
    except SyntaxError:
        return out

    if rules.get('no_unused_imports', True):
        out += _unused_imports(tree)
    if rules.get('no_unused_assignments', True):
        out += _unused_assignments(tree)
    run = rules.get('duplicate_block_lines', 5)
    if run:
        out += _duplicate_blocks(lines, run)
    return out
