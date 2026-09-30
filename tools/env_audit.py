"""AST audit of environment-variable and .env-config reads.

Finds: os.environ[...], os.environ.get(...), os.getenv(...), os.environ.setdefault,
`X in os.environ`, and string subscripts / .get() on names that came from
dotenv_values(...) (tracked per-function by simple name binding)."""
import ast
import os
import sys
from collections import defaultdict

root = sys.argv[1]
found = defaultdict(list)   # var -> [(file, line, how, default)]

def const(node):
    return node.value if isinstance(node, ast.Constant) and isinstance(node.value, str) else None

def chain(n):
    p = []
    while isinstance(n, ast.Attribute):
        p.append(n.attr); n = n.value
    if isinstance(n, ast.Name):
        p.append(n.id)
    return '.'.join(reversed(p))

for dirpath, _, files in os.walk(root):
    if '__pycache__' in dirpath:
        continue
    for fn in files:
        if not fn.endswith('.py'):
            continue
        path = os.path.join(dirpath, fn)
        rel = os.path.relpath(path, os.path.dirname(root))
        tree = ast.parse(open(path, encoding='utf-8').read())
        # Names bound to dotenv_values(...) results.
        cfg_names = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
                if chain(n.value.func).split('.')[-1] == 'dotenv_values':
                    for t in n.targets:
                        if isinstance(t, ast.Name):
                            cfg_names.add(t.id)
        for n in ast.walk(tree):
            # os.environ['X'] / config['X']
            if isinstance(n, ast.Subscript):
                base = chain(n.value)
                key = const(n.slice)
                if key and (base in ('os.environ', 'environ') or base in cfg_names):
                    how = 'os.environ[]' if 'environ' in base else f'{base}[] (dotenv)'
                    found[key].append((rel, n.lineno, how, None))
            if isinstance(n, ast.Call):
                name = chain(n.func)
                args = n.args
                key = const(args[0]) if args else None
                default = ast.unparse(args[1]) if len(args) > 1 else None
                for kw in n.keywords:
                    if kw.arg == 'default':
                        default = ast.unparse(kw.value)
                if not key:
                    continue
                if name in ('os.getenv', 'getenv'):
                    found[key].append((rel, n.lineno, 'os.getenv', default))
                elif name in ('os.environ.get', 'environ.get'):
                    found[key].append((rel, n.lineno, 'os.environ.get', default))
                elif name in ('os.environ.setdefault',):
                    found[key].append((rel, n.lineno, 'os.environ.setdefault', default))
                elif name.endswith('.get') and name[:-4] in cfg_names:
                    found[key].append((rel, n.lineno, f'{name[:-4]}.get (dotenv)', default))
            if isinstance(n, ast.Compare) and len(n.comparators) == 1:
                if chain(n.comparators[0]) in ('os.environ', 'environ') and const(n.left):
                    found[const(n.left)].append((rel, n.lineno, 'in os.environ', None))

for var in sorted(found):
    sites = found[var]
    print(f'{var}')
    for rel, line, how, default in sites:
        d = f'  default={default}' if default is not None else ''
        print(f'    {rel}:{line}  [{how}]{d}')
print(f'\n{len(found)} distinct variables, {sum(len(v) for v in found.values())} read sites')
