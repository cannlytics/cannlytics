"""
`.env.example` is complete, both ways
=====================================
Every environment variable the package reads is documented there, and
every variable documented there has a reader: the package, a dependency
it drives, or (the Metrc names) your own scripts, by convention.
"""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]

READS = [
    r"os\.environ\.get\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]",
    r"os\.getenv\(\s*['\"]([A-Z][A-Z0-9_]+)['\"]",
    r"os\.environ\[\s*['\"]([A-Z][A-Z0-9_]+)['\"]\s*\]",
    r"\.get\(\s*['\"]([A-Z][A-Z0-9_]+_(?:KEY|PATH|DIR|DATASET|CREDENTIALS))['\"]",
    r"['\"]env_key['\"]\s*:\s*['\"]([A-Z][A-Z0-9_]+)['\"]",
    r"_ENV\s*=\s*['\"]([A-Z][A-Z0-9_]+)['\"]",
]
SYSTEM = {'PATH', 'PATHEXT'}
READ_ELSEWHERE = {
    'FRED_API_KEY': 'the fredapi library',
    'GEMINI_API_KEY': 'the Google GenAI SDK',
    'METRC_VENDOR_API_KEY': 'your scripts (a naming convention)', 'METRC_USER_API_KEY': 'your scripts (a naming convention)',
    'METRC_LICENSE_NUMBER': 'your scripts (a naming convention)', 'METRC_STATE': 'your scripts (a naming convention)',
}

def package_reads():
    names = set()
    for path in (ROOT / 'cannlytics').rglob('*.py'):
        text = path.read_text(encoding='utf-8', errors='ignore')
        for pattern in READS:
            names.update(re.findall(pattern, text))
    return names - SYSTEM

def documented():
    text = (ROOT / '.env.example').read_text(encoding='utf-8')
    return set(re.findall(r'^#?\s*([A-Z][A-Z0-9_]+)=', text, re.M))

def test_every_variable_the_package_reads_is_documented():
    assert sorted(package_reads() - documented()) == []

def test_every_documented_variable_has_a_reader():
    assert sorted(documented() - package_reads() - set(READ_ELSEWHERE)) == []

def test_the_scan_sees_the_known_readers():
    # Guards the scan itself: if these vanish, the patterns broke.
    assert {'ANTHROPIC_API_KEY', 'GOOGLE_MAPS_API_KEY', 'QRUSTIE_PATH', 'CANNLYTICS_QRUSTIE_ALLOW_CWD',
            'CANNLYTICS_RESULTS_DATASET', 'GOOGLE_APPLICATION_CREDENTIALS'} <= package_reads()

def test_it_ships_and_holds_no_values():
    assert '.env.example' in (ROOT / 'MANIFEST.in').read_text(encoding='utf-8')
    values = re.findall(r'^([A-Z][A-Z0-9_]+)=(.+)$', (ROOT / '.env.example').read_text(encoding='utf-8'), re.M)
    assert values == [], 'an example file must not carry a value'
