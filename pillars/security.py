# Software pillar, deterministic: flag vulnerabilities, brittle code, and anything that could be exploited. This is
# the native-lane security check; in the Java, JavaScript and CSS lanes the deep scan is TestThisPuppy's (SpotBugs,
# FindSecBugs, security rules). Here it catches the common, exact, exploitable patterns, token-free.
import ast
import re

SECRET_NAME = re.compile(r'(password|passwd|secret|api[_-]?key|token|private[_-]?key)', re.I)


def _call_name(func):
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        base = _call_name(func.value)
        return f'{base}.{func.attr}' if base else func.attr
    return ''


def check(source_path, rules):
    # Return security findings. Empty means nothing exploitable was found by these exact rules.
    src = open(source_path, encoding='utf-8').read()
    out = []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return out

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = _call_name(node.func)
            line = node.lineno
            if name in ('eval', 'exec', '__import__'):
                out.append(f'line {line}: {name}() runs code built at runtime: a direct code-injection risk')
            if name in ('pickle.loads', 'pickle.load', 'marshal.loads', 'dill.loads'):
                out.append(f'line {line}: {name}() will execute code from the data it loads: exploitable')
            if name == 'yaml.load' and not any(k.arg == 'Loader' for k in node.keywords):
                out.append(f'line {line}: yaml.load without a safe Loader runs code from the input')
            if name in ('os.system', 'os.popen', 'subprocess.call', 'subprocess.run', 'subprocess.Popen'):
                if any(k.arg == 'shell' and getattr(k.value, 'value', False) is True for k in node.keywords):
                    out.append(f'line {line}: {name}(shell=True) invites shell injection')

        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and SECRET_NAME.search(target.id):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str) and node.value.value:
                        out.append(f'line {node.lineno}: {target.id!r} looks like a hardcoded secret in the code')

        # Brittle: validating with assert, which is stripped when Python runs optimized, so the check vanishes in prod.
        if rules.get('no_assert_validation', True) and isinstance(node, ast.Assert):
            out.append(f'line {node.lineno}: assert used as a check (brittle: assertions are removed with -O in production)')

    return out
