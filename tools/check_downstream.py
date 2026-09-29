"""AST contract check: every `from cannlytics... import name` in a downstream
tree, verified against the package actually on disk."""
import ast
import importlib
import os
import sys
from collections import defaultdict

downstream, pkg_root = sys.argv[1], sys.argv[2]
sys.path.insert(0, pkg_root)

wanted = defaultdict(lambda: defaultdict(list))   # module -> name -> [sites]
for root, _, files in os.walk(downstream):
    for fn in files:
        if not fn.endswith('.py'):
            continue
        path = os.path.join(root, fn)
        try:
            tree = ast.parse(open(path, encoding='utf-8').read())
        except SyntaxError as e:
            print('SYNTAX', path, e); continue
        # Record whether the import sits inside a try (guarded) or not.
        guarded = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                for sub in ast.walk(node):
                    if isinstance(sub, (ast.Import, ast.ImportFrom)):
                        guarded.add(id(sub))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.split('.')[0] == 'cannlytics':
                for alias in node.names:
                    site = f'{os.path.relpath(path, downstream)}:{node.lineno}' + (' (guarded)' if id(node) in guarded else '')
                    wanted[node.module][alias.name].append(site)

ok = bad = 0
missing = []
for module in sorted(wanted):
    try:
        mod = importlib.import_module(module)
        mod_err = None
    except Exception as e:  # noqa: BLE001
        mod, mod_err = None, f'{type(e).__name__}: {e}'
    for name, sites in sorted(wanted[module].items()):
        if mod is not None and hasattr(mod, name):
            ok += 1
        else:
            bad += 1
            missing.append((module, name, mod_err, sites))

print(f'{ok} imports resolve, {bad} do not\n')
for module, name, err, sites in missing:
    why = 'MODULE MISSING' if err else 'NAME MISSING'
    print(f'[{why}] from {module} import {name}')
    if err:
        print(f'      {err.splitlines()[0][:110]}')
    for s in sites[:4]:
        print(f'      <- {s}')
    if len(sites) > 4:
        print(f'      <- ... and {len(sites) - 4} more')
