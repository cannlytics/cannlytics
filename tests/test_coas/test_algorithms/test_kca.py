"""
Validation & regression tests for kca.py (KCA Laboratories COA parser).

Encodes the guide-specified expected values and the four doctrine
fixtures the Kentucky integration guide requires:
    - null-vs-zero (ND/<LOQ/NT -> None, never 0.0)
    - failing results preserved (Salmonella / Aspergillus / Y&M fail)
    - Sample-ID reuse deduplicated by pdf_hash (not sample_id)
    - decarboxylation arithmetic (0.877 * THCa + d9-THC == printed Total THC)

Run:
    python test_kca.py                      # pytest-free, self-contained
    pytest test_kca.py -v                   # or under pytest
"""
import hashlib
import json
import os
import sys

from cannlytics.data.coas.algorithms import kca

HERE = os.path.dirname(os.path.abspath(__file__))
KY = os.path.join(HERE, 'ky')

CLEAN = os.path.join(KY, 'KY-2025-12-05_17-42-30-1A4220100000259000000084_1.pdf')
SCRAMBLED = os.path.join(KY, 'KY-2025-11-26_18-30-03-1A4220100000259000000081_1.pdf')

_cache = {}


def parse(fp):
    if fp not in _cache:
        _cache[fp] = kca.parse_kca_coa(None, fp)
    return _cache[fp]


def results(fp):
    return json.loads(parse(fp)['results'])


def by_key(fp, analysis, key):
    for r in results(fp):
        if r['analysis'] == analysis and r['key'] == key:
            return r
    return None


def full_sha256(fp):
    h = hashlib.sha256()
    with open(fp, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


# ── Metadata & identity ────────────────────────────────────────────

def test_lab_identity():
    d = parse(CLEAN)
    assert d['lab'] == 'KCA Laboratories'
    assert d['lab_license_number'] == 'P_0058'
    assert d['lab_state'] == 'KY'


def test_product_and_strain():
    d = parse(CLEAN)
    assert d['product_name'] == 'Stella Blue-2025-09-09'
    assert d['strain_name'] == 'Stella Blue'          # date stripped
    assert d['product_type'] == 'flower'              # from "Plant - Flower"


def test_producer_and_metrc():
    d = parse(CLEAN)
    assert d['producer'] == 'Armory Kentucky LLC'
    assert d['producer_license_number'] == 'CULT0009033'
    assert d['metrc_id'] == '1A4220100000259000000084'
    assert d['sample_id'] == 'SA-251119-72867'
    assert d['date_tested'] == '11/26/2025'


# ── Cannabinoid totals & decarb arithmetic ─────────────────────────

def test_total_thc_printed():
    # Printed Total THC on the summary strip is 16.46%.
    assert parse(CLEAN)['total_thc'] == 16.46


def test_decarb_arithmetic():
    # Guide fixture: 0.877 * 12.14 (THCa) + 5.81 (d9) == 16.46 (Total THC).
    thca = by_key(CLEAN, 'cannabinoids', 'thca')['value']
    d9 = by_key(CLEAN, 'cannabinoids', 'delta_9_thc')['value']
    computed = round(0.877 * thca + d9, 2)
    assert abs(computed - 16.46) <= 0.02, computed
    # And the parser's own fallback matches within rounding.
    assert abs(kca._compute_total_thc(results(CLEAN)) - 16.46) <= 0.02


def test_total_thc_fallback_when_not_printed():
    # Simulate a COA with no printed total (biomass-style): the decarb
    # fallback must reconstruct it from the acid + neutral forms.
    fake = [
        {'analysis': 'cannabinoids', 'key': 'thca', 'value': 29.77},
        {'analysis': 'cannabinoids', 'key': 'delta_9_thc', 'value': 0.195},
    ]
    assert kca._compute_total_thc(fake) == round(0.877 * 29.77 + 0.195, 4)


# ── NULL vs ZERO doctrine ──────────────────────────────────────────

def test_total_cbd_is_null_not_zero():
    # Summary strip prints ND for Total CBD; the detail table prints a
    # literal "0". The strip (None) must win -- never 0.0.
    d = parse(CLEAN)
    assert d['total_cbd'] is None
    d2 = parse(SCRAMBLED)
    assert d2['total_cbd'] is None


def test_nd_analytes_serialize_null():
    # Delta-8-THC is ND on the cannabinoid table.
    d8 = by_key(CLEAN, 'cannabinoids', 'delta_8_thc')
    assert d8['value'] is None
    assert d8['result_raw'] == 'ND'


def test_below_loq_serializes_null_but_flagged():
    # CBD is ND, CBDA is <LOQ, CBG is <LOQ -> all None, raw preserved.
    cbda = by_key(CLEAN, 'cannabinoids', 'cbda')
    assert cbda['value'] is None
    assert cbda['result_raw'] == '<LOQ'


def test_no_zero_values_leak_from_nondetects():
    # No cannabinoid/terpene/pesticide result should be exactly 0.0
    # (they should be None instead). A real measured 0 does not occur
    # in this corpus; a 0.0 here would signal a null-vs-zero regression.
    for r in results(CLEAN):
        if r['analysis'] in ('cannabinoids', 'terpenes', 'pesticides'):
            assert r['value'] != 0.0, r


# ── Failing results preserved ──────────────────────────────────────

def test_microbial_fails_preserved():
    # Guide fixture: Stella Blue fails microbials hard.
    salm = by_key(CLEAN, 'microbials', 'salmonella')
    asp = by_key(CLEAN, 'microbials', 'pathogenic_aspergillus')
    ym = by_key(CLEAN, 'microbials', 'yeast_and_mold')
    assert salm['status'] == 'Fail'
    assert salm['qualitative'] == 'Detected'
    assert asp['status'] == 'Fail'
    assert ym['status'] == 'Fail'
    assert ym['value'] == 11000.0            # quantitative fail preserved


def test_overall_status_is_fail():
    # Any failing analysis -> overall fail. COA is NOT filtered out.
    assert parse(CLEAN)['status'] == 'fail'


# ── Sample-ID reuse deduped by hash, not sample_id ─────────────────

def test_sample_id_reuse_distinct_by_hash():
    # Both COAs share Sample ID SA-251119-72867 but are distinct samples.
    a, b = parse(CLEAN), parse(SCRAMBLED)
    assert a['sample_id'] == b['sample_id'] == 'SA-251119-72867'
    # Distinct Metrc tags & batches prove they are different samples...
    assert a['metrc_id'] != b['metrc_id']
    assert a['batch_number'] != b['batch_number']
    # ...and the canonical dedup key (full-file SHA-256) differs.
    assert full_sha256(CLEAN) != full_sha256(SCRAMBLED)


# ── Scramble resilience ────────────────────────────────────────────

def test_scramble_resilient_cannabinoids():
    # The scrambled ...081 must yield the same key cannabinoid values
    # as the clean ...084 (both are Stella Blue potency).
    for fp in (CLEAN, SCRAMBLED):
        assert by_key(fp, 'cannabinoids', 'delta_9_thc')['value'] == 5.81
        assert parse(fp)['total_thc'] == 16.46


# ── Analysis coverage ──────────────────────────────────────────────

def test_all_analyses_present():
    got = set(json.loads(parse(CLEAN)['analyses']))
    expected = {'cannabinoids', 'terpenes', 'heavy_metals', 'pesticides',
                'mycotoxins', 'microbials', 'vitamin_e_acetate',
                'moisture', 'water_activity'}
    assert expected <= got, expected - got


def test_pesticide_two_column_fully_captured():
    # KCA pesticide panel is 57 analytes across two columns.
    pest = [r for r in results(CLEAN) if r['analysis'] == 'pesticides']
    assert len(pest) == 57, len(pest)
    # Right-column analyte must be present (proves both columns parsed).
    assert by_key(CLEAN, 'pesticides', 'trifloxystrobin') is not None


def test_heavy_metals_values():
    assert by_key(CLEAN, 'heavy_metals', 'arsenic')['value'] == 0.023
    assert by_key(CLEAN, 'heavy_metals', 'mercury')['value'] is None  # ND


# ── Runner ─────────────────────────────────────────────────────────

def _run():
    tests = [v for k, v in sorted(globals().items())
             if k.startswith('test_') and callable(v)]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f'  PASS  {t.__name__}')
            passed += 1
        except AssertionError as e:
            print(f'  FAIL  {t.__name__}: {e}')
            failed += 1
        except Exception as e:
            print(f'  ERROR {t.__name__}: {type(e).__name__}: {e}')
            failed += 1
    print(f'\n{passed}/{passed + failed} tests passed'
          + (f', {failed} FAILED' if failed else ''))
    return failed == 0


if __name__ == '__main__':
    sys.exit(0 if _run() else 1)
