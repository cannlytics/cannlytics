"""
Package-level contracts
=======================
What ``import cannlytics`` promises on a core install: it imports
nothing optional, every ``__all__`` is a list of resolvable strings,
and there is one version number.
"""
import ast
import importlib
import pathlib
import re
import subprocess
import sys
import textwrap

import pytest

import cannlytics

ROOT = pathlib.Path(cannlytics.__file__).parent
CORE = ['cannlytics', 'cannlytics.utils', 'cannlytics.utils.hashing', 'cannlytics.metrc',
        'cannlytics.stats', 'cannlytics.ai', 'cannlytics.data.cache',
        'cannlytics.data.constants', 'cannlytics.data.compounds',
        'cannlytics.constants', 'cannlytics.clean', 'cannlytics.licenses', 'cannlytics.datasets',
        'cannlytics.schema', 'cannlytics.collect']

def run_blocked(body):
    """Run code in a clean interpreter with every optional dependency blocked."""
    code = textwrap.dedent('''
        import sys
        BLOCKED = ('openai', 'anthropic', 'google', 'firebase_admin', 'pypdf', 'pydantic',
                   'skimage', 'sklearn', 'pdfplumber', 'PIL', 'cv2', 'pyzbar', 'bs4',
                   'selenium', 'googlemaps', 'zipcodes', 'fredapi', 'matplotlib')
        class Blocker:
            def find_spec(self, fullname, path=None, target=None):
                if fullname.split('.')[0] in BLOCKED:
                    raise ImportError(f"No module named {fullname!r} (blocked)")
        sys.meta_path.insert(0, Blocker())
    ''') + textwrap.dedent(body)
    return subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, timeout=180)

class TestCoreInstall:

    def test_core_modules_import_with_no_extras(self):
        result = run_blocked(f'''
            import importlib
            for name in {CORE!r}:
                importlib.import_module(name)
            from cannlytics import *
            loaded = sorted({{m.split('.')[0] for m in sys.modules}} & set(BLOCKED))
            assert not loaded, loaded
            print('ok')
        ''')
        assert result.stdout.strip() == 'ok', result.stderr[-2000:]

    @pytest.mark.parametrize('module, extra', [
        ('cannlytics.firebase', 'firebase'),
        ('cannlytics.auth', 'firebase'),
    ])
    def test_optional_modules_name_their_extra(self, module, extra):
        result = run_blocked(f'''
            import importlib
            try:
                importlib.import_module({module!r})
            except ImportError as error:
                assert 'cannlytics[' in str(error) and {extra!r} in str(error), str(error)
                print('ok')
        ''')
        assert result.stdout.strip() == 'ok', result.stdout + result.stderr[-2000:]

    def test_lazy_attribute_access(self):
        assert cannlytics.metrc.Metrc and cannlytics.stats.calc_purpleness
        with pytest.raises(AttributeError):
            cannlytics.not_a_module  # noqa: B018 (the access is the test)

class TestAllLists:

    @pytest.mark.parametrize('path', sorted(ROOT.rglob('__init__.py')), ids=lambda p: str(p.relative_to(ROOT.parent)))
    def test_all_is_a_list_of_strings(self, path):
        for node in ast.parse(path.read_text(encoding='utf-8')).body:
            if isinstance(node, ast.Assign) and any(getattr(t, 'id', '') == '__all__' for t in node.targets):
                bad = [ast.unparse(e) for e in node.value.elts
                       if not (isinstance(e, ast.Constant) and isinstance(e.value, str))]
                assert not bad, f'non-string __all__ entries: {bad}'

    @pytest.mark.parametrize('name', ['cannlytics.utils', 'cannlytics.metrc', 'cannlytics.stats',
                                      'cannlytics.ai', 'cannlytics.data.cache', 'cannlytics.auth',
                                      'cannlytics.constants', 'cannlytics.clean', 'cannlytics.licenses',
                                      'cannlytics.datasets', 'cannlytics.schema', 'cannlytics.collect'])
    def test_every_name_in_all_resolves(self, name):
        module = importlib.import_module(name)
        assert [n for n in module.__all__ if not hasattr(module, n)] == []

class TestVersion:

    def test_one_source_of_truth(self):
        import tomllib
        pyproject = tomllib.loads((ROOT.parent / 'pyproject.toml').read_text(encoding='utf-8'))
        assert 'version' not in pyproject['project'], 'pyproject.toml restates the version'
        assert 'version' in pyproject['project']['dynamic']
        assert pyproject['tool']['setuptools']['dynamic']['version'] == {'attr': 'cannlytics.__version__'}
        assert re.fullmatch(r'\d+\.\d+\.\d+((a|b|rc)\d+)?(\.dev\d+)?', cannlytics.__version__)

    def test_changelog_has_an_entry_for_this_version(self):
        # Between releases, main carries x.y.z.devN with an
        # "## [x.y.z] — Unreleased" entry (see RELEASING.md).
        import re
        version = cannlytics.__version__
        assert re.fullmatch(r'\d+\.\d+\.\d+(\.dev\d+)?', version), version
        changelog = (ROOT.parent / 'CHANGELOG.md').read_text(encoding='utf-8')
        release = re.sub(r'\.dev\d+$', '', version)
        assert f'## [{release}]' in changelog
        if release != version:
            assert f'## [{release}] — Unreleased' in changelog

class TestHygiene:

    def test_no_print_in_library_code(self):
        offenders = []
        for path in ROOT.rglob('*.py'):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            mains = [(n.lineno, max(getattr(x, 'lineno', n.lineno) for x in ast.walk(n)))
                     for n in ast.walk(tree) if isinstance(n, ast.If) and isinstance(n.test, ast.Compare)
                     and getattr(n.test.left, 'id', '') == '__name__']
            # Helpers only ever called from a __main__ demo block may print.
            demo = {n.name for n in tree.body if isinstance(n, ast.FunctionDef)
                    and n.name.startswith(('_demo', 'demo_', '_cli', '_main', 'main'))}
            for func in (n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name in demo):
                mains.append((func.lineno, max(getattr(x, 'lineno', func.lineno) for x in ast.walk(func))))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'print' \
                        and not any(a <= node.lineno <= b for a, b in mains):
                    offenders.append(f'{path.relative_to(ROOT.parent)}:{node.lineno}')
        assert offenders == []

    def test_no_basic_config_in_library_code(self):
        # A library never configures the application's root logger. A
        # module's own `if __name__ == '__main__':` demo block may.
        offenders = []
        for path in ROOT.rglob('*.py'):
            tree = ast.parse(path.read_text(encoding='utf-8'))
            mains = [(n.lineno, max(getattr(x, 'lineno', n.lineno) for x in ast.walk(n)))
                     for n in ast.walk(tree) if isinstance(n, ast.If) and isinstance(n.test, ast.Compare)
                     and getattr(n.test.left, 'id', '') == '__name__']
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and getattr(node.func, 'attr', '') == 'basicConfig' \
                        and not any(a <= node.lineno <= b for a, b in mains):
                    offenders.append(f'{path.relative_to(ROOT.parent)}:{node.lineno}')
        assert offenders == []

    def test_coas_imports_on_a_core_install(self):
        # pdfplumber is optional at import time; parsing needs the `coa` extra.
        result = run_blocked('''
            import cannlytics.data.coas as coas
            assert coas.COAdoc
            print('ok')
        ''')
        assert result.stdout.strip() == 'ok', result.stderr[-2000:]
