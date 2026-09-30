"""
The shipped readmes document code that exists
=============================================
The readmes inside the package reach users through the wheel. In 1.0.5
they documented 48 functions and methods that no longer existed; these
tests keep that from happening again.
"""
import importlib
import pathlib
import re

import pytest

PACKAGE = pathlib.Path(__file__).resolve().parents[2] / 'cannlytics'
READMES = sorted(PACKAGE.rglob('*.md'))

def _defined_names():
    names = set()
    for path in PACKAGE.rglob('*.py'):
        text = path.read_text(encoding='utf-8', errors='ignore')
        names.update(re.findall(r'^\s*(?:async\s+)?def (\w+)\(', text, re.M))
        names.update(re.findall(r'^\s*class (\w+)', text, re.M))
    return names

DEFINED = _defined_names()

@pytest.mark.parametrize('readme', READMES, ids=lambda p: str(p.relative_to(PACKAGE)))
def test_every_documented_callable_is_defined(readme):
    documented = set(re.findall(r'`(\w+)\(', readme.read_text(encoding='utf-8')))
    assert sorted(documented - DEFINED) == []

@pytest.mark.parametrize('readme', READMES, ids=lambda p: str(p.relative_to(PACKAGE)))
def test_every_import_in_a_readme_resolves(readme):
    for module, names in re.findall(r'from (cannlytics[\w.]*) import \(?([\w,\s]+?)\)?\s*$', readme.read_text(encoding='utf-8'), re.M):
        try:
            imported = importlib.import_module(module)
        except ImportError as error:
            pytest.skip(f'{module} needs an extra here: {error}')
        for name in (n.strip() for n in names.split(',')):
            if name:
                assert hasattr(imported, name), f'{module}.{name}'

def test_readmes_link_absolutely():
    # Relative links break on PyPI, where READMEs are rendered.
    for readme in READMES:
        relative = re.findall(r'\]\((?!https?://|#|mailto:)([^)]+)\)', readme.read_text(encoding='utf-8'))
        assert relative == [], f'{readme.relative_to(PACKAGE)}: {relative}'
